# PROJECT_REQUIREMENTS.md — Product & Technical Requirements Specification
**Smart India Hackathon 2026 — Gen AI Platform for Automated Content Transformation**

---

## 1. Executive Summary & Problem Context
Governmental and enterprise entities produce high-volume authoritative documentation (white papers, policy gazettes, statistical briefs, research reports). Disseminating this information requires synthesizing distinct communication formats customized for different target demographics:
- **Executive Summary**: Synthesizes strategic implications, key metrics, and recommended actions for senior leaders.
- **Public Advisory**: Clear, direct, action-oriented guidance and precautions for citizens with zero jargon.
- **Social Media Posts**: High-impact, character-constrained posts for LinkedIn and X with relevant hashtags and verifiable assertions.
- **FAQ**: Structured Question-and-Answer pairs resolving high-frequency queries backed strictly by cited source passages.

### Core Problem
Traditional automated generation produces:
1. Hallucinated numbers, ungrounded dates, and fabricated policies.
2. Loss of critical nuances and vital context across summarization.
3. Inability to control tone, complexity, and audience targeting.
4. Opaque black-box models with zero source traceability or explainability.

---

## 2. Functional Requirements (FR)

### FR-1: Multi-Source Document Ingestion
- Ingest PDF documents via PyMuPDF (`fitz`), preserving page structure and metadata.
- Ingest DOCX files via `python-docx`, maintaining section hierarchy and lists.
- Ingest TXT and direct plain-text strings.
- Ingest Web URLs with SSRF protection, automated article text extraction, and domain metadata recording.
- Validate MIME type, reject malicious file extensions, and enforce a 25MB maximum upload limit.

### FR-2: Document Segmentation & Traceability
- Segment raw text into semantic sentence chunks with configurable overlap.
- Assign every chunk a deterministic `chunk_id`, `page_number` (where applicable), `section_heading`, and character offset range (`char_start`, `char_end`).
- Maintain bidirectional references between generated claims and source chunks.

### FR-3: Multi-Paradigmatic Transformation Engine
- Support 3 distinct generation approaches:
  1. **Extractive**: TF-IDF & TextRank sentence ranking (100% local, no external API).
  2. **Local Transformer Seq2Seq**: Hugging Face `google/flan-t5-base` and `facebook/bart-base` with dynamic CPU/GPU inference.
  3. **Instruction-Tuned LLM**: Groq Cloud SDK (`GROQ_MODEL`) with streaming/batch token telemetry.
- Support 4 target formats:
  - Executive Summary (Overview, Key Findings, Statistics, Implications, Recommended Actions).
  - Public Advisory (Title, Intended Audience, Situation, Verified Facts, Precautions, Official Contacts).
  - Social Media Posts (LinkedIn formatted post, X/Twitter concise post with hashtags).
  - FAQ (Question, Grounded Answer, Supporting Evidence, Out-of-Scope indicators).
- Controllable Parameters:
  - Target Audience: Senior Management, Citizens, Industry Professionals, Students, Technical Experts.
  - Tone: Professional, Formal, Conversational, Neutral, Persuasive, Informative.
  - Length Budget: Short (<150 words), Medium (150-350 words), Detailed (350-700 words), Custom Word Limit.
  - Constraints: Required keywords, prohibited claims/phrases, required sections, must-preserve numbers and dates.

### FR-4: Factual Verification & Hallucination Detection
- Parse generated output into atomic factual claims (numbers, dates, percentages, entities, events, policies).
- Retrieve top $K$ relevant source chunks per claim using semantic search and token overlap.
- Classify each claim into one of five statuses:
  - `SUPPORTED`: Direct factual corroboration in source text.
  - `PARTIALLY_SUPPORTED`: Main premise corroborated; secondary detail unverified.
  - `UNSUPPORTED`: Claim cannot be established from source text.
  - `CONTRADICTED`: Claim conflicts directly with stated source figures, dates, or assertions.
  - `REQUIRES_HUMAN_REVIEW`: Nuanced, speculative, or inferential claim requiring expert verification.
- Provide a confidence score ($0.0 - 1.0$) and human-readable explanation for each verdict.

### FR-5: Quantitative 5-Dimension Evaluation
- **Content Coverage**: Key fact recall, entity coverage, numerical preservation ratio.
- **Text Similarity**: ROUGE-1, ROUGE-2, ROUGE-L, and BERTScore (precision, recall, F1).
- **Factual Consistency**: Factual Consistency Score ($\text{FCS} \in [0, 1]$), contradiction rate, unsupported claim count.
- **Controllability**: Word budget compliance percentage, required keyword presence rate, prohibited term violation count, structural section adherence.
- **Computational Efficiency**: Wall-clock generation latency (ms), input/output tokens, tokens/second throughput, peak VRAM/RAM utilization, estimated API cost.
- **Human Evaluation**: 5-point Likert scale on Accuracy, Completeness, Readability, and Suitability.

### FR-6: Export & Versioning
- Export generated and approved outputs into PDF (ReportLab), DOCX (python-docx), Markdown, and TXT with evidence footnotes.
- Maintain full version history for every output revision, tracking editor changes and updated verification scores.

---

## 3. Non-Functional Requirements (NFR)

### NFR-1: Performance & Resource Footprint
- Extractive summarization latency $< 1.5$ seconds for documents under 20 pages.
- Local neural models (`flan-t5-base`, `bart-base`) must fit within a 6GB VRAM budget and execute with automatic CPU fallback.
- Lazy model loading: models are loaded on-demand and can be explicitly purged from GPU memory.

### NFR-2: Security & Reliability
- Zero leak of API keys (`GROQ_API_KEY`, `HF_TOKEN`) to the client or in API responses.
- SSRF mitigation on URL imports: reject localhost, loopback, private RFC 1918 subnets, and cloud metadata IPs.
- Prevent Prompt Injection: source document content is strictly sanitized and passed as isolated untrusted text context.

### NFR-3: Modularity & Extensibility
- Clean separation between API routes, application services, and ML execution engines.
- Adding a new model provider requires only subclassing `BaseTransformationModel` and registering it in `ModelRegistry`.
