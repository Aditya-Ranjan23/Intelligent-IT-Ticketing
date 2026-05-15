import os
import time
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from api.schemas import ResolveTicketRequest, StoreAnswerRequest
from ml.memory.qa_store import memory_stats, upsert_answer
from ml.resolver import resolve_ticket, store_resolved_answer

load_dotenv()

app = FastAPI(
    title="IT Ticket Auto-Resolution (ML)",
    description="Classify tickets, suggest fixes, reuse cached Q&A for token savings.",
)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/ml/stats")
def ml_stats():
    return memory_stats()


@app.post("/tickets/resolve")
def tickets_resolve(body: ResolveTicketRequest):
    started = time.perf_counter()
    outcome = resolve_ticket(
        text=body.text,
        image_base64=body.image_base64,
        log_snippet=body.log_snippet,
    )
    latency_ms = round((time.perf_counter() - started) * 1000)
    ml = outcome.ml

    if outcome.mode == "cache_hit":
        steps = list(outcome.cache.suggested_steps)
        if outcome.cache.deep_answer:
            steps.extend(
                ["--- Cached deep resolution ---", outcome.cache.deep_answer]
            )
        return {
            "ticket_id": None,
            "latency_ms": latency_ms,
            "classification": outcome.cache.classification,
            "confidence": 1.0,
            "suggested_steps": steps,
            "has_screenshot": ml.has_screenshot,
            "ocr_hint": ml.ocr_hint,
            "resolution_mode": "cache_hit",
            "cache": {
                "memory_id": outcome.cache.memory_id,
                "similarity": outcome.cache.similarity,
                "tokens_saved": True,
            },
            "deep_resolution": None,
        }

    if outcome.mode == "ml_complete":
        return {
            "ticket_id": None,
            "latency_ms": latency_ms,
            "classification": ml.classification,
            "confidence": ml.confidence,
            "suggested_steps": ml.suggested_steps,
            "has_screenshot": ml.has_screenshot,
            "ocr_hint": ml.ocr_hint,
            "resolution_mode": "ml_complete",
            "cache": None,
            "deep_resolution": None,
        }

    ticket_id = str(uuid.uuid4())
    return {
        "ticket_id": ticket_id,
        "latency_ms": latency_ms,
        "classification": ml.classification,
        "confidence": ml.confidence,
        "suggested_steps": ml.suggested_steps,
        "has_screenshot": ml.has_screenshot,
        "ocr_hint": ml.ocr_hint,
        "resolution_mode": "ml_needs_deep",
        "cache": None,
        "deep_resolution": {
            "poll_path": f"/tickets/{ticket_id}/status",
            "note": "Low confidence — add answer via POST /memory/store or LLM integration later.",
        },
    }


@app.post("/memory/store")
def memory_store(body: StoreAnswerRequest):
    entry = upsert_answer(
        question_text=body.question_text,
        classification=body.classification,
        suggested_steps=body.suggested_steps or ["See stored answer."],
        deep_answer=body.deep_answer,
    )
    return {"id": entry.id, "stored": True}


@app.post("/memory/resolve-and-store")
def memory_resolve_and_store(body: StoreAnswerRequest):
    """Store a verified answer after manual or external LLM resolution."""
    store_resolved_answer(
        question_text=body.question_text,
        classification=body.classification,
        suggested_steps=body.suggested_steps,
        deep_answer=body.deep_answer,
    )
    return {"stored": True}


@app.get("/tickets/{ticket_id}/status")
def ticket_status(ticket_id: str):
    raise HTTPException(
        status_code=501,
        detail="Deep-resolution polling not implemented in Python API yet.",
    )


def main():
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("api.main:app", host="127.0.0.1", port=port, reload=False)


if __name__ == "__main__":
    main()
