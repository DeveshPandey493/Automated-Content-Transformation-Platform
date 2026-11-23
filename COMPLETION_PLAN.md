# Completion Plan — Automated Content Transformation Platform (SIH 2026)

## Current Status
- **Phases 0-4 + 5 (partial)**: ✅ COMPLETED
- **Phase 5**: TASK-502 (Benchmark Dataset) & TASK-503 (Evaluation Dashboard UI) — 🟡 IN_PROGRESS
- **Phases 6-8**: ⏳ NOT_STARTED

---

## Phase 5: Evaluation Framework & Benchmark Dataset (Complete)

### TASK-502: Expand Benchmark Dataset (2 → 30+ Documents)
**Files**: `backend/app/data/curated_benchmark.json`, `docs/DATASET_CARD.md`
- Add 28+ documents from: NITI Aayog, WHO, Govt of India (MNRE, NITI, DST, MoHFW), World Bank
- Each doc: extracted_text, gold_key_facts, gold_entities, gold_numbers, reference_outputs for 4 formats
- Run `DatasetService.seed_benchmark_dataset()` to populate

### TASK-503: Evaluation Dashboard UI with Recharts
**Files**: `frontend/src/app/evaluation/page.tsx`, `frontend/src/app/datasets/page.tsx`
- Radar charts comparing 3 models × 5 dimensions
- Bar charts for ROUGE/BERTScore/Factual Consistency
- Comparison tables with sortable columns
- Filter by document, format type, model
- Connect to `/api/evaluations/compare` and `/api/evaluations/run/{output_id}`

---

## Phase 6: Export, Human Review & Versioning

### TASK-601: Multi-Format Export Engine (Already Implemented - Connect UI)
**Files**: `backend/app/services/export/exporter.py` (✅), `backend/app/api/routes/exports.py` (✅)
- Export buttons already in Review page - verify they work
- Test PDF, DOCX, Markdown, TXT exports

### TASK-602: Output Versioning & Human Feedback History
**Files**: `backend/app/services/transformation/versioning.py`, `backend/app/db/models/output.py`, `frontend/src/app/review/history.tsx`
- Add version tracking to GeneratedOutput model
- Store edit history with diffs
- Display rating history in Review page
- API endpoints for version tree and feedback retrieval

---

## Phase 7: Comprehensive Testing & Security Hardening

### TASK-701: Backend Test Suite
**Files**: `backend/tests/` (expand existing)
- Add tests for: local seq2seq models, Groq engine, evaluation metrics, export endpoints, dataset seeding
- SSRF boundary testing
- Target: ≥80% core service coverage

### TASK-702: Frontend Tests
**Files**: `frontend/tests/`
- Component unit tests (Jest/React Testing Library)
- Playwright E2E: Document upload → Transform → Verify → Export workflow

---

## Phase 8: SIH Demonstration Readiness

### TASK-801: End-to-End Demo Script & Sample Dossiers
**Files**: `docs/DEMO_SCRIPT.md`, `sample_data/`
- Step-by-step walkthrough with screenshots
- 3-5 curated sample documents (Govt reports)
- Expected outputs for all 4 formats × 3 models
- Fact verification breakdown
- One-click PDF export demo

---

## Implementation Order

1. **TASK-502**: Expand benchmark dataset (28+ more documents)
2. **TASK-503**: Create Evaluation Dashboard UI (`/evaluation` page) with Recharts
3. **TASK-503**: Create Datasets UI (`/datasets` page) for browsing benchmark
4. **TASK-602**: Add versioning + feedback history to Review page
5. **TASK-701**: Expand backend tests
6. **TASK-702**: Add frontend E2E tests
7. **TASK-801**: Create demo script and sample dossiers
8. **Final**: Run all tests, verify build, commit