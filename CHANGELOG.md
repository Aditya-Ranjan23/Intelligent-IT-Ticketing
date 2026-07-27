# Changelog

All notable changes to the Intelligent IT Ticket Auto-Resolution System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-07-27

### Added
- **Full Stack Python Rewrite**: Replaced legacy TypeScript/Hono implementation with a modular Python FastAPI architecture (`app/`).
- **PostgreSQL + pgvector**: Vector database support with 384-dimensional `sentence-transformers` embeddings (`all-MiniLM-L6-v2`) for semantic issue cluster search and Q&A memory.
- **Hybrid Classifier**: Primary vector embedding similarity search with scikit-learn (TF-IDF + LogisticRegression) fallback classifier (`app/services/classifier_service.py`).
- **Real OCR Integration**: Real image text extraction from screenshot bytes using `pytesseract` and `Pillow` (`app/services/ocr_service.py`).
- **Google Gemini RAG Deep Resolution**: Replaced Cursor Agent SDK with direct Google Gemini API (`gemini-2.5-flash`) RAG deep resolution with structured mock fallback (`app/services/llm_service.py`).
- **Redis Cache Layer**: Caches ticket resolution responses keyed by SHA-256 hash of normalized text (`app/services/cache_service.py`).
- **Docker Compose Environment**: Local orchestration via `docker-compose.yml` (FastAPI + PostgreSQL pg16 + Redis 7).
- **Expanded Seed Dataset**: Expanded `eval/data/tickets-labeled.csv` to 63 labeled ticket examples across 5 IT categories and unknown escalation.
- **Python Evaluation & Demo Scripts**: Added `scripts/eval.py`, `scripts/seed_db.py`, and `scripts/demo.py`.

### Changed
- **Legacy Code Preservation**: Moved legacy TypeScript files to `legacy/src/` and `legacy/scripts/`.
- **Status Polling**: Fully implemented active polling endpoint `GET /tickets/{ticket_id}/status`.

---

## [0.1.0] - 2026-07-27

### Added
- Initial baseline documentation suite (`README.md`, `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/KNOWN_LIMITATIONS.md`).
- Versioning baseline `v0.1.0`.
