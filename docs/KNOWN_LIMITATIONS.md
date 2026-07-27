# Known Limitations & Technical Tradeoffs (`v0.2.0`)

This document tracks technical limitations, tradeoffs, and stubs in the codebase across version iterations.

---

## 1. Status of v0.1.0 Stubs in v0.2.0

| Component | v0.1.0 Status | v0.2.0 Implementation | Resolution Status |
| :--- | :--- | :--- | :--- |
| **Screenshot OCR** | Stub string hint | Integrated real `pytesseract` + `Pillow` image OCR parsing in `app/services/ocr_service.py`. | **RESOLVED** |
| **Vector Search** | None | Integrated `pgvector` extension with 384-dimensional `sentence-transformers` embeddings in PostgreSQL. | **RESOLVED** |
| **Persistence** | In-memory `Map` | Replaced with PostgreSQL tables (`tickets`, `issue_clusters`, `qa_memory`). | **RESOLVED** |
| **Caching** | None | Integrated Redis cache layer (`app/services/cache_service.py`) for text-hash resolution lookups. | **RESOLVED** |
| **Deep Resolution** | Cursor SDK | Direct RAG LLM call using Google Gemini API (`gemini-2.5-flash`) with vector memory retrieval (`llm_service.py`). | **RESOLVED** |
| **Status Polling** | 501 Not Implemented | Active status polling endpoint `GET /tickets/{ticket_id}/status` implemented in `app/api/endpoints.py`. | **RESOLVED** |
| **Evaluation Dataset** | 15 rows | Expanded seed dataset to 63 labeled ticket rows across categories in `eval/data/tickets-labeled.csv`. | **RESOLVED** |

---

## 2. Current v0.2.0 Known Limitations & Tradeoffs

1. **Taxonomy Scale (63 Seed Rows vs. 5,000 Enterprise Categories)**:
   - *Current State*: The vector database contains seed clusters from 63 labeled ticket examples across 5 IT categories.
   - *Tradeoff*: While vector embeddings allow semantic generalization for similar phrasing, full enterprise deployment requires thousands of labeled issue clusters.

2. **Scikit-Learn Fallback Model vs. Fine-Tuned Transformer**:
   - *Current State*: Marginal confidence tickets use a scikit-learn TF-IDF + LogisticRegression fallback classifier.
   - *Tradeoff*: A lightweight scikit-learn model avoids heavy fine-tuning overhead, but a fine-tuned domain LLM/transformer classifier will offer higher accuracy on subtle edge cases in future phases.

3. **Local OCR Engine Dependencies**:
   - *Current State*: `pytesseract` requires system `tesseract-ocr` binaries installed (handled automatically in `Dockerfile`). On local Windows environments without Tesseract installed, a graceful fallback note is returned.
   - *Tradeoff*: Cloud multi-modal vision APIs (e.g. Gemini 2.5 Flash Vision / AWS Textract) can be added in future phases for enhanced handwriting/dense UI diagram parsing.
