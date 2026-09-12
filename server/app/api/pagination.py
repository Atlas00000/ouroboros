"""Cursor-based pagination helpers."""

from __future__ import annotations

import base64
import json
from typing import Any, TypeVar

from pydantic import BaseModel, Field

from app.api.errors import AppError

T = TypeVar("T")


def encode_cursor(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def decode_cursor(cursor: str) -> dict[str, Any]:
    if not cursor:
        raise AppError(status=400, title="Bad Request", detail="Empty cursor")
    pad = "=" * (-len(cursor) % 4)
    try:
        raw = base64.urlsafe_b64decode(cursor + pad)
        data = json.loads(raw.decode("utf-8"))
    except (ValueError, json.JSONDecodeError) as exc:
        raise AppError(status=400, title="Bad Request", detail="Invalid cursor") from exc
    if not isinstance(data, dict):
        raise AppError(status=400, title="Bad Request", detail="Invalid cursor payload")
    return data


class CursorPage(BaseModel):
    """Generic cursor page envelope (items typed per-route)."""

    items: list[Any]
    next_cursor: str | None = None
    has_more: bool = False


class ProvenanceEnvelope(BaseModel):
    """Lightweight provenance attached to list endpoints."""

    sources: list[str] = Field(default_factory=list)
    generated_at: str
    model_version: str
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    stale: bool = False
