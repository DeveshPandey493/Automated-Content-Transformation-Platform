from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class EvidenceReferenceResponse(BaseModel):
    id: str
    chunk_id: str
    relevance_score: float
    evidence_text: str

    class Config:
        from_attributes = True

class ExtractedClaimResponse(BaseModel):
    id: str
    output_id: str
    claim_text: str
    claim_type: str
    verification_status: str
    confidence_score: float
    explanation: Optional[str]
    evidence_references: List[EvidenceReferenceResponse] = []

    class Config:
        from_attributes = True

class VerificationReportResponse(BaseModel):
    id: str
    output_id: str
    total_claims: int
    supported_claims: int
    partially_supported: int
    unsupported_claims: int
    contradicted_claims: int
    factual_consistency_score: float
    summary: Optional[str]
    claims: List[ExtractedClaimResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True
