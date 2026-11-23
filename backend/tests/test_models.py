import pytest
from app.ml.registry import get_model_registry
from app.ml.extractive.engine import ExtractiveEngine
from app.schemas.model import GenerationConfig
from app.core.exceptions import ModelNotFoundError

SAMPLE_POLICY = (
    "The Digital India Programme is a flagship initiative of the Government of India with a vision "
    "to transform India into a digitally empowered society and knowledge economy. "
    "Key focus areas include digital infrastructure as a utility to every citizen, governance and services on demand, "
    "and digital empowerment of citizens. Over 1.4 billion Aadhaar identity cards have been generated. "
    "Digital transactions surged by 45% during the financial year, reaching 131 billion transactions."
)

def test_model_registry_discovery():
    registry = get_model_registry()
    models = registry.list_models()
    assert len(models) >= 4

    model_ids = [m.model_id for m in models]
    assert "extractive/textrank" in model_ids
    assert "extractive/tfidf" in model_ids
    assert any("groq" in mid for mid in model_ids)
    assert any("seq2seq" in mid for mid in model_ids)

def test_extractive_textrank_executive_summary():
    engine = ExtractiveEngine(method="textrank")
    config = GenerationConfig(
        format_type="EXECUTIVE_SUMMARY",
        audience="Senior Leadership",
        tone="Formal",
        target_length_words=80
    )
    result = engine.generate(SAMPLE_POLICY, config)
    assert result.model_id == "extractive/textrank"
    assert "Executive Summary" in result.content
    assert "Strategic Overview" in result.content
    assert result.word_count > 10
    assert result.latency_ms > 0

def test_extractive_tfidf_public_advisory():
    engine = ExtractiveEngine(method="tfidf")
    config = GenerationConfig(
        format_type="PUBLIC_ADVISORY",
        audience="General Citizens",
        tone="Direct",
        target_length_words=70
    )
    result = engine.generate(SAMPLE_POLICY, config)
    assert result.model_id == "extractive/tfidf"
    assert "Public Advisory" in result.content
    assert result.word_count > 10

def test_extractive_social_post_format():
    engine = ExtractiveEngine(method="textrank")
    config = GenerationConfig(
        format_type="SOCIAL_POST",
        required_keywords=["Digital India", "Aadhaar"],
        target_length_words=50
    )
    result = engine.generate(SAMPLE_POLICY, config)
    assert result.model_id == "extractive/textrank"
    assert "Key Takeaway" in result.content
    assert "#DigitalIndia" in result.content or "#" in result.content

def test_extractive_faq_format():
    engine = ExtractiveEngine(method="textrank")
    config = GenerationConfig(
        format_type="FAQ",
        target_length_words=100
    )
    result = engine.generate(SAMPLE_POLICY, config)
    assert "Frequently Asked Questions" in result.content
    assert "Q1:" in result.content
    assert "A:" in result.content

def test_model_not_found():
    registry = get_model_registry()
    with pytest.raises(ModelNotFoundError):
        registry.get_model("nonexistent_model_xyz_123")
