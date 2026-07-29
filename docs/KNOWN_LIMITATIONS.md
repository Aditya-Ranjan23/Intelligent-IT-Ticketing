# Known Limitations & Technical Tradeoffs (`v0.2.0` / Phase 2.5 Verified)

This document tracks technical limitations, tradeoffs, and verified capabilities in the codebase.

---

## 1. Verified System Audit (Phase 2.5 Findings)

| Component | Phase 2 Claim | Phase 2.5 Verification Finding | Real-World Status |
| :--- | :--- | :--- | :--- |
| **Classifier Evaluation Accuracy** | 100.0% (63/63) | **66.7% (8/12)** on held-out test data (`eval/data/holdout.csv`). | Phase 2 claim was a data leakage artifact (evaluating against seed dataset). Real top-1 accuracy on unseen data is 66.7%. |
| **Deep Resolution API Path** | Live Gemini RAG API | **Mock Fallback Mode** (`GEMINI_API_KEY` is unset in local environment). | Structured mock resolution generated; live Gemini API call requires valid `GEMINI_API_KEY`. |
| **Screenshot OCR Parsing** | Real pytesseract OCR | **Partial / Host Fallback** (`tesseract` binary missing on local Windows PATH). | Base64 image decoding and PIL parsing verified; local Windows host returns fallback note. Native Tesseract binary included in `Dockerfile`. |

---

## 2. Current v0.2.0 Known Limitations & Tradeoffs

1. **Held-Out Accuracy Gap (66.7% vs. 80.0% Target)**:
   - *Current State*: On unseen held-out ticket data, sentence-transformers embedding similarity achieved 8/12 top-1 accuracy.
   - *Tradeoff*: 4 out-of-distribution ticket phrasings fell back to `UNKNOWN_ESCALATION` because cosine distance exceeded 0.65 threshold. Expanding the seed dataset or fine-tuning embeddings is required to reach >80% held-out accuracy.

2. **Unauthenticated Gemini API Key Default**:
   - *Current State*: Without `GEMINI_API_KEY`, deep resolution defaults to deterministic mock output (`app/services/llm_service.py`).
   - *Tradeoff*: Ensures local offline demo readiness without crashing, but live LLM generation requires key configuration.

3. **Local Tesseract Binary Dependency**:
   - *Current State*: Local Windows execution relies on system `tesseract-ocr` installation.
   - *Tradeoff*: Resolved in containerized deployments (`Dockerfile`), but host development requires manual Tesseract installation or cloud Vision API integration.
