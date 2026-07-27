import time
import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.ticket import (
    ResolveTicketRequest,
    ResolveTicketResponse,
    CacheDetail,
    DeepResolutionDetail,
    TicketStatusResponse,
    StoreAnswerRequest,
    MemoryStatsResponse,
)
from app.services.ocr_service import extract_text_from_base64
from app.services.classifier_service import classify_ticket
from app.services.cache_service import get_cached_resolution, set_cached_resolution
from app.services.ticket_service import (
    find_similar_qa_memory,
    create_ticket_record,
    get_ticket_by_id,
    upsert_qa_memory,
)
from app.services.llm_service import generate_deep_resolution
from app.models.ticket import QAMemory, Ticket

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
def health(db: Session = Depends(get_db)):
    return {"ok": True, "service": "Intelligent IT Ticket Auto-Resolution (v0.2.0 Python)"}


@router.get("/ml/stats", response_model=MemoryStatsResponse)
def ml_stats(db: Session = Depends(get_db)):
    count = db.query(QAMemory).count()
    return MemoryStatsResponse(count=count, storage_type="pgvector")


def run_async_deep_resolution(
    ticket_id: str,
    tenant_id: str,
    normalized_text: str,
    log_snippet: str | None,
    repo_url: str | None,
    db_session: Session,
):
    try:
        success, result_text = generate_deep_resolution(
            db=db_session,
            ticket_id=ticket_id,
            tenant_id=tenant_id,
            normalized_text=normalized_text,
            log_snippet=log_snippet,
            repo_url=repo_url,
        )
        ticket = get_ticket_by_id(db_session, ticket_id)
        if ticket:
            if success:
                ticket.status = "deep_resolution_finished"
                ticket.deep_result_text = result_text
            else:
                ticket.status = "deep_resolution_error"
                ticket.deep_error = result_text
            db_session.commit()
    except Exception as e:
        logger.error(f"Async deep resolution failed for ticket {ticket_id}: {e}")
        ticket = get_ticket_by_id(db_session, ticket_id)
        if ticket:
            ticket.status = "deep_resolution_error"
            ticket.deep_error = str(e)
            db_session.commit()
    finally:
        db_session.close()


