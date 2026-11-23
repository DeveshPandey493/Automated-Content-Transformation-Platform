import os
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import DocumentProcessingError
from app.db.models.document import Document, DocumentChunk
from app.services.ingestion.validator import validate_uploaded_file, compute_sha256
from app.services.ingestion.extractors import (
    extract_from_pdf,
    extract_from_docx,
    extract_from_txt,
    normalize_text,
    count_words,
)
from app.services.ingestion.url_fetcher import fetch_and_extract_url
from app.services.chunking.chunker import chunk_document_text

class DocumentIngestionService:
    @staticmethod
    def ingest_text(
        text: str,
        title: str,
        meta_info: Optional[Dict[str, Any]],
        db: Session,
    ) -> Document:
        """Ingests raw text directly, chunks it, and persists to database."""
        cleaned = normalize_text(text)
        if len(cleaned) < 20:
            raise DocumentProcessingError("Text content too brief (minimum 20 characters required).")

        total_words = count_words(cleaned)
        total_pages = max(1, (total_words + 449) // 450)

        doc = Document(
            title=title.strip(),
            source_type="PASTED_TEXT",
            file_type="txt",
            total_pages=total_pages,
            total_characters=len(cleaned),
            total_words=total_words,
            cleaned_text=cleaned,
            meta_info=meta_info or {},
        )
        db.add(doc)
        db.flush()

        # Generate traceable chunks
        chunks_data = chunk_document_text(cleaned)
        for c in chunks_data:
            chunk = DocumentChunk(
                document_id=doc.id,
                chunk_index=c["chunk_index"],
                char_start=c["char_start"],
                char_end=c["char_end"],
                text=c["text"],
                token_count=c["token_count"],
            )
            db.add(chunk)

        db.commit()
        db.refresh(doc)
        return doc

    @staticmethod
    async def ingest_file(
        file: UploadFile,
        title: Optional[str],
        db: Session,
    ) -> Document:
        """Ingests an uploaded PDF, DOCX, or TXT file with validation and persistent storage."""
        filename, ext = validate_uploaded_file(file)
        settings = get_settings()

        content_bytes = await file.read()
        file_size = len(content_bytes)

        if file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise DocumentProcessingError(
                f"File size ({round(file_size / (1024*1024), 2)}MB) exceeds limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
            )

        file_hash = compute_sha256(content_bytes)
        
        # Save raw file to upload storage
        saved_filename = f"{uuid.uuid4()}_{filename}"
        raw_path = Path(settings.UPLOAD_DIR) / saved_filename
        with open(raw_path, "wb") as f:
            f.write(content_bytes)

        # Extract content based on format
        page_records = None
        section_records = None

        if ext == ".pdf":
            cleaned_text, total_pages, meta, page_records = extract_from_pdf(content_bytes)
        elif ext == ".docx":
            cleaned_text, total_pages, meta, section_records = extract_from_docx(content_bytes)
        elif ext == ".txt":
            cleaned_text, total_pages, meta, records = extract_from_txt(content_bytes)
        else:
            raise DocumentProcessingError(f"Unsupported file format: {ext}")

        doc_title = title.strip() if title else (meta.get("title") or filename)
        total_words = count_words(cleaned_text)

        doc = Document(
            title=doc_title,
            source_type="FILE_UPLOAD",
            file_type=ext.replace(".", ""),
            file_size_bytes=file_size,
            file_hash=file_hash,
            raw_file_path=str(raw_path),
            total_pages=total_pages,
            total_characters=len(cleaned_text),
            total_words=total_words,
            cleaned_text=cleaned_text,
            meta_info=meta,
        )
        db.add(doc)
        db.flush()

        # Chunk with page / section traceability
        chunks_data = chunk_document_text(
            cleaned_text,
            page_records=page_records,
            section_records=section_records,
        )
        for c in chunks_data:
            chunk = DocumentChunk(
                document_id=doc.id,
                chunk_index=c["chunk_index"],
                page_number=c.get("page_number"),
                section_heading=c.get("section_heading"),
                char_start=c["char_start"],
                char_end=c["char_end"],
                text=c["text"],
                token_count=c["token_count"],
            )
            db.add(chunk)

        db.commit()
        db.refresh(doc)
        return doc

    @staticmethod
    async def ingest_url(
        url: str,
        title: Optional[str],
        db: Session,
    ) -> Document:
        """Safely fetches an external URL with SSRF guards, chunks, and stores."""
        extracted_title, cleaned_text, meta = await fetch_and_extract_url(url)
        doc_title = title.strip() if title else extracted_title
        total_words = count_words(cleaned_text)
        total_pages = max(1, (total_words + 449) // 450)

        doc = Document(
            title=doc_title,
            source_type="URL",
            file_type="html",
            source_url=url,
            total_pages=total_pages,
            total_characters=len(cleaned_text),
            total_words=total_words,
            cleaned_text=cleaned_text,
            meta_info=meta,
        )
        db.add(doc)
        db.flush()

        chunks_data = chunk_document_text(cleaned_text)
        for c in chunks_data:
            chunk = DocumentChunk(
                document_id=doc.id,
                chunk_index=c["chunk_index"],
                char_start=c["char_start"],
                char_end=c["char_end"],
                text=c["text"],
                token_count=c["token_count"],
            )
            db.add(chunk)

        db.commit()
        db.refresh(doc)
        return doc
