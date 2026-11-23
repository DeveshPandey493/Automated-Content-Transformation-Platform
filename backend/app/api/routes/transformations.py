from typing import List
from fastapi import APIRouter, Depends, Query, BackgroundTasks, status
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.db.session import get_db
from app.db.models.document import Document
from app.db.models.job import TransformationJob
from app.db.models.output import GeneratedOutput
from app.core.exceptions import DocumentNotFoundError, JobNotFoundError
from app.schemas.transformation import (
    TransformationCreateRequest,
    TransformationJobResponse,
    GeneratedOutputResponse,
)
from app.pipelines.transformation_pipeline import TransformationPipeline

router = APIRouter(prefix="/transformations", tags=["Transformations"])

@router.post("", response_model=TransformationJobResponse, status_code=status.HTTP_201_CREATED)
def create_transformation(
    payload: TransformationCreateRequest,
    db: Session = Depends(get_db)
):
    doc = db.get(Document, payload.document_id)
    if not doc:
        raise DocumentNotFoundError(payload.document_id)

    job = TransformationJob(
        document_id=payload.document_id,
        format_type=payload.format_type,
        audience=payload.audience,
        tone=payload.tone,
        length_target=payload.length_target,
        custom_word_limit=payload.custom_word_limit,
        required_keywords=payload.required_keywords,
        prohibited_terms=payload.prohibited_terms,
        status="PENDING",
    )
    # Stash requested model_ids on transient attribute
    setattr(job, "_requested_model_ids", payload.model_ids or ["extractive/textrank"])

    db.add(job)
    db.commit()
    db.refresh(job)

    # Execute transformation pipeline synchronously for now or via threadpool
    # (Fast execution for extractive, neural and groq)
    setattr(job, "_requested_model_ids", payload.model_ids or ["extractive/textrank"])
    completed_job = TransformationPipeline.run_transformation_job(job.id, db)
    return completed_job

@router.get("/{job_id}", response_model=TransformationJobResponse)
def get_transformation(
    job_id: str,
    db: Session = Depends(get_db)
):
    job = db.get(TransformationJob, job_id)
    if not job:
        raise JobNotFoundError(job_id)
    return job

@router.get("/{job_id}/results", response_model=List[GeneratedOutputResponse])
def get_transformation_results(
    job_id: str,
    db: Session = Depends(get_db)
):
    job = db.get(TransformationJob, job_id)
    if not job:
        raise JobNotFoundError(job_id)
    return job.outputs

@router.get("", response_model=List[TransformationJobResponse])
def list_transformations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    stmt = (
        select(TransformationJob)
        .order_by(desc(TransformationJob.created_at))
        .offset(skip)
        .limit(limit)
    )
    jobs = db.scalars(stmt).all()
    return jobs
