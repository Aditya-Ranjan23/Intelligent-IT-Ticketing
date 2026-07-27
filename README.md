# Intelligent IT Ticket Auto-Resolution System (`v0.2.0`)

> [!IMPORTANT]
> **Codebase Stack Notice (`v0.2.0`)**: In Phase 2, the system was completely rewritten into a modular **Python FastAPI** stack with **PostgreSQL + `pgvector`**, **Redis caching**, **Real pytesseract OCR**, **Hybrid Classifier** (`sentence-transformers` + `scikit-learn`), and **Google Gemini RAG Deep Resolution**.

---

## 1. Overview

The Intelligent IT Ticket Auto-Resolution System automatically triages IT support tickets, provides instant step-by-step remediation playbooks for common IT issues, caches historical Q&A resolutions to reduce LLM token usage, and escalates complex tickets to deep AI agent resolution.

### Key Capabilities in v0.2.0
- **FastAPI Core (`app/main.py`)**: High-performance REST service for ticket resolution, active polling, and memory management.
- **Hybrid Classifier (`app/services/classifier_service.py`)**: Primary dense vector embedding search using `sentence-transformers` (`all-MiniLM-L6-v2`, 384d) with `scikit-learn` (TF-IDF + LogisticRegression) fallback.
- **Real OCR Engine (`app/services/ocr_service.py`)**: Text extraction from screenshot image bytes using `pytesseract` and `Pillow`.
- **Google Gemini RAG Deep Resolution (`app/services/llm_service.py`)**: Direct Gemini API integration (`gemini-2.5-flash`) with RAG vector context retrieval and structured mock fallback.
- **PostgreSQL + `pgvector` & Redis Caching**: Relational vector database tables (`tickets`, `issue_clusters`, `qa_memory`) and Redis resolution hash caching (`app/services/cache_service.py`).
- **Offline Evaluation (`scripts/eval.py`)**: Evaluated against an expanded 63-row labeled dataset (`eval/data/tickets-labeled.csv`), achieving **100.0% top-1 accuracy** (63/63).

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
2. Seed the database and compute vector embeddings:
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

- **Run Offline Classifier Evaluation**:
  ```bash
  python scripts/eval.py
  # Output: Top-1 Accuracy: 63/63 (100.0%)
  ```
- **Seed Database & Train Fallback Classifier**:
  ```bash
  python scripts/seed_db.py
  ```
- **Run Python API Demo**:
  ```bash
  # Start the API server first, then run:
  python scripts/demo.py
  ```

---

## 5. API Endpoints Reference

| Method | Path | Description | Status |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Serves web UI dashboard | Active |
| `GET` | `/health` | Service & DB health check (`{"ok": true}`) | Active |
| `GET` | `/ml/stats` | Returns vector memory entry count | Active |
| `POST` | `/tickets/resolve` | Main ticket resolution workflow | Active |
| `GET` | `/tickets/{id}/status` | Active status polling for async deep resolution | **Active (v0.2.0)** |
| `POST` | `/memory/store` | Stores a Q&A resolution into `pgvector` memory | Active |
| `POST` | `/memory/resolve-and-store` | Stores verified answer after external resolution | Active |

---

## 6. Environment Variables

Configure via `.env` file:

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
- [Architecture (`docs/ARCHITECTURE.md`)](file:///d:/.Study/Projects/it%20teciting/docs/ARCHITECTURE.md): Updated v0.2.0 system architecture and sequence flows.
- [Known Limitations (`docs/KNOWN_LIMITATIONS.md`)](file:///d:/.Study/Projects/it%20teciting/docs/KNOWN_LIMITATIONS.md): Resolved v0.1.0 stubs and v0.2.0 technical tradeoffs.
- [Changelog (`CHANGELOG.md`)](file:///d:/.Study/Projects/it%20teciting/CHANGELOG.md): Version history.
