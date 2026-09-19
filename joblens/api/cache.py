import hashlib
import time
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ResponseCache:


    def __init__(self, max_size: int = 500, ttl_seconds: int = 3600):
        self._cache: dict = {}
        self._max_size = max_size
        self._ttl = ttl_seconds

    def _make_key(self, question: str, session_id: str = "") -> str:
  
        content = f"{question.lower().strip()}:{session_id}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, question: str, session_id: str = "") -> Optional[dict]:
        key = self._make_key(question, session_id)
        entry = self._cache.get(key)

        if entry is None:
            return None

        # Check if expired
        if time.time() - entry["timestamp"] > self._ttl:
            del self._cache[key]
            logger.info(f"[Cache] expired: {question[:40]}")
            return None

        logger.info(f"[Cache] HIT: {question[:40]}")
        return entry["value"]

    def set(self, question: str, value: dict, session_id: str = ""):
        # Evict oldest entry if at max size
        if len(self._cache) >= self._max_size:
            oldest_key = min(self._cache, key=lambda k: self._cache[k]["timestamp"])
            del self._cache[oldest_key]

        key = self._make_key(question, session_id)
        self._cache[key] = {
            "value": value,
            "timestamp": time.time()
        }
        logger.info(f"[Cache] SET: {question[:40]}")

    def stats(self) -> dict:
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "ttl_seconds": self._ttl
        }


response_cache = ResponseCache()