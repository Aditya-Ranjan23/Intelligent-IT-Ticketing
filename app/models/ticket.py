import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import String, Text, Float, Boolean, Integer, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.core.database import Base
from app.core.config import settings


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    normalized_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)
    
    classification: Mapped[str] = mapped_column(String(100), nullable=False, default="UNKNOWN_ESCALATION")
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    suggested_steps: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    resolution_mode: Mapped[str] = mapped_column(String(50), nullable=False, default="ml_needs_deep")

    has_screenshot: Mapped[bool] = mapped_column(Boolean, default=False)
    ocr_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    deep_result_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    deep_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class IssueCluster(Base):
    __tablename__ = "issue_clusters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    example_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding = mapped_column(Vector(settings.EMBEDDING_DIM), nullable=True)
    suggested_steps: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)


class QAMemory(Base):
    __tablename__ = "qa_memory"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding = mapped_column(Vector(settings.EMBEDDING_DIM), nullable=True)
    classification: Mapped[str] = mapped_column(String(100), nullable=False)
    suggested_steps: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    deep_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    hit_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
