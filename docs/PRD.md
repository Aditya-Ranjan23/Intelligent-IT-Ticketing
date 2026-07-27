# Product Requirements Document (PRD) — Intelligent IT Ticket Auto-Resolution System

## 1. Problem Statement

IT helpdesks in enterprise environments suffer from high ticket volumes, long resolution times for routine issues (password resets, VPN drops, Outlook sync bugs), and significant engineer toil handling repetitive tier-1 support tasks. 

The goal of the Intelligent IT Ticket Auto-Resolution System is to automatically triage incoming IT support tickets, provide instant step-by-step remediation playbooks for routine issues, maintain a cache of historical solutions to reduce LLM token usage, and escalate complex or low-confidence tickets to deep AI agent resolution or tier-2 human support.

---

## 2. Project Goals & Target Metrics

> [!NOTE]
> The numbers below represent long-term target goals for production deployment, **not** the current measured baseline of the v0.1.0 codebase.

- **Scale Target**: Support a taxonomy of 5,000+ enterprise IT issue categories.
- **Fast-Path Latency Target**: Sub-second (< 500ms) triage and playbook generation for high-confidence tickets.
- **Deflection Rate Target**: 40%+ tier-1 ticket auto-resolution without human intervention.
- **Multi-Modal Processing**: Process text, attached log snippets, and error screenshots via OCR.

---

## 3. Current Scope (v0.1.0 Baseline)

The current implementation (`v0.1.0`) provides a baseline prototype with the following functional scope:

1. **Rule-Based Keyword Classifier**:
   - Classifies tickets into 5 hardcoded IT categories (`NET_VPN_DISCONNECT`, `MAIL_OUTLOOK_SYNC`, `ACC_PASSWORD_RESET`, `HW_PRINT_SPOOLER`, `APP_TEAMS_CRASH`) or falls back to `UNKNOWN_ESCALATION`.
   - Computes a confidence score based on keyword match count and a pseudo-noise penalty heuristic.

2. **Q&A Memory Cache**:
   - Stores verified question/answer pairs in a JSON file (`data/qa-memory.json`).
   - Uses character-set Jaccard/overlap string similarity matching (`ml/memory/similarity.py`) to serve instant cache hits for recurring questions.

3. **Routing Logic & Escalation**:
   - Evaluates ticket confidence against a configurable threshold (`CONFIDENCE_THRESHOLD`, default `0.72`).
   - High-confidence matches return immediate playbook remediation steps (`ml_complete` or `cache_hit`).
   - Low-confidence or unclassified tickets are routed to deep resolution (`ml_needs_deep`).

4. **Async Cursor SDK Deep Resolution Worker**:
   - An asynchronous TypeScript background job (`src/agents/resolveTicket.ts`) that calls `@cursor/sdk` for complex tickets when `CURSOR_API_KEY` is configured.
   - Updates an in-memory ticket status map (`src/store.ts`).

5. **Offline Evaluation**:
   - Evaluates keyword classifier accuracy against a 15-row labeled CSV dataset (`eval/data/tickets-labeled.csv`).
   - Current measured performance on this 15-row slice: **100.0% top-1 accuracy** (15/15).

---

## 4. Explicit Non-Goals for Phase 1

To maintain a strict documentation and versioning baseline without unverified code changes, the following are **explicitly out of scope**:

- **No Logic Modifications**: No alterations to `ml/classifier.py`, `src/fastPath.ts`, `src/agents/resolveTicket.ts`, or `src/store.ts`.
- **No Database Migration**: No replacement of the file-backed JSON store (`data/qa-memory.json`) or in-memory TypeScript Map store with SQL/NoSQL databases.
- **No Real OCR Engine**: No integration of Tesseract, AWS Textract, or vision language models for actual image OCR parsing.
- **No Playbook Expansion**: No adding categories beyond the initial 5 hardcoded entries.
- **No Dataset Expansion**: No additions to the 15-row `eval/data/tickets-labeled.csv` dataset.
- **No Production Metrics Claims**: No claiming multi-thousand category support, vector embedding similarity, or sub-50ms latency as current codebase facts.
