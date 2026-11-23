
# TASKS.md — Project Roadmap & Task Execution Tracker
**Smart India Hackathon 2026 — Gen AI Platform for Automated Content Transformation**

---

## Task Status Legend
- `NOT_STARTED`: Work has not commenced.
- `IN_PROGRESS`: Currently being actively implemented.
- `BLOCKED`: Blocked by an unresolved dependency or external issue.
- `COMPLETED`: Verified against acceptance criteria with automated tests passing.

---

## Phase 0: Foundation & Environment Setup

- [ ] **TASK-001**: Inspect hardware, Python, Node.js, GPU/VRAM, disk space, Docker, and environment configuration.
  - **Priority**: High | **Dependencies**: None | **Status**: COMPLETED
  - **Acceptance Criteria**: Machine profile verified (RTX 4050 6GB VRAM, Python 3.13.5, Node 24.19, 33GB+ free disk). `.env` verified and validated without exposing credentials.
  - **Files**: `.env`, `.env.example`, `.gitignore`

- [ ] **TASK-002**: Initialize core multi-agent continuity documents.
  - **Priority**: High | **Dependencies**: TASK-001 | **Status**: COMPLETED
  - **Acceptance Criteria**: `AGENTS.md`, `ARCHITECTURE.md`, `TASKS.md`, `DECISIONS.md`, `HANDOFF.md`, `README.md` established and compliant with master prompt.
  - **Files**: `AGENTS.md`, `ARCHITECTURE.md`, `TASKS.md`, `DECISIONS.md`, `HANDOFF.md`, `README.md`

- [ ] **TASK-003**: Scaffold Backend directory structure, configuration management, and database abstraction.
  - **Priority**: High | **Dependencies**: TASK-002 | **Status**: COMPLETED
  - **Acceptance Criteria**: `backend/` structured into `app/`, `api/`, `core/`, `db/`, `schemas/`, `services/`, `ml/`, `pipelines/`, `tests/`. FastAPI app boots, config parses `.env`, database connects with PostgreSQL primary and SQLite fallback.
  - **Files**: `backend/app/main.py`, `backend/app/core/config.py`, `backend/app/db/session.py`, `backend/app/db/base.py`, `backend/requirements.txt`

- [ ] **TASK-004**: Implement database models and migration foundation.
  - **Priority**: High | **Dependencies**: TASK-003 | **Status**: COMPLETED
  - **Acceptance Criteria**: SQLAlchemy models for `Document`, `DocumentChunk`, `TransformationJob`, `GeneratedOutput`, `ExtractedClaim`, `EvidenceReference`, `VerificationReport`, `EvaluationResult`, `Dataset`, `ReferenceAnnotation`.
  - **Files**: `backend/app/db/models/`, `backend/alembic.ini`

- [ ] **TASK-005**: Scaffold Frontend (Next.js 14+ App Router, Tailwind, TypeScript, Navigation Shell).
  - **Priority**: High | **Dependencies**: TASK-003 | **Status**: COMPLETED
  - **Acceptance Criteria**: Frontend app boots on `localhost:3000`, displays primary navigation for 7 core views, communicates with backend `/api/health`.
  - **Files**: `frontend/package.json`, `frontend/src/app/layout.tsx`, `frontend/src/app/page.tsx`, `frontend/src/components/layout/sidebar.tsx`

---

## Phase 1: Document Ingestion & Traceable Chunking

- [ ] **TASK-101**: Build Document Ingestion Service for PDF, DOCX, TXT, and Plain Text.
  - **Priority**: High | **Dependencies**: TASK-004 | **Status**: COMPLETED
  - **Acceptance Criteria**: Extracts clean text, preserves page numbers (PDF), paragraph headings (DOCX), and validates MIME types and file sizes (<=25MB).
  - **Files**: `backend/app/services/ingestion/extractors.py`, `backend/app/services/ingestion/validator.py`

- [ ] **TASK-102**: Build SSRF-Protected URL Ingestion Service.
  - **Priority**: Medium | **Dependencies**: TASK-101 | **Status**: COMPLETED
  - **Acceptance Criteria**: Blocks loopback (127.0.0.1, localhost), RFC 1918 subnets, cloud metadata endpoints (169.254.169.254). Extracts main article text and metadata.
  - **Files**: `backend/app/services/ingestion/url_fetcher.py`

