"""Unit tests for source registry cadence + heartbeats."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import text

from app.db.session import get_session_factory
from app.ingestion.registry import (
    STATUS_ERROR,
    STATUS_OK,
    STATUS_STALE,
    STATUS_UNKNOWN,
    compute_status,
    mark_error,
    record_heartbeat,
    refresh_statuses,
    snapshot,
)


def test_compute_status_unknown_without_heartbeat() -> None:
    assert compute_status(last_seen_at=None, expected_cadence_seconds=60) == STATUS_UNKNOWN


def test_compute_status_ok_and_stale() -> None:
    now = datetime(2026, 9, 12, 12, 0, tzinfo=UTC)
    fresh = now - timedelta(seconds=30)
    stale = now - timedelta(seconds=200)
    assert compute_status(last_seen_at=fresh, expected_cadence_seconds=60, now=now) == STATUS_OK
    assert compute_status(last_seen_at=stale, expected_cadence_seconds=60, now=now) == STATUS_STALE


def test_record_heartbeat_and_refresh() -> None:
    session = get_session_factory()()
    try:
        exists = session.execute(
            text("SELECT 1 FROM source_registry WHERE source_id = 'mt5.prices'")
        ).scalar()
        assert exists == 1

        # Force stale age then heartbeat
        session.execute(
            text(
                "UPDATE source_registry SET last_seen_at = :ts, status = 'unknown' "
                "WHERE source_id = 'mt5.prices'"
            ),
            {"ts": datetime(2020, 1, 1, tzinfo=UTC)},
        )
        session.commit()

        row = record_heartbeat(session, "mt5.prices")
        assert row.status == STATUS_OK
        assert row.last_seen_at is not None

        snaps = refresh_statuses(session)
        mt5 = next(s for s in snaps if s.source_id == "mt5.prices")
        assert mt5.status == STATUS_OK
        assert mt5.stale is False
        assert snapshot(row).status == STATUS_OK

        mark_error(session, "mt5.prices")
        snaps = refresh_statuses(session)
        mt5 = next(s for s in snaps if s.source_id == "mt5.prices")
        assert mt5.status == STATUS_ERROR
    finally:
        # Restore healthy heartbeat for other tests / live backfill
        record_heartbeat(session, "mt5.prices")
        session.close()
