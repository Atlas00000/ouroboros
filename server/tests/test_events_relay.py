"""W6·D3 outbox → Redis Streams relay tests."""

from __future__ import annotations

from uuid import uuid4

from sqlalchemy import select

from app.db.session import get_session_factory
from app.events.relay import ack, get_redis, read_group, relay_unpublished
from app.models.outbox import OutboxMessage


def test_relay_publishes_and_consumer_can_ack() -> None:
    session = get_session_factory()()
    r = get_redis()
    event_id = str(uuid4())
    try:
        session.add(
            OutboxMessage(
                event_id=event_id,
                event="profile.updated",
                payload_json='{"schema_id":"events.v1","event":"profile.updated"}',
            )
        )
        session.commit()

        result = relay_unpublished(session, client=r)
        session.commit()
        assert result.published >= 1

        msgs = read_group(consumer="test-w6d3", count=50, block_ms=500, client=r)
        matched = [m for m in msgs if m[1].get("event_id") == event_id]
        assert matched, f"expected event {event_id} in stream"
        ack([matched[0][0]], client=r)

        row = session.scalar(select(OutboxMessage).where(OutboxMessage.event_id == event_id))
        assert row is not None
        assert row.published_at is not None
    finally:
        session.close()
