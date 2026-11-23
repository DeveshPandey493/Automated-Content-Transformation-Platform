# TROUBLESHOOTING.md — Diagnostics & Operational Resolution Guide
**Smart India Hackathon 2026 — Gen AI Platform for Automated Content Transformation**

---

## 1. Common Issues & Quick Solutions

### 1.1 "Connection to PostgreSQL failed on port 5432"
- **Cause**: PostgreSQL service or Docker container is stopped.
- **Automatic Resolution**: The backend automatically falls back to an embedded SQLite database (`content_transformer.db`) in development mode so you can continue testing without interruption.
- **Manual Resolution**:
  ```bash
  docker-compose up -d postgres
  # Or start the local PostgreSQL service in Windows Services (services.msc)
  ```

### 1.2 "Groq API: Connection error or RateLimitError"
- **Cause**: Network disconnection or rate limits reached on free tier.
- **Resolution**:
  1. The platform automatically catches `RateLimitError` and applies exponential backoff.
  2. If the key is exhausted, switch the generation selector to **Extractive (TF-IDF/TextRank)** or **Local Seq2Seq (FLAN-T5)**. The platform is designed to function completely offline without Groq.

### 1.3 "CUDA out of memory during FLAN-T5 / BART inference"
- **Cause**: GPU VRAM is full from concurrent applications.
- **Resolution**:
  1. Click **Unload Model** in the Model Laboratory to flush VRAM (`torch.cuda.empty_cache()`).
  2. The model engine automatically falls back to CPU inference if available VRAM $< 1.5\text{ GB}$.
  3. Reduce `max_length` in the transformation configuration.

### 1.4 "PyMuPDF (fitz) or docx import error"
- **Resolution**:
  ```bash
  pip install pymupdf python-docx
  ```

### 1.5 "SSRF Blocked: Destination IP is in a private or restricted subnet"
- **Cause**: Attempting to ingest `http://localhost`, `127.0.0.1`, or an internal network IP via the URL Ingestion tool.
- **Resolution**: This is an intentional security safeguard. Only public web addresses with resolvable public IPs are allowed for document fetching. For local testing, use the **Paste Text** or **File Upload** tabs.
