# ARCHITECTURE.md — System Architecture & Design Specification
**Gen AI Platform for Automated Content Transformation (ACTP) — Smart India Hackathon 2026**

---

## 1. System Overview & Core Mission

Organizations repeatedly transform a single source document into different communication formats for diverse audiences:
1. **Executive Summary** for senior leadership and decision makers.
2. **Public Advisory** for citizens with actionable precautions and facts.
3. **Social Media Posts** for LinkedIn and X (formerly Twitter) with appropriate conciseness and hashtags.
4. **FAQ** for citizen and operational query resolution with grounded evidence.

### Core Product Principle
> **One source of truth. Multiple audiences. Multiple communication formats. Verifiable factual accuracy.**

The platform implements, benchmarks, and provides transparent comparisons across three distinct generation paradigms:
1. **Extractive Summarisation (Local Baseline)**: TF-IDF & TextRank sentence graph ranking. Verbatim, zero-hallucination baseline.
2. **Transformer Seq2Seq Generation (Local Neural)**: Hugging Face `google/flan-t5-base` & `facebook/bart-base` running locally on GPU/CPU with dynamic VRAM management and CUDA-to-CPU failure recovery.
3. **Instruction-Tuned LLM (Cloud High-Throughput)**: Groq SDK inference (`openai/gpt-oss-120b`) with bounded extractive context reduction for long documents, exponential backoff, and token/cost telemetry.

---

## 2. High-Level Architecture Diagram

```mermaid
flowchart TD
    subgraph Client["Presentation Layer (Next.js 14 / TypeScript)"]
        UI_Dash["Dashboard (/)"]
        UI_Doc["Document Library (/documents)"]
        UI_Trans["Transformation Studio (/transform)"]
        UI_Review["Review & Traceability (/review)"]
        UI_Lab["Model Laboratory (/models)"]
        UI_Eval["Evaluation Dashboard (/evaluation)"]
        UI_Dataset["Dataset Management (/datasets)"]
    end

    subgraph API["API Gateway & Dispatch Layer (FastAPI 0.115)"]
        R_Health["/api/health"]
        R_Doc["/api/documents"]
        R_Trans["/api/transformations"]
        R_Models["/api/models"]
        R_Verif["/api/verification"]
        R_Eval["/api/evaluations"]
        R_Data["/api/datasets"]
        R_Exp["/api/exports"]
        R_Ver["/api/versioning"]
    end

    subgraph CoreServices["Application Services & Pipelines"]
        S_Ingest["Document Ingestion & Chunking (PyMuPDF, python-docx, Trafilatura)"]
        S_SSRF["SSRF Defense Guard (DNS & Private IP Filter)"]
        S_TransPipeline["Transformation Orchestration Pipeline"]
        S_Constraint["Constraint Validator (Keywords, Length, Prohibitions)"]
        S_VerifEngine["Factual Verification Engine (Claim Extractor, Evidence Retriever, Verifier)"]
        S_EvalEngine["Evaluation Engine (ROUGE-1/2/L, Coverage, FCS, Controllability)"]
        S_Export["Multi-Format Exporter (ReportLab PDF, python-docx DOCX, MD, TXT)"]
        S_Version["Output Versioning & Human Feedback Service"]
    end

    subgraph MLRegistry["AI Model Layer (Common Interface)"]
        MR["Thread-Safe Singleton ModelRegistry"]
        M_Extractive["Extractive Engine (TF-IDF Centroid & TextRank PageRank)"]
        M_T5["Local Seq2Seq (FLAN-T5-base)"]
        M_BART["Local Seq2Seq (BART-base)"]
        M_Groq["Instruction LLM (Groq API / Context Bounding)"]
    end

    subgraph Storage["Persistence & Artifacts"]
        DB[("Dual-Mode Database: PostgreSQL 16 / SQLite Fallback")]
        DiskStorage["Local File Storage (/storage/uploads, /storage/exports)"]
        HF_Cache["HuggingFace Cache (/models_cache)"]
    end

    Client --> API
    API --> CoreServices
    CoreServices --> MLRegistry
    CoreServices --> Storage
    MLRegistry --> HF_Cache
```

---

## 3. Complete Project Directory Structure

