# Changelog

All notable changes to the Intelligent IT Ticket Auto-Resolution System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-07-29

### Added
- **Phase 3 Dataset Expansion**: Expanded total labeled ticket dataset from 63 to 108 rows across 6 categories (`NET_VPN_DISCONNECT`, `MAIL_OUTLOOK_SYNC`, `ACC_PASSWORD_RESET`, `HW_PRINT_SPOOLER`, `APP_TEAMS_CRASH`, `UNKNOWN_ESCALATION`).
- **Expanded Held-Out Evaluation**: Re-partitioned dataset into `eval/data/seed.csv` (84 rows, ~78%) and `eval/data/holdout.csv` (24 rows, ~22%, 4 samples per category).
- **Environment Example Alignment**: Updated `.env.example` with `POSTGRES_URI`, `REDIS_URL`, `EMBEDDING_MODEL_NAME`, `GEMINI_API_KEY`, and `GEMINI_MODEL`.

### Changed
- **Verified Held-Out Accuracy (`v0.3.0`)**: Re-evaluated classifier performance on uncompromised expanded holdout set, reporting **62.5% (15/24)** top-1 accuracy.
- **Limitation Analysis**: Documented that dataset expansion alone does not resolve the 0.65 embedding similarity cutoff bottleneck, establishing that embedding fine-tuning is required for further accuracy gains.

---

## [0.2.5] - 2026-07-29

### Added
- **Phase 2.5 Verification Audit**: Executed verification audit removing data leakage artifacts and testing OCR and deep resolution paths.
- **Held-Out Evaluation Split**: Partitioned dataset into `eval/data/seed.csv` (51 rows) and `eval/data/holdout.csv` (12 rows).

---

## [0.2.0] - 2026-07-27

### Added
- **Full Stack Python Rewrite**: Replaced legacy TypeScript implementation with Python FastAPI, PostgreSQL (`pgvector`), Redis caching, Pytesseract OCR, and Gemini RAG.
