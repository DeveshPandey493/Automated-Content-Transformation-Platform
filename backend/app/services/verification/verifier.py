import re
from typing import Dict, Any, List, Tuple
from app.db.models.document import DocumentChunk

class FactVerifier:
    """Verifies factual claims against retrieved evidence passages."""

    @staticmethod
    def verify_claim(
        claim_data: Dict[str, Any],
        evidence_pairs: List[Tuple[DocumentChunk, float]],
    ) -> Dict[str, Any]:
        """
        Classifies claim into SUPPORTED, PARTIALLY_SUPPORTED, UNSUPPORTED, CONTRADICTED, or REQUIRES_HUMAN_REVIEW.
        """
        claim_text = claim_data["claim_text"]
        numbers = claim_data.get("numbers", [])
        dates = claim_data.get("dates", [])
        entities = claim_data.get("entities", [])

        if not evidence_pairs or evidence_pairs[0][1] < 0.15:
            return {
                "status": "UNSUPPORTED",
                "confidence_score": 0.2,
                "explanation": "No relevant supporting passages found in the source document.",
                "evidence": []
            }

        top_chunk, top_score = evidence_pairs[0]
        combined_evidence = " ".join([c.text for c, _ in evidence_pairs[:2]])

        # 1. Number & Date Verification
        unmatched_numbers = []
        matched_numbers = []
        for num in numbers:
            # Clean number string for matching
            num_clean = num.replace(",", "").strip()
            if num_clean.lower() in combined_evidence.lower().replace(",", ""):
                matched_numbers.append(num)
            else:
                unmatched_numbers.append(num)

        unmatched_dates = []
        matched_dates = []
        for dt in dates:
            if dt.lower() in combined_evidence.lower():
                matched_dates.append(dt)
            else:
                unmatched_dates.append(dt)

        # 2. Entity Overlap
        matched_entities = []
        unmatched_entities = []
        for ent in entities:
            if ent.lower() in combined_evidence.lower():
                matched_entities.append(ent)
            else:
                unmatched_entities.append(ent)

        # 3. Status Decision Matrix
        # Contradiction Check: If claim has numbers that fail to match despite high semantic relevance
        if numbers and len(unmatched_numbers) > 0 and top_score > 0.45:
            status = "CONTRADICTED"
            confidence = 0.85
            explanation = (
                f"Numerical discrepancy detected: '{', '.join(unmatched_numbers)}' "
                f"was cited, but source passage states different figures in the same context."
            )

        elif numbers and len(matched_numbers) == len(numbers) and top_score >= 0.4:
            status = "SUPPORTED"
            confidence = min(0.98, top_score + 0.3)
            explanation = (
                f"Direct factual alignment: All quantitative figures ({', '.join(matched_numbers)}) "
                f"and semantic context match source Chunk #{top_chunk.chunk_index}."
            )

        elif top_score >= 0.60:
            if unmatched_entities:
                status = "PARTIALLY_SUPPORTED"
                confidence = 0.70
                explanation = f"High semantic similarity, but entity '{', '.join(unmatched_entities)}' is not explicitly corroborated."
            else:
                status = "SUPPORTED"
                confidence = round(min(0.95, top_score + 0.25), 2)
                explanation = f"Corroborated by source passage in Chunk #{top_chunk.chunk_index}."

        elif top_score >= 0.30:
            status = "PARTIALLY_SUPPORTED"
            confidence = round(top_score, 2)
            explanation = f"Broad context present in Chunk #{top_chunk.chunk_index}, but specific assertion lacks complete corroboration."

        else:
            status = "REQUIRES_HUMAN_REVIEW"
            confidence = 0.45
            explanation = "Complex or inferential statement with marginal evidence match. Expert human verification recommended."

        # Format evidence list
        evidence_list = [
            {
                "chunk_id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "relevance_score": round(score, 3),
                "text": chunk.text,
                "page_number": chunk.page_number,
                "section_heading": chunk.section_heading,
            }
            for chunk, score in evidence_pairs[:2]
        ]

        return {
            "status": status,
            "confidence_score": round(confidence, 2),
            "explanation": explanation,
            "evidence": evidence_list,
        }
