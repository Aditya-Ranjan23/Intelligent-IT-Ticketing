import uuid
import logging
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ticket import Ticket, QAMemory
from app.services.classifier_service import compute_embedding, cosine_similarity
from app.core.config import settings

logger = logging.getLogger(__name__)


def find_similar_qa_memory(db: Session, normalized_text: str, threshold: float | None = None) -> tuple[QAMemory, float] | None:
    thresh = settings.CACHE_SIMILARITY_THRESHOLD if threshold is None else threshold
    query_vec = compute_embedding(normalized_text)

    entries: Sequence[QAMemory] = db.scalars(select(QAMemory)).all()
    best_entry: QAMemory | None = None
    best_sim = 0.0

    for entry in entries:
        if entry.embedding:
            sim = cosine_similarity(query_vec, entry.embedding)
            if sim >= thresh and sim > best_sim:
                best_sim = sim
                best_entry = entry

    if best_entry:
        return best_entry, best_sim
    return None


def create_ticket_record(
    db: Session,
    tenant_id: str,
    text: str,
    normalized_text: str,
    classification: str,
    confidence: float,
    suggested_steps: list[str],
    resolution_mode: str,
    has_screenshot: bool = False,
    ocr_text: str | None = None,
    status: str = "pending",
) -> Ticket:
    ticket = Ticket(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        text=text,
        normalized_text=normalized_text,
        status=status,
        classification=classification,
        confidence=confidence,
        suggested_steps=suggested_steps,
        resolution_mode=resolution_mode,
        has_screenshot=has_screenshot,
        ocr_text=ocr_text,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def get_ticket_by_id(db: Session, ticket_id: str) -> Ticket | None:
    return db.scalar(select(Ticket).where(Ticket.id == ticket_id))


def upsert_qa_memory(
    db: Session,
    question_text: str,
    classification: str,
    suggested_steps: list[str],
    deep_answer: str | None = None,
) -> QAMemory:
    query_vec = compute_embedding(question_text)
    hit = find_similar_qa_memory(db, question_text, threshold=0.90)

    if hit:
        entry, _ = hit
        entry.classification = classification
        entry.suggested_steps = suggested_steps
        if deep_answer:
            entry.deep_answer = deep_answer
        db.commit()
        db.refresh(entry)
        return entry

    entry = QAMemory(
        id=str(uuid.uuid4()),
        question_text=question_text,
        embedding=query_vec,
        classification=classification,
        suggested_steps=suggested_steps,
        deep_answer=deep_answer,
        hit_count=0,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
