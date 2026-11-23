# ACTP - Automated Content Transformation Platform
## SIH 2026 Demonstration Script & Walkthrough

---

## 🎯 Demo Overview

**Duration:** 15-20 minutes  
**Audience:** SIH 2026 Judges, Government Officials, Technical Evaluators  
**Objective:** Demonstrate end-to-end transformation of a single government report into 4 communication formats with 3-model comparison, factual verification, and professional export.

---

## 📋 Pre-Requisites

### System Requirements
- Backend running on `http://localhost:8000`
- Frontend running on `http://localhost:3000`
- Sample document: `sample_data/NITI_Aayog_AI_Strategy_2024.pdf` (provided)

### Quick Start
```bash
# Terminal 1 - Backend
cd backend
source venv/Scripts/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend
cd frontend
npm run dev

# Access: http://localhost:3000
```

---

## 🎬 Step-by-Step Demo Walkthrough

### Phase 1: Document Ingestion (2 minutes)

**Goal:** Upload and process a government report with traceable chunking.

**Steps:**
1. **Navigate to Document Library** → Click "Document Library" in sidebar
2. **Upload Document** → Click "Upload Document" → Select `sample_data/NITI_Aayog_AI_Strategy_2024.pdf`
3. **Observe Processing** → System extracts text, identifies pages/sections, creates chunks
4. **Inspect Chunks** → Click document card → Open "Chunk Inspector" drawer
   - Show: Page numbers, section headings, character offsets, token counts
   - Highlight: 100% traceability from any generated claim back to source

**Talking Points:**
- "Every sentence is mapped to its exact source location (page, section, character offset)"
- "SSRF-protected URL ingestion also available for live government portals"
- "Supports PDF, DOCX, TXT, and direct text paste"

---

### Phase 2: Transformation Studio - Multi-Format Generation (5 minutes)

**Goal:** Configure and execute transformation into 4 formats with 3 AI models.

**Steps:**
1. **Navigate to Transformation Studio** → Click "Transformation Studio" in sidebar
2. **Select Source Document** → Choose "NITI Aayog AI Strategy 2024" from dropdown
3. **Configure Format 1: Executive Summary**
   - Format: Executive Summary
   - Audience: Senior Management & Leadership
   - Tone: Formal & Authoritative
   - Length: Medium (~250 words)
4. **Configure Format 2: Public Advisory**
   - Format: Public Advisory
   - Audience: General Citizens & Public
   - Tone: Clear & Direct (Plain Language)
   - Length: Short (~120 words)
5. **Configure Format 3: Social Media Posts**
   - Format: Social Media Post
   - Audience: Industry & Domain Professionals
   - Tone: Conversational & Engaging
   - Length: Short
6. **Configure Format 4: FAQ Document**
   - Format: FAQ Document
   - Audience: Students & Academic Researchers
   - Tone: Neutral & Analytical
   - Length: Detailed (~500 words)

**Multi-Model Selection (Key Differentiator):**
- Select **ALL THREE** model families:
  - ✅ **Extractive (TextRank)** - Local baseline, verbatim sentences
  - ✅ **Extractive (TF-IDF)** - Local baseline, statistical relevance
  - ✅ **Seq2Seq (FLAN-T5-Base)** - Local neural, generative
  - ✅ **Seq2Seq (BART-Base)** - Local neural, generative
  - ✅ **Groq (GPT-OSS-120B)** - Cloud instruction-tuned LLM
- Explain: "Simultaneous 5-model comparison on IDENTICAL input chunks"

**Execute Transformation:**
- Click "Execute Transformation (5 Models)"
- Watch real-time progress: PENDING → PROCESSING → COMPLETED
- Navigate to Review page via auto-redirect

**Talking Points:**
- "Zero hardcoded responses - every output comes from actual model execution"
- "Local models run 100% offline on RTX 4050 (6GB VRAM) with CPU fallback"
- "Groq integration handles rate limits with exponential backoff"
- "Controllability constraints: required keywords, prohibited terms, word budgets"

---

### Phase 3: Factual Verification & Source Traceability (4 minutes)

**Goal:** Demonstrate claim-level verification with source grounding.

**Steps:**
1. **Navigate to Review & Traceability** → Click "Review & Traceability" in sidebar
2. **Select Job** → Choose the transformation job just created
3. **Inspect Executive Summary (TextRank)**
   - Show colored claim highlights:
     - 🟢 **Green (Supported)** - Direct source match
     - 🟡 **Yellow (Partially Supported)** - Context match, partial evidence
     - 🔴 **Red (Contradicted/Unsupported)** - No evidence or discrepancy
4. **Click Any Claim** → Side panel opens showing:
   - Exact source chunk text
   - Page number & section heading
   - Character offsets
   - Relevance score (TF-IDF cosine similarity)
   - Verification rationale
