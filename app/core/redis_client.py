import logging
import json
from typing import Any
import redis

from app.core.config import settings

logger = logging.getLogger(__name__)

_memory_cache: dict[str, str] = {}
_redis_instance: redis.Redis | None = None


def get_redis() -> redis.Redis | None:
    global _redis_instance
    if _redis_instance is None:
        try:
            client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True, socket_timeout=1.5)
            client.ping()
            _redis_instance = client
            logger.info("Connected to Redis server.")
        except Exception as err:
            logger.warning(f"Redis connection failed ({err}). Using in-memory dict cache fallback.")
            _redis_instance = None
    return _redis_instance


def cache_get(key: str) -> dict[str, Any] | None:
    r = get_redis()
    try:
        if r:
            val = r.get(key)
            return json.loads(val) if val else None
        val = _memory_cache.get(key)
        return json.loads(val) if val else None
    except Exception as e:
        logger.warning(f"Cache get failed for key {key}: {e}")
        return None


def cache_set(key: str, value: dict[str, Any], ttl_seconds: int = 86400) -> None:
    r = get_redis()
    payload = json.dumps(value)
    try:
        if r:
            r.setex(key, ttl_seconds, payload)
        else:
            _memory_cache[key] = payload
    except Exception as e:
        logger.warning(f"Cache set failed for key {key}: {e}")
