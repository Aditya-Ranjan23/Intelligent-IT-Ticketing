import json
import os
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from ml.memory.similarity import text_similarity

DEFAULT_PATH = Path("data") / "qa-memory.json"


@dataclass
class QaMemoryEntry:
    id: str
    question_text: str
    classification: str
    suggested_steps: list[str]
    deep_answer: str | None
    created_at: str
    updated_at: str
    hit_count: int


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def memory_path() -> Path:
    raw = os.environ.get("QA_MEMORY_PATH", "").strip()
    return Path(raw) if raw else DEFAULT_PATH


def similarity_threshold() -> float:
    raw = os.environ.get("CACHE_SIMILARITY_THRESHOLD", "0.82")
    try:
        n = float(raw)
    except ValueError:
        n = 0.82
    return min(0.99, max(0.5, n))


def _load() -> list[QaMemoryEntry]:
    path = memory_path()
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = []
    for e in data.get("entries", []):
        entries.append(
            QaMemoryEntry(
                id=e["id"],
                question_text=e["question_text"],
                classification=e["classification"],
                suggested_steps=list(e["suggested_steps"]),
                deep_answer=e.get("deep_answer"),
                created_at=e["created_at"],
                updated_at=e["updated_at"],
                hit_count=int(e.get("hit_count", 0)),
            )
        )
    return entries


def _save(entries: list[QaMemoryEntry]) -> None:
    path = memory_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "entries": [asdict(e) for e in entries],
    }
    tmp = path.with_suffix(f".{uuid.uuid4().hex}.tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.replace(path)


_cache: list[QaMemoryEntry] | None = None


def get_entries() -> list[QaMemoryEntry]:
    global _cache
    if _cache is None:
        _cache = _load()
    return _cache


def reload_entries() -> list[QaMemoryEntry]:
    global _cache
    _cache = _load()
    return _cache


@dataclass
class SimilarHit:
    entry: QaMemoryEntry
    similarity: float


def find_similar_question(
    normalized_question: str,
    threshold: float | None = None,
) -> SimilarHit | None:
    thresh = similarity_threshold() if threshold is None else threshold
    best: SimilarHit | None = None
    for entry in get_entries():
        sim = text_similarity(normalized_question, entry.question_text)
        if sim >= thresh and (best is None or sim > best.similarity):
            best = SimilarHit(entry=entry, similarity=sim)
    return best


def record_memory_hit(entry_id: str) -> None:
    entries = get_entries()
    for e in entries:
        if e.id == entry_id:
            e.hit_count += 1
            e.updated_at = _now_iso()
            _save(entries)
            return


def upsert_answer(
    question_text: str,
    classification: str,
    suggested_steps: list[str],
    deep_answer: str | None = None,
) -> QaMemoryEntry:
    existing = find_similar_question(question_text)
    entries = get_entries()
    now = _now_iso()

    if existing:
        e = existing.entry
        e.classification = classification
        e.suggested_steps = suggested_steps
        if deep_answer:
            e.deep_answer = deep_answer
        e.updated_at = now
        _save(entries)
        return e

    entry = QaMemoryEntry(
        id=str(uuid.uuid4()),
        question_text=question_text,
        classification=classification,
        suggested_steps=suggested_steps,
        deep_answer=deep_answer,
        created_at=now,
        updated_at=now,
        hit_count=0,
    )
    entries.append(entry)
    _save(entries)
    return entry


def memory_stats() -> dict[str, str | int]:
    return {"count": len(get_entries()), "path": str(memory_path())}
