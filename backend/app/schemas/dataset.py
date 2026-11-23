from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class ReferenceAnnotationResponse(BaseModel):
    id: str
    format_type: str
    reference_text: str
    meta_info: Dict[str, Any] = {}

    class Config:
        from_attributes = True

class DatasetDocumentResponse(BaseModel):
    id: str
    dataset_id: str
    title: str
    publisher: Optional[str]
    source_url: Optional[str]
    split: str
    extracted_text: str
    gold_key_facts: List[str]
    gold_entities: List[str]
    gold_numbers: List[str]
    reference_annotations: List[ReferenceAnnotationResponse] = []

    class Config:
        from_attributes = True

class DatasetResponse(BaseModel):
    id: str
    name: str
    description: str
    domain: str
    version: str
    documents: List[DatasetDocumentResponse] = []

    class Config:
        from_attributes = True
