import time
import os
import re
import logging
from typing import Dict, Any, List, Optional
from app.ml.base import BaseTransformationModel
from app.schemas.model import GenerationConfig, GenerationResult, ModelMetadataResponse
from app.core.config import get_settings
from app.core.exceptions import ModelInferenceError

logger = logging.getLogger("actp.ml.seq2seq")

class LocalSeq2SeqEngine(BaseTransformationModel):
    """
    Local neural sequence-to-sequence generation engine.
    Wraps FLAN-T5 or BART with lazy weight & module loading, dynamic VRAM detection, and CPU fallback.
    """

    def __init__(self, model_name_or_path: str = "google/flan-t5-base"):
        settings = get_settings()
        clean_id = model_name_or_path.replace("/", "_")
        super().__init__(model_id=f"seq2seq/{clean_id}", name=f"Local Seq2Seq ({model_name_or_path})")
        self.raw_model_name = model_name_or_path
        self.cache_dir = settings.HF_HOME
        self.tokenizer = None
        self.model = None
        self.device = "cpu"
        self._is_loaded = False
        self._force_cpu = False

    def _determine_device(self) -> str:
        settings = get_settings()
        if self._force_cpu:
            return "cpu"
        if settings.DEVICE in ["cpu", "cuda"]:
            return settings.DEVICE
        try:
            import torch
            if torch.cuda.is_available():
                free_vram = torch.cuda.mem_get_info()[0] / (1024**3)
                if free_vram >= 1.5:
                    return "cuda"
                else:
                    logger.warning(f"CUDA VRAM low ({free_vram:.2f} GB free). Falling back to CPU for stability.")
                    return "cpu"
        except Exception:
            pass
        return "cpu"

    def load(self) -> None:
        if self._is_loaded and self.model is not None:
            return

        start = time.perf_counter()
        logger.info(f"Loading local Seq2Seq model '{self.raw_model_name}' from cache '{self.cache_dir}'...")

        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

            self.device = self._determine_device()
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.raw_model_name,
                cache_dir=self.cache_dir,
            )

            dtype = torch.float16 if self.device == "cuda" else torch.float32
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                self.raw_model_name,
                cache_dir=self.cache_dir,
                torch_dtype=dtype,
            ).to(self.device)

            if self.tokenizer is None or not callable(self.tokenizer):
                raise RuntimeError("Loaded tokenizer is missing or not callable")
            if self.model is None or not callable(getattr(self.model, "generate", None)):
                raise RuntimeError("Loaded model does not provide a callable generate method")

            self.model.eval()
            self._is_loaded = True
            logger.info(f"Loaded '{self.raw_model_name}' onto {self.device} in {round(time.perf_counter() - start, 2)}s.")
        except Exception as e:
            self.unload()
            raise ModelInferenceError(self.model_id, f"Failed to load transformer model '{self.raw_model_name}': {e}")

    def unload(self) -> None:
        if self.model is not None:
            del self.model
            self.model = None
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass
        self._is_loaded = False
        logger.info(f"Unloaded '{self.raw_model_name}' from memory.")

    def is_available(self) -> bool:
        return True

    def validate_configuration(self, config: GenerationConfig) -> bool:
        return True

    def get_metadata(self) -> ModelMetadataResponse:
        settings = get_settings()
        is_gpu = False
        try:
            import torch
            is_gpu = torch.cuda.is_available()
        except Exception:
            pass
        device_type = "LOCAL_GPU" if is_gpu else "LOCAL_CPU"
        return ModelMetadataResponse(
            model_id=self.model_id,
            name=self.name,
            family="SEQ2SEQ",
            provider="LOCAL_HUGGINGFACE",
            execution_type=device_type,
            supported_tasks=["EXECUTIVE_SUMMARY", "PUBLIC_ADVISORY", "SOCIAL_POST", "FAQ"],
            is_available=True,
            description=(
                f"Local neural generation with {self.raw_model_name} (lazy loaded on {self.device}); "
                "CUDA inference failures retry on CPU."
            ),
            resource_requirements={
                "device": self.device,
                "vram_mb": 1500 if is_gpu else 0,
                "cuda_failure_fallback": "cpu_retry",
            }
        )

    def _build_task_prefix(self, config: GenerationConfig) -> str:
        fmt = config.format_type.upper()
        if "t5" in self.raw_model_name.lower():
            if fmt == "EXECUTIVE_SUMMARY":
                return f"summarize for {config.audience} in a {config.tone} tone: "
            elif fmt == "PUBLIC_ADVISORY":
                return f"generate a public advisory with actionable facts for {config.audience}: "
            elif fmt == "SOCIAL_POST":
                return f"write a social media post with key takeaways: "
            elif fmt == "FAQ":
                return f"generate frequently asked questions and answers: "
            return "summarize: "
        return ""

    def generate(
        self,
        source_text: str,
        config: GenerationConfig,
        source_chunks: Optional[List[Dict[str, Any]]] = None,
    ) -> GenerationResult:
        if not self._is_loaded or self.model is None or self.tokenizer is None:
            self.load()

        import torch
        start_time = time.perf_counter()
        prefix = self._build_task_prefix(config)
        input_text = prefix + source_text
        max_target_tokens = min(config.max_tokens, int(config.target_length_words * 1.5))
        min_target_tokens = max(30, int(config.target_length_words * 0.4))

        def infer() -> tuple[str, int, int]:
            if self.tokenizer is None or self.model is None:
                raise RuntimeError("Model and tokenizer must be loaded before inference")
            encoded = self.tokenizer(
                input_text,
                max_length=1024,
                truncation=True,
                return_tensors="pt",
            )
            inputs = encoded.to(self.device)
            input_tokens = inputs["input_ids"].shape[1]
            with torch.inference_mode():
                generated = self.model.generate(
                    **inputs,
                    max_new_tokens=max_target_tokens,
                    min_new_tokens=min_target_tokens,
                    num_beams=config.beam_size,
                    no_repeat_ngram_size=3,
                    length_penalty=1.0,
                    early_stopping=True,
                )
            if generated is None or not hasattr(generated, "shape"):
                raise RuntimeError("Model returned no generated token sequence")
            decoded_text = self.tokenizer.decode(
                generated[0], skip_special_tokens=True
            ).strip()
            return decoded_text, input_tokens, generated.shape[1]

        fallback_reason = None
        try:
            decoded, input_token_count, output_token_count = infer()
        except Exception as gpu_error:
            if self.device != "cuda":
                raise ModelInferenceError(
                    self.model_id,
                    f"Inference failed on {self.device}: {gpu_error}",
                ) from gpu_error

            fallback_reason = f"CUDA inference failed ({type(gpu_error).__name__}); retried on CPU"
            logger.exception("CUDA inference failed for %s; retrying on CPU", self.model_id)
            self._force_cpu = True
            self.unload()
            try:
                self.load()
                decoded, input_token_count, output_token_count = infer()
            except Exception as cpu_error:
                raise ModelInferenceError(
                    self.model_id,
                    f"CUDA inference failed ({gpu_error}); CPU retry also failed ({cpu_error})",
                ) from cpu_error

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        words = len(re.findall(r"\b\w+\b", decoded))

        return GenerationResult(
            model_id=self.model_id,
            content=decoded,
            word_count=words,
            latency_ms=latency_ms,
            input_tokens=input_token_count,
            output_tokens=output_token_count,
            estimated_cost_usd=0.0,
            extra={
                "device": self.device,
                "device_fallback_reason": fallback_reason,
                "beam_size": config.beam_size,
                "raw_model": self.raw_model_name,
            }
        )
