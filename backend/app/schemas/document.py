from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl

class DocumentCreateText(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Document title")
    text: str = Field(..., min_length=10, description="Full text content")
    meta_info: Optional[Dict[str, Any]] = Field(default_factory=dict)

class DocumentCreateURL(BaseModel):
    url: str = Field(..., description="Target webpage URL")
    title: Optional[str] = Field(default=None, max_length=255)

class DocumentChunkResponse(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    page_number: Optional[int]
    section_heading: Optional[str]
    char_start: int
    char_end: int
    text: str
    token_count: int

    class Config:
        from_attributes = True

class DocumentSummaryResponse(BaseModel):
    id: str
    title: str
    source_type: str
    file_type: Optional[str]
    file_size_bytes: Optional[int]
    total_pages: int
    total_characters: int
    total_words: int
    source_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentDetailResponse(DocumentSummaryResponse):
    cleaned_text: str
    meta_info: Dict[str, Any]
    chunks: List[DocumentChunkResponse] = []

    class Config:
        from_attributes = True
