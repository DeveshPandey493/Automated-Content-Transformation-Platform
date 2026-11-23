from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ModelMetadataResponse(BaseModel):
    model_id: str
    name: str
    family: str  # EXTRACTIVE, SEQ2SEQ, INSTRUCTION_LLM
    provider: str  # LOCAL, GROQ
    execution_type: str  # LOCAL_CPU, LOCAL_GPU, CLOUD_API
    supported_tasks: List[str]
    is_available: bool
    description: str
    resource_requirements: Dict[str, Any] = {}

class GenerationConfig(BaseModel):
    format_type: str
    audience: str = "General"
    tone: str = "Neutral"
    target_length_words: int = 300
    required_keywords: List[str] = []
    prohibited_terms: List[str] = []
    max_tokens: int = 1024
    temperature: float = 0.3
    top_p: float = 0.95
    beam_size: int = 4

class GenerationResult(BaseModel):
    model_id: str
    content: str
    word_count: int
    latency_ms: float
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost_usd: float = 0.0
    extra: Dict[str, Any] = {}
