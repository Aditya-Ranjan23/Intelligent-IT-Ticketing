# Changelog

All notable changes to the Intelligent IT Ticket Auto-Resolution System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.5] - 2026-07-29

### Added
- **Phase 2.5 Verification Audit**: Executed uncompromised verification phase auditing classifier accuracy, Gemini deep-path execution, and OCR text extraction.
- **Held-Out Evaluation Split**: Partitioned evaluation dataset into `eval/data/seed.csv` (51 rows) and `eval/data/holdout.csv` (12 rows, ~20% stratified across categories) to eliminate data leakage artifacts.
- **Audit Verification Scripts**: Created `scripts/create_split.py`, `scripts/test_deep_path.py`, and `scripts/test_ocr.py`.

### Changed
- **Held-Out Classifier Evaluation**: Corrected classification top-1 accuracy metric to **66.7% (8/12)** on uncompromised held-out test data (`holdout.csv`), replacing the 100% Phase 2 data leakage claim.
- **Deep Resolution Status**: Documented that local execution runs in **Mock Fallback Mode** when `GEMINI_API_KEY` is not set.
- **OCR Status**: Verified base64 image decoding and PIL canvas rendering; documented local Windows host fallback note when native `tesseract` binary is missing on host PATH.

---

## [0.2.0] - 2026-07-27

### Added
- **Full Stack Python Rewrite**: Replaced legacy TypeScript/Hono implementation with a modular Python FastAPI architecture (`app/`).
- **PostgreSQL + pgvector**: Vector database support with 384-dimensional `sentence-transformers` embeddings (`all-MiniLM-L6-v2`).
- **Hybrid Classifier**: Vector embedding similarity search with scikit-learn (TF-IDF + LogisticRegression) fallback classifier.
- **Real OCR Integration**: Text extraction from screenshot bytes using `pytesseract` and `Pillow`.
- **Google Gemini RAG Deep Resolution**: Google Gemini API (`gemini-2.5-flash`) integration with structured mock fallback.
- **Redis Cache Layer**: Caches ticket resolution responses keyed by SHA-256 hash of normalized text.

---

## [0.1.0] - 2026-07-27

### Added
- Initial baseline documentation suite and versioning baseline `v0.1.0`.
