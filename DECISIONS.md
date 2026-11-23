# DECISIONS.md — Architectural Decision Records (ADRs)
**Smart India Hackathon 2026 — Gen AI Platform for Automated Content Transformation**

---

## ADR-001: Decoupled Multi-Approach Model Architecture
- **Date**: 2026-11-15
- **Context**: The platform must support three fundamentally different generation paradigms:
  1. Local Extractive Summarisation (TF-IDF & TextRank sentence graph ranking).
  2. Local Transformer Seq2Seq Generation (`google/flan-t5-base` & `facebook/bart-base`).
  3. Instruction-Tuned LLMs via Groq Cloud API.
- **Alternatives Considered**:
  - Tight coupling to an LLM provider (e.g. relying entirely on Groq or OpenAI).
  - Calling Hugging Face inference pipeline directly inside API route handlers.
- **Selected Decision**:
  - Implement an abstract `BaseTransformationModel` class with a thread-safe `ModelRegistry`.
  - All models adhere to uniform interfaces: `load()`, `unload()`, `generate()`, `get_metadata()`, `validate_configuration()`, and `is_available()`.
- **Reason**:
  - Ensures the platform works 100% offline with zero API keys using extractive or local transformer models.
  - Keeps FastAPI route handlers completely free of model-specific inference logic.
  - Allows benchmarking all three models on identical input conditions without rewriting pipelines.
- **Consequences**:
  - Requires maintaining common generation configuration abstractions (`GenerationConfig`) that gracefully map to both extractive sentence selectors and neural beam search/temperature sampling.

---

## ADR-002: Dual-Mode Database Layer (PostgreSQL Primary with SQLite Fallback)
- **Date**: 2026-11-15
- **Context**: In production and during SIH evaluation environments, PostgreSQL 16 is the standard relational database. However, during rapid local development, offline judge demonstrations, or testing on environments where the Docker daemon is temporarily inactive, database connection failure would block the application.
- **Alternatives Considered**:
  - Hard dependency on PostgreSQL only (fails to boot if port 5432 is down).
  - SQLite only (insufficient concurrency and lack of JSONB / UUID optimization for scaled deployment).
- **Selected Decision**:
  - SQLAlchemy 2.0 with unified declarative models.
  - The database connection manager attempts connection to `DATABASE_URL` (PostgreSQL). If connection fails and `APP_ENV=development`, it gracefully logs a warning and initializes an optimized local SQLite database (`content_transformer.db`) with equivalent schema.
- **Reason**:
  - Zero-friction developer setup and failsafe demo reliability. Judges or evaluators can run the platform with `python main.py` immediately without running Docker or installing PostgreSQL.
- **Consequences**:
  - Dialect-specific constructs (like native Postgres `JSONB` or `UUID` types) are typed using SQLAlchemy's generic `JSON` and `String(36)` representations to ensure 100% compatibility across both engines.

---

## ADR-003: Multi-Method Factual Verification Pipeline
- **Date**: 2026-11-15
- **Context**: LLMs generate fluent text that may contain subtle hallucinations (incorrect numbers, fabricated dates, misplaced entity associations). A core requirement is that factual claims must never be declared correct merely because an LLM said so.
- **Alternatives Considered**:
  - Prompting an LLM to "verify itself" (circular hallucination vulnerability).
  - Relying exclusively on vector cosine similarity (fails to catch negated facts or number mismatches, as opposite numbers often share high semantic similarity).
- **Selected Decision**:
  - Implement a hybrid factual verification engine combining:
    1. **Exact Number and Date Extractor & Matcher**: Strict verification of quantitative claims against source chunks.
    2. **Named Entity Overlap**: Strict alignment of persons, organizations, locations, and policies.
    3. **Semantic Evidence Retrieval**: Cosine similarity over sentence vectors to retrieve the most relevant source passages.
    4. **Verification Status Classification**: Output categorized into `SUPPORTED`, `PARTIALLY_SUPPORTED`, `UNSUPPORTED`, `CONTRADICTED`, and `REQUIRES_HUMAN_REVIEW`.
- **Reason**:
  - High explainability: users and judges can inspect the exact evidence passage and verify the reasoning for every single claim.
- **Consequences**:
  - Processing time includes claim extraction and evidence ranking passes. Verification runs asynchronously or as an explicit pipeline stage to preserve UI responsiveness.

---

## ADR-004: SSRF Protection for URL Ingestion
- **Date**: 2026-11-15
- **Context**: Ingesting content from arbitrary user-provided URLs introduces Server-Side Request Forgery (SSRF) vulnerabilities (e.g. attacking internal cloud metadata `169.254.169.254` or local network endpoints `127.0.0.1`, `10.0.0.0/8`, `192.168.0.0/16`).
- **Alternatives Considered**:
  - Relying on simple URL regex matching.
  - Allowing direct HTTP client requests.
- **Selected Decision**:
  - Custom DNS resolution validator that resolves hostnames to IP addresses before initiating HTTP requests.
  - Explicitly denies loopback addresses, RFC 1918 private subnets, link-local addresses, and AWS/GCP metadata endpoints.
  - Enforces strict redirect limits (max 3), payload size caps (10MB), and connection timeouts.
- **Reason**:
  - Robust enterprise-grade security adhering to OWASP Top 10 guidelines.
- **Consequences**:
  - Internal testing cannot point to `localhost:8000` URLs directly for ingestion, which is the correct security posture.

## ADR-005: Bounded LLM Context and Explicit Extractive Baseline
- **Date**: 2026-11-15
- **Context**: Long reports exceeded the configured Groq token-per-minute request budget. The UI also selected the extractive baseline by default and presented its verbatim passages under synthesis-like section headings, while hiding errors from other selected models when any model succeeded.
- **Alternatives Considered**:
  - Send the entire report and rely on provider limits.
  - Silently fall back to extractive output after a cloud model fails.
  - Label extractive sentence selections as a fully rewritten summary.
- **Selected Decision**:
  - Rank and include at most 3,500 source words in Groq prompt context, preserve the full source for verification, prefer configured Groq in the workspace, and visibly describe extractive results as verbatim source passages. Surface model errors on partial jobs.
- **Reason**:
  - Keep requests within practical provider limits and prevent users from mistaking an extractive baseline for a generated rewrite or an all-model success.
- **Consequences**:
  - Groq may not receive every passage in a long source; the chosen context is ranked and the full document remains the verification source. Live Groq generation against the supplied report was not exercised because the approval reviewer rejected sending that uploaded report to an external provider.

## ADR-006: CPU Retry for Local Transformer Runtime Failures
- **Date**: 2026-11-15
- **Context**: The local FLAN-T5 model failed during inference in the running application with an opaque `NoneType is not callable` error, while its cached weights and tokenizer were usable in isolated CPU inference.
- **Alternatives Considered**:
  - Fail the selected model and leave the user with another model's result.
  - Always disable GPU inference.
- **Selected Decision**:
  - Keep normal GPU inference; when CUDA inference fails, unload the GPU instance, load the already-cached model on CPU, retry once, and preserve both failure details if fallback also fails.
- **Reason**:
  - Recover from device-specific runtime failures without sacrificing GPU performance for healthy runs or downloading another model.
- **Consequences**:
  - A GPU failure can make one request slower because CPU loading/inference is retried. The runtime metadata identifies when that happened.
