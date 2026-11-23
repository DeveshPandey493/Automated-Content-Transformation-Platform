import datetime
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.db.models.document import Document
from app.db.models.job import TransformationJob
from app.db.models.output import GeneratedOutput
from app.ml.registry import get_model_registry
from app.schemas.model import GenerationConfig
from app.services.transformation.constraints import ConstraintValidator
from app.services.verification.service import VerificationService
from app.core.exceptions import JobNotFoundError, DocumentNotFoundError

logger = logging.getLogger("actp.pipelines.transformation")

LENGTH_MAPPING = {
    "SHORT": 120,
    "MEDIUM": 250,
    "DETAILED": 500,
    "CUSTOM": 300,
}

class TransformationPipeline:
    @staticmethod
    def run_transformation_job(
        job_id: str,
        db: Session,
    ) -> TransformationJob:
        """
        Executes end-to-end transformation pipeline for a job:
        1. Loads source document and chunks
        2. Configures target length budget and constraints
        3. Invokes each requested model from ModelRegistry
        4. Evaluates controllability constraints
        5. Runs factual verification audit per output
        6. Persists all outputs and updates job status
        """
        job = db.get(TransformationJob, job_id)
        if not job:
            raise JobNotFoundError(job_id)

        doc = job.document
        if not doc:
            raise DocumentNotFoundError(job.document_id)

        job.status = "PROCESSING"
        db.commit()

        target_words = job.custom_word_limit if job.length_target == "CUSTOM" and job.custom_word_limit else LENGTH_MAPPING.get(job.length_target, 250)

        config = GenerationConfig(
            format_type=job.format_type,
            audience=job.audience,
            tone=job.tone,
            target_length_words=target_words,
            required_keywords=job.required_keywords or [],
            prohibited_terms=job.prohibited_terms or [],
        )

        registry = get_model_registry()
        # Source chunks metadata for model context
        chunks_data = [
            {"chunk_index": c.chunk_index, "text": c.text, "page_number": c.page_number}
            for c in doc.chunks
        ]

        # Extract model IDs from job metadata or default to textrank
        # Note: model_ids were passed during creation
        model_ids = job.required_keywords_or_extra if hasattr(job, "model_ids") else None

        generated_any = False
        error_msgs = []

        # If job doesn't explicitly store model_ids, use active models
        # For our pipeline, we can check outputs already created or run registered models
        target_model_ids = getattr(job, "_requested_model_ids", ["extractive/textrank"])

        for mid in target_model_ids:
            try:
                model = registry.get_model(mid)
                logger.info(f"Executing model '{mid}' for job '{job_id}'...")

                result = model.generate(
                    source_text=doc.cleaned_text,
                    config=config,
                    source_chunks=chunks_data,
                )

                # Determine model provider label
                if "extractive" in mid:
                    provider_label = "LOCAL_EXTRACTIVE"
                elif "groq" in mid:
                    provider_label = "GROQ"
                else:
                    provider_label = "LOCAL_SEQ2SEQ"

                # Check constraints
                constraints_eval = ConstraintValidator.evaluate_constraints(
                    content=result.content,
                    target_words=target_words,
                    required_keywords=job.required_keywords or [],
                    prohibited_terms=job.prohibited_terms or [],
                    format_type=job.format_type,
                )

                output_record = GeneratedOutput(
                    job_id=job.id,
                    model_id=result.model_id,
                    model_provider=provider_label,
                    version=1,
                    content=result.content,
                    word_count=result.word_count,
                    generation_latency_ms=result.latency_ms,
                    input_tokens=result.input_tokens,
                    output_tokens=result.output_tokens,
                    estimated_cost_usd=result.estimated_cost_usd,
                    generation_params={
                        "target_words": target_words,
                        "audience": job.audience,
                        "tone": job.tone,
                        "format_type": job.format_type,
                        "constraints_eval": constraints_eval,
                        **result.extra,
                    },
                )
                db.add(output_record)
                db.flush()

                # Automatically trigger factual verification
                try:
                    VerificationService.verify_output(output_record.id, db)
                except Exception as ve:
                    logger.warning(f"Verification warning for output '{output_record.id}': {ve}")

                generated_any = True

            except Exception as e:
                logger.error(f"Error executing model '{mid}' on job '{job_id}': {e}", exc_info=True)
                error_msgs.append(f"{mid}: {str(e)}")

        if generated_any:
            job.status = "COMPLETED"
            job.completed_at = datetime.datetime.utcnow()
            if error_msgs:
                job.error_message = "; ".join(error_msgs)
        else:
            job.status = "FAILED"
            job.error_message = "; ".join(error_msgs) or "No models succeeded in generating content."

        db.commit()
        db.refresh(job)
        return job
