import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from app.main import app
from app.core.config import get_settings
from app.core.security import is_ip_private_or_restricted, validate_url_for_ssrf
from app.core.exceptions import SSRFSecurityViolation
from app.db.session import get_db, init_db, get_engine, get_active_engine_name
from app.db.models import Document, DocumentChunk, TransformationJob, GeneratedOutput

client = TestClient(app)

def test_settings_loaded():
    settings = get_settings()
    assert settings.APP_NAME is not None
    assert settings.UPLOAD_DIR is not None
    assert settings.EXPORT_DIR is not None

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
    assert "gpu" in data
    assert data["database_engine"] in ["postgresql", "sqlite"]

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "docs" in data
    assert "health" in data

def test_ssrf_protection_denies_localhost():
    with pytest.raises(SSRFSecurityViolation):
        validate_url_for_ssrf("http://localhost:8000/secret")
    with pytest.raises(SSRFSecurityViolation):
        validate_url_for_ssrf("http://127.0.0.1:8000/secret")
    with pytest.raises(SSRFSecurityViolation):
        validate_url_for_ssrf("http://169.254.169.254/latest/meta-data/")

def test_ssrf_ip_check():
    assert is_ip_private_or_restricted("127.0.0.1") is True
    assert is_ip_private_or_restricted("10.0.0.1") is True
    assert is_ip_private_or_restricted("192.168.1.1") is True
    assert is_ip_private_or_restricted("172.16.0.1") is True
    assert is_ip_private_or_restricted("169.254.169.254") is True
    assert is_ip_private_or_restricted("8.8.8.8") is False

def test_db_models_crud(monkeypatch):
    from app.db.session import get_session_factory
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        doc = Document(
            title="Test Budget Document",
            source_type="PASTED_TEXT",
            file_type="txt",
            total_characters=120,
            total_words=20,
            cleaned_text="The union budget allocates 10,000 crores to artificial intelligence development in 2026."
        )
        session.add(doc)
        session.commit()
        session.refresh(doc)
        assert doc.id is not None

        chunk = DocumentChunk(
            document_id=doc.id,
            chunk_index=0,
            char_start=0,
            char_end=120,
            text=doc.cleaned_text,
            token_count=20
        )
        session.add(chunk)
        session.commit()
        session.refresh(chunk)
        assert chunk.id is not None
        assert chunk.document_id == doc.id

        # Verify relationship
        assert len(doc.chunks) == 1
        assert doc.chunks[0].text == doc.cleaned_text
    finally:
        session.close()
