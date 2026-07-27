import hashlib
from typing import Any

from app.core.redis_client import cache_get, cache_set


def compute_text_hash(text: str) -> str:
    return hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()


def get_cached_resolution(text: str) -> dict[str, Any] | None:
    h = compute_text_hash(text)
    key = f"ticket_resolution:{h}"
    return cache_get(key)


def set_cached_resolution(text: str, data: dict[str, Any], ttl_seconds: int = 86400) -> None:
    h = compute_text_hash(text)
    key = f"ticket_resolution:{h}"
    cache_set(key, data, ttl_seconds)
