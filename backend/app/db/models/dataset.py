from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, generate_uuid, TimestampMixin

class Dataset(Base, TimestampMixin):
    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str] = mapped_column(String(64), nullable=False)
    version: Mapped[str] = mapped_column(String(32), default="v1.0", nullable=False)

    # Relationships
    documents: Mapped[List["DatasetDocument"]] = relationship(
        "DatasetDocument", back_populates="dataset", cascade="all, delete-orphan"
    )

class DatasetDocument(Base, TimestampMixin):
    __tablename__ = "dataset_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    dataset_id: Mapped[str] = mapped_column(String(36), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    publisher: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    split: Mapped[str] = mapped_column(String(32), default="TEST", nullable=False)  # TRAIN, VALIDATION, TEST
    extracted_text: Mapped[str] = mapped_column(Text, nullable=False)
    gold_key_facts: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    gold_entities: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    gold_numbers: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    # Relationships
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="documents")
    reference_annotations: Mapped[List["ReferenceAnnotation"]] = relationship(
        "ReferenceAnnotation", back_populates="dataset_document", cascade="all, delete-orphan"
    )

class ReferenceAnnotation(Base):
    __tablename__ = "reference_annotations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("dataset_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    format_type: Mapped[str] = mapped_column(String(32), nullable=False)  # EXECUTIVE_SUMMARY, PUBLIC_ADVISORY, SOCIAL_POST, FAQ
    reference_text: Mapped[str] = mapped_column(Text, nullable=False)
    meta_info: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    dataset_document: Mapped["DatasetDocument"] = relationship("DatasetDocument", back_populates="reference_annotations")