- [ ] **TASK-103**: Implement Sentence Segmentation & Intelligent Chunking Pipeline.
  - **Priority**: High | **Dependencies**: TASK-101 | **Status**: COMPLETED
  - **Acceptance Criteria**: Chunks text at sentence boundaries (configurable overlap), assigns unique `chunk_id`, records `page_number`, `section_heading`, `char_start`, `char_end`.
  - **Files**: `backend/app/services/chunking/chunker.py`

- [ ] **TASK-104**: Implement Document Management API Endpoints & Document Library UI.
  - **Priority**: High | **Dependencies**: TASK-103, TASK-005 | **Status**: COMPLETED
  - **Acceptance Criteria**: REST endpoints `POST /api/documents/upload`, `POST /api/documents/text`, `POST /api/documents/url`, `GET /api/documents`, `GET /api/documents/{id}/chunks`. UI displays document cards with chunk inspection drawer.
  - **Files**: `backend/app/api/routes/documents.py`, `frontend/src/app/documents/page.tsx`

---

## Phase 2: AI Model Infrastructure & Model Registry

- [ ] **TASK-201**: Define Unified `BaseTransformationModel` and `ModelRegistry`.
  - **Priority**: High | **Dependencies**: TASK-003 | **Status**: COMPLETED
  - **Acceptance Criteria**: Extensible interface with `load()`, `unload()`, `generate()`, `get_metadata()`, `validate_configuration()`, `is_available()`. Registry manages model lifecycles and concurrency.
  - **Files**: `backend/app/ml/base.py`, `backend/app/ml/registry.py`

- [ ] **TASK-202**: Implement Local Extractive Summarisation Engine (TF-IDF & TextRank).
  - **Priority**: High | **Dependencies**: TASK-201 | **Status**: COMPLETED
  - **Acceptance Criteria**: Pure local computation, zero external API. Splits sentences, computes TF-IDF sentence vectors and TextRank PageRank graph, selects top $K$ sentences preserving verbatim text and chunk links.
  - **Files**: `backend/app/ml/extractive/tfidf.py`, `backend/app/ml/extractive/textrank.py`, `backend/app/ml/extractive/engine.py`

- [ ] **TASK-203**: Implement Local Seq2Seq Transformer Engine (FLAN-T5-Base & BART-Base).
  - **Priority**: High | **Dependencies**: TASK-201 | **Status**: COMPLETED
  - **Acceptance Criteria**: Lazy weight loading from `./models_cache`, GPU/CUDA auto-detection (with CPU fallback), memory-safe generation with batch size and max length limits, explicit unload.
  - **Files**: `backend/app/ml/seq2seq/transformer_engine.py`

- [ ] **TASK-204**: Implement Groq Instruction-Tuned LLM Engine.
  - **Priority**: High | **Dependencies**: TASK-201 | **Status**: COMPLETED
  - **Acceptance Criteria**: Uses official `groq` SDK, reads `GROQ_API_KEY` and `GROQ_MODEL`, handles rate limits with exponential backoff, returns input/output token counts, latency, and estimated cost.
  - **Files**: `backend/app/ml/instruction/groq_engine.py`

- [ ] **TASK-205**: Model Laboratory API & UI.
  - **Priority**: Medium | **Dependencies**: TASK-202, TASK-203, TASK-204 | **Status**: COMPLETED
  - **Acceptance Criteria**: `GET /api/models` lists all registered engines with availability status. UI displays model cards and side-by-side prompt test runner.
  - **Files**: `backend/app/api/routes/models.py`, `frontend/src/app/models/page.tsx`

---

## Phase 3: Transformation Engine & Output Formats

- [ ] **TASK-301**: Implement Multi-Format Prompt & Context Assembly Engine.
  - **Priority**: High | **Dependencies**: TASK-201 | **Status**: COMPLETED
  - **Acceptance Criteria**: Builds specialized prompts/instructions for:
    1. Executive Summary (Overview, Key Findings, Statistics, Implications, Supported Actions)
    2. Public Advisory (Title, Audience, Situation, Facts, Precautions, Official Contacts)
    3. Social Media Posts (LinkedIn structured post, X/Twitter concise post with hashtags)
    4. FAQ (Questions, Evidence-based answers, Out-of-scope notifications)
  - **Files**: `backend/app/services/transformation/prompt_templates.py`, `backend/app/services/transformation/builder.py`

