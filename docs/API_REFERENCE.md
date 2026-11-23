# API_REFERENCE.md — RESTful API Specification
**Smart India Hackathon 2026 — Gen AI Platform for Automated Content Transformation**

---

## 1. Overview
The platform exposes a standard REST API documented via OpenAPI at `http://localhost:8000/docs`.
- Base URL: `http://localhost:8000/api`
- Request Content-Type: `application/json` (or `multipart/form-data` for file uploads)
- Response Content-Type: `application/json`
- Standard Status Codes: `200 OK`, `201 Created`, `400 Bad Request`, `404 Not Found`, `422 Unprocessable Entity`, `500 Internal Error`.

---

## 2. API Endpoints

### 2.1 System & Health
- **`GET /api/health`**
  - Response: `{"status": "ok", "app_env": "development", "database": "connected", "database_engine": "postgresql", "gpu_available": true}`

### 2.2 Document Management (`/api/documents`)
- **`POST /api/documents/upload`**
  - Form Data: `file: UploadFile`, `title: Optional[str]`
  - Supports: `.pdf`, `.docx`, `.txt` (max 25MB).
  - Response: `DocumentResponse`
- **`POST /api/documents/text`**
  - Body: `{"title": "Policy Brief", "text": "Raw text content..."}`
  - Response: `DocumentResponse`
- **`POST /api/documents/url`**
  - Body: `{"url": "https://pib.gov.in/PressReleasePage.aspx?PRID=...", "title": "Optional Title"}`
  - Response: `DocumentResponse`
- **`GET /api/documents`**
  - Query: `skip=0`, `limit=20`, `search=...`
  - Response: `List[DocumentSummaryResponse]`
- **`GET /api/documents/{document_id}`**
  - Response: Full document details with metadata and chunk counts.
- **`GET /api/documents/{document_id}/chunks`**
  - Query: `skip=0`, `limit=100`
  - Response: `List[DocumentChunkResponse]`

### 2.3 Transformation Engine (`/api/transformations`)
- **`POST /api/transformations`**
  - Body:
    ```json
    {
      "document_id": "uuid-here",
      "format_type": "EXECUTIVE_SUMMARY", // EXECUTIVE_SUMMARY | PUBLIC_ADVISORY | SOCIAL_POST | FAQ
      "audience": "Senior Management",
      "tone": "Formal",
      "length_target": "MEDIUM", // SHORT | MEDIUM | DETAILED | CUSTOM
      "custom_word_limit": null,
      "required_keywords": ["fiscal deficit", "GDP"],
      "prohibited_terms": ["unconfirmed", "rumor"],
      "model_ids": ["extractive/textrank", "groq/default"] // Can select 1 or more for multi-model comparison
    }
    ```
  - Response: `{"job_id": "uuid", "status": "PENDING", "created_at": "..."}`
- **`GET /api/transformations/{job_id}`**
  - Response: `TransformationJobResponse` (includes execution status, progress, outputs)
- **`GET /api/transformations/{job_id}/results`**
  - Response: List of generated outputs for this job with metrics and models.

### 2.4 Factual Verification (`/api/verification`)
- **`POST /api/verification/{output_id}`**
  - Triggers on-demand claim extraction and factuality verification for an output.
  - Response: `VerificationReportResponse`
- **`GET /api/verification/{output_id}`**
  - Response: Full verification report including all extracted claims, supporting source chunks, confidence scores, and status tags.

### 2.5 Evaluations & Benchmarking (`/api/evaluations`)
- **`POST /api/evaluations/run`**
  - Body: `{"output_ids": ["uuid-1", "uuid-2"], "reference_id": "optional-uuid"}`
  - Computes ROUGE, BERTScore, Coverage, and Controllability.
- **`GET /api/evaluations/{output_id}`**
  - Response: Granular evaluation breakdown.
- **`GET /api/evaluations/compare`**
  - Query: `output_ids=uuid1,uuid2,uuid3`
  - Response: Side-by-side comparison matrix across Extractive, T5/BART, and Groq models.
- **`POST /api/evaluations/feedback`**
  - Body: `{"output_id": "uuid", "accuracy": 5, "completeness": 4, "readability": 5, "suitability": 4, "notes": "..."}`
  - Response: Stored human feedback score.

### 2.6 Model Laboratory (`/api/models`)
- **`GET /api/models`**
  - Response: List of registered models with capabilities, execution type (`LOCAL_EXTRACTIVE`, `LOCAL_SEQ2SEQ`, `GROQ_API`), and availability status.
- **`POST /api/models/{model_id}/unload`**
  - Purges model weights from GPU/RAM to free memory.

### 2.7 Datasets (`/api/datasets`)
- **`GET /api/datasets`**
  - List curated benchmark datasets (e.g. NITI Aayog, WHO).
- **`GET /api/datasets/{dataset_id}`**
  - Details and reference outputs.

### 2.8 Export (`/api/exports/{output_id}`)
- Query: `format=pdf|docx|md|txt`
- Response: Downloadable file attachment.
