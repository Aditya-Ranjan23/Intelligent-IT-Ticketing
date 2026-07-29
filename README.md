# Intelligent IT Ticket Auto-Resolution System (`v0.3.0`)

> [!IMPORTANT]
> **Verified Stack & Baseline (`v0.3.0`)**: The system operates on a **Python FastAPI** stack with **PostgreSQL + `pgvector`**, **Redis caching**, **Pytesseract OCR**, **Hybrid Classifier** (`sentence-transformers` + `scikit-learn`), and **Google Gemini RAG Deep Resolution**. Evaluated on an uncompromised 24-row held-out dataset (`eval/data/holdout.csv`).

---

## 1. Overview

The Intelligent IT Ticket Auto-Resolution System automatically triages IT support tickets, provides instant step-by-step remediation playbooks for common IT issues, caches historical Q&A resolutions to reduce LLM token usage, and escalates complex tickets to deep AI agent resolution.

### System Capabilities (v0.3.0)
- **FastAPI Core (`app/main.py`)**: High-performance REST service for ticket resolution, active status polling (`/tickets/{id}/status`), and memory management.
- **Hybrid Classifier (`app/services/classifier_service.py`)**: Primary dense vector embedding search using `sentence-transformers` (`all-MiniLM-L6-v2`, 384d) with `scikit-learn` (TF-IDF + LogisticRegression) fallback model.
- **Real OCR Engine (`app/services/ocr_service.py`)**: Text extraction from base64 screenshot bytes using `pytesseract` and `Pillow`.
- **Google Gemini RAG Deep Resolution (`app/services/llm_service.py`)**: Direct Gemini API integration (`gemini-2.5-flash`) with RAG vector context retrieval and structured mock fallback when `GEMINI_API_KEY` is not provided.
- **PostgreSQL + `pgvector` & Redis Caching**: Relational vector database tables (`tickets`, `issue_clusters`, `qa_memory`) and Redis resolution hash caching.
- **Held-Out Evaluation (`scripts/eval.py`)**: Evaluated against an expanded 24-row held-out dataset (`eval/data/holdout.csv`, 108 total dataset rows), achieving **62.5% top-1 accuracy** (15/24).

---

## 2. Technology Stack

- **Framework**: Python 3.11+, FastAPI, Uvicorn, Pydantic, SQLAlchemy, asyncpg / psycopg2
- **Vector Search**: PostgreSQL 16 with `pgvector` extension (`pgvector/pgvector:pg16`)
- **ML & NLP**: `sentence-transformers` (`all-MiniLM-L6-v2`), `scikit-learn`, `numpy`
- **OCR**: `pytesseract`, `Pillow`, Tesseract OCR Engine
- **LLM RAG**: Google Gemini API (`google-genai` / `google-generativeai`)
- **Cache**: Redis 7 (`redis:7-alpine`)
- **Containerization**: Docker, Docker Compose

---

## 3. Quickstart

### Prerequisites
- Python 3.10+ and `pip`
- Docker & Docker Compose (optional for containerized orchestration)

### Installation
1. Clone the repository and install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Seed the database vector store from `eval/data/seed.csv`:
   ```bash
   python scripts/seed_db.py
   # OR
   npm run seed
   ```

### Running Locally with Docker Compose
To launch the API, PostgreSQL (pgvector), and Redis in Docker containers:
```bash
docker-compose up -d --build
# OR
npm run docker:up
```

### Running Locally without Docker
Start the FastAPI server directly:
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
# OR
npm run serve
```

Open `http://127.0.0.1:8000/` in your browser for the web interface or `/docs` for Swagger UI.

---

## 4. Evaluation & Demo Scripts

- **Run Held-Out Classifier Evaluation**:
  ```bash
  python scripts/eval.py
  # Output: Top-1 Accuracy on Holdout Set: 15/24 (62.5%)
  ```
- **Audit Deep Resolution Path**:
  ```bash
  python scripts/test_deep_path.py
  ```
- **Audit Real Image OCR Extraction**:
  ```bash
  python scripts/test_ocr.py
  ```

---

## 5. API Endpoints Reference

| Method | Path | Description | Status |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Serves web UI dashboard | Active |
| `GET` | `/health` | Service & DB health check (`{"ok": true}`) | Active |
| `GET` | `/ml/stats` | Returns vector memory entry count | Active |
| `POST` | `/tickets/resolve` | Main ticket resolution workflow | Active |
| `GET` | `/tickets/{id}/status` | Active status polling for async deep resolution | Active |
| `POST` | `/memory/store` | Stores a Q&A resolution into `pgvector` memory | Active |
| `POST` | `/memory/resolve-and-store` | Stores verified answer after external resolution | Active |

---

## 6. Environment Variables

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `PORT` | `8000` | FastAPI server port |
| `POSTGRES_URI` | `postgresql://postgres:postgres@localhost:5432/it_ticketing` | PostgreSQL database connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `CONFIDENCE_THRESHOLD` | `0.72` | Classifier confidence threshold before triggering deep resolution |
| `CACHE_SIMILARITY_THRESHOLD` | `0.82` | Minimum similarity ratio for Q&A cache hit |
| `EMBEDDING_MODEL_NAME` | `all-MiniLM-L6-v2` | Sentence-transformers model name |
| `GEMINI_API_KEY` | *(None)* | API Key for Google Gemini RAG Deep Resolution |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model identifier |

---

## 7. Documentation Suite

- [PRD (`docs/PRD.md`)](file:///d:/.Study/Projects/it%20teciting/docs/PRD.md): Product requirements and baseline goals.
- [Architecture (`docs/ARCHITECTURE.md`)](file:///d:/.Study/Projects/it%20teciting/docs/ARCHITECTURE.md): System architecture and held-out evaluation methodology.
- [Known Limitations (`docs/KNOWN_LIMITATIONS.md`)](file:///d:/.Study/Projects/it%20teciting/docs/KNOWN_LIMITATIONS.md): Phase 3 verified evaluation audit and bottleneck analysis.
- [Changelog (`CHANGELOG.md`)](file:///d:/.Study/Projects/it%20teciting/CHANGELOG.md): Version history.
