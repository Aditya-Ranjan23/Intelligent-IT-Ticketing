import os
from dataclasses import dataclass
from typing import Literal

from ml.memory.qa_store import (
    find_similar_question,
    record_memory_hit,
    upsert_answer,
)
from ml.pipeline import MlResult, run_ml_pipeline
from ml.playbooks import UNKNOWN_ESCALATION


def ml_confidence_threshold() -> float:
    raw = os.environ.get("CONFIDENCE_THRESHOLD", "0.72")
    try:
        return float(raw)
    except ValueError:
        return 0.72


def should_store_playbook_hits() -> bool:
    raw = os.environ.get("STORE_PLAYBOOK_HITS", "true").strip().lower()
    return raw not in ("false", "0", "no")


@dataclass
class CachedResolution:
    memory_id: str
    similarity: float
    classification: str
    suggested_steps: list[str]
    deep_answer: str | None


@dataclass
class CacheHitOutcome:
    mode: Literal["cache_hit"]
    ml: MlResult
    cache: CachedResolution


@dataclass
class MlCompleteOutcome:
    mode: Literal["ml_complete"]
    ml: MlResult


@dataclass
class MlNeedsDeepOutcome:
    mode: Literal["ml_needs_deep"]
    ml: MlResult


ResolveOutcome = CacheHitOutcome | MlCompleteOutcome | MlNeedsDeepOutcome


def resolve_ticket(
    text: str = "",
    image_base64: str | None = None,
    log_snippet: str | None = None,
) -> ResolveOutcome:
    ml = run_ml_pipeline(
        text=text,
        image_base64=image_base64,
        log_snippet=log_snippet,
    )

    hit = find_similar_question(ml.normalized_text)
    if hit:
        record_memory_hit(hit.entry.id)
        return CacheHitOutcome(
            mode="cache_hit",
            ml=ml,
            cache=CachedResolution(
                memory_id=hit.entry.id,
                similarity=hit.similarity,
                classification=hit.entry.classification,
                suggested_steps=hit.entry.suggested_steps,
                deep_answer=hit.entry.deep_answer,
            ),
        )

    threshold = ml_confidence_threshold()
    needs_deep = ml.confidence < threshold or ml.classification == UNKNOWN_ESCALATION

    if not needs_deep and should_store_playbook_hits():
        upsert_answer(
            question_text=ml.normalized_text,
            classification=ml.classification,
            suggested_steps=ml.suggested_steps,
        )

    if needs_deep:
        return MlNeedsDeepOutcome(mode="ml_needs_deep", ml=ml)
    return MlCompleteOutcome(mode="ml_complete", ml=ml)


def store_resolved_answer(
    question_text: str,
    classification: str,
    suggested_steps: list[str],
    deep_answer: str | None = None,
) -> None:
    upsert_answer(
        question_text=question_text,
        classification=classification,
        suggested_steps=suggested_steps,
        deep_answer=deep_answer,
    )