@router.post("/tickets/resolve", response_model=ResolveTicketResponse)
def resolve_ticket(
    body: ResolveTicketRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    start_time = time.perf_counter()

    # 1. OCR text extraction
    ocr_text, has_screenshot = extract_text_from_base64(body.imageBase64)

    # 2. Redis Hash Cache check
    combined_raw = f"{body.text} {ocr_text or ''} {body.logSnippet or ''}"
    cached_data = get_cached_resolution(combined_raw)
    if cached_data:
        latency_ms = round((time.perf_counter() - start_time) * 1000)
        return ResolveTicketResponse(
            ticket_id=None,
            latency_ms=latency_ms,
            classification=cached_data["classification"],
            confidence=1.0,
            suggested_steps=cached_data["suggested_steps"],
            has_screenshot=has_screenshot,
            ocr_text=ocr_text,
            resolution_mode="cache_hit",
            cache=CacheDetail(
                memory_id=cached_data.get("memory_id", "redis-cache"),
                similarity=1.0,
                tokens_saved=True,
            ),
        )

    # 3. Hybrid Classification (Sentence-Transformers + Scikit-Learn Fallback)
    ml = classify_ticket(
        db=db,
        text=body.text,
        ocr_text=ocr_text,
        log_snippet=body.logSnippet,
        has_screenshot=has_screenshot,
    )

    # 4. Q&A Vector Memory Search
    qa_hit = find_similar_qa_memory(db, ml.normalized_text)
    latency_ms = round((time.perf_counter() - start_time) * 1000)

    if qa_hit:
        entry, similarity = qa_hit
        entry.hit_count += 1
        db.commit()

        steps = list(entry.suggested_steps)
        if entry.deep_answer:
            steps.extend(["--- Cached Deep Resolution ---", entry.deep_answer])

        # Cache in Redis
        set_cached_resolution(combined_raw, {
            "classification": entry.classification,
            "suggested_steps": steps,
            "memory_id": entry.id,
        })

        return ResolveTicketResponse(
            ticket_id=None,
            latency_ms=latency_ms,
            classification=entry.classification,
            confidence=1.0,
            suggested_steps=steps,
            has_screenshot=has_screenshot,
            ocr_text=ocr_text,
            resolution_mode="cache_hit",
            cache=CacheDetail(
                memory_id=entry.id,
                similarity=similarity,
                tokens_saved=True,
            ),
        )

    # 5. Check if high-confidence fast path
    if ml.confidence >= 0.72 and ml.classification != "UNKNOWN_ESCALATION":
        # Cache in Redis
        set_cached_resolution(combined_raw, {
            "classification": ml.classification,
            "suggested_steps": ml.suggested_steps,
        })

        return ResolveTicketResponse(
            ticket_id=None,
            latency_ms=latency_ms,
            classification=ml.classification,
            confidence=ml.confidence,
            suggested_steps=ml.suggested_steps,
            has_screenshot=has_screenshot,
            ocr_text=ocr_text,
            resolution_mode="ml_complete",
            cache=None,
            deep_resolution=None,
        )

    # 6. Low Confidence / UNKNOWN -> Escalate to Deep Path
    ticket = create_ticket_record(
        db=db,
        tenant_id=body.tenantId,
        text=body.text,
        normalized_text=ml.normalized_text,
        classification=ml.classification,
        confidence=ml.confidence,
        suggested_steps=ml.suggested_steps,
        resolution_mode="ml_needs_deep",
        has_screenshot=has_screenshot,
        ocr_text=ocr_text,
        status="deep_resolution_running",
    )

    # Spawn background task for RAG Deep Resolution
    from app.core.database import SessionLocal
    bg_db = SessionLocal()
    background_tasks.add_task(
        run_async_deep_resolution,
        ticket_id=ticket.id,
        tenant_id=body.tenantId,
        normalized_text=ml.normalized_text,
        log_snippet=body.logSnippet,
        repo_url=body.repoUrl,
        db_session=bg_db,
    )

    return ResolveTicketResponse(
        ticket_id=ticket.id,
        latency_ms=latency_ms,
        classification=ml.classification,
        confidence=ml.confidence,
        suggested_steps=ml.suggested_steps,
        has_screenshot=has_screenshot,
        ocr_text=ocr_text,
        resolution_mode="ml_needs_deep",
        cache=None,
        deep_resolution=DeepResolutionDetail(
            poll_path=f"/tickets/{ticket.id}/status",
            note="Low confidence or unknown issue — deep RAG resolution initiated.",
        ),
    )


@router.get("/tickets/{ticket_id}/status", response_model=TicketStatusResponse)
def get_ticket_status(ticket_id: str, db: Session = Depends(get_db)):
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket '{ticket_id}' not found.")

    return TicketStatusResponse(
        id=ticket.id,
        tenant_id=ticket.tenant_id,
        status=ticket.status,
        classification=ticket.classification,
        confidence=ticket.confidence,
        suggested_steps=ticket.suggested_steps,
        deep_result_text=ticket.deep_result_text,
        deep_error=ticket.deep_error,
        created_at=ticket.created_at.isoformat() if ticket.created_at else "",
        updated_at=ticket.updated_at.isoformat() if ticket.updated_at else "",
    )


@router.post("/memory/store")
def store_memory(body: StoreAnswerRequest, db: Session = Depends(get_db)):
    entry = upsert_qa_memory(
        db=db,
        question_text=body.question_text,
        classification=body.classification,
        suggested_steps=body.suggested_steps or ["See stored answer."],
        deep_answer=body.deep_answer,
    )
    return {"id": entry.id, "stored": True}


@router.post("/memory/resolve-and-store")
def resolve_and_store(body: StoreAnswerRequest, db: Session = Depends(get_db)):
    entry = upsert_qa_memory(
        db=db,
        question_text=body.question_text,
        classification=body.classification,
        suggested_steps=body.suggested_steps,
        deep_answer=body.deep_answer,
    )
    return {"id": entry.id, "stored": True}