- [ ] **TASK-302**: Implement Audience, Tone, Length, and Controllability Constraints.
  - **Priority**: High | **Dependencies**: TASK-301 | **Status**: COMPLETED
  - **Acceptance Criteria**: Supports configurable audiences, tones, word count budgets, required keywords, and prohibited claims. Validates constraints post-generation.
  - **Files**: `backend/app/services/transformation/constraints.py`

- [ ] **TASK-303**: Transformation Orchestration Pipeline & Asynchronous Execution.
  - **Priority**: High | **Dependencies**: TASK-302 | **Status**: COMPLETED
  - **Acceptance Criteria**: `POST /api/transformations` triggers async job execution, stores intermediate status (`PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`), persists outputs with versioning.
  - **Files**: `backend/app/pipelines/transformation_pipeline.py`, `backend/app/api/routes/transformations.py`

- [ ] **TASK-304**: Transformation Studio UI.
  - **Priority**: High | **Dependencies**: TASK-303 | **Status**: COMPLETED
  - **Acceptance Criteria**: Interactive transformation builder with document picker, format selector, audience/tone dropdowns, constraint inputs, and live generation progress.
  - **Files**: `frontend/src/app/transform/page.tsx`

- [ ] **TASK-305**: Make model selection and partial generation outcomes transparent.
  - **Priority**: High | **Dependencies**: TASK-301, TASK-304 | **Status**: COMPLETED
  - **Acceptance Criteria**: Select configured Groq by default when available; disclose extractive outputs as verbatim passages; bound long-document Groq context; show provider errors when another selected model succeeds.
  - **Files**: `backend/app/ml/instruction/groq_engine.py`, `backend/app/ml/extractive/engine.py`, `frontend/src/app/transform/page.tsx`, `frontend/src/app/review/page.tsx`

- [ ] **TASK-306**: Recover local seq2seq inference on CUDA runtime failures.
  - **Priority**: High | **Dependencies**: TASK-203 | **Status**: COMPLETED
  - **Acceptance Criteria**: Validate loaded tokenizer/generator callability; retry inference on CPU when CUDA inference fails; report the fallback device and reason; preserve a clear error if CPU retry also fails.
  - **Files**: `backend/app/ml/seq2seq/transformer_engine.py`

---

## Phase 4: Factual Verification & Hallucination Detection

- [ ] **TASK-401**: Build Factual Claim Extractor.
  - **Priority**: High | **Dependencies**: TASK-303 | **Status**: COMPLETED
  - **Acceptance Criteria**: Identifies atomic factual claims from generated output: dates, numbers, percentages, named entities, policy statements, cause-and-effect assertions.
  - **Files**: `backend/app/services/verification/claim_extractor.py`

- [ ] **TASK-402**: Build Semantic Evidence Retriever & Source Matcher.
  - **Priority**: High | **Dependencies**: TASK-401 | **Status**: COMPLETED
  - **Acceptance Criteria**: Matches extracted claims against source document chunks using TF-IDF / sentence embeddings, ranking top supporting passages.
  - **Files**: `backend/app/services/verification/evidence_retriever.py`

- [ ] **TASK-403**: Build Multi-Method Fact Verification Classifier.
  - **Priority**: High | **Dependencies**: TASK-402 | **Status**: COMPLETED
  - **Acceptance Criteria**: Classifies claims as `SUPPORTED`, `PARTIALLY_SUPPORTED`, `UNSUPPORTED`, `CONTRADICTED`, or `REQUIRES_HUMAN_REVIEW` with granular confidence score and rationale.
  - **Files**: `backend/app/services/verification/verifier.py`

- [ ] **TASK-404**: Interactive Review & Source Traceability UI.
  - **Priority**: High | **Dependencies**: TASK-403 | **Status**: COMPLETED
  - **Acceptance Criteria**: Shows generated text with colored claim highlights. Clicking any claim opens a side panel displaying the exact source chunk, page number, and evidence comparison. Allows human edits and approval.
  - **Files**: `frontend/src/app/review/page.tsx`

