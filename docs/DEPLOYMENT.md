# DEPLOYMENT.md — Production & Evaluation Deployment Guide
**Smart India Hackathon 2026 — Gen AI Platform for Automated Content Transformation**

---

## 1. Deployment Topologies

### Topology A: Standalone Single-Machine (SIH Hackathon Demonstration)
- Both backend and frontend run locally on the demonstrator's laptop.
- Local SQLite fallback allows instant demonstration without Docker if needed.
- Uses RTX 4050 GPU for local FLAN-T5/BART inference and Groq cloud for fast LLM inference.

### Topology B: Docker Compose Multi-Container (Recommended)
- Containerized PostgreSQL 16, FastAPI backend, and Next.js frontend managed via `docker-compose.yml`.

---

## 2. Step-by-Step Setup

### Step 1: Clone Repository & Configure Environment
```bash
git clone <repository_url>
cd "Automated Content Transformation Platform"
cp .env.example .env
```
Ensure `.env` contains:
```env
APP_ENV=development
APP_DEBUG=true
DATABASE_URL=postgresql+psycopg://postgres:postgrespassword@localhost:5432/content_transformer
GROQ_API_KEY=gsk_...
GROQ_MODEL=openai/gpt-oss-120b
FLAN_T5_MODEL=google/flan-t5-base
BART_MODEL=facebook/bart-base
UPLOAD_DIR=./storage/uploads
EXPORT_DIR=./storage/exports
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 2: Running with Docker Compose
```bash
docker-compose up --build -d
```
Verify container statuses:
```bash
docker-compose ps
```

### Step 3: Running Manually (Without Docker)
**Backend:**
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Visit:
- Frontend App: [http://localhost:3000](http://localhost:3000)
- Interactive API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 3. Healthcheck & Readiness Probe
```bash
curl -X GET http://localhost:8000/api/health
```
Expected response:
```json
{
  "status": "ok",
  "app_env": "development",
  "database": "connected",
  "database_engine": "postgresql",
  "gpu_available": true
}
```
