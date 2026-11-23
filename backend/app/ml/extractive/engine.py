import time
import re
from typing import Dict, Any, List, Optional
from app.ml.base import BaseTransformationModel
from app.schemas.model import GenerationConfig, GenerationResult, ModelMetadataResponse
from app.ml.extractive.tfidf import TfidfSentenceRanker
from app.ml.extractive.textrank import TextRankSentenceRanker
from app.services.chunking.chunker import split_into_sentences

class ExtractiveEngine(BaseTransformationModel):
    """
    Extractive summarisation engine implementing TF-IDF and TextRank ranking.
    Runs 100% locally on CPU without external API keys or heavy weight downloads.
    """

    def __init__(self, method: str = "textrank"):
        model_id = f"extractive/{method}"
        name = f"Extractive Baseline ({method.upper()})"
        super().__init__(model_id, name)
        self.method = method
        self._is_loaded = True

    def load(self) -> None:
        self._is_loaded = True

    def unload(self) -> None:
        self._is_loaded = True  # Extractive requires no persistent GPU weight state

    def is_available(self) -> bool:
        return True

    def validate_configuration(self, config: GenerationConfig) -> bool:
        return True

    def get_metadata(self) -> ModelMetadataResponse:
        return ModelMetadataResponse(
            model_id=self.model_id,
            name=self.name,
            family="EXTRACTIVE",
            provider="LOCAL",
            execution_type="LOCAL_CPU",
            supported_tasks=["EXECUTIVE_SUMMARY", "PUBLIC_ADVISORY", "SOCIAL_POST", "FAQ"],
            is_available=True,
            description=f"Local sentence-ranking baseline using {self.method.upper()} graph/vector algorithms.",
            resource_requirements={"vram_mb": 0, "ram_mb": 50, "offline": True}
        )

    def generate(
        self,
        source_text: str,
        config: GenerationConfig,
        source_chunks: Optional[List[Dict[str, Any]]] = None,
    ) -> GenerationResult:
        start_time = time.perf_counter()
        sentences = split_into_sentences(source_text)

        target_words = config.target_length_words or 250
        if self.method == "tfidf":
            selected = TfidfSentenceRanker.select_top_sentences(sentences, target_words=target_words)
        else:
            selected = TextRankSentenceRanker.select_top_sentences(sentences, target_words=target_words)

        selected_texts = [s for _, s in selected]

        # Format output according to requested format_type
        formatted_content = self._format_output(selected_texts, config)

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        words = len(re.findall(r"\b\w+\b", formatted_content))
        approx_tokens = int(words * 1.3)

        return GenerationResult(
            model_id=self.model_id,
            content=formatted_content,
            word_count=words,
            latency_ms=latency_ms,
            input_tokens=approx_tokens,
            output_tokens=approx_tokens,
            estimated_cost_usd=0.0,
            extra={
                "method": self.method,
                "sentences_extracted": len(selected),
                "sentence_indices": [idx for idx, _ in selected]
            }
        )

    def _format_output(self, sentences: List[str], config: GenerationConfig) -> str:
        fmt = config.format_type.upper()
        if not sentences:
            return "No content could be extracted from the source document."

        if fmt == "EXECUTIVE_SUMMARY":
            passages = "\n".join(f"- {sentence}" for sentence in sentences)
            return (
                "### Extractive Executive Summary\n\n"
                "*Verbatim source passages selected by sentence ranking; this baseline does not paraphrase.*\n\n"
                f"**Key source passages:**\n{passages}"
            )

        elif fmt == "PUBLIC_ADVISORY":
            title = f"### Public Advisory Source Notes ({config.audience})"
            points = "\n".join(f"• {s}" for s in sentences)
            return f"{title}\n\n*Extractive source passages; no new instructions or precautions have been generated.*\n\n{points}"

        elif fmt == "SOCIAL_POST":
            lead = sentences[0] if sentences else ""
            body = " ".join(sentences[1:3])
            keywords_tags = " ".join([f"#{k.replace(' ', '')}" for k in config.required_keywords[:3]])
            hashtags = keywords_tags
            return f"📌 **Key Takeaway**:\n{lead}\n\n{body}\n\n{hashtags}"

        elif fmt == "FAQ":
            passages = "\n".join(f"- {sentence}" for sentence in sentences[:5])
            return (
                "### FAQ Source Notes (Extractive Baseline)\n\n"
                "*These are source passages for FAQ drafting; questions are not inferred by extractive ranking.*\n\n"
                f"{passages}"
            )

        else:
            return "\n\n".join(sentences)
