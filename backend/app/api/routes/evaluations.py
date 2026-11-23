from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.db.models.output import GeneratedOutput
from app.db.models.evaluation import EvaluationResult, HumanFeedback
from app.db.models.dataset import DatasetDocument, ReferenceAnnotation
from app.db.models.job import TransformationJob
from app.core.exceptions import OutputNotFoundError
from app.schemas.evaluation import (
    EvaluationResultResponse,
    HumanFeedbackCreate,
    HumanFeedbackResponse,
    ComparisonMatrixResponse,
    ModelComparisonRow,
)
from app.services.evaluation.evaluator import OutputEvaluator

router = APIRouter(prefix="/evaluations", tags=["Evaluations"])

@router.post("/run/{output_id}", response_model=EvaluationResultResponse)
def evaluate_output_endpoint(
    output_id: str,
    db: Session = Depends(get_db)
):
    output = db.get(GeneratedOutput, output_id)
    if not output:
        raise OutputNotFoundError(output_id)

    # Check for matching dataset document references
    job = output.job
    doc = job.document

    # Try to find gold reference
    ref_text = None
    gold_facts = None
    gold_entities = None
    gold_numbers = None

    ds_doc = db.scalars(select(DatasetDocument).where(DatasetDocument.extracted_text == doc.cleaned_text)).first()
    if ds_doc:
        gold_facts = ds_doc.gold_key_facts
        gold_entities = ds_doc.gold_entities
        gold_numbers = ds_doc.gold_numbers
        ref = db.scalars(
            select(ReferenceAnnotation).where(
                ReferenceAnnotation.document_id == ds_doc.id,
                ReferenceAnnotation.format_type == job.format_type
            )
        ).first()
        if ref:
            ref_text = ref.reference_text

    evaluator = OutputEvaluator()
    eval_dict = evaluator.evaluate_output(
        output=output,
        reference_text=ref_text,
        gold_facts=gold_facts,
        gold_entities=gold_entities,
        gold_numbers=gold_numbers,
    )

    # Persist or update EvaluationResult
    record = output.evaluation_result
    if not record:
        record = EvaluationResult(output_id=output.id)
        db.add(record)

    record.rouge_1_f1 = eval_dict["rouge_1_f1"]
    record.rouge_2_f1 = eval_dict["rouge_2_f1"]
    record.rouge_l_f1 = eval_dict["rouge_l_f1"]
    record.bert_score_f1 = eval_dict["bert_score_f1"]
    record.key_fact_coverage = eval_dict["key_fact_coverage"]
    record.entity_coverage = eval_dict["entity_coverage"]
    record.numerical_coverage = eval_dict["numerical_coverage"]
    record.controllability_score = eval_dict["controllability_score"]
    record.detailed_metrics = eval_dict["detailed_metrics"]

    db.commit()
    db.refresh(record)
    return record

@router.get("/compare", response_model=ComparisonMatrixResponse)
def compare_models(
    output_ids: str = Query(..., description="Comma-separated output UUIDs"),
    db: Session = Depends(get_db)
):
    ids = [i.strip() for i in output_ids.split(",") if i.strip()]
    outputs = db.scalars(select(GeneratedOutput).where(GeneratedOutput.id.in_(ids))).all()
    if not outputs:
        raise OutputNotFoundError(output_ids)

    first_job = outputs[0].job
    first_doc = first_job.document

    rows = []
    evaluator = OutputEvaluator()

    for out in outputs:
        # Compute metrics if not present
        if not out.evaluation_result:
            eval_dict = evaluator.evaluate_output(output=out)
        else:
            er = out.evaluation_result
            eval_dict = {
                "rouge_1_f1": er.rouge_1_f1,
                "rouge_2_f1": er.rouge_2_f1,
                "rouge_l_f1": er.rouge_l_f1,
                "controllability_score": er.controllability_score,
            }

        report = out.verification_report
        fcs = report.factual_consistency_score if report else 1.0
        supported = report.supported_claims if report else 0
        total_claims = report.total_claims if report else 0

        rows.append(
            ModelComparisonRow(
                model_id=out.model_id,
                model_name=out.model_id.replace("extractive/", "").replace("seq2seq/", ""),
                provider=out.model_provider,
                content=out.content,
                word_count=out.word_count,
                latency_ms=out.generation_latency_ms,
                factual_consistency_score=fcs,
                supported_claims=supported,
                total_claims=total_claims,
                rouge_1_f1=eval_dict.get("rouge_1_f1", 0.0),
                rouge_2_f1=eval_dict.get("rouge_2_f1", 0.0),
                rouge_l_f1=eval_dict.get("rouge_l_f1", 0.0),
                controllability_score=eval_dict.get("controllability_score", 0.8),
                estimated_cost_usd=out.estimated_cost_usd,
            )
        )

    return ComparisonMatrixResponse(
        document_id=first_doc.id,
        document_title=first_doc.title,
        format_type=first_job.format_type,
        rows=rows,
    )

