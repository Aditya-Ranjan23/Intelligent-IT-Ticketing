# Known Limitations & Code Stubs

This document provides an exhaustive inventory of code stubs, placeholders, in-memory stores, and technical shortcuts present in the `v0.1.0` codebase, along with notes on what a real production implementation would require.

---

## Inventory of Stubs & Limitations

| Component | File Location | Current Code Behavior | Real-World Requirement |
| :--- | :--- | :--- | :--- |
| **Screenshot OCR** | [`ml/preprocess.py`](file:///d:/.Study/Projects/it%20teciting/ml/preprocess.py#L11-L16) | `screenshot_ocr_hint()` returns a static hardcoded hint (`"[Screenshot attached — OCR pending...]"`) without reading image bytes. | Real OCR engine (e.g., Tesseract, AWS Textract, or multi-modal Vision LLM API) to extract text from images. |
| **Playbook Scale** | [`ml/playbooks.py`](file:///d:/.Study/Projects/it%20teciting/ml/playbooks.py#L20-L71) | Hardcoded array of 5 category rules (`NET_VPN_DISCONNECT`, `MAIL_OUTLOOK_SYNC`, `ACC_PASSWORD_RESET`, `HW_PRINT_SPOOLER`, `APP_TEAMS_CRASH`). | Trained ML classification model (e.g., TF-IDF / Transformer classifier) backed by a database-driven taxonomy of 5,000+ enterprise categories. |
| **TypeScript Ticket Store** | [`src/store.ts`](file:///d:/.Study/Projects/it%20teciting/src/store.ts#L20) | Uses an in-memory JavaScript `Map<string, AsyncTicketRecord>`; all state is lost on process exit. | Production relational or key-value database (e.g., PostgreSQL, Redis) with multi-tenant isolation. |
| **Q&A Memory Cache Store** | [`ml/memory/qa_store.py`](file:///d:/.Study/Projects/it%20teciting/ml/memory/qa_store.py#L43-L75) | Reads and overwrites an unindexed JSON file (`data/qa-memory.json`) in its entirety on memory updates. | Production vector database (e.g., Pgvector, Qdrant, Pinecone) supporting concurrent vector indexing. |
| **Cache Similarity Heuristic** | [`ml/memory/similarity.py`](file:///d:/.Study/Projects/it%20teciting/ml/memory/similarity.py#L4-L10) | Computes token character-set overlap ratio (`len(set_a & set_b) / len(set_a | set_b)`). | Dense vector embeddings (e.g., OpenAI `text-embedding-3-small` or HuggingFace transformers) for semantic similarity. |
| **Evaluation Dataset** | [`eval/data/tickets-labeled.csv`](file:///d:/.Study/Projects/it%20teciting/eval/data/tickets-labeled.csv) | Contains a 15-row sample dataset. | Comprehensive benchmark dataset with thousands of multi-tenant enterprise ticket samples across stratified splits. |
| **Status Polling Endpoint** | [`api/main.py`](file:///d:/.Study/Projects/it%20teciting/api/main.py#L130-L135) | `GET /tickets/{ticket_id}/status` returns HTTP 501 Not Implemented. | Background job queue (e.g., Celery, Redis Streams, or Temporal) integrated with API status endpoints. |
| **Deprecated TS Fast-Path** | [`src/fastPath.ts`](file:///d:/.Study/Projects/it%20teciting/src/fastPath.ts#L2) | Empty export stub (`export {}`), causing legacy `scripts/eval.ts` execution to fail. | Replacing or updating legacy TypeScript eval scripts to make HTTP requests against `api/main.py`. |
| **Noise Penalty Calculation** | [`ml/preprocess.py`](file:///d:/.Study/Projects/it%20teciting/ml/preprocess.py#L31-L33) | Computes noise penalty via SHA-256 byte modulo heuristic (`digest[0] % 7 / 100.0`). | Statistical text quality and entropy analysis (e.g., out-of-vocabulary ratio, character randomness). |