5. **Review Factual Consistency Score (FCS)**
   - Displayed per output: `FCS = (Supported + 0.5 × Partially Supported) / Total Claims`
   - Example: 87% FCS = 13/15 claims fully supported

**Verification Methods Demonstrated:**
- **Number/Date Matching** - Exact figure verification (e.g., "₹10,000 crore" vs "₹10000 crore")
- **Entity Matching** - Named entity presence in source
- **Semantic Similarity** - TF-IDF cosine + embedding overlap
- **NLI Logic** - Natural Language Inference for contradiction detection

**Talking Points:**
- "No claim is trusted merely because an LLM generated it"
- "Every statistic, date, entity is cross-referenced against source chunks"
- "Human-in-the-loop: reviewers can approve/reject individual claims"
- "Audit trail: complete verification report exportable for compliance"

---

### Phase 4: Evaluation Dashboard - Comparative Benchmarking (3 minutes)

**Goal:** Show quantitative comparison across all 5 models × 4 formats.

**Steps:**
1. **Navigate to Evaluation Dashboard** → Click "Evaluation Dashboard" in sidebar
2. **Select Document** → Choose "NITI Aayog AI Strategy 2024"
3. **View Radar Chart** → 5-dimensional comparison:
   - **ROUGE-1/2/L** - N-gram overlap with reference
   - **BERTScore** - Contextual semantic similarity
   - **Key Fact Coverage** - % of gold facts captured
   - **Controllability** - Constraint adherence (length, keywords, tone)
   - **Factual Consistency** - Verification-derived score
4. **View Bar Charts** → Latency & Cost comparison
   - Extractive: ~50ms, $0.00
   - FLAN-T5/BART: ~2-5s (GPU), $0.00
   - Groq: ~1-3s, ~$0.0001 per 1K tokens
5. **Detailed Comparison Table** → Side-by-side metrics per format
6. **Export Evaluation Report** → Click "Export" → PDF with full methodology

**Talking Points:**
- "Identical input chunks → fair apples-to-apples comparison"
- "30+ curated benchmark documents (NITI Aayog, WHO, Govt of India)"
- "Human reference annotations for all 4 formats"
- "Transparent methodology: all formulas documented in DATASET_CARD.md"

---

### Phase 5: Professional Export & Versioning (2 minutes)

**Goal:** Export verified output in multiple formats with traceability.

**Steps:**
1. **From Review Page** → Select best output (e.g., Groq Executive Summary)
2. **Click Export** → Choose format:
   - **PDF** (ReportLab) - Formal briefing with tables, footnotes
   - **DOCX** (python-docx) - Editable Word document
   - **Markdown** - Developer-friendly, version-controllable
   - **TXT** - Plain text for archival
3. **Show Exported PDF** → Open and highlight:
   - Verification badges (🟢 Supported, 🟡 Partial, 🔴 Unsupported)
   - Source traceability footnotes: `[Chunk #3, p.5, §2.1]`
   - Evaluation metrics appendix
   - Generation parameters
   - Watermark: "ACTP - SIH 2026 | Model: groq/openai/gpt-oss-120b"
4. **Demonstrate Versioning** → Click "New Version" → Edit text → Save
   - Show version history tree
   - Compare v1 vs v2 (diff view)
5. **Human Feedback** → Submit 5-star rating (Accuracy, Completeness, Readability, Suitability)

**Talking Points:**
- "Production-ready exports with full audit trail"
- "Version control for collaborative editing workflows"
- "Human feedback loop for continuous model improvement"
- "All exports include verification report and evaluation metrics"

---

### Phase 6: Model Laboratory - Interactive Testing (1 minute)

**Goal:** Quick side-by-side prompt testing across models.

**Steps:**
1. **Navigate to Model Laboratory** → Click "Model Laboratory" in sidebar
2. **Enter Custom Prompt** → "Summarize India's AI mission in 3 sentences"
3. **Run All Models** → Observe parallel execution
4. **Compare Outputs** → Side-by-side view with latency/cost

**Talking Points:**
- "Instant model comparison for prompt engineering"
- "Availability status: Local models always available, Groq requires API key"
- "Resource monitoring: VRAM usage, latency, token counts"

---

## 📊 Sample Dossier: NITI Aayog AI Strategy 2024

### Source Document
- **Title:** "National Strategy for Artificial Intelligence - 2024 Update"
- **Source:** NITI Aayog, Government of India
- **Pages:** 42 | **Words:** ~18,500 | **Chunks:** 247
- **Key Topics:** AI Mission, Healthcare AI, Agriculture AI, Education, Smart Cities, Governance

### Expected Transformation Outputs

#### 1. Executive Summary (Senior Leadership)
**Key Elements:** Strategic Overview, Budget Allocation (₹10,300 cr), 5-Year Roadmap, 3 Priority Sectors, Governance Framework

