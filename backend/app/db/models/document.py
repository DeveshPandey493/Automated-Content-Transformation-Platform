from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import String, Integer, Text, JSON, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, generate_uuid, TimestampMixin

class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)  # FILE_UPLOAD, PASTED_TEXT, URL
    file_type: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)  # pdf, docx, txt, html
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_hash: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    raw_file_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    total_pages: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    total_characters: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_words: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cleaned_text: Mapped[str] = mapped_column(Text, nullable=False)
    meta_info: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Relationships
    chunks: Mapped[List["DocumentChunk"]] = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan", order_by="DocumentChunk.chunk_index"
    )
    jobs: Mapped[List["TransformationJob"]] = relationship(
        "TransformationJob", back_populates="document", cascade="all, delete-orphan"
    )

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    section_heading: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    char_start: Mapped[int] = mapped_column(Integer, nullable=False)
    char_end: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="chunks")
    evidence_references: Mapped[List["EvidenceReference"]] = relationship(
        "EvidenceReference", back_populates="chunk", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_chunks_doc_idx", "document_id", "chunk_index"),
    )
