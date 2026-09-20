import json
import logging
import time
from datetime import datetime


class StructuredLogger:
    """
    Logs events as JSON for production observability.
    Each log line is a valid JSON object — parseable by any log tool.
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log_request(
        self,
        endpoint: str,
        session_id: str,
        question: str,
        question_type: str,
        latency_ms: float,
        cache_hit: bool,
        iterations: int,
        sources: list
    ):
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "api_request",
            "endpoint": endpoint,
            "session_id": session_id,
            "question_preview": question[:50],
            "question_type": question_type,
            "latency_ms": latency_ms,
            "cache_hit": cache_hit,
            "iterations": iterations,
            "sources": sources
        }
        self.logger.info(json.dumps(record))

    def log_error(self, endpoint: str, error: str, session_id: str = ""):
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "api_error",
            "endpoint": endpoint,
            "session_id": session_id,
            "error": error[:200]
        }
        self.logger.error(json.dumps(record))


structured_logger = StructuredLogger("joblens.api")