```
Automated Content Transformation Platform/
├── .env                                  # Active credentials (DB, Groq, HF, Ports)
├── .env.example                          # Configuration template
├── .gitignore                            # Excludes venv, node_modules, cache, credentials
├── AGENTS.md                             # Multi-agent protocol & development guidelines
├── ARCHITECTURE.md                       # Complete system architecture specification
├── COMPLETION_PLAN.md                    # Roadmap & execution checklist
├── DECISIONS.md                          # Architecture Decision Records (ADRs)
├── docker-compose.yml                    # Multi-container orchestration (PostgreSQL, backend, frontend)
├── HANDOFF.md                            # Session continuity state and diagnostic history
├── pytest.ini                            # Pytest configuration
├── README.md                             # Master project overview
├── TASKS.md                              # Phase-by-phase task tracking (Phases 0-8)
│
├── backend/                              # Python 3.13+ FastAPI Application
│   ├── alembic.ini                       # Migration configuration
│   ├── requirements.txt                  # Python package dependencies
│   ├── content_transformer.db            # Local SQLite database (auto-fallback)
│   ├── models_cache/                     # Local Hugging Face model checkpoints (FLAN-T5, BART)
│   ├── storage/                          # File persistence (uploads/ and exports/)
│   │
│   ├── app/                              # Application Package
│   │   ├── main.py                       # FastAPI factory, lifespan, CORS, and routers
│   │   ├── api/routes/                   # 9 Route Handlers (health, documents, transformations, etc.)
│   │   ├── core/                         # Config, domain exceptions, structured logging, SSRF guard
│   │   ├── data/                         # Built-in benchmark seed dataset (curated_benchmark.json)
│   │   ├── db/                           # Database session, base declarative model, 10 ORM models
│   │   ├── ml/                           # AI Model Layer: base interface, registry, 3 model engines
│   │   ├── pipelines/                    # Transformation orchestration pipeline
│   │   ├── schemas/                      # Pydantic v2 validation contracts
│   │   └── services/                     # Ingestion, chunking, verification, evaluation, export, versioning
│   │
│   └── tests/                            # Comprehensive Pytest test suite (7 test suites)
│
├── frontend/                             # Next.js 14+ TypeScript Client Application
│   ├── package.json                      # Next.js, React, Tailwind, Recharts, Lucide
│   ├── tsconfig.json                     # Strict TypeScript configuration
│   ├── tailwind.config.ts                # Styling design tokens
│   ├── playwright.config.ts              # E2E test configuration
│   ├── src/
│   │   ├── app/                          # Next.js App Router (7 operational views)
│   │   │   ├── page.tsx                  # Dashboard
│   │   │   ├── documents/page.tsx        # Document Library
│   │   │   ├── transform/page.tsx        # Transformation Studio
│   │   │   ├── review/page.tsx           # Review & Traceability Workspace
│   │   │   ├── models/page.tsx           # Model Laboratory
│   │   │   ├── evaluation/page.tsx       # Evaluation Dashboard
│   │   │   └── datasets/page.tsx         # Dataset Management
│   │   ├── components/layout/            # Sidebar and Header components
│   │   └── lib/utils.ts                  # Classname utilities
│   └── tests/                            # Component and Playwright E2E tests
│
├── sample_data/                          # Benchmark dossiers & reference outputs
└── docs/                                 # 12 comprehensive architecture and operational guides
```

---

## 4. End-to-End Execution Sequences

### 4.1 Ingestion & Traceable Chunking Sequence
```mermaid
sequenceDiagram
    autonumber
    actor User as User / Operator
    participant UI as Document Library UI
    participant Route as /api/documents Route
    participant Ingest as Ingestion Service
    participant SSRF as SSRF Security Guard
    participant Chunker as Sentence Chunker
    participant DB as Database (SQLAlchemy)

    User->>UI: Uploads PDF / DOCX / TXT or submits URL
    UI->>Route: POST /api/documents/upload or /url
    alt Input is URL
        Route->>SSRF: Validate URL & Resolve DNS
        SSRF-->>Route: Valid public address
        Route->>Ingest: Fetch via URLFetcher (HTML to clean prose)
    else Input is File
        Route->>Ingest: Validate MIME, size (<=25MB), compute SHA-256
        Ingest->>Ingest: Extract text & metadata via PyMuPDF / python-docx
    end
    Route->>DB: Insert Document record
    Route->>Chunker: chunk_document(full_text)
    loop Sentence Boundary Windowing
        Chunker->>Chunker: Segment sentences, track char_start & char_end
        Chunker->>Chunker: Preserve page numbers & paragraph section headings
    end
    Chunker-->>Route: List of DocumentChunk objects
    Route->>DB: Bulk insert DocumentChunks
    Route-->>UI: HTTP 201 Created (Document details & chunk count)
```