@router.post("/feedback", response_model=HumanFeedbackResponse)
def submit_human_feedback(
    payload: HumanFeedbackCreate,
    db: Session = Depends(get_db)
):
    output = db.get(GeneratedOutput, payload.output_id)
    if not output:
        raise OutputNotFoundError(payload.output_id)

    feedback = HumanFeedback(
        output_id=payload.output_id,
        rating_accuracy=payload.rating_accuracy,
        rating_completeness=payload.rating_completeness,
        rating_readability=payload.rating_readability,
        rating_suitability=payload.rating_suitability,
        reviewer_notes=payload.reviewer_notes,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.get("/compare-all")
def compare_all_models(db: Session = Depends(get_db)):
    """
    Returns all evaluation comparisons grouped by document and format type.
    Used by the Evaluation Dashboard UI.
    """
    # Get all outputs that have evaluation results or verification reports
    stmt = select(GeneratedOutput).join(TransformationJob).where(
        GeneratedOutput.evaluation_result != None
    )
    outputs_with_eval = db.scalars(stmt).all()

    # Also get outputs with verification reports (for factual consistency)
    stmt2 = select(GeneratedOutput).join(TransformationJob).where(
        GeneratedOutput.verification_report != None
    )
    outputs_with_verif = db.scalars(stmt2).all()

    # Combine unique outputs
    all_outputs = {o.id: o for o in outputs_with_eval}
    for o in outputs_with_verif:
        all_outputs[o.id] = o

    outputs_list = list(all_outputs.values())

    if not outputs_list:
        return []

    # Group by document_id + format_type
    groups = {}
    for out in outputs_list:
        job = out.job
        doc = job.document
        key = f"{doc.id}:{job.format_type}"
        if key not in groups:
            groups[key] = {
                "document_id": doc.id,
                "document_title": doc.title,
                "format_type": job.format_type,
                "rows": []
            }

        # Get evaluation metrics
        eval_dict = {}
        if out.evaluation_result:
            er = out.evaluation_result
            eval_dict = {
                "rouge_1_f1": er.rouge_1_f1,
                "rouge_2_f1": er.rouge_2_f1,
                "rouge_l_f1": er.rouge_l_f1,
                "controllability_score": er.controllability_score,
                "key_fact_coverage": er.key_fact_coverage,
                "entity_coverage": er.entity_coverage,
                "numerical_coverage": er.numerical_coverage,
            }

        # Get factual consistency from verification report
        report = out.verification_report
        fcs = report.factual_consistency_score if report else 1.0
        supported = report.supported_claims if report else 0
        total_claims = report.total_claims if report else 0

        groups[key]["rows"].append({
            "model_id": out.model_id,
            "model_name": out.model_id.replace("extractive/", "").replace("seq2seq/", ""),
            "provider": out.model_provider,
            "content": out.content[:500],  # truncate for response size
            "word_count": out.word_count,
            "latency_ms": out.generation_latency_ms,
            "factual_consistency_score": fcs,
            "supported_claims": supported,
            "total_claims": total_claims,
            "rouge_1_f1": eval_dict.get("rouge_1_f1", 0.0),
            "rouge_2_f1": eval_dict.get("rouge_2_f1", 0.0),
            "rouge_l_f1": eval_dict.get("rouge_l_f1", 0.0),
            "controllability_score": eval_dict.get("controllability_score", 0.8),
            "key_fact_coverage": eval_dict.get("key_fact_coverage", 0.0),
            "entity_coverage": eval_dict.get("entity_coverage", 0.0),
            "numerical_coverage": eval_dict.get("numerical_coverage", 0.0),
            "estimated_cost_usd": out.estimated_cost_usd,
        })

    return list(groups.values())
