# Known Limitations & Technical Tradeoffs (`v0.3.0` / Phase 3 Verified)

This document tracks technical limitations, tradeoffs, and verified capabilities in the codebase across version iterations.

---

## 1. Verified System Audit & Evaluation (Phase 3 Findings)

| Component | Phase 2 Claim | Phase 2.5 Audit | Phase 3 Re-Evaluation (`v0.3.0`) |
| :--- | :--- | :--- | :--- |
| **Classifier Evaluation Accuracy** | 100.0% (63/63) | 66.7% (8/12) on held-out split | **62.5% (15/24)** on expanded held-out split (`eval/data/holdout.csv`, 108 total rows). |
| **Deep Resolution API Path** | Live Gemini RAG API | Mock Fallback Mode | **Mock Fallback Mode** (`GEMINI_API_KEY` unset in environment). |
| **Screenshot OCR Parsing** | Real pytesseract OCR | Host Fallback | **Host Fallback** (Host Windows environment lacks `tesseract-ocr` binary; containerized in `Dockerfile`). |

---

## 2. Current v0.3.0 Known Limitations & Bottlenecks

1. **Embedding Similarity Threshold Bottleneck (62.5% Accuracy)**:
   - *Finding*: Expanding the seed dataset from 51 to 84 rows did not increase held-out classification accuracy (62.5% on 24 held-out samples).
   - *Root Cause*: Off-the-shelf `sentence-transformers` (`all-MiniLM-L6-v2`) embeddings for complex phrasings (e.g. `"SSO authentication error invalid credentials"`) produce cosine similarity slightly below the rigid 0.65 threshold, falling back to `UNKNOWN_ESCALATION`.
   - *Recommendation*: Fine-tuning the embedding model on domain-specific IT ticket pairs or calibrating category-specific similarity thresholds is required to improve generalization.

2. **Unauthenticated Gemini API Key Default**:
   - *Current State*: Without `GEMINI_API_KEY`, deep resolution defaults to structured mock output (`app/services/llm_service.py`).
   - *Tradeoff*: Enables local demo execution without crashing, but live LLM generation requires key configuration.

3. **Local Host Tesseract Binary Dependency**:
   - *Current State*: Local Windows execution relies on system `tesseract-ocr` installation.
   - *Tradeoff*: Handled in containerized deployments (`Dockerfile`), but host development requires manual Tesseract installation.
