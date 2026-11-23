import json
import logging
from pathlib import Path
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.dataset import Dataset, DatasetDocument, ReferenceAnnotation
from app.db.models.document import Document
from app.services.ingestion.service import DocumentIngestionService

logger = logging.getLogger("actp.services.dataset")

DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "curated_benchmark.json"

class DatasetService:
    @staticmethod
    def seed_benchmark_dataset(db: Session) -> Dataset:
        """Seeds curated public policy dataset and reference annotations into database."""
        existing = db.scalars(select(Dataset).where(Dataset.name == "SIH-ACTP-Benchmark-v1")).first()
        if existing:
            return existing

        dataset = Dataset(
            name="SIH-ACTP-Benchmark-v1",
            description="Authoritative public policy and technical reports from NITI Aayog, MNRE, and Government of India with human gold-standard annotations.",
            domain="Public Governance & Strategic Policy",
            version="v1.0"
        )
        db.add(dataset)
        db.flush()

        if not DATA_FILE.exists():
            logger.warning(f"Benchmark file not found at {DATA_FILE}")
            db.commit()
            return dataset

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            raw_docs = json.load(f)

        for d in raw_docs:
            doc_record = DatasetDocument(
                dataset_id=dataset.id,
                title=d["title"],
                publisher=d.get("publisher"),
                source_url=d.get("source_url"),
                split=d.get("split", "TEST"),
                extracted_text=d["extracted_text"],
                gold_key_facts=d.get("gold_key_facts", []),
                gold_entities=d.get("gold_entities", []),
                gold_numbers=d.get("gold_numbers", []),
            )
            db.add(doc_record)
            db.flush()

            # Also ingest into active Document Library so user can instantly transform it!
            try:
                DocumentIngestionService.ingest_text(
                    text=d["extracted_text"],
                    title=f"[Benchmark] {d['title']}",
                    meta_info={"dataset": dataset.name, "publisher": d.get("publisher")},
                    db=db
                )
            except Exception as e:
                logger.warning(f"Could not mirror benchmark to library: {e}")

            # Add references
            refs = d.get("reference_outputs", {})
            for fmt, ref_text in refs.items():
                ref_record = ReferenceAnnotation(
                    document_id=doc_record.id,
                    format_type=fmt,
                    reference_text=ref_text,
                    meta_info={"gold_standard": True}
                )
                db.add(ref_record)

        db.commit()
        db.refresh(dataset)
        logger.info(f"Seeded benchmark dataset with {len(raw_docs)} documents.")
        return dataset
