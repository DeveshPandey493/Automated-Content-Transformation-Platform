from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, generate_uuid

class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    output_id: Mapped[str] = mapped_column(String(36), ForeignKey("generated_outputs.id", ondelete="CASCADE"), unique=True, nullable=False)
    rouge_1_f1: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rouge_2_f1: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rouge_l_f1: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    bert_score_f1: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    key_fact_coverage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    entity_coverage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    numerical_coverage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    controllability_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    detailed_metrics: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    output: Mapped["GeneratedOutput"] = relationship("GeneratedOutput", back_populates="evaluation_result")

class HumanFeedback(Base):
    __tablename__ = "human_feedbacks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    output_id: Mapped[str] = mapped_column(String(36), ForeignKey("generated_outputs.id", ondelete="CASCADE"), nullable=False, index=True)
    rating_accuracy: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 to 5
    rating_completeness: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 to 5
    rating_readability: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 to 5
    rating_suitability: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 to 5
    reviewer_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    output: Mapped["GeneratedOutput"] = relationship("GeneratedOutput", back_populates="human_feedbacks")