#### 2. Public Advisory (Citizens)
**Key Elements:** What AI means for you, Data privacy rights, Government helplines, Digital literacy programs, Grievance redressal

#### 3. Social Media Posts
- **LinkedIn:** Professional announcement with 3 key stats, 5 hashtags (#AIForAll #DigitalIndia #NITIAayog)
- **X/Twitter:** 280-char hook + thread with infographics, #AIRevolution #IndiaAI

#### 4. FAQ (Operations)
**Sample Q&A:**
- Q: "How much funding for AI Mission?" A: "₹10,300 crore over 5 years (Source: p.3, §1.2)"
- Q: "Which sectors prioritized?" A: "Healthcare, Agriculture, Education (Source: p.7, §2.1)"
- Q: "Data privacy safeguards?" A: "DPDP Act 2023 compliance, sectoral regulators (Source: p.15, §3.4)"

---

## 🔬 Technical Deep-Dive Points (For Technical Evaluators)

### Architecture Highlights
1. **ModelRegistry Pattern** - Clean abstraction, hot-swappable engines
2. **Async Pipeline** - `run_in_threadpool` for GPU inference, non-blocking FastAPI
3. **Dual Database** - PostgreSQL primary, SQLite fallback (zero-config dev)
4. **Traceable Chunking** - Sentence-boundary aware, metadata-preserving
5. **Verification Pipeline** - Extractor → Retriever → Multi-method Classifier

### Code Quality
- **79% backend test coverage** (74 tests passing)
- **Type-safe** - Pydantic v2, strict TypeScript, SQLAlchemy 2.0
- **Security** - SSRF protection, input validation, rate limiting
- **Observability** - Structured logging, OpenAPI docs, health endpoints

### Innovation
- **Multi-paradigm comparison** on identical inputs (Extractive vs Seq2Seq vs Instruction-LLM)
- **Verification not trust** - Mathematical factual consistency scoring
- **Controllability as metric** - Keyword, length, tone, format adherence scored
- **Human-in-the-loop** - Versioning + 5-star feedback + claim-level approval

---

## 🎯 Key Demo Messages

| Message | Evidence in Demo |
|---------|------------------|
| **One Source → Multiple Audiences** | 4 formats from 1 PDF |
| **Verifiable, Not Just Generated** | Claim-level verification with source links |
| **Fair Model Comparison** | 5 models × identical chunks × 5 metrics |
| **Production Ready** | Export, versioning, feedback, audit trail |
| **Government-Grade Security** | SSRF protection, offline-capable, no data leakage |
| **Cost Effective** | Local models free, cloud only when needed |

---

## 🚨 Troubleshooting Quick Reference

| Issue | Resolution |
|-------|------------|
| Backend won't start | Check `.env` has `DATABASE_URL`, run `init_db()` |
| Frontend blank | Ensure backend on :8000, check browser console for CORS |
| Groq fails | Verify `GROQ_API_KEY` in `.env`, check rate limits |
| GPU OOM | Reduce batch size, enable CPU fallback in config |
| Port 8000/3000 busy | `netstat -ano \| findstr :8000` → kill process |

---

## 📁 Sample Data Files

```
sample_data/
├── NITI_Aayog_AI_Strategy_2024.pdf      # Primary demo document (42 pages)
├── WHO_Climate_Health_2023.pdf           # Backup: WHO report (28 pages)
├── MeitY_Digital_India_2024.pdf          # Backup: MeitY report (35 pages)
└── reference_outputs/                    # Gold standard references
    ├── executive_summary_ref.md
    ├── public_advisory_ref.md
    ├── social_posts_ref.md
    └── faq_ref.md
```

---

## 🏁 Demo Conclusion Script

> "In summary, the ACTP platform demonstrates:
> 
> 1. **Ingestion** - Any government document → traceable chunks
> 2. **Transformation** - 4 formats × 5 models → simultaneous generation
> 3. **Verification** - Every claim → source evidence → consistency score
> 4. **Evaluation** - Quantitative benchmarks → transparent comparison
> 5. **Export** - Professional outputs → full audit trail
> 
> This is not a prototype. This is a production-ready platform that government departments can deploy today to transform how they communicate with citizens, leadership, and stakeholders—grounded in factual accuracy, transparent in methodology, and accountable in execution.
> 
> **Thank you. Questions welcome."**

---

## 📞 Contact & Resources

- **Repository:** [GitHub Link]
- **Documentation:** `docs/ARCHITECTURE.md`, `docs/DATASET_CARD.md`
- **API Docs:** `http://localhost:8000/docs` (Swagger UI)
- **Health Check:** `http://localhost:8000/api/health`
- **Team:** SIH 2026 Team ACTP