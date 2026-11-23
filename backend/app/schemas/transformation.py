from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

FormatType = Literal["EXECUTIVE_SUMMARY", "PUBLIC_ADVISORY", "SOCIAL_POST", "FAQ"]
LengthTarget = Literal["SHORT", "MEDIUM", "DETAILED", "CUSTOM"]

class TransformationCreateRequest(BaseModel):
    document_id: str = Field(..., description="Source document UUID")
    format_type: FormatType = Field(..., description="Target output format")
    audience: str = Field(default="Senior Management", description="Target audience")
    tone: str = Field(default="Formal", description="Desired tone")
    length_target: LengthTarget = Field(default="MEDIUM", description="Length constraint")
    custom_word_limit: Optional[int] = Field(default=None, ge=10, le=5000, description="Word count limit if CUSTOM")
    required_keywords: List[str] = Field(default_factory=list, description="Must-include terms")
    prohibited_terms: List[str] = Field(default_factory=list, description="Must-avoid terms")
    model_ids: List[str] = Field(
        default=["extractive/textrank"],
        description="One or more model identifiers to execute (Extractive, Seq2Seq, Groq)"
    )

class GeneratedOutputResponse(BaseModel):
    id: str
    job_id: str
    model_id: str
    model_provider: str
    version: int
    parent_output_id: Optional[str]
    content: str
    word_count: int
    generation_latency_ms: float
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    is_approved: bool
    generation_params: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

class TransformationJobResponse(BaseModel):
    id: str
    document_id: str
    format_type: str
    audience: str
    tone: str
    length_target: str
    custom_word_limit: Optional[int]
    required_keywords: List[str]
    prohibited_terms: List[str]
    status: str
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    outputs: List[GeneratedOutputResponse] = []

    class Config:
        from_attributes = True