### 4.2 Multi-Model Transformation Sequence
```mermaid
sequenceDiagram
    autonumber
    actor User as User / Operator
    participant Studio as Transformation Studio UI
    participant Route as /api/transformations Route
    participant Pipe as Transformation Pipeline
    participant Registry as ModelRegistry
    participant Model as BaseTransformationModel
    participant Validator as Constraint Validator
    participant Verif as Verification Service
    participant DB as Database

    User->>Studio: Selects Document, Format, Audience, Tone, Constraints & Models
    Studio->>Route: POST /api/transformations (Job Request)
    Route->>DB: Create TransformationJob (status: PENDING)
    Route->>Pipe: Execute Job asynchronously
    Pipe->>DB: Update Job status to PROCESSING
    
    par For Each Selected Model
        Pipe->>Registry: get_model(model_id)
        Registry-->>Pipe: Model Instance
        alt Long Document & Model is Groq
            Pipe->>Pipe: Context Extractive Reducer (bound prompt to 3,500 words)
        end
        Pipe->>Model: generate(prompt_context, generation_params)
        alt Generation succeeds on CUDA
            Model-->>Pipe: GenerationResult (content, tokens, latency)
        else CUDA fails (e.g. OOM or driver issue)
            Model->>Model: Automatic recovery -> Reload cached model on CPU
            Model-->>Pipe: GenerationResult (device: cpu, fallback_reason recorded)
        end
        Pipe->>Validator: evaluate_constraints(content, keywords, prohibitions, length)
        Validator-->>Pipe: Controllability Score & Compliance Dictionary
        Pipe->>DB: Insert GeneratedOutput
        Pipe->>Verif: verify_output(output_id, content, original_document_chunks)
        Verif-->>Pipe: VerificationReport (FCS, supported/contradicted claims)
        Pipe->>DB: Save VerificationReport, ExtractedClaims, EvidenceReferences
    end

    Pipe->>DB: Update Job status to COMPLETED
    Studio->>Route: GET /api/transformations/{job_id}/results
    Route-->>Studio: Returns all generated outputs with verification badges
```

---

## 5. Database Schema & Entity Relationships

```mermaid
erDiagram
    DOCUMENTS ||--o{ DOCUMENT_CHUNKS : "contains"
    DOCUMENTS ||--o{ TRANSFORMATION_JOBS : "source_of"
    TRANSFORMATION_JOBS ||--o{ GENERATED_OUTPUTS : "produces"
    GENERATED_OUTPUTS ||--o{ EXTRACTED_CLAIMS : "contains"
    EXTRACTED_CLAIMS ||--o{ EVIDENCE_REFERENCES : "supported_by"
    DOCUMENT_CHUNKS ||--o{ EVIDENCE_REFERENCES : "provides_evidence_for"
    GENERATED_OUTPUTS ||--o{ VERIFICATION_REPORTS : "validated_by"
    GENERATED_OUTPUTS ||--o{ EVALUATION_RESULTS : "scored_by"
    GENERATED_OUTPUTS ||--o{ HUMAN_FEEDBACK : "rated_by"
    DATASETS ||--o{ DATASET_DOCUMENTS : "contains"
    DATASET_DOCUMENTS ||--o{ REFERENCE_ANNOTATIONS : "has_reference_outputs"
```

Primary tables:
- `documents`: Source file metadata, hash, extracted text, raw file path.
- `document_chunks`: Fine-grained chunk units with page, section, and character offsets.
- `transformation_jobs`: Execution job state, target format, audience, tone, constraints.
- `generated_outputs`: Model outputs, versioning, generation parameters, latency, tokens.
- `extracted_claims`: Atomic claims parsed from outputs.
- `evidence_references`: Mappings between claims and supporting source chunks.
- `verification_reports`: Aggregated verification scores and summaries.
- `evaluation_results`: Granular ROUGE, coverage, consistency, and controllability metrics.
- `human_feedback`: Likert-scale human ratings (accuracy, completeness, readability, suitability).
- `datasets` & `reference_annotations`: Golden benchmarks for repeatable comparisons.

---

## 6. AI Model Layer & Registry Pattern

