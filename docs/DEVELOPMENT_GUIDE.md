# DEVELOPMENT_GUIDE.md — Engineer & Developer Onboarding Guide
**Smart India Hackathon 2026 — Gen AI Platform for Automated Content Transformation**

---

## 1. Directory Structure

```
Automated Content Transformation Platform/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # FastAPI routers (documents, transformations, models, verification, etc.)
│   │   ├── core/                # config.py, security.py, logging.py, exceptions.py
│   │   ├── db/
│   │   │   ├── base.py          # Declarative Base
│   │   │   ├── session.py       # Engine & session management (dual-mode)
│   │   │   └── models/          # SQLAlchemy model definitions
│   │   ├── schemas/             # Pydantic v2 schemas
│   │   ├── services/
│   │   │   ├── ingestion/       # PDF, DOCX, TXT, URL extractors & validators
│   │   │   ├── chunking/        # Sentence chunking & offset tracking
│   │   │   ├── transformation/  # Prompt assembly, constraint enforcement
│   │   │   ├── verification/    # Claim extraction, evidence retrieval, verification
│   │   │   ├── evaluation/      # ROUGE, BERTScore, consistency, controllability
│   │   │   └── export/          # PDF (ReportLab), DOCX, MD, TXT exporter
│   │   ├── ml/
│   │   │   ├── base.py          # BaseTransformationModel interface
│   │   │   ├── registry.py      # ModelRegistry singleton
│   │   │   ├── extractive/      # TF-IDF & TextRank implementations
│   │   │   ├── seq2seq/         # FLAN-T5 & BART local engines
│   │   │   └── instruction/     # Groq API engine
│   │   └── pipelines/           # Multi-stage transformation & verification pipelines
│   ├── tests/                   # Pytest automated test suite
│   └── requirements.txt         # Dependencies
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js 14 App Router pages
│   │   ├── components/          # Reusable UI components & drawers
│   │   ├── lib/                 # API client & utilities
│   │   └── types/               # TypeScript interfaces
│   └── package.json
└── docs/                        # Complete technical documentation
```

---

## 2. Adding a New Model Provider

To add a new generation engine (e.g. Anthropic, Mistral, or Llama 3 via Ollama):
1. Create a class subclassing `BaseTransformationModel` in `backend/app/ml/`.
2. Implement all required methods: `load()`, `unload()`, `generate()`, `get_metadata()`, `validate_configuration()`, `is_available()`.
3. Register the class in `backend/app/ml/registry.py`.
4. The new model will immediately become available in the Model Laboratory, Transformation Studio, and Evaluation comparison matrix without modifying route handlers!

---

## 3. Code Standards & Git Workflow
- Format with `ruff` or `black` for Python; `prettier` and `eslint` for TypeScript.
- Type hints are strictly required on all Python function arguments and return types.
- Never write credentials into source code. Always use `get_settings()` from `app.core.config`.
- Maintain test coverage by adding tests in `backend/tests/` for every new service or endpoint.
