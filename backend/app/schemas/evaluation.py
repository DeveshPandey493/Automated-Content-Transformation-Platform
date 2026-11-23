from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class EvaluationResultResponse(BaseModel):
    id: str
    output_id: str
    rouge_1_f1: float
    rouge_2_f1: float
    rouge_l_f1: float
    bert_score_f1: float
    key_fact_coverage: float
    entity_coverage: float
    numerical_coverage: float
    controllability_score: float
    detailed_metrics: Dict[str, Any] = {}
    created_at: datetime

    class Config:
        from_attributes = True

class HumanFeedbackCreate(BaseModel):
    output_id: str
    rating_accuracy: int = Field(..., ge=1, le=5)
    rating_completeness: int = Field(..., ge=1, le=5)
    rating_readability: int = Field(..., ge=1, le=5)
    rating_suitability: int = Field(..., ge=1, le=5)
    reviewer_notes: Optional[str] = None

class HumanFeedbackResponse(HumanFeedbackCreate):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class ModelComparisonRow(BaseModel):
    model_id: str
    model_name: str
    provider: str
    content: str
    word_count: int
    latency_ms: float
    factual_consistency_score: float
    supported_claims: int
    total_claims: int
    rouge_1_f1: float
    rouge_2_f1: float
    rouge_l_f1: float
    controllability_score: float
    estimated_cost_usd: float

class ComparisonMatrixResponse(BaseModel):
    document_id: str
    document_title: str
    format_type: str
    rows: List[ModelComparisonRow]
