from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.db.models.output import GeneratedOutput
from app.db.models.evaluation import HumanFeedback


class VersioningService:
    """Manages output versioning and revision history."""

    @staticmethod
    def create_new_version(
        db: Session,
        original_output: GeneratedOutput,
        new_content: str,
        editor_notes: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> GeneratedOutput:
        """Create a new version of an output with edited content."""
        # Calculate new version number
        latest_version = db.scalars(
            select(GeneratedOutput.version)
            .where(GeneratedOutput.parent_output_id == original_output.id)
            .order_by(desc(GeneratedOutput.version))
        ).first()

        new_version = (latest_version or original_output.version) + 1

        # Create new version record
        new_output = GeneratedOutput(
            job_id=original_output.job_id,
            model_id=original_output.model_id,
            model_provider=original_output.model_provider,
            version=new_version,
            parent_output_id=original_output.id,
            content=new_content,
            word_count=len(new_content.split()),
            generation_latency_ms=0.0,  # Manual edit, no generation latency
            input_tokens=0,
            output_tokens=0,
            estimated_cost_usd=0.0,
            is_approved=False,
            generation_params={
                **original_output.generation_params,
                "edited_from_version": original_output.version,
                "editor_notes": editor_notes,
                "edited_by": user_id,
                "edited_at": datetime.utcnow().isoformat(),
            },
        )
        db.add(new_output)
        db.commit()
        db.refresh(new_output)
        return new_output

    @staticmethod
    def get_version_history(db: Session, output_id: str) -> List[GeneratedOutput]:
        """Get complete version history for an output (including original and all edits)."""
        # Get original output
        original = db.get(GeneratedOutput, output_id)
        if not original:
            return []

        # If this is a child version, find the root
        root_id = original.parent_output_id or original.id

        # Get all versions in the tree using recursive CTE
        # First get the root
        root = db.get(GeneratedOutput, root_id)
        if not root:
            return []

        # Build version tree iteratively
        all_versions = [root]
        to_process = [root.id]

        while to_process:
            current_id = to_process.pop(0)
            children = db.scalars(
                select(GeneratedOutput)
                .where(GeneratedOutput.parent_output_id == current_id)
                .order_by(GeneratedOutput.version)
            ).all()
            for child in children:
                all_versions.append(child)
                to_process.append(child.id)

        # Sort by version
        all_versions.sort(key=lambda v: v.version)
        return all_versions

    @staticmethod
    def get_version(db: Session, output_id: str) -> Optional[GeneratedOutput]:
        """Get a specific version by ID."""
        return db.get(GeneratedOutput, output_id)

    @staticmethod
    def compare_versions(db: Session, version_a_id: str, version_b_id: str) -> Dict[str, Any]:
        """Compare two versions and return diff information."""
        version_a = db.get(GeneratedOutput, version_a_id)
        version_b = db.get(GeneratedOutput, version_b_id)

        if not version_a or not version_b:
            raise ValueError("One or both versions not found")

        # Simple text diff
        lines_a = version_a.content.splitlines()
        lines_b = version_b.content.splitlines()

        added = [line for line in lines_b if line not in lines_a]
        removed = [line for line in lines_a if line not in lines_b]

        return {
            "version_a": {
                "id": version_a.id,
                "version": version_a.version,
                "created_at": version_a.created_at.isoformat(),
                "word_count": version_a.word_count,
            },
            "version_b": {
                "id": version_b.id,
                "version": version_b.version,
                "created_at": version_b.created_at.isoformat(),
                "word_count": version_b.word_count,
            },
            "diff": {
                "lines_added": len(added),
                "lines_removed": len(removed),
                "added_content": added[:20],  # Limit for response size
                "removed_content": removed[:20],
            },
            "word_count_change": version_b.word_count - version_a.word_count,
        }


class HumanFeedbackService:
    """Manages human feedback and ratings for outputs."""

    @staticmethod
    def submit_feedback(
        db: Session,
        output_id: str,
        rating_accuracy: int,
        rating_completeness: int,
        rating_readability: int,
        rating_suitability: int,
        reviewer_notes: Optional[str] = None,
        reviewer_id: Optional[str] = None
    ) -> HumanFeedback:
        """Submit human feedback for an output."""
        feedback = HumanFeedback(
            output_id=output_id,
            rating_accuracy=rating_accuracy,
            rating_completeness=rating_completeness,
            rating_readability=rating_readability,
            rating_suitability=rating_suitability,
            reviewer_notes=reviewer_notes,
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback

    @staticmethod
    def get_feedback_summary(db: Session, output_id: str) -> Dict[str, Any]:
        """Get aggregated feedback summary for an output."""
        feedbacks = db.scalars(
            select(HumanFeedback).where(HumanFeedback.output_id == output_id)
        ).all()

        if not feedbacks:
            return {
                "total_reviews": 0,
                "average_ratings": {},
                "latest_review": None,
            }

        avg_accuracy = sum(f.rating_accuracy for f in feedbacks) / len(feedbacks)
        avg_completeness = sum(f.rating_completeness for f in feedbacks) / len(feedbacks)
        avg_readability = sum(f.rating_readability for f in feedbacks) / len(feedbacks)
        avg_suitability = sum(f.rating_suitability for f in feedbacks) / len(feedbacks)

        return {
            "total_reviews": len(feedbacks),
            "average_ratings": {
                "accuracy": round(avg_accuracy, 2),
                "completeness": round(avg_completeness, 2),
                "readability": round(avg_readability, 2),
                "suitability": round(avg_suitability, 2),
                "overall": round((avg_accuracy + avg_completeness + avg_readability + avg_suitability) / 4, 2),
            },
            "latest_review": {
                "id": feedbacks[-1].id,
                "created_at": feedbacks[-1].created_at.isoformat(),
                "ratings": {
                    "accuracy": feedbacks[-1].rating_accuracy,
                    "completeness": feedbacks[-1].rating_completeness,
                    "readability": feedbacks[-1].rating_readability,
                    "suitability": feedbacks[-1].rating_suitability,
                },
                "notes": feedbacks[-1].reviewer_notes,
            } if feedbacks else None,
            "all_reviews": [
                {
                    "id": f.id,
                    "created_at": f.created_at.isoformat(),
                    "ratings": {
                        "accuracy": f.rating_accuracy,
                        "completeness": f.rating_completeness,
                        "readability": f.rating_readability,
                        "suitability": f.rating_suitability,
                    },
                    "notes": f.reviewer_notes,
                }
                for f in feedbacks
            ],
        }

    @staticmethod
    def get_all_feedback_for_job(db: Session, job_id: str) -> List[Dict[str, Any]]:
        """Get all feedback for all outputs of a job."""
        from app.db.models.job import TransformationJob
        from sqlalchemy.orm import joinedload

        job = db.get(TransformationJob, job_id)
        if not job:
            return []

        all_feedback = []
        for output in job.outputs:
            feedbacks = db.scalars(
                select(HumanFeedback).where(HumanFeedback.output_id == output.id)
            ).all()

            for f in feedbacks:
                all_feedback.append({
                    "output_id": output.id,
                    "output_version": output.version,
                    "model_id": output.model_id,
                    "feedback_id": f.id,
                    "created_at": f.created_at.isoformat(),
                    "ratings": {
                        "accuracy": f.rating_accuracy,
                        "completeness": f.rating_completeness,
                        "readability": f.rating_readability,
                        "suitability": f.rating_suitability,
                    },
                    "notes": f.reviewer_notes,
                })

        return sorted(all_feedback, key=lambda x: x["created_at"], reverse=True)