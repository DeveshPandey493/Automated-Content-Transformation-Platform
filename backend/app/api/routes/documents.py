from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.db.session import get_db
from app.db.models.document import Document, DocumentChunk
from app.core.exceptions import DocumentNotFoundError
from app.schemas.document import (
    DocumentCreateText,
    DocumentCreateURL,
    DocumentSummaryResponse,
    DocumentDetailResponse,
    DocumentChunkResponse,
)
from app.services.ingestion.service import DocumentIngestionService

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentSummaryResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    doc = await DocumentIngestionService.ingest_file(file, title, db)
    return doc

@router.post("/text", response_model=DocumentSummaryResponse, status_code=status.HTTP_201_CREATED)
def ingest_text(
    payload: DocumentCreateText,
    db: Session = Depends(get_db)
):
    doc = DocumentIngestionService.ingest_text(payload.text, payload.title, payload.meta_info, db)
    return doc

@router.post("/url", response_model=DocumentSummaryResponse, status_code=status.HTTP_201_CREATED)
async def ingest_url(
    payload: DocumentCreateURL,
    db: Session = Depends(get_db)
):
    doc = await DocumentIngestionService.ingest_url(payload.url, payload.title, db)
    return doc

@router.get("", response_model=List[DocumentSummaryResponse])
def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    stmt = select(Document).order_by(desc(Document.created_at)).offset(skip).limit(limit)
    if search:
        stmt = stmt.where(Document.title.ilike(f"%{search}%"))
    results = db.scalars(stmt).all()
    return results

@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    doc = db.get(Document, document_id)
    if not doc:
        raise DocumentNotFoundError(document_id)
    return doc

@router.get("/{document_id}/chunks", response_model=List[DocumentChunkResponse])
def get_document_chunks(
    document_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db)
):
    doc = db.get(Document, document_id)
    if not doc:
        raise DocumentNotFoundError(document_id)
    stmt = (
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
        .offset(skip)
        .limit(limit)
    )
    chunks = db.scalars(stmt).all()
    return chunks
