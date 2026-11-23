import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_session_factory
from app.db.models.document import Document
from app.db.models.job import TransformationJob
from app.db.models.output import GeneratedOutput
from app.services.verification.claim_extractor import ClaimExtractor
from app.services.verification.evidence_retriever import EvidenceRetriever
from app.services.verification.verifier import FactVerifier
from app.services.evaluation.evaluator import OutputEvaluator
from app.services.transformation.constraints import ConstraintValidator
from app.ml.extractive.engine import ExtractiveEngine
from app.ml.seq2seq.transformer_engine import LocalSeq2SeqEngine
from app.services.chunking.chunker import chunk_document_text as chunk_document, split_into_sentences

client = TestClient(app)

class TestTransformationPipeline:
    def test_extractive_engine(self):
        engine = ExtractiveEngine(method="textrank")
        assert engine.is_available()
        metadata = engine.get_metadata()
        assert metadata.model_id == "extractive/textrank"
        assert metadata.family == "EXTRACTIVE"

    def test_extractive_engine_tfidf(self):
        engine = ExtractiveEngine(method="tfidf")
        assert engine.is_available()
        metadata = engine.get_metadata()
        assert metadata.model_id == "extractive/tfidf"

    def test_seq2seq_engine_metadata(self):
        engine = LocalSeq2SeqEngine(model_name_or_path="google/flan-t5-base")
        metadata = engine.get_metadata()
        assert metadata.model_id == "seq2seq/google_flan-t5-base"
        assert metadata.family == "SEQ2SEQ"
        assert metadata.provider == "LOCAL_HUGGINGFACE"

    def test_constraint_validator(self):
        validator = ConstraintValidator()
        content = "The government announced new growth policies for economic development."
        constraints = {
            "target_words": 100,
            "audience": "Senior Leadership",
            "tone": "Formal",
            "required_keywords": ["growth", "policy"],
            "prohibited_terms": ["unverified"]
        }
        result = validator.evaluate_constraints(
            content=content,
            target_words=constraints["target_words"],
            required_keywords=constraints["required_keywords"],
            prohibited_terms=constraints["prohibited_terms"],
            format_type="EXECUTIVE_SUMMARY"
        )
        assert "controllability_score" in result
        assert 0 <= result["controllability_score"] <= 1
        assert result["length_score"] <= 1
        assert result["keyword_score"] <= 1
        assert result["prohibited_score"] <= 1
        assert result["format_score"] <= 1

    def test_create_transformation_job(self):
        # First create a document
        # Ensure database is initialized
        from app.db.session import init_db
        init_db()

        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            doc = Document(
                title="Test Document",
                source_type="PASTED_TEXT",
                file_type="txt",
                total_characters=100,
                total_words=20,
                cleaned_text="This is a test document for transformation testing.",
            )
            session.add(doc)
            session.flush()

            # Override the get_db dependency to use the test session
            from app.db.session import get_db
            from app.main import app

            def override_get_db():
                try:
                    yield session
                finally:
                    pass

            app.dependency_overrides[get_db] = override_get_db
            try:
                response = client.post("/api/transformations", json={
                    "document_id": str(doc.id),
                    "format_type": "EXECUTIVE_SUMMARY",
                    "audience": "Senior Leadership",
                    "tone": "Formal",
                    "length_target": "MEDIUM",
                    "model_ids": ["extractive/textrank"],
                })
                assert response.status_code in [200, 201]
                data = response.json()
                assert "id" in data
                assert data["status"] in ["PENDING", "PROCESSING", "COMPLETED"]
            finally:
                app.dependency_overrides.clear()
        finally:
            session.close()


class TestVerificationPipeline:
    def test_claim_extraction(self):
        text = """
        The report states that GDP grew by 5.2% in Q3 2024.
        The Prime Minister announced new policies on Monday.
        Climate change is causing global temperatures to rise.
        """
        claims = ClaimExtractor.extract_claims(text)
        assert len(claims) > 0
        for claim in claims:
            assert "claim_text" in claim
            assert "claim_type" in claim
            assert "numbers" in claim
            assert "dates" in claim
            assert "entities" in claim

    def test_evidence_retriever(self):
        retriever = EvidenceRetriever()
        from app.db.models.document import DocumentChunk
        source_chunks = [
            DocumentChunk(
                id="c1",
                document_id="doc1",
                chunk_index=0,
                text="GDP grew by 5.2% in Q3 2024 according to official statistics.",
                page_number=1,
                section_heading="Introduction",
                token_count=100,
                char_start=0,
                char_end=50
            ),
            DocumentChunk(
                id="c2",
                document_id="doc1",
                chunk_index=1,
                text="The Prime Minister spoke on Monday about economic growth.",
                page_number=2,
                section_heading="Economy",
                token_count=80,
                char_start=51,
                char_end=100
            ),
        ]
        claim_text = "GDP grew by 5.2% in Q3 2024"
        results = retriever.retrieve_evidence_chunks(claim_text, source_chunks, top_k=2)
        assert len(results) == 2
        for chunk, score in results:
            assert isinstance(chunk, DocumentChunk)
            assert isinstance(score, float)
            assert score >= 0

    def test_fact_verifier(self):
        verifier = FactVerifier()
        from app.db.models.document import DocumentChunk
        claim_data = {
            "claim_text": "GDP grew by 5.2% in Q3 2024",
            "claim_type": "NUMERICAL",
            "numbers": ["5.2%"],
            "dates": ["Q3 2024"],
            "entities": ["GDP"]
        }
        evidence_chunk = DocumentChunk(
            id="c1",
            document_id="doc1",
            chunk_index=0,
            text="GDP grew by 5.2% in Q3 2024 according to official statistics.",
            page_number=1,
            section_heading="Introduction",
            token_count=100,
            char_start=0,
            char_end=50
        )
        evidence_pairs = [(evidence_chunk, 0.95)]
        result = verifier.verify_claim(claim_data, evidence_pairs)
        assert "status" in result
        assert "confidence_score" in result
        assert "explanation" in result
        assert "evidence" in result
        assert result["status"] in ["SUPPORTED", "PARTIALLY_SUPPORTED", "UNSUPPORTED", "CONTRADICTED", "REQUIRES_HUMAN_REVIEW"]


