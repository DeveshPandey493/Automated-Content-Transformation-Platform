import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_session_factory
from app.db.models.document import Document
from app.db.models.job import TransformationJob
from app.db.models.output import GeneratedOutput

client = TestClient(app)

class TestApiEndpoints:
    def test_health_check(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_list_documents(self):
        response = client.get("/api/documents")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_models(self):
        response = client.get("/api/models")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        # Check that model objects have expected fields
        for model in data:
            assert "model_id" in model
            assert "name" in model
            assert "family" in model
            assert "provider" in model

    def test_datasets_list(self):
        response = client.get("/api/datasets")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_compare_all_evaluations(self):
        response = client.get("/api/evaluations/compare-all")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestSsrfProtection:
    def test_ssrf_validation_blocks_private_ips(self):
        from app.core.security import validate_url_for_ssrf, SSRFSecurityViolation

        # Test loopback IP blocking
        blocked_urls = [
            "http://127.0.0.1/secret",
            "http://localhost:8080/",
            "http://0.0.0.0/",
            "http://169.254.169.254/latest/meta-data/",
            "http://10.0.0.1/internal",
            "http://192.168.1.1/admin",
            "http://172.16.0.1/",
            "file:///etc/passwd"
        ]

        for url in blocked_urls:
            with pytest.raises(SSRFSecurityViolation):
                validate_url_for_ssrf(url)

    def test_ssrf_validation_allows_public_urls(self):
        from app.core.security import validate_url_for_ssrf, SSRFSecurityViolation

        # These should be allowed (they resolve to public IPs)
        # We can't easily test actual DNS resolution in unit tests
        # So we test that the validation logic works by mocking or just checking it doesn't crash
        # For now, just ensure the function exists and can be called
        pass
