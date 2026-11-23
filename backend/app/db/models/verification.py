from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, generate_uuid

class ExtractedClaim(Base):
    __tablename__ = "extracted_claims"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    output_id: Mapped[str] = mapped_column(String(36), ForeignKey("generated_outputs.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    claim_type: Mapped[str] = mapped_column(String(32), default="GENERAL", nullable=False)  # NUMERICAL, DATE, ENTITY, POLICY, GENERAL
    verification_status: Mapped[str] = mapped_column(String(32), default="REQUIRES_HUMAN_REVIEW", nullable=False)
    # SUPPORTED, PARTIALLY_SUPPORTED, UNSUPPORTED, CONTRADICTED, REQUIRES_HUMAN_REVIEW
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    output: Mapped["GeneratedOutput"] = relationship("GeneratedOutput", back_populates="claims")
    evidence_references: Mapped[List["EvidenceReference"]] = relationship(
        "EvidenceReference", back_populates="claim", cascade="all, delete-orphan"
    )

class EvidenceReference(Base):
    __tablename__ = "evidence_references"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    claim_id: Mapped[str] = mapped_column(String(36), ForeignKey("extracted_claims.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_id: Mapped[str] = mapped_column(String(36), ForeignKey("document_chunks.id", ondelete="CASCADE"), nullable=False, index=True)
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    evidence_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    claim: Mapped["ExtractedClaim"] = relationship("ExtractedClaim", back_populates="evidence_references")
    chunk: Mapped["DocumentChunk"] = relationship("DocumentChunk", back_populates="evidence_references")

class VerificationReport(Base):
    __tablename__ = "verification_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    output_id: Mapped[str] = mapped_column(String(36), ForeignKey("generated_outputs.id", ondelete="CASCADE"), unique=True, nullable=False)
    total_claims: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    supported_claims: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    partially_supported: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unsupported_claims: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    contradicted_claims: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    factual_consistency_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    output: Mapped["GeneratedOutput"] = relationship("GeneratedOutput", back_populates="verification_report")
