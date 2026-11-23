from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.schemas.model import GenerationConfig, GenerationResult, ModelMetadataResponse

class BaseTransformationModel(ABC):
    """
    Unified abstract interface for all content transformation engines.
    Implemented by Extractive, Local Seq2Seq, and Instruction LLM providers.
    """

    def __init__(self, model_id: str, name: str):
        self.model_id = model_id
        self.name = name
        self._is_loaded = False

    @abstractmethod
    def load(self) -> None:
        """Loads model weights or initializes external client."""
        pass

    @abstractmethod
    def unload(self) -> None:
        """Purges model weights from VRAM/RAM to free memory."""
        pass

    @abstractmethod
    def generate(
        self,
        source_text: str,
        config: GenerationConfig,
        source_chunks: Optional[List[Dict[str, Any]]] = None,
    ) -> GenerationResult:
        """
        Executes transformation given source text and configuration parameters.
        Must return GenerationResult with latency, word count, tokens, and output.
        """
        pass

    @abstractmethod
    def get_metadata(self) -> ModelMetadataResponse:
        """Returns capabilities, execution mode, and resource profiles."""
        pass

    @abstractmethod
    def validate_configuration(self, config: GenerationConfig) -> bool:
        """Validates if the provided configuration is supported by this engine."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Checks if the model can currently execute (weights present / API key valid)."""
        pass
