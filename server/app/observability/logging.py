"""Structured JSON logging setup + request context helpers."""

from __future__ import annotations

import json
import logging
import sys
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

_request_id: ContextVar[str | None] = ContextVar("ouroboros_request_id", default=None)
_request_path: ContextVar[str | None] = ContextVar("ouroboros_request_path", default=None)


def set_request_context(*, request_id: str | None, path: str | None = None) -> None:
    """Bind per-request fields for structured logs (middleware)."""
    _request_id.set(request_id)
    _request_path.set(path)


def clear_request_context() -> None:
    _request_id.set(None)
    _request_path.set(None)


def get_request_id() -> str | None:
    return _request_id.get()


class JsonFormatter(logging.Formatter):
    """One JSON object per line — easy to grep / pipe into jq."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }

        rid = _request_id.get()
        if rid:
            payload["request_id"] = rid
        path = _request_path.get()
        if path:
            payload["path"] = path

        # Explicit structured extras (avoid LogRecord internals).
        skip = {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "exc_info",
            "exc_text",
            "stack_info",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "message",
            "taskName",
        }
        for key, value in record.__dict__.items():
            if key in skip or key.startswith("_"):
                continue
            payload[key] = value

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO", *, service: str = "ouroboros-server") -> None:
    root = logging.getLogger()
    root.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)
    root.setLevel(level.upper())

    # Keep access noise readable; silence chatty libs unless DEBUG.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    if level.upper() == "DEBUG":
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    else:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    logging.LoggerAdapter(logging.getLogger(service), {"service": service}).debug(
        "logging_configured level=%s",
        level.upper(),
    )
