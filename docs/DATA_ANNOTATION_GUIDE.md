# DATA_ANNOTATION_GUIDE.md — Human Annotation Guidelines & Protocol
**Smart India Hackathon 2026 — Gen AI Platform for Automated Content Transformation**

---

## 1. Principles of Gold-Standard Reference Creation
Reference transformations must be generated or verified by human domain experts. Do NOT rely on model outputs as ground truth.

### Universal Principles:
1. **Factual Grounding**: Every assertion, figure, and date in the reference output must be directly verifiable in the source document.
2. **Zero Extrapolation**: Do not infer unstated conclusions, motives, or emergency recommendations.
3. **Audience-Calibrated Vocabulary**: Adapt vocabulary without altering underlying semantics.

---

## 2. Format-Specific Annotation Rules

### 2.1 Executive Summary
- **Structure**:
  1. Strategic Context (1–2 sentences).
  2. Key Findings & Metric Trajectory (3–4 bullet points with exact statistics).
  3. Structural Implications (1–2 sentences).
  4. Formally Endorsed Actions (only if explicitly recommended in source text).
- **Target Length**: 250 – 400 words.

### 2.2 Public Advisory
- **Structure**:
  1. Clear, non-sensational heading.
  2. Targeted citizen group.
  3. Situation summary in plain language.
  4. Mandatory precautions or steps.
  5. Official helpline, dates, or contact channels from the text.
- **Tone**: Direct, reassuring, unambiguous, neutral.

### 2.3 Social Media Posts
- **LinkedIn**:
  - 120 – 200 words.
  - Professional tone, bulleted takeaways, 3–4 policy-relevant hashtags.
- **X (Twitter)**:
  - <= 280 characters.
  - Punchy key takeaway, 2 hashtags, zero fluff.

### 2.4 FAQ
- 3 to 6 QA pairs covering the most frequent inquiries.
- If a query cannot be answered from the text, annotate the answer as: *"The source document does not provide information regarding this query."*

---

## 3. Key Fact & Entity Annotation Rubric
- **Numbers**: Annotate exact numerical values, percentages, currency amounts, and reference years.
- **Entities**: Annotate organizations, schemes, geographic regions, and legislative acts.
- **Fact Units**: Annotate discrete assertions (e.g., "[Country X] reduced infant mortality by [Y%] between [Year A] and [Year B]").
