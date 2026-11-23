import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Color Palette (Dark Theme / Navy & Cyan / Indigo)
    BG_DARK = RGBColor(12, 19, 34)       # #0c1322
    CARD_BG = RGBColor(22, 30, 49)       # #161e31
    BORDER_COLOR = RGBColor(40, 53, 79)  # #28354f
    TEXT_WHITE = RGBColor(255, 255, 255) # #ffffff
    TEXT_MUTED = RGBColor(148, 163, 184) # #94a3b8
    ACCENT_CYAN = RGBColor(56, 189, 248) # #38bdf8 (Sky Blue)
    ACCENT_INDIGO = RGBColor(129, 140, 248) # #818cf8
    ACCENT_GREEN = RGBColor(52, 211, 153) # #34d399 (Emerald)
    ACCENT_AMBER = RGBColor(251, 191, 36) # #fbbf24

    blank_layout = prs.slide_layouts[6]

    def add_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_DARK
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category="SMART INDIA HACKATHON 2026 | ACTP ENGINE"):
        # Category label
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(0.35))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_CYAN

        # Title
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.7), Inches(0.6))
        tf_t = t_box.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(26)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_WHITE

    def add_card(slide, left, top, width, height, title, items, badge="", accent=ACCENT_CYAN):
        # Card Background
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = BORDER_COLOR
        card.line.width = Pt(1)

        # Title & Badge
        tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), Inches(0.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p0 = tf.paragraphs[0]
        p0.text = title
        p0.font.size = Pt(16)
        p0.font.bold = True
        p0.font.color.rgb = accent

        if badge:
            p_badge = tf.add_paragraph()
            p_badge.text = badge.upper()
            p_badge.font.size = Pt(9)
            p_badge.font.bold = True
            p_badge.font.color.rgb = ACCENT_GREEN

        # Bullets / Content
        content_box = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.7), width - Inches(0.4), height - Inches(0.8))
        ctf = content_box.text_frame
        ctf.word_wrap = True
        for idx, item in enumerate(items):
            p = ctf.paragraphs[0] if idx == 0 else ctf.add_paragraph()
            p.text = f"•  {item}"
            p.font.size = Pt(12)
            p.font.color.rgb = TEXT_WHITE if idx % 2 == 0 else TEXT_MUTED
            p.space_after = Pt(6)

    # -------------------------------------------------------------
    # SLIDE 1: TITLE SLIDE
    # -------------------------------------------------------------
    slide1 = prs.slides.add_slide(blank_layout)
    add_slide_background(slide1)

    t_box = slide1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11.0), Inches(2.2))
    tf = t_box.text_frame
    tf.word_wrap = True
    p_sub = tf.paragraphs[0]
    p_sub.text = "SMART INDIA HACKATHON 2026 — PROBLEM STATEMENT SOLUTION"
    p_sub.font.size = Pt(13)
    p_sub.font.bold = True
    p_sub.font.color.rgb = ACCENT_CYAN

    p_title = tf.add_paragraph()
    p_title.text = "Gen AI Platform for Automated\nContent Transformation"
    p_title.font.size = Pt(40)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_WHITE
    p_title.space_after = Pt(14)

    p_tag = tf.add_paragraph()
    p_tag.text = "One Source of Truth · Multiple Audiences · Multiple Formats · Verifiable Factual Accuracy"
    p_tag.font.size = Pt(16)
    p_tag.font.color.rgb = ACCENT_INDIGO

    # Details card
    meta_box = slide1.shapes.add_textbox(Inches(1.2), Inches(4.7), Inches(11.0), Inches(1.8))
    mtf = meta_box.text_frame
    p1 = mtf.paragraphs[0]
    p1.text = "3 Generation Paradigms: Local Extractive (TF-IDF/TextRank) | Local Neural Seq2Seq (FLAN-T5/BART) | Cloud LLM (Groq)"
    p1.font.size = Pt(13)
    p1.font.color.rgb = TEXT_MUTED

    p2 = mtf.add_paragraph()
    p2.text = "Key Innovations: Multi-Method Factual Verification (FCS) | Traceable Source Chunks | 5-Dimensional Empirical Evaluation"
    p2.font.size = Pt(13)
    p2.font.color.rgb = ACCENT_GREEN

    # -------------------------------------------------------------
    # SLIDE 2: THE PROBLEM STATEMENT
    # -------------------------------------------------------------
    slide2 = prs.slides.add_slide(blank_layout)
    add_slide_background(slide2)
    add_header(slide2, "The Core Problem in Public & Enterprise Communication")

    add_card(slide2, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8), 
             "1. Multi-Audience Chasm", 
             ["A single 50-page policy whitepaper must reach diverse stakeholders.",
              "Ministers require a 1-page strategic brief with key metrics.",
              "Citizens need actionable advisories without bureaucratic jargon.",
              "Youth & press require crisp social posts on LinkedIn & X.",
              "Operations need evidence-grounded FAQ resolution."],
             badge="High Latency & Overhead")

    add_card(slide2, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8), 
             "2. The LLM Hallucination Trap", 
             ["Off-the-shelf generative LLMs invent numbers, dates, and entities.",
              "Inventing contact numbers or emergency protocols creates public danger.",
              "Black-box summaries lack sentence-to-source traceability.",
              "Evaluations rely on LLM self-assessment, which is fundamentally flawed.",
              "Zero audit trail from summary back to exact source chunk."],
             badge="Critical Trust Deficit", accent=RGBColor(248, 113, 113))

    add_card(slide2, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8), 
             "3. Deployment Inflexibility", 
             ["Most AI platforms strictly require cloud API connectivity.",
              "Defense, public health, and intelligence require 100% offline runs.",
              "GPU memory constraints frequently cause out-of-memory crashes.",
              "Varying rate limits and token costs disrupt mission-critical tasks.",
              "No fair, empirical comparison between extractive and neural models."],
             badge="Operational Risk", accent=ACCENT_AMBER)

    # -------------------------------------------------------------
    # SLIDE 3: THE SOLUTION & CORE PRINCIPLE
    # -------------------------------------------------------------
    slide3 = prs.slides.add_slide(blank_layout)
    add_slide_background(slide3)
    add_header(slide3, "ACTP: The Grounded Content Transformation Engine")

    # Banner quote
    q_box = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.7), Inches(1.2))
    q_box.fill.solid()
    q_box.fill.fore_color.rgb = CARD_BG
    q_box.line.color.rgb = ACCENT_CYAN
    q_tf = q_box.text_frame
    q_tf.word_wrap = True
    qp = q_tf.paragraphs[0]
    qp.text = "CORE PRODUCT PRINCIPLE: One Source of Truth. Multiple Audiences. Multiple Communication Formats. Verifiable Factual Accuracy."
    qp.font.size = Pt(17)
    qp.font.bold = True
    qp.font.color.rgb = ACCENT_CYAN
    qp.alignment = PP_ALIGN.CENTER

    add_card(slide3, Inches(0.8), Inches(3.3), Inches(2.7), Inches(3.6),
             "Ingestion & Chunking",
             ["PDF, DOCX, TXT, Web URLs.",
              "Sentence-boundary windowing.",
              "Character offsets & page attribution.",
              "SSRF protection on external URLs."])

    add_card(slide3, Inches(3.8), Inches(3.3), Inches(2.7), Inches(3.6),
             "3 AI Paradigms",
             ["Local Extractive (TF-IDF/TextRank).",
              "Local Seq2Seq (FLAN-T5 & BART).",
              "Cloud LLM (Groq SDK).",
              "Independent offline executability."])

    add_card(slide3, Inches(6.8), Inches(3.3), Inches(2.7), Inches(3.6),
             "Factual Verification",
             ["Atomic claim extraction.",
              "TF-IDF evidence retrieval.",
              "Multi-method fact classifier.",
              "Mathematical Consistency Score (FCS)."])

    add_card(slide3, Inches(9.8), Inches(3.3), Inches(2.7), Inches(3.6),
             "Evaluation & Export",
             ["ROUGE-1/2/L & BERTScore.",
              "Key Fact & Entity coverage.",
              "Controllability validation.",
              "Export to PDF, DOCX, MD, TXT."])

    # -------------------------------------------------------------
    # SLIDE 4: THE 4 TARGET COMMUNICATION FORMATS
    # -------------------------------------------------------------
    slide4 = prs.slides.add_slide(blank_layout)
    add_slide_background(slide4)
    add_header(slide4, "Target Communication Formats with Strict Guardrails")

    add_card(slide4, Inches(0.8), Inches(1.8), Inches(2.7), Inches(4.8),
             "1. Executive Summary",
             ["Audience: Senior Leadership & Ministers.",
              "Structure: Overview, Key Findings, Core Statistics, Strategic Implications.",
              "Guardrail: Actionable recommendations permitted ONLY when directly corroborated by source text.",
              "Target Length: 150 - 300 words."],
             badge="High-Level Decision Making")

    add_card(slide4, Inches(3.8), Inches(1.8), Inches(2.7), Inches(4.8),
             "2. Public Advisory",
             ["Audience: Citizens & Community.",
              "Structure: Clear Title, Situation Context, Relevant Facts, Precautions, Official Contacts.",
              "Guardrail: NEVER invent emergency numbers, hotlines, or official health recommendations.",
              "Target Length: 200 - 400 words."],
             badge="Citizen Safety & Clarity")

    add_card(slide4, Inches(6.8), Inches(1.8), Inches(2.7), Inches(4.8),
             "3. Social Media Posts",
             ["Platforms: LinkedIn (Structured) & X (Concise).",
              "Structure: Impact headline, key verified metrics, actionable takeaways, hashtags.",
              "Guardrail: No sensationalized claims for engagement; strict factual preservation.",
              "Target Length: 280 chars (X) / 150 words (LinkedIn)."],
             badge="Public Outreach")

    add_card(slide4, Inches(9.8), Inches(1.8), Inches(2.7), Inches(4.8),
             "4. Fact-Based FAQ",
             ["Audience: Citizens & Operational Support.",
              "Structure: Question, Grounded Answer, Supporting Evidence Snippet.",
              "Guardrail: If source lacks information, explicitly state: 'The source does not provide sufficient data.'",
              "Target Length: 3 - 6 Q&A pairs."],
             badge="Query Resolution")

    # -------------------------------------------------------------
    # SLIDE 5: THREE GENERATION PARADIGMS COMPARED
    # -------------------------------------------------------------
    slide5 = prs.slides.add_slide(blank_layout)
    add_slide_background(slide5)
    add_header(slide5, "Three Distinct AI Generation Paradigms")

    add_card(slide5, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Local Extractive (Baseline)",
             ["Algorithms: TF-IDF Centroid Ranking & TextRank Sentence Graph (PageRank).",
              "Hardware: 100% CPU, 0 MB VRAM, 0 tokens.",
              "Factual Accuracy: 100% Verbatim (Zero Hallucination).",
              "Offline Ready: Completely self-contained.",
              "Trade-off: Phrasing is rigid; lacks natural human paraphrasing."],
             badge="100% Offline · Deterministic", accent=ACCENT_GREEN)

    add_card(slide5, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Local Seq2Seq Neural",
             ["Models: google/flan-t5-base (945 MB) & facebook/bart-base (532 MB).",
              "Hardware: GPU accelerated (CUDA fp16) or CPU threadpool.",
              "Innovation: Automatic CUDA OOM fallback to CPU reload.",
              "Factual Accuracy: High when temperature is bounded.",
              "Trade-off: Requires local disk space and ~4-6GB VRAM."],
             badge="Local Neural · Private", accent=ACCENT_INDIGO)

    add_card(slide5, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Cloud Instruction LLM",
             ["Model: Groq SDK inference (openai/gpt-oss-120b).",
              "Throughput: 300+ tokens/second ultra-low latency.",
              "Innovation: Automatic 3,500-word extractive context bounding to avoid rate limits.",
              "Telemetry: Tracks prompt tokens, completion tokens, latency, cost.",
              "Trade-off: Requires internet connectivity."],
             badge="High-Speed Synthesis", accent=ACCENT_CYAN)

    # -------------------------------------------------------------
    # SLIDE 6: END-TO-END SYSTEM ARCHITECTURE
    # -------------------------------------------------------------
    slide6 = prs.slides.add_slide(blank_layout)
    add_slide_background(slide6)
    add_header(slide6, "Decoupled & Extensible System Architecture")

    add_card(slide6, Inches(0.8), Inches(1.8), Inches(5.6), Inches(2.3),
             "1. Presentation Layer (Next.js 14)",
             ["React 18, TypeScript, Tailwind CSS, Recharts, Lucide.",
              "7 Integrated Workspaces: Dashboard, Library, Studio, Review, Models, Evaluation, Datasets.",
              "Real-time streaming responses & interactive claim highlight inspection."])

    add_card(slide6, Inches(6.8), Inches(1.8), Inches(5.7), Inches(2.3),
             "2. API Gateway (FastAPI 0.115)",
             ["Thin route handlers (zero AI logic in routes).",
              "Pydantic v2 strict contract validation & custom AppException handlers.",
              "35 REST endpoints across 9 specialized routers; OpenAPI/Swagger at /docs."])

    add_card(slide6, Inches(0.8), Inches(4.4), Inches(5.6), Inches(2.5),
             "3. AI Model Layer (ModelRegistry)",
             ["Unified BaseTransformationModel abstract interface.",
              "Thread-safe ModelRegistry singleton with fuzzy ID discovery.",
              "Decoupled from frontend; interchangeable model providers.",
              "Automated CUDA failure recovery reload on CPU."])

    add_card(slide6, Inches(6.8), Inches(4.4), Inches(5.7), Inches(2.5),
             "4. Dual-Mode Persistence & Storage",
             ["SQLAlchemy 2.0 dual-mode engine: PostgreSQL 16 primary with automatic SQLite fallback.",
              "10 relational models with cascade traceability from document to claim.",
              "Local storage for uploads, exports, and Hugging Face model checkpoints."])

    # -------------------------------------------------------------
    # SLIDE 7: FACTUAL VERIFICATION & HALLUCINATION DETECTION
    # -------------------------------------------------------------
    slide7 = prs.slides.add_slide(blank_layout)
    add_slide_background(slide7)
    add_header(slide7, "The Key Differentiator: Multi-Method Factual Grounding")

    # FCS Box
    fcs_box = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.7), Inches(1.1))
    fcs_box.fill.solid()
    fcs_box.fill.fore_color.rgb = CARD_BG
    fcs_box.line.color.rgb = ACCENT_GREEN
    fcs_tf = fcs_box.text_frame
    fcs_tf.word_wrap = True
    fcs_p = fcs_tf.paragraphs[0]
    fcs_p.text = "Factual Consistency Score (FCS) = [ N_supported + 0.5 * N_partially_supported ] / N_total_claims"
    fcs_p.font.size = Pt(17)
    fcs_p.font.bold = True
    fcs_p.font.color.rgb = ACCENT_GREEN
    fcs_p.alignment = PP_ALIGN.CENTER

    add_card(slide7, Inches(0.8), Inches(3.2), Inches(3.6), Inches(3.7),
             "1. Atomic Claim Extraction",
             ["Regex grammar & linguistic pattern parsing.",
              "Extracts: Numerical values, dates, percentages, named entities, policy directives, cause-and-effect assertions.",
              "Breaks complex generated paragraphs into testable atomic claims."])

    add_card(slide7, Inches(4.8), Inches(3.2), Inches(3.6), Inches(3.7),
             "2. Evidence Retrieval",
             ["TF-IDF vector cosine similarity across all original document chunks.",
              "Retrieves top-K candidate supporting passages.",
              "Preserves page number, chunk ID, and exact character offsets."])

    add_card(slide7, Inches(8.8), Inches(3.2), Inches(3.6), Inches(3.7),
             "3. Multi-Method Classification",
             ["Method 1: Exact numerical/date match.",
              "Method 2: Named entity intersection overlap.",
              "Method 3: Contextual semantic entailment.",
              "5 Statuses: Supported (Green), Partially Supported (Yellow), Unsupported (Orange), Contradicted (Red), Human Review (Gray)."])

    # -------------------------------------------------------------
    # SLIDE 8: 5-DIMENSIONAL EMPIRICAL EVALUATION
    # -------------------------------------------------------------
    slide8 = prs.slides.add_slide(blank_layout)
    add_slide_background(slide8)
    add_header(slide8, "Scientific Evaluation on Curated Benchmark Datasets")

    add_card(slide8, Inches(0.8), Inches(1.8), Inches(2.2), Inches(4.8),
             "1. Text Similarity",
             ["ROUGE-1: Unigram overlap with gold reference.",
              "ROUGE-2: Bigram phrasing continuity.",
              "ROUGE-L: Longest common subsequence.",
              "BERTScore: Contextual embedding similarity."])

    add_card(slide8, Inches(3.2), Inches(1.8), Inches(2.2), Inches(4.8),
             "2. Content Coverage",
             ["Key Fact Recall: Percentage of gold facts preserved.",
              "Entity Recall: Crucial names, places, organizations.",
              "Numerical Recall: Accurate statistics and dates."])

    add_card(slide8, Inches(5.6), Inches(1.8), Inches(2.2), Inches(4.8),
             "3. Factual Grounding",
             ["FCS Metric (0.0 to 1.0).",
              "Hallucination rate detection.",
              "Contradiction flagging.",
              "Direct source chunk attribution."])

    add_card(slide8, Inches(8.0), Inches(1.8), Inches(2.2), Inches(4.8),
             "4. Controllability",
             ["Length budget compliance.",
              "Required keyword presence.",
              "Prohibited phrase rejection.",
              "Format section adherence."])

    add_card(slide8, Inches(10.4), Inches(1.8), Inches(2.1), Inches(4.8),
             "5. Efficiency",
             ["Inference latency (ms).",
              "Token throughput (tok/sec).",
              "VRAM peak consumption.",
              "Estimated cost ($ USD)."])

    # -------------------------------------------------------------
    # SLIDE 9: PLATFORM WALKTHROUGH & UI MODULES
    # -------------------------------------------------------------
    slide9 = prs.slides.add_slide(blank_layout)
    add_slide_background(slide9)
    add_header(slide9, "Comprehensive UI/UX Workspace Suite (Next.js 14)")

    add_card(slide9, Inches(0.8), Inches(1.8), Inches(3.6), Inches(2.4),
             "1. Document Library",
             ["Triple ingestion: PDF, DOCX, TXT upload or Web URL.",
              "Chunk inspection drawer displaying page numbers, word counts, and char offsets."])

    add_card(slide9, Inches(4.8), Inches(1.8), Inches(3.6), Inches(2.4),
             "2. Transformation Studio",
             ["4-step wizard: Source selection, format/audience/tone, constraint inputs, multi-model picker.",
              "Real-time generation status and telemetry."])

    add_card(slide9, Inches(8.8), Inches(1.8), Inches(3.6), Inches(2.4),
             "3. Review & Traceability",
             ["Color-coded claim highlights (Green/Yellow/Red).",
              "Click-to-inspect source chunk drawer.",
              "In-browser text editor & version branching."])

    add_card(slide9, Inches(0.8), Inches(4.5), Inches(3.6), Inches(2.4),
             "4. Model Laboratory",
             ["Live model cards: VRAM, latency, execution mode.",
              "Paradigm comparison matrix and runtime unloader."])

    add_card(slide9, Inches(4.8), Inches(4.5), Inches(3.6), Inches(2.4),
             "5. Evaluation Dashboard",
             ["Recharts 5-axis Radar chart & grouped ROUGE bars.",
              "Head-to-head model comparison matrix with latency."])

    add_card(slide9, Inches(8.8), Inches(4.5), Inches(3.6), Inches(2.4),
             "6. Dataset Management & Export",
             ["Curated benchmark documents with gold annotations.",
              "1-click export to PDF (ReportLab), DOCX, MD, TXT."])

    # -------------------------------------------------------------
    # SLIDE 10: SECURITY & OPERATIONAL RESILIENCE
    # -------------------------------------------------------------
    slide10 = prs.slides.add_slide(blank_layout)
    add_slide_background(slide10)
    add_header(slide10, "Enterprise Security & Failure Resilience")

    add_card(slide10, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "1. SSRF Defense Guard",
             ["DNS resolution validation prior to any network connection.",
              "Strictly blocks loopback addresses (127.0.0.1, localhost).",
              "Blocks RFC 1918 private subnets (10.x, 172.16-31.x, 192.168.x).",
              "Blocks Cloud metadata endpoints (169.254.169.254, AWS/GCP/Azure).",
              "Enforces strict 5-second connection timeout & size limits."],
             badge="Network Boundary Defense", accent=ACCENT_CYAN)

    add_card(slide10, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "2. Prompt Injection Defense",
             ["Source document text is strictly treated as untrusted data.",
              "Ingested content is isolated within <source_document> delimiters.",
              "System prompt instructs model to ignore directives embedded in files.",
              "API keys (Groq, HF) are strictly backend-only (never in browser).",
              "MIME-type validation and SHA-256 deduplication."],
             badge="Data Isolation", accent=ACCENT_INDIGO)

    add_card(slide10, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "3. Hardware Auto-Recovery",
             ["Dynamic device placement: CUDA fp16 with CPU fallback.",
              "Automatic CUDA failure recovery: reloads model on CPU and retries once.",
              "Extractive context bounding: reduces long texts to 3,500 words for Groq.",
              "Dual-Mode DB: Automatic fallback from PostgreSQL to SQLite.",
              "Independent executability even when cloud is offline."],
             badge="High Availability", accent=ACCENT_GREEN)

    # -------------------------------------------------------------
    # SLIDE 11: LIVE DEMONSTRATION WORKFLOW (SIH JURY SCRIPT)
    # -------------------------------------------------------------
    slide11 = prs.slides.add_slide(blank_layout)
    add_slide_background(slide11)
    add_header(slide11, "Demonstration Workflow for SIH 2026 Jury")

    add_card(slide11, Inches(0.8), Inches(1.8), Inches(2.7), Inches(4.8),
             "Step 1: Ingest",
             ["Upload authoritative government dossier (e.g. NITI Aayog AI Strategy).",
              "Inspect chunk visualization drawer.",
              "Verify exact sentence boundaries, page numbers, and character offsets.",
              "Confirm SHA-256 integrity hash."])

    add_card(slide11, Inches(3.8), Inches(1.8), Inches(2.7), Inches(4.8),
             "Step 2: Transform",
             ["Select target: Executive Summary & Public Advisory.",
              "Configure audience: Senior Leadership / General Citizens.",
              "Set constraints: 250 words, required keywords.",
              "Select models: Extractive, FLAN-T5, Groq simultaneously."])

    add_card(slide11, Inches(6.8), Inches(1.8), Inches(2.7), Inches(4.8),
             "Step 3: Verify",
             ["Observe side-by-side output comparison.",
              "Review factual verification scorecard (FCS: 92%).",
              "Click on a green highlighted claim to view supporting chunk.",
              "Demonstrate contradiction detection on manipulated facts."])

    add_card(slide11, Inches(9.8), Inches(1.8), Inches(2.7), Inches(4.8),
             "Step 4: Export",
             ["Edit text inline with version branch tracking.",
              "Submit 5-star human review feedback.",
              "1-click export to formatted PDF with official footnotes.",
              "Inspect Evaluation Dashboard radar chart."])

    # -------------------------------------------------------------
    # SLIDE 12: SOCIETAL IMPACT & CONCLUSION
    # -------------------------------------------------------------
    slide12 = prs.slides.add_slide(blank_layout)
    add_slide_background(slide12)
    add_header(slide12, "Impact, Future Roadmap & Conclusion")

    add_card(slide12, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "Key Achievements & Societal Impact",
             ["Zero-Hallucination Governance: Citizens and officials receive trustworthy information with verifiable source footnotes.",
              "10x Acceleration in Public Notification Dissemination: From hours of manual rewriting to seconds of automated generation.",
              "Democratized Access: Multi-audience transformation ensures complex policies are understandable by all literacy levels.",
              "100% Offline Capability: Operates in air-gapped environments without dependency on foreign cloud servers.",
              "Scientific Transparency: Empirical metrics replace subjective hype with rigorous ROUGE, coverage, and FCS validation."],
             badge="Measurable Value", accent=ACCENT_CYAN)

    add_card(slide12, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8),
             "Future Roadmap & Enhancements",
             ["Multilingual Indian Languages: Integration with Bhashini API for 22 scheduled official Indian languages.",
              "Speech-to-Speech Accessibility: Voice advisories generated for rural radio and IVR citizen helplines.",
              "Automated Tesseract OCR: Scanned historical gazette document processing.",
              "Enterprise Connector Hub: Native integrations with government portals and CMS platforms.",
              "Open-Source Benchmark Contribution: Publishing curated Indian governance transformation datasets."],
             badge="Next Milestones", accent=ACCENT_INDIGO)

    # Output path
    output_path = "ACTP_Presentation_SIH2026.pptx"
    prs.save(output_path)
    print(f"Presentation saved to {output_path}")

if __name__ == "__main__":
    create_deck()