class TestEvaluationMetrics:
    def test_rouge_calculation(self):
        evaluator = OutputEvaluator()
        reference = "The government announced new policies for economic growth."
        hypothesis = "The government announced new policies to boost economic growth."
        scores = evaluator.scorer.score(reference, hypothesis)
        assert "rouge_1_f1" in scores or "rouge1" in scores
        rouge_1_f1 = scores["rouge1"].fmeasure
        assert 0 <= rouge_1_f1 <= 1

    def test_key_fact_coverage(self):
        evaluator = OutputEvaluator()
        gold_facts = ["GDP grew by 5.2%", "Q3 2024", "new policies"]
        generated_text = "The report shows GDP grew by 5.2% in Q3 2024 with new policies."
        # Test via evaluate_output
        from app.db.models.output import GeneratedOutput
        from unittest.mock import MagicMock
        mock_output = MagicMock(spec=GeneratedOutput)
        mock_output.content = generated_text
        mock_output.word_count = len(generated_text.split())
        mock_output.generation_params = {}
        mock_output.verification_report = None
        result = evaluator.evaluate_output(mock_output, reference_text=None, gold_facts=gold_facts)
        assert "key_fact_coverage" in result
        assert 0 <= result["key_fact_coverage"] <= 1

    def test_entity_coverage(self):
        evaluator = OutputEvaluator()
        gold_entities = ["GDP", "Prime Minister", "India"]
        generated_text = "The Prime Minister of India announced GDP growth."
        from app.db.models.output import GeneratedOutput
        from unittest.mock import MagicMock
        mock_output = MagicMock(spec=GeneratedOutput)
        mock_output.content = generated_text
        mock_output.word_count = len(generated_text.split())
        mock_output.generation_params = {}
        mock_output.verification_report = None
        result = evaluator.evaluate_output(mock_output, reference_text=None, gold_entities=gold_entities)
        assert "entity_coverage" in result
        assert 0 <= result["entity_coverage"] <= 1

    def test_controllability_score(self):
        from app.services.transformation.constraints import ConstraintValidator
        validator = ConstraintValidator()
        content = "The government announced new growth policies for economic development."
        result = validator.evaluate_constraints(
            content=content,
            target_words=100,
            required_keywords=["growth", "policy"],
            prohibited_terms=["unverified"],
            format_type="EXECUTIVE_SUMMARY"
        )
        assert "controllability_score" in result
        assert 0 <= result["controllability_score"] <= 1


class TestModelRegistryFallback:
    def test_model_registry_lists_all_models(self):
        from app.ml.registry import get_model_registry
        registry = get_model_registry()
        models = registry.list_models()
        assert len(models) >= 5  # At least 5 models registered
        model_ids = [m.model_id for m in models]
        assert "extractive/textrank" in model_ids
        assert "extractive/tfidf" in model_ids
        assert "seq2seq/google_flan-t5-base" in model_ids
        assert "seq2seq/facebook_bart-base" in model_ids
        # Groq model might not be available without API key
        assert any("groq" in m for m in model_ids)

    def test_model_availability(self):
        from app.ml.registry import get_model_registry
        registry = get_model_registry()
        # Extractive models should always be available
        textrank = registry.get_model("extractive/textrank")
        assert textrank.is_available()
        tfidf = registry.get_model("extractive/tfidf")
        assert tfidf.is_available()

    def test_invalid_model_raises(self):
        from app.ml.registry import get_model_registry
        from app.core.exceptions import ModelNotFoundError
        registry = get_model_registry()
        with pytest.raises(ModelNotFoundError):
            registry.get_model("nonexistent/model")


class TestDocumentChunking:
    def test_chunking_pipeline(self):
        text = "This is sentence one. This is sentence two. This is sentence three. " * 10
        chunks = chunk_document(full_text=text, target_words=50, overlap_words=10)
        assert len(chunks) > 1
        for chunk in chunks:
            assert "chunk_index" in chunk
            assert "text" in chunk
            assert "char_start" in chunk
            assert "char_end" in chunk

    def test_chunk_metadata_preservation(self):
        text = "Chapter 1\nThis is the first paragraph.\n\nChapter 2\nThis is the second paragraph."
        chunks = chunk_document(full_text=text, target_words=50, overlap_words=10)
        # Should preserve some structural info
        for chunk in chunks:
            assert "section_heading" in chunk or "page_number" in chunk

    def test_sentence_splitting(self):
        text = "This is sentence one. This is sentence two? This is sentence three!"
        sentences = split_into_sentences(text)
        assert len(sentences) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])