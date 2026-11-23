# AGENTS.md — Multi-Agent Engineering Protocol & System Guidelines
**Smart India Hackathon 2026 — Gen AI Platform for Automated Content Transformation**

---

## 1. Project Purpose
Organizations repeatedly transform a single source document into different communication formats for diverse audiences:
1. **Executive Summary** for senior leadership and decision makers.
2. **Public Advisory** for citizens with actionable precautions and facts.
3. **Social Media Posts** for LinkedIn and X (formerly Twitter) with appropriate conciseness and hashtags.
4. **FAQ** for operational or citizen query resolution with grounded evidence.

### Core Product Principle
> **One source of truth. Multiple audiences. Multiple communication formats. Verifiable factual accuracy.**

The platform implements, benchmarks, and provides transparent comparisons across three distinct generation paradigms:
1. **Extractive Summarisation (Local Baseline)**: TF-IDF & TextRank sentence graph ranking.
2. **Transformer Seq2Seq Generation (Local Neural)**: Hugging Face `google/flan-t5-base` & `facebook/bart-base`.
3. **Instruction-Tuned LLM (Cloud High-Throughput)**: Groq SDK inference (`GROQ_MODEL`).

---

## 2. Technology Stack & Environment
- **Operating System**: Windows 11 (PowerShell terminal)
- **Hardware Profile**: NVIDIA GeForce RTX 4050 Laptop GPU (6GB VRAM, CUDA 13.2), Intel/AMD CPU, 33GB+ free storage.
- **Backend**: Python 3.13+, FastAPI, Pydantic v2, SQLAlchemy 2.0 (PostgreSQL primary with automatic SQLite fallback), Alembic.
- **AI/ML Engine**: PyTorch 2.6+cu124, Hugging Face Transformers & Tokenizers, Groq Python SDK, Scikit-learn, NLTK, ROUGE, BERTScore.
- **Document Processing**: PyMuPDF (fitz), python-docx, Trafilatura/BeautifulSoup4, Tesseract OCR hook.
- **Frontend**: Next.js 14+ (App Router), React 18/19, TypeScript, Tailwind CSS, Lucide icons, Recharts.
- **Containers & Infrastructure**: Docker, Docker Compose (PostgreSQL 16).

---

## 3. Strict Architectural Rules
1. **Never use hardcoded mock responses**: Every generation, metric, and verification report must originate from an actual model or algorithmic evaluation.
2. **Thin API Route Handlers**: Zero business or AI logic inside route handlers (`backend/app/api/`). Handlers only validate requests with Pydantic and delegate to `services/` or `pipelines/`.
3. **Decoupled Model Providers**: All generation engines implement the unified `BaseTransformationModel` interface registered in `ModelRegistry`. The frontend only communicates with backend API endpoints.
4. **Independent Executability**: The platform must run full extractive and local transformer workflows even when Groq is unavailable, offline, or rate-limited.
5. **No Blind Model Downloads**: Model loading must verify disk space and GPU memory before initializing heavy neural weights.
6. **Factual Grounding & Traceability**: Generated claims must be extracted and mapped to specific source document chunks (Document ID, Chunk ID, Page/Section number, character offsets).
7. **Empirical Evaluation**: Benchmark comparisons must run on identical input chunks and consistent parameters using standard metrics (Coverage, ROUGE-1/2/L, BERTScore, Controllability, Latency, and Human Review).
8. **Never claim an LLM statement is factual merely because the LLM generated it**: Verification must use multi-method evidence checking (exact number/date matching, entity matching, embedding similarity, and NLI logic).

---

## 4. Coding Conventions & Standards
- **Python**: PEP 8 compliance, strict type hints (`typing`, `pydantic`), explicit docstrings, structured logging with `structlog`/standard `logging`.
- **Async vs Sync**: CPU/GPU-bound ML inference runs in threadpools (`run_in_threadpool` or `asyncio.to_thread`) to prevent blocking FastAPI's async event loop.
- **Database Access**: SQLAlchemy 2.0 select syntax (`select(Model).where(...)`). Sessions managed via FastAPI dependency injection.
- **TypeScript / React**: Strict type checking, zero `any` types where possible, client-side state driven by clean custom hooks or React Query/SWR patterns.
- **Error Handling**: Use custom domain exceptions (`AppException`, `ModelInferenceError`, `DocumentProcessingError`) with structured JSON error responses.

---

## 5. Setup & Operational Commands
```powershell
# Backend Setup
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run Backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run Tests
pytest tests/ -v

# Frontend Setup
cd frontend
npm install
npm run dev
```

---

## 6. Multi-Agent Protocol
Before starting work in any session:
1. Read `AGENTS.md`, `ARCHITECTURE.md`, `TASKS.md`, `DECISIONS.md`, and `HANDOFF.md`.
2. Inspect Git status and existing code.
3. Select the next `NOT_STARTED` or `IN_PROGRESS` task in `TASKS.md`.
4. Implement the task completely with verifiable automated tests.
5. Update `TASKS.md`, `DECISIONS.md`, and `HANDOFF.md` before concluding.
