# Automated Content Transformation Platform
### Smart India Hackathon (SIH) 2026 — Gen AI Platform for Automated Content Transformation

> **One source of truth. Multiple audiences. Multiple communication formats. Verifiable factual accuracy.**

---

## 🌟 Vision & Key Capabilities

Organizations repeatedly transform a single source document into different communication formats for different audiences:
- **Executive Summary** for senior management and decision makers.
- **Public Advisory** for citizens with actionable facts and precautions.
- **Social Media Posts** for LinkedIn and X (Twitter) with tailored conciseness and hashtags.
- **FAQ** for operational or citizen query resolution with source evidence.

This platform automates this transformation while preserving factual accuracy, enforcing source traceability, and benchmarking three generation paradigms:
1. **Extractive Summarisation (Baseline)**: TF-IDF and graph-based TextRank sentence ranking.
2. **Local Transformer Seq2Seq**: Hugging Face `google/flan-t5-base` and `facebook/bart-base`.
3. **Instruction-Tuned Cloud LLM**: High-speed inference via Groq Cloud API.

### Differentiating Capabilities
- **Factual Verification & Hallucination Detection**: Extracts atomic factual claims (numbers, dates, entities, policies) and cross-checks them against source text chunks, classifying them into `Supported`, `Partially Supported`, `Unsupported`, `Contradicted`, or `Requires Human Review`.
- **Source Traceability**: Every sentence and claim links directly to its source chunk, page number, and character offsets.
- **Audience & Tone Controllability**: Fine-grained configuration for target audience, tone, length, required keywords, and prohibited claims.
- **Empirical 5-Dimensional Evaluation**: Quantitative benchmarking covering Content Coverage, ROUGE-1/2/L & BERTScore, Factual Consistency Score, Controllability Compliance, and Latency/Token Efficiency.
- **Curated Ground-Truth Benchmark**: 30+ public domain policy, health, and economic documents (NITI Aayog, WHO, Govt of India) with reference annotations.

---

## 🏗️ Architecture

```
Automated Content Transformation Platform/
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── api/routes/       # Thin API route controllers
│   │   ├── core/             # Configuration, logging, security, errors
│   │   ├── db/               # SQLAlchemy models & dual-mode session manager
│   │   ├── schemas/          # Pydantic v2 validation models
│   │   ├── services/         # Ingestion, chunking, transformation, verification, evaluation
│   │   ├── ml/               # Model registry, extractive, seq2seq, Groq engines
│   │   └── pipelines/        # Transformation & verification orchestration pipelines
│   ├── tests/                # Automated pytest suite
│   └── requirements.txt      # Backend Python dependencies
├── frontend/                 # Next.js 14+ App Router & Tailwind CSS UI
│   ├── src/app/              # Dashboard, Documents, Transform, Review, Models, Evaluation, Datasets
│   ├── src/components/       # Reusable UI widgets & inspection drawers
│   └── package.json
├── docs/                     # Specifications, guides, methodology & architecture
├── storage/                  # Uploads and export artifacts
├── docker-compose.yml        # PostgreSQL 16 & full container orchestration
├── AGENTS.md                 # Multi-agent protocol & coding conventions
├── ARCHITECTURE.md           # System design & architecture specification
├── TASKS.md                  # Task roadmap with acceptance criteria
├── DECISIONS.md              # Architectural Decision Records (ADR)
└── HANDOFF.md                # Session continuity & resume state
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11+ (Python 3.13 recommended)
- Node.js 18+ (Node 24 recommended)
- Git
- NVIDIA GPU with CUDA (optional, CPU inference supported)
- Docker & Docker Compose (optional; SQLite fallback enabled for zero-dependency development)

### 1. Clone & Configure Environment
```bash
git clone <repo-url>
cd "Automated Content Transformation Platform"
cp .env.example .env
# Edit .env with your GROQ_API_KEY and preferences
```

### 2. Run Backend
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive API docs are available at [http://localhost:8000/docs](http://localhost:8000/docs).

### 3. Run Frontend
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🧪 Running Tests
```bash
# Backend unit & integration tests
pytest backend/tests/ -v

# Frontend tests
cd frontend
npm test
```

---

## ⚖️ License
Developed for Smart India Hackathon 2026. Open-source under the Apache 2.0 License.
