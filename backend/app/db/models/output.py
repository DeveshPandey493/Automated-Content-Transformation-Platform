from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import String, Integer, Float, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, generate_uuid

class GeneratedOutput(Base):
    __tablename__ = "generated_outputs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("transformation_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    model_id: Mapped[str] = mapped_column(String(128), nullable=False)
    model_provider: Mapped[str] = mapped_column(String(64), nullable=False)  # LOCAL_EXTRACTIVE, LOCAL_SEQ2SEQ, GROQ
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    parent_output_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    generation_latency_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    generation_params: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    job: Mapped["TransformationJob"] = relationship("TransformationJob", back_populates="outputs")
    claims: Mapped[List["ExtractedClaim"]] = relationship(
        "ExtractedClaim", back_populates="output", cascade="all, delete-orphan"
    )
    verification_report: Mapped[Optional["VerificationReport"]] = relationship(
        "VerificationReport", back_populates="output", uselist=False, cascade="all, delete-orphan"
    )
    evaluation_result: Mapped[Optional["EvaluationResult"]] = relationship(
        "EvaluationResult", back_populates="output", uselist=False, cascade="all, delete-orphan"
    )
    human_feedbacks: Mapped[List["HumanFeedback"]] = relationship(
        "HumanFeedback", back_populates="output", cascade="all, delete-orphan"
    )
