from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.db.models.output import GeneratedOutput
from app.core.exceptions import OutputNotFoundError
from app.services.transformation.versioning import VersioningService, HumanFeedbackService


router = APIRouter(prefix="/versioning", tags=["Versioning & Human Feedback"])


# Request/Response Models
class CreateVersionRequest(BaseModel):
    new_content: str
    editor_notes: Optional[str] = None
    user_id: Optional[str] = None


class VersionResponse(BaseModel):
    id: str
    version: int
    parent_output_id: Optional[str]
    content: str
    word_count: int
    is_approved: bool
    generation_params: dict
    created_at: str

    class Config:
        from_attributes = True


class VersionHistoryResponse(BaseModel):
    versions: List[VersionResponse]


class CompareVersionsRequest(BaseModel):
    version_a_id: str
    version_b_id: str


class CompareVersionsResponse(BaseModel):
    version_a: dict
    version_b: dict
    diff: dict
    word_count_change: int


class HumanFeedbackRequest(BaseModel):
    output_id: str
    rating_accuracy: int = Field(..., ge=1, le=5)
    rating_completeness: int = Field(..., ge=1, le=5)
    rating_readability: int = Field(..., ge=1, le=5)
    rating_suitability: int = Field(..., ge=1, le=5)
    reviewer_notes: Optional[str] = None
    reviewer_id: Optional[str] = None


class HumanFeedbackResponse(BaseModel):
    id: str
    output_id: str
    rating_accuracy: int
    rating_completeness: int
    rating_readability: int
    rating_suitability: int
    reviewer_notes: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class FeedbackSummaryResponse(BaseModel):
    total_reviews: int
    average_ratings: dict
    latest_review: Optional[dict]
    all_reviews: List[dict]


# Endpoints
@router.post("/{output_id}/new-version", response_model=VersionResponse, status_code=status.HTTP_201_CREATED)
def create_new_version(
    output_id: str,
    request: CreateVersionRequest,
    db: Session = Depends(get_db)
):
    """Create a new version of an output with edited content."""
    original = db.get(GeneratedOutput, output_id)
    if not original:
        raise OutputNotFoundError(output_id)

    new_version = VersioningService.create_new_version(
        db=db,
        original_output=original,
        new_content=request.new_content,
        editor_notes=request.editor_notes,
        user_id=request.user_id
    )
    return new_version


@router.get("/{output_id}/history", response_model=VersionHistoryResponse)
def get_version_history(
    output_id: str,
    db: Session = Depends(get_db)
):
    """Get complete version history for an output."""
    original = db.get(GeneratedOutput, output_id)
    if not original:
        raise OutputNotFoundError(output_id)

    versions = VersioningService.get_version_history(db, output_id)
    return {"versions": versions}


@router.post("/compare", response_model=CompareVersionsResponse)
def compare_versions(
    request: CompareVersionsRequest,
    db: Session = Depends(get_db)
):
    """Compare two versions of an output."""
    try:
        result = VersioningService.compare_versions(db, request.version_a_id, request.version_b_id)
        return result
    except ValueError as e:
        raise OutputNotFoundError(str(e))


@router.post("/feedback", response_model=HumanFeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    request: HumanFeedbackRequest,
    db: Session = Depends(get_db)
):
    """Submit human feedback for an output."""
    output = db.get(GeneratedOutput, request.output_id)
    if not output:
        raise OutputNotFoundError(request.output_id)

    feedback = HumanFeedbackService.submit_feedback(
        db=db,
        output_id=request.output_id,
        rating_accuracy=request.rating_accuracy,
        rating_completeness=request.rating_completeness,
        rating_readability=request.rating_readability,
        rating_suitability=request.rating_suitability,
        reviewer_notes=request.reviewer_notes,
        reviewer_id=request.reviewer_id
    )
    return feedback


@router.get("/{output_id}/feedback", response_model=FeedbackSummaryResponse)
def get_feedback_summary(
    output_id: str,
    db: Session = Depends(get_db)
):
    """Get aggregated feedback summary for an output."""
    output = db.get(GeneratedOutput, output_id)
    if not output:
        raise OutputNotFoundError(output_id)

    summary = HumanFeedbackService.get_feedback_summary(db, output_id)
    return summary


@router.get("/job/{job_id}/feedback")
def get_job_feedback(
    job_id: str,
    db: Session = Depends(get_db)
):
    """Get all feedback for all outputs of a job."""
    from app.db.models.job import TransformationJob
    job = db.get(TransformationJob, job_id)
    if not job:
        raise OutputNotFoundError(job_id)

    feedback = HumanFeedbackService.get_all_feedback_for_job(db, job_id)
    return {"job_id": job_id, "feedback": feedback}