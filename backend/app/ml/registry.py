import logging
import threading
from typing import Dict, List, Optional
from app.ml.base import BaseTransformationModel
from app.ml.extractive.engine import ExtractiveEngine
from app.ml.instruction.groq_engine import GroqInstructionEngine
from app.ml.seq2seq.transformer_engine import LocalSeq2SeqEngine
from app.schemas.model import ModelMetadataResponse
from app.core.config import get_settings
from app.core.exceptions import ModelNotFoundError

logger = logging.getLogger("actp.ml.registry")

class ModelRegistry:
    """
    Singleton registry managing lifecycle, discovery, and execution
    of all AI transformation models across the platform.
    """

    _instance = None
    _lock = threading.RLock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._models: Dict[str, BaseTransformationModel] = {}
                cls._instance._active_neural_model: Optional[str] = None
                cls._instance._initialize_default_models()
            return cls._instance

    def _initialize_default_models(self) -> None:
        settings = get_settings()

        # 1. Extractive Baselines
        textrank_engine = ExtractiveEngine(method="textrank")
        tfidf_engine = ExtractiveEngine(method="tfidf")
        self.register_model(textrank_engine)
        self.register_model(tfidf_engine)

        # 2. Groq Instruction Engine
        groq_engine = GroqInstructionEngine(model_id=settings.GROQ_MODEL)
        self.register_model(groq_engine)

        # 3. Local Seq2Seq Engines
        flan_engine = LocalSeq2SeqEngine(model_name_or_path=settings.FLAN_T5_MODEL)
        bart_engine = LocalSeq2SeqEngine(model_name_or_path=settings.BART_MODEL)
        self.register_model(flan_engine)
        self.register_model(bart_engine)

        logger.info(f"ModelRegistry initialized with {len(self._models)} engines: {list(self._models.keys())}")

    def register_model(self, model: BaseTransformationModel) -> None:
        with self._lock:
            self._models[model.model_id] = model

    def get_model(self, model_id: str) -> BaseTransformationModel:
        # Normalize model_id aliases
        if model_id in ["extractive", "default_extractive"]:
            model_id = "extractive/textrank"
        elif model_id in ["groq", "default_groq"]:
            settings = get_settings()
            model_id = f"groq/{settings.GROQ_MODEL}"
        elif model_id in ["flan-t5", "t5"]:
            settings = get_settings()
            clean_id = settings.FLAN_T5_MODEL.replace("/", "_")
            model_id = f"seq2seq/{clean_id}"
        elif model_id in ["bart"]:
            settings = get_settings()
            clean_id = settings.BART_MODEL.replace("/", "_")
            model_id = f"seq2seq/{clean_id}"

        model = self._models.get(model_id)
        if not model:
            # Fuzzy match
            for k in self._models.keys():
                if model_id.lower() in k.lower():
                    return self._models[k]
            raise ModelNotFoundError(model_id)
        return model

    def list_models(self) -> List[ModelMetadataResponse]:
        return [model.get_metadata() for model in self._models.values()]

    def unload_model(self, model_id: str) -> None:
        model = self.get_model(model_id)
        model.unload()

    def unload_all_neural(self) -> None:
        with self._lock:
            for m in self._models.values():
                if isinstance(m, LocalSeq2SeqEngine):
                    m.unload()

_registry: Optional[ModelRegistry] = None

def get_model_registry() -> ModelRegistry:
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry
