from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import String, Integer, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, generate_uuid, TimestampMixin

class TransformationJob(Base, TimestampMixin):
    __tablename__ = "transformation_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    format_type: Mapped[str] = mapped_column(String(32), nullable=False)  # EXECUTIVE_SUMMARY, PUBLIC_ADVISORY, SOCIAL_POST, FAQ
    audience: Mapped[str] = mapped_column(String(64), nullable=False)
    tone: Mapped[str] = mapped_column(String(64), nullable=False)
    length_target: Mapped[str] = mapped_column(String(32), nullable=False)  # SHORT, MEDIUM, DETAILED, CUSTOM
    custom_word_limit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    required_keywords: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    prohibited_terms: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="PENDING", nullable=False)  # PENDING, PROCESSING, COMPLETED, FAILED
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="jobs")
    outputs: Mapped[List["GeneratedOutput"]] = relationship(
        "GeneratedOutput", back_populates="job", cascade="all, delete-orphan"
    )