---

## Phase 5: Evaluation Framework & Benchmark Dataset

- [ ] **TASK-501**: Implement Coverage, Text Similarity, and Factual Consistency Metric Evaluator.
  - **Priority**: High | **Dependencies**: TASK-403 | **Status**: COMPLETED
  - **Acceptance Criteria**: Computes ROUGE-1/2/L, BERTScore, Key Fact Coverage, Controllability Score, and Factual Consistency Score with clear mathematical formulas.
  - **Files**: `backend/app/services/evaluation/evaluator.py`, `backend/app/services/evaluation/metrics.py`

- [ ] **TASK-502**: Create Curated Public Benchmark Dataset & Reference Annotations.
  - **Priority**: High | **Dependencies**: TASK-501 | **Status**: COMPLETED
  - **Acceptance Criteria**: Ingests 30+ real public documents (NITI Aayog, WHO, Govt of India reports) with human-quality reference summaries, advisories, social posts, FAQs, and annotated key facts.
  - **Files**: `backend/app/data/curated_datasets.json`, `docs/DATASET_CARD.md`, `backend/app/services/dataset/dataset_service.py`

- [ ] **TASK-503**: Multi-Model Comparative Evaluation Engine & Dashboard UI.
  - **Priority**: High | **Dependencies**: TASK-502 | **Status**: COMPLETED
  - **Acceptance Criteria**: Side-by-side radar and bar charts comparing Extractive vs FLAN-T5 vs BART vs Groq across all 5 evaluation dimensions on identical test documents.
  - **Files**: `backend/app/api/routes/evaluations.py`, `frontend/src/app/evaluation/page.tsx`

---

## Phase 6: Export, Human Review & Versioning

- [ ] **TASK-601**: Multi-Format Export Engine (PDF, DOCX, Markdown, Plain Text).
  - **Priority**: Medium | **Dependencies**: TASK-404 | **Status**: COMPLETED
  - **Acceptance Criteria**: Generates clean, formatted PDF (via ReportLab), DOCX (via python-docx), Markdown, and TXT including traceability footnotes and verification badges.
  - **Files**: `backend/app/services/export/exporter.py`, `backend/app/api/routes/exports.py`

- [ ] **TASK-602**: Output Versioning, Revision History & Human Feedback Collection.
  - **Priority**: Medium | **Dependencies**: TASK-601 | **Status**: COMPLETED
  - **Acceptance Criteria**: Tracks version tree when users edit text, stores 5-star human evaluation ratings (Accuracy, Completeness, Readability, Suitability).
  - **Files**: `backend/app/services/transformation/versioning.py`, `backend/app/api/routes/versioning.py`

---

## Phase 7: Comprehensive Testing & Security Hardening

- [ ] **TASK-701**: Backend Test Suite (Unit, Integration, Security, SSRF).
  - **Priority**: High | **Dependencies**: TASK-602 | **Status**: COMPLETED
  - **Acceptance Criteria**: Pytest suite covering all API endpoints, model registry fallback, chunking, verification logic, and SSRF boundary testing. >=80% core service test coverage.
  - **Files**: `backend/tests/`

- [ ] **TASK-702**: Frontend Component & Workflow Tests.
  - **Priority**: Medium | **Dependencies**: TASK-701 | **Status**: COMPLETED
  - **Acceptance Criteria**: Component unit tests and Playwright end-to-end integration test validating the complete document-to-transformation-to-verification workflow.
  - **Files**: `frontend/tests/`

---

## Phase 8: SIH Demonstration Readiness

- [ ] **TASK-801**: End-to-End Demo Script & Sample Dossiers.
  - **Priority**: High | **Dependencies**: TASK-702 | **Status**: COMPLETED
  - **Acceptance Criteria**: Step-by-step repeatable walkthrough showcasing 1 real government report transformed into 4 formats with 3-model comparison, fact verification breakdown, and instant PDF export.
  - **Files**: `docs/DEMO_SCRIPT.md`, `sample_data/`
