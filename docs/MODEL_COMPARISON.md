# MODEL_COMPARISON.md — Paradigm Comparison & Benchmark Methodology
**Smart India Hackathon 2026 — Gen AI Platform for Automated Content Transformation**

---

## 1. Overview of the Three Generation Paradigms

| Feature / Dimension | Approach A: Extractive Summarisation | Approach B: Local Seq2Seq Transformer | Approach C: Instruction-Tuned LLM |
|---|---|---|---|
| **Representative Engine** | TF-IDF & TextRank Graph | `google/flan-t5-base` & `facebook/bart-base` | Groq Cloud (`GROQ_MODEL`) |
| **Execution Environment** | 100% Local CPU | Local GPU (RTX 4050) / CPU Fallback | Cloud API (Groq LPU) |
| **External Dependency** | None | Hugging Face Hub (initial cache only) | Internet & Groq API Key |
| **Factual Accuracy** | **Absolute (100% verbatim source text)** | Moderate (Subject to neural compression errors) | High (Grounded with system prompt constraints) |
| **Hallucination Risk** | **Zero** | Low-to-Medium | Low (Mitigated by verification pipeline) |
| **Stylistic Adaptability** | Low (Cannot rewrite or alter tone) | Moderate (Limited to pretrained domain) | **Very High (Precise audience & tone tuning)** |
| **Generation Latency** | **Fastest (~50 - 200 ms)** | Moderate (~1.5 - 4.5 s on GPU) | **Fastest Neural (~400 - 900 ms)** |
| **Resource Consumption** | Minimal (< 100 MB RAM) | High (~1.2 - 2.5 GB VRAM) | Zero local VRAM (Network I/O) |
| **Traceability** | Exact sentence-to-chunk index | Approximate token overlap | Semantic claim-to-chunk mapping |

---

## 2. Experimental Hypotheses for Hackathon Evaluation

1. **Hypothesis 1 (Accuracy Baseline)**:
   *Extractive summarisation will achieve the highest Factual Consistency Score ($\text{FCS} \approx 1.0$) but lower Readability and Audience Suitability for non-technical audiences.*
2. **Hypothesis 2 (Controllability Trade-off)**:
   *Instruction-tuned LLMs (Groq) will drastically outperform Seq2Seq (FLAN-T5) in format conformity (Executive Summary vs Public Advisory vs Social Media) and constraint adherence (keywords and tone).*
3. **Hypothesis 3 (Offline Self-Sufficiency)**:
   *The local Transformer approach provides a privacy-preserving, zero-data-leakage alternative capable of running on modest consumer hardware (6GB RTX 4050).*

---

## 3. Comparison Visualization Structure
The comparison dashboard renders:
1. **Radar Chart**: Normalized comparison across Coverage, Factual Consistency, Controllability, Readability, and Efficiency.
2. **Latency vs FCS Scatter Plot**: Evaluating the trade-off between execution speed and factual fidelity.
3. **Claim Status Breakdown Bar Chart**: Visual distribution of Supported vs Partially Supported vs Unsupported claims.
4. **Side-by-Side Content Matrix**: Synchronized columns comparing the generated text of each model on identical source chunks.
