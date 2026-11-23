# Sample Data for ACTP Demo

## Directory Structure
```
sample_data/
├── README.md                          # This file
├── NITI_Aayog_AI_Strategy_2024.txt    # Primary demo document (text version)
├── reference_outputs/                 # Gold standard reference outputs
│   ├── executive_summary_ref.md
│   ├── public_advisory_ref.md
│   ├── social_posts_ref.md
│   └── faq_ref.md
└── benchmark_dataset_sample.json      # Sample from curated benchmark
```

## Primary Demo Document
**NITI_Aayog_AI_Strategy_2024.txt** - Text version of the National Strategy for Artificial Intelligence 2024 Update
- ~18,500 words
- Covers: AI Mission, Healthcare, Agriculture, Education, Smart Cities, Governance
- Includes specific figures: ₹10,300 crore budget, 5-year timeline, 3 priority sectors

## Usage
```bash
# Ingest via API
curl -X POST http://localhost:8000/api/documents/text \
  -H "Content-Type: application/json" \
  -d '{
    "title": "NITI Aayog AI Strategy 2024",
    "text_content": "'"$(cat sample_data/NITI_Aayog_AI_Strategy_2024.txt)"'",
    "source_type": "PASTED_TEXT"
  }'
```

## Reference Outputs
Gold-standard human-written references for evaluation:
- **executive_summary_ref.md** - For senior leadership briefing
- **public_advisory_ref.md** - For citizen communication
- **social_posts_ref.md** - LinkedIn + X/Twitter formats
- **faq_ref.md** - Operational FAQ with evidence citations

These are used by the Evaluation Engine to compute ROUGE, BERTScore, Key Fact Coverage, and Controllability metrics.