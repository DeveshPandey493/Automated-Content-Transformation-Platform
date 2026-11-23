# DATASET_CARD.md — Curated Benchmark Dataset Specification
**Smart India Hackathon 2026 — Gen AI Platform for Automated Content Transformation**

---

## 1. Dataset Summary
- **Dataset Name**: SIH-ACTP-Benchmark-v1
- **Domain**: Public Policy, Public Health, Economic Surveys, Science & Technology Reports
- **Size**: 35 Curated Long-Form Documents
- **Languages**: English
- **Licensing**: Open Government Data (OGD) India / Creative Commons CC-BY 4.0 / Public Domain

---

## 2. Source Documents & Provenance

The evaluation benchmark contains real, unedited public documents from authoritative bodies:
1. **NITI Aayog**: Reports on Sustainable Development Goals (SDG) India Index, National Multidimensional Poverty Index, AI for All Strategy.
2. **Ministry of Health and Family Welfare (MoHFW)**: National Health Policy advisories, vaccination and vector-borne disease guidelines.
3. **Reserve Bank of India (RBI) & Ministry of Finance**: Annual Economic Survey summaries, Digital Payment Index reports.
4. **World Health Organization (WHO)**: Global Health Security briefs and epidemiological bulletins.
5. **ISRO & Department of Space**: Space Exploration and Chandrayaan/Aditya-L1 mission overview reports.

---

## 3. Annotation Schema

Each dataset entry contains ground-truth reference transformations across all 4 formats:
```json
{
  "document_id": "doc-niti-sdg-2024",
  "title": "SDG India Index 2023-24: Sustainable Development Goals Progress Report",
  "publisher": "NITI Aayog, Government of India",
  "publication_date": "2024-07-12",
  "source_url": "https://www.niti.gov.in/report/sdg-india-index",
  "extracted_text": "...full text...",
  "reference_outputs": {
    "executive_summary": {
      "text": "...expertly drafted reference summary...",
      "word_count": 320
    },
    "public_advisory": {
      "text": "...citizen focused advisory...",
      "word_count": 240
    },
    "social_post": {
      "linkedin": "...structured LinkedIn post...",
      "x_post": "...concise thread post with #SDGIndia #NITIAayog..."
    },
    "faq": [
      {
        "question": "Which state achieved the highest composite score in the 2023-24 index?",
        "answer": "Kerala secured the top rank with a composite score of 79, followed by Uttarakhand and Tamil Nadu.",
        "evidence_chunk_index": 4
      }
    ]
  },
  "gold_key_facts": [
    "India's composite SDG score improved from 57 in 2018 to 74 in 2023-24.",
    "Goal 1 (No Poverty) and Goal 13 (Climate Action) recorded the highest state-level gains.",
    "32 states and union territories entered the 'Front Runner' category."
  ],
  "gold_entities": [
    "NITI Aayog", "Kerala", "Uttarakhand", "Tamil Nadu", "United Nations Development Programme"
  ],
  "gold_numbers": [
    "57", "74", "32", "79", "2023-24"
  ]
}
```

---

## 4. Evaluation Splits
- **Validation Split**: 10 Documents (Used for prompt calibration and parameter tuning).
- **Held-Out Test Split**: 25 Documents (Used strictly for automated model benchmarking and human evaluation; never included in prompt few-shot context).
