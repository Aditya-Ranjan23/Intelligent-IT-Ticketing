# Changelog

All notable changes to the Intelligent IT Ticket Auto-Resolution System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-27

### Added
- **Python FastAPI ML Service**: Core HTTP server (`api/main.py`) exposing ticket resolution (`POST /tickets/resolve`), memory persistence (`POST /memory/store`, `POST /memory/resolve-and-store`), health monitoring (`GET /health`), and memory statistics (`GET /ml/stats`).
- **Keyword Classifier & Playbook Engine**: Rule-based ticket classifier (`ml/classifier.py`) supporting 5 baseline IT categories (`NET_VPN_DISCONNECT`, `MAIL_OUTLOOK_SYNC`, `ACC_PASSWORD_RESET`, `HW_PRINT_SPOOLER`, `APP_TEAMS_CRASH`) plus `UNKNOWN_ESCALATION` fallback (`ml/playbooks.py`).
- **Q&A Memory Cache**: JSON-backed resolution memory store (`ml/memory/qa_store.py`) with character-set Jaccard/overlap string similarity matching (`ml/memory/similarity.py`) to reuse previously resolved tickets.
- **Offline ML Evaluation**: Python evaluation script (`scripts/eval_ml.py`) testing classifier accuracy against a 15-row labeled CSV benchmark (`eval/data/tickets-labeled.csv`).
- **TypeScript / Cursor SDK Deep Resolution Worker**: Asynchronous deep resolution agent (`src/agents/resolveTicket.ts`) using `@cursor/sdk` for low-confidence tickets, backed by an in-memory `Map` ticket store (`src/store.ts`).
- **Documentation Baseline**: Technical documentation suite including PRD (`docs/PRD.md`), Architecture (`docs/ARCHITECTURE.md`), and Known Limitations (`docs/KNOWN_LIMITATIONS.md`).

### Deprecated
- **TypeScript Entrypoints**: `src/index.ts` and `src/fastPath.ts` deprecated in favor of the Python ML FastAPI service.
