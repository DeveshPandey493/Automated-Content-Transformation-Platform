import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.document import Document, DocumentChunk
from app.db.models.output import GeneratedOutput
from app.db.models.verification import ExtractedClaim, EvidenceReference, VerificationReport
from app.services.verification.claim_extractor import ClaimExtractor
from app.services.verification.evidence_retriever import EvidenceRetriever
from app.services.verification.verifier import FactVerifier

logger = logging.getLogger("actp.services.verification")

class VerificationService:
    @staticmethod
    def verify_output(
        output_id: str,
        db: Session,
    ) -> VerificationReport:
        """
        Runs full verification audit on a generated output.
        Extracts claims, matches evidence against source chunks, classifies factuality,
        and persists verification report.
        """
        output = db.get(GeneratedOutput, output_id)
        if not output:
            raise ValueError(f"Output '{output_id}' not found.")

        job = output.job
        document = job.document
        chunks = document.chunks

        # 1. Extract claims
        claims_data = ClaimExtractor.extract_claims(output.content)

        total_claims = len(claims_data)
        supported_count = 0
        partially_count = 0
        unsupported_count = 0
        contradicted_count = 0

        # Purge existing claims if re-running
        db.query(ExtractedClaim).filter(ExtractedClaim.output_id == output_id).delete()
        db.query(VerificationReport).filter(VerificationReport.output_id == output_id).delete()
        db.flush()

        for c_data in claims_data:
            # 2. Retrieve evidence chunks
            evidence_pairs = EvidenceRetriever.retrieve_evidence_chunks(
                claim_text=c_data["claim_text"],
                chunks=chunks,
                top_k=2
            )

            # 3. Verify claim
            verdict = FactVerifier.verify_claim(c_data, evidence_pairs)
            status = verdict["status"]

            if status == "SUPPORTED":
                supported_count += 1
            elif status == "PARTIALLY_SUPPORTED":
                partially_count += 1
            elif status == "UNSUPPORTED":
                unsupported_count += 1
            elif status == "CONTRADICTED":
                contradicted_count += 1

            # Persist Claim
            claim_record = ExtractedClaim(
                output_id=output.id,
                claim_text=c_data["claim_text"],
                claim_type=c_data["claim_type"],
                verification_status=status,
                confidence_score=verdict["confidence_score"],
                explanation=verdict["explanation"],
            )
            db.add(claim_record)
            db.flush()

            # Persist Evidence References
            for ev in verdict["evidence"]:
                ref = EvidenceReference(
                    claim_id=claim_record.id,
                    chunk_id=ev["chunk_id"],
                    relevance_score=ev["relevance_score"],
                    evidence_text=ev["text"],
                )
                db.add(ref)

        # 4. Compute Factual Consistency Score (FCS)
        if total_claims > 0:
            fcs = round((supported_count + 0.5 * partially_count) / total_claims, 3)
        else:
            fcs = 1.0

        summary = (
            f"Factual Audit Complete: {supported_count} Supported, {partially_count} Partially Supported, "
            f"{unsupported_count} Unsupported, {contradicted_count} Contradicted across {total_claims} atomic claims. "
            f"FCS: {fcs * 100:.1f}%."
        )

        report = VerificationReport(
            output_id=output.id,
            total_claims=total_claims,
            supported_claims=supported_count,
            partially_supported=partially_count,
            unsupported_claims=unsupported_count,
            contradicted_claims=contradicted_count,
            factual_consistency_score=fcs,
            summary=summary,
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        logger.info(f"Generated verification report for output '{output_id}': FCS={fcs}")
        return report
