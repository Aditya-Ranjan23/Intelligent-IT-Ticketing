# Intelligent IT Ticket Auto-Resolution System (`v0.1.0`)

> [!IMPORTANT]
> **Codebase Baseline Notice**: This documentation accurately reflects the current `v0.1.0` codebase state. The project combines a **Python FastAPI ML service** for ticket classification and Q&A memory caching with an optional **TypeScript Cursor SDK worker** for asynchronous deep resolution.

---

## 1. Overview

The Intelligent IT Ticket Auto-Resolution System automatically triages IT support tickets, provides step-by-step remediation playbooks for common IT issues, caches historical Q&A resolutions to reduce LLM token usage, and escalates complex tickets to deep AI agent resolution.

### Current Implementation (v0.1.0 Baseline)
- **FastAPI HTTP Service (`api/main.py`)**: Primary REST API for ticket resolution and memory store management.
- **Rule-Based Keyword Classifier (`ml/classifier.py`)**: Classifies tickets into 5 baseline IT categories (`NET_VPN_DISCONNECT`, `MAIL_OUTLOOK_SYNC`, `ACC_PASSWORD_RESET`, `HW_PRINT_SPOOLER`, `APP_TEAMS_CRASH`) or `UNKNOWN_ESCALATION`.
- **Q&A Memory Cache Store (`ml/memory/qa_store.py`)**: Stores verified Q&A pairs in `data/qa-memory.json` and performs character-set token similarity matching to serve instant cache hits.
- **Cursor SDK Deep Resolution Worker (`src/agents/resolveTicket.ts`)**: Asynchronous background worker leveraging `@cursor/sdk` for low-confidence ticket escalation.
- **Offline Evaluation (`scripts/eval_ml.py`)**: Evaluates classifier performance against a 15-row labeled CSV dataset (`eval/data/tickets-labeled.csv`), achieving **100.0% top-1 accuracy** (15/15) on this slice.

---

## 2. Technology Stack

- **Python ML Layer**: Python 3.10+, FastAPI, Uvicorn, Pydantic, python-dotenv
- **TypeScript Worker Layer**: Node.js 20+, TypeScript, `@cursor/sdk`, Zod
- **Storage**: JSON file-backed store (`data/qa-memory.json`), In-memory TypeScript `Map` (`src/store.ts`)

---

## 3. Quickstart

### Prerequisites
- Python 3.10 or higher
- Node.js 20 or higher (for Cursor SDK deep resolution worker)

### Installation
1. Clone the repository and install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. (Optional) Install Node dependencies:
   ```bash
   npm install
   ```

### Running the API Server
Start the FastAPI server on `http://127.0.0.1:8000`:
```bash
npm run ml:serve
# OR
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

Open `http://127.0.0.1:8000/` in your browser to view the interactive web interface.

---

## 4. Evaluation & Demo Scripts

- **Run Offline ML Classifier Evaluation**:
  ```bash
  python scripts/eval_ml.py
  # Output: Offline eval: 15/15 top-1 = 100.0%
  ```
- **Seed Q&A Memory Cache**:
  ```bash
  python scripts/seed_memory.py
  ```
- **Run Python API Demo**:
  ```bash
  # Ensure the API server is running in another terminal
  python scripts/demo_api.py
  ```

---

## 5. API Endpoints Reference

| Method | Path | Description | Status |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Serves web UI interface | Active |
| `GET` | `/health` | Health check endpoint (`{"ok": true}`) | Active |
| `GET` | `/ml/stats` | Returns Q&A memory store count and file path | Active |
| `POST` | `/tickets/resolve` | Resolves ticket via Q&A cache or keyword ML pipeline | Active |
| `POST` | `/memory/store` | Stores a Q&A resolution entry into `data/qa-memory.json` | Active |
| `POST` | `/memory/resolve-and-store` | Stores verified answer after external or manual resolution | Active |
| `GET` | `/tickets/{ticket_id}/status` | Status polling for async deep resolution | **501 Not Implemented** |

---

## 6. Environment Variables

Configure via `.env` file:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `PORT` | `8000` | FastAPI server listening port |
| `CONFIDENCE_THRESHOLD` | `0.72` | Minimum classifier confidence before triggering deep resolution |
| `STORE_PLAYBOOK_HITS` | `true` | Automatically cache high-confidence playbook resolutions |
| `QA_MEMORY_PATH` | `data/qa-memory.json` | Path to JSON Q&A memory storage file |
| `CACHE_SIMILARITY_THRESHOLD` | `0.82` | Minimum similarity ratio to trigger a Q&A cache hit |
| `CURSOR_API_KEY` | *(None)* | API key for `@cursor/sdk` deep resolution worker |
| `CURSOR_MODEL_ID` | `composer-2` | Model identifier used by Cursor Agent SDK |

---

## 7. Documentation Suite

- [PRD (`docs/PRD.md`)](file:///d:/.Study/Projects/it%20teciting/docs/PRD.md): Product overview, target goals vs. current baseline, and non-goals.
- [Architecture (`docs/ARCHITECTURE.md`)](file:///d:/.Study/Projects/it%20teciting/docs/ARCHITECTURE.md): System design, sequence flows, component interactions, and stubs.
- [Known Limitations (`docs/KNOWN_LIMITATIONS.md`)](file:///d:/.Study/Projects/it%20teciting/docs/KNOWN_LIMITATIONS.md): Exhaustive list of code placeholders, stubs, and production requirements.
- [Changelog (`CHANGELOG.md`)](file:///d:/.Study/Projects/it%20teciting/CHANGELOG.md): Version history following Keep a Changelog standards.
