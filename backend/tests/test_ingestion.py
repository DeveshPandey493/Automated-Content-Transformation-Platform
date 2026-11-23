import pytest
from app.db.session import get_session_factory
from app.services.chunking.chunker import split_into_sentences, chunk_document_text
from app.services.ingestion.extractors import normalize_text, count_words, extract_from_txt
from app.services.ingestion.service import DocumentIngestionService
from app.core.exceptions import DocumentProcessingError, SSRFSecurityViolation
from app.core.security import validate_url_for_ssrf

def test_normalize_text():
    raw = "  This is a   test   document.\r\n\r\nWith  multiple   spaces.  "
    cleaned = normalize_text(raw)
    assert cleaned == "This is a test document.\n\nWith multiple spaces."

def test_split_into_sentences():
    text = "The Reserve Bank of India announced new fiscal guidelines. Dr. Sharma attended the meeting. The GDP projected growth is 7.2%."
    sentences = split_into_sentences(text)
    assert len(sentences) >= 2
    assert "The Reserve Bank of India announced new fiscal guidelines." in sentences

def test_chunking_with_offsets():
    doc_text = (
        "India's digital economy has expanded rapidly over the past decade. "
        "The Unified Payments Interface (UPI) recorded over 13 billion transactions in a single month. "
        "Financial inclusion metrics have improved substantially across rural districts. "
        "Government initiatives continue to drive citizen adoption across all states."
    )
    chunks = chunk_document_text(doc_text, target_words=20, overlap_words=5)
    assert len(chunks) >= 2
    for c in chunks:
        assert "chunk_index" in c
        assert "char_start" in c
        assert "char_end" in c
        assert "text" in c
        assert c["char_start"] >= 0
        assert c["char_end"] > c["char_start"]
        # Verify slice in original text
        assert doc_text[c["char_start"]:c["char_end"]] == c["text"]

def test_ingest_text_service():
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        sample_policy = (
            "National Green Hydrogen Mission aims to facilitate demand creation, production, "
            "utilization and export of Green Hydrogen. India aims to develop green hydrogen "
            "production capacity of at least 5 Million Metric Tonnes per annum with an associated "
            "renewable energy capacity addition of about 125 GW in the country by 2030."
        )
        doc = DocumentIngestionService.ingest_text(
            text=sample_policy,
            title="National Green Hydrogen Mission 2030",
            meta_info={"author": "Ministry of New and Renewable Energy"},
            db=session
        )
        assert doc.id is not None
        assert doc.title == "National Green Hydrogen Mission 2030"
        assert doc.total_characters == len(sample_policy)
        assert doc.total_words > 20
        assert len(doc.chunks) >= 1
        assert doc.chunks[0].chunk_index == 0
        assert doc.chunks[0].token_count > 0
    finally:
        session.close()

def test_ingest_too_short_text():
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        with pytest.raises(DocumentProcessingError):
            DocumentIngestionService.ingest_text(text="Too brief", title="Brief", meta_info={}, db=session)
    finally:
        session.close()

def test_extract_from_txt():
    content = b"Sample text for extraction test.\nSecond line with data."
    cleaned, pages, meta, records = extract_from_txt(content)
    assert "Sample text for extraction test." in cleaned
    assert meta["format"] == "txt"
    assert pages >= 1