### 6.1 Class Hierarchy
```mermaid
classDiagram
    class BaseTransformationModel {
        <<abstract>>
        +load() None*
        +unload() None*
        +generate(prompt_or_text: str, config: GenerationConfig) GenerationResult*
        +get_metadata() ModelMetadata*
        +validate_configuration(config: GenerationConfig) bool*
        +is_available() bool*
    }

    class ExtractiveEngine {
        -tfidf_ranker: TFIDFSummarizer
        -textrank_ranker: TextRankSummarizer
        +generate() GenerationResult
        +get_metadata() ModelMetadata
    }

    class LocalSeq2SeqEngine {
        -model_name: str
        -model: PreTrainedModel
        -tokenizer: PreTrainedTokenizer
        -device: str
        +load() None
        +unload() None
        +generate() GenerationResult
        -_recover_cpu_inference() GenerationResult
    }

    class GroqInstructionEngine {
        -client: Groq
        -model_id: str
        -context_reducer: ExtractiveEngine
        +generate() GenerationResult
        -_build_system_prompt() str
        -_reduce_context_if_needed() str
    }

    class ModelRegistry {
        -_instance: ModelRegistry
        -_lock: RLock
        -_models: Dict[str, BaseTransformationModel]
        +register_model(model: BaseTransformationModel)
        +get_model(model_id: str) BaseTransformationModel
        +list_models() List[ModelMetadata]
        +unload_all()
    }

    BaseTransformationModel <|-- ExtractiveEngine
    BaseTransformationModel <|-- LocalSeq2SeqEngine
    BaseTransformationModel <|-- GroqInstructionEngine
    ModelRegistry o-- BaseTransformationModel : registers and manages
```

### 6.2 Architectural Highlights
1. **Thread-Safe Singleton Registry**: Uses `threading.RLock` to eliminate race conditions during concurrent multi-model executions.
2. **CUDA Failure Auto-Recovery**: If a GPU inference fails, `LocalSeq2SeqEngine` frees GPU cache, reloads the model on `cpu`, retries generation, and annotates the fallback reason in output metadata.
3. **Context Bounding for Cloud LLMs**: Long documents (>3,500 words) are reduced using an extractive ranking pass before prompting Groq, avoiding TPM limits while preserving the complete source for claim verification.

---

## 7. Factual Verification & Hallucination Detection

```mermaid
flowchart LR
    A["Generated Content"] --> B["Atomic Claim Extractor"]
    B --> C["Numbers, Dates, Entities, Policies"]
    C --> D["TF-IDF Evidence Retriever"]
    D --> E["Source Document Chunks"]
    E --> F["Multi-Method Fact Verifier"]
    F --> G["Decision Matrix"]
    G --> H1["SUPPORTED (Green)"]
    G --> H2["PARTIALLY SUPPORTED (Yellow)"]
    G --> H3["UNSUPPORTED (Orange)"]
    G --> H4["CONTRADICTED (Red)"]
    G --> H5["REQUIRES HUMAN REVIEW (Gray)"]
```

### Mathematical Formula for Factual Consistency Score (FCS)
$$\text{FCS} = \frac{N_{\text{supported}} + 0.5 \cdot N_{\text{partially\_supported}}}{N_{\text{total\_claims}}}$$

---

## 8. Five Evaluation Dimensions

1. **Text Similarity**: ROUGE-1, ROUGE-2, ROUGE-L, and BERTScore token similarity.
2. **Content Coverage**: Key Fact Recall, Named Entity Recall, and Numerical Fact Recall against gold annotations.
3. **Factual Grounding**: Factual Consistency Score (FCS).
4. **Controllability**: Compliance with word count budgets, required keywords, and prohibited terms.
5. **Computational Efficiency**: Latency (ms), token throughput, memory usage (MB), and estimated cost ($).

---

## 9. Security & SSRF Defense

```mermaid
flowchart TD
    URL["Target URL"] --> DNS["DNS Resolution Check"]
    DNS --> Filter{"IP Classifier Check"}
    Filter -->|127.0.0.1 / localhost| Block["Block (Loopback)"]
    Filter -->|10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16| Block2["Block (RFC 1918 Private)"]
    Filter -->|169.254.169.254| Block3["Block (Cloud Metadata)"]
    Filter -->|Public IP| Allow["Permit Scrape"]
```

- **SSRF Protection**: Private subnets and cloud metadata endpoints are strictly denied.
- **Server-Side API Keys**: Groq and Hugging Face secrets remain exclusively on the backend.
- **Prompt Injection Defense**: Source chunks are isolated as pure data within `<source_document>` delimiters.
