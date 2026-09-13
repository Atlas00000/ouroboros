"""Transactional outbox helpers → Redis Streams (W6·D3)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import redis
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.outbox import OutboxMessage

logger = logging.getLogger(__name__)

# Single stream for all durable events; type in payload / Redis field ``event``.
STREAM_KEY = "ouroboros:events"
CONSUMER_GROUP = "quant-platforms"


def get_redis() -> redis.Redis:
    settings = get_settings()
    return redis.Redis.from_url(settings.redis_url, decode_responses=True)


def ensure_consumer_group(
    client: redis.Redis | None = None,
    *,
    stream: str = STREAM_KEY,
    group: str = CONSUMER_GROUP,
) -> None:
    r = client or get_redis()
    try:
        r.xgroup_create(stream, group, id="0", mkstream=True)
    except redis.ResponseError as exc:
        if "BUSYGROUP" not in str(exc):
            raise


@dataclass(frozen=True)
class RelayResult:
    published: int
    failed: int


def relay_unpublished(
    session: Session,
    *,
    batch_size: int = 100,
    client: redis.Redis | None = None,
) -> RelayResult:
    """
    Publish unpublished outbox rows to Redis Streams and mark ``published_at``.

    Same DB session should commit after success. Failed rows increment
    ``publish_attempts`` and keep ``published_at`` null for retry.
    """
    r = client or get_redis()
    ensure_consumer_group(r)
    rows = list(
        session.scalars(
            select(OutboxMessage)
            .where(OutboxMessage.published_at.is_(None))
            .order_by(OutboxMessage.id.asc())
            .limit(batch_size)
        ).all()
    )
    published = 0
    failed = 0
    now = datetime.now(UTC)
    for row in rows:
        try:
            fields: dict[str, Any] = {
                "event_id": row.event_id,
                "event": row.event,
                "payload_json": row.payload_json,
            }
            r.xadd(STREAM_KEY, fields)
            row.published_at = now
            row.last_error = None
            published += 1
        except Exception as exc:  # noqa: BLE001
            failed += 1
            row.publish_attempts = int(row.publish_attempts or 0) + 1
            row.last_error = str(exc)[:500]
            logger.warning("outbox_relay_failed id=%s err=%s", row.id, exc)
    session.flush()
    return RelayResult(published=published, failed=failed)


def read_group(
    *,
    consumer: str,
    count: int = 10,
    block_ms: int = 1000,
    group: str = CONSUMER_GROUP,
    stream: str = STREAM_KEY,
    client: redis.Redis | None = None,
) -> list[tuple[str, dict[str, str]]]:
    """Read pending/new messages for a consumer in the quant-platforms group."""
    r = client or get_redis()
    ensure_consumer_group(r, stream=stream, group=group)
    raw = r.xreadgroup(group, consumer, {stream: ">"}, count=count, block=block_ms)
    out: list[tuple[str, dict[str, str]]] = []
    if not raw:
        return out
    for _stream_name, messages in raw:
        for msg_id, fields in messages:
            out.append((msg_id, dict(fields)))
    return out


def ack(
    message_ids: list[str],
    *,
    group: str = CONSUMER_GROUP,
    stream: str = STREAM_KEY,
    client: redis.Redis | None = None,
) -> int:
    if not message_ids:
        return 0
    r = client or get_redis()
    return int(r.xack(stream, group, *message_ids))
