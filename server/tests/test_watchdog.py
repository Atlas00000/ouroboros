"""Watchdog unit + DB tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.db.session import get_session_factory
from app.ingestion.registry import STATUS_OK, STATUS_STALE, SourceSnapshot, record_heartbeat
from app.watchdog.checker import emit_alerts, run_check
from app.watchdog.kill_feed_drill import run_kill_feed_drill


def _snap(
    source_id: str,
    *,
    kind: str = "news",
    status: str = STATUS_STALE,
    age: float = 600,
    cadence: int = 60,
) -> SourceSnapshot:
    return SourceSnapshot(
        source_id=source_id,
        name=source_id,
        kind=kind,
        expected_cadence_seconds=cadence,
        last_seen_at=datetime.now(UTC) - timedelta(seconds=age),
        status=status,
        age_seconds=age,
        stale=(status == STATUS_STALE),
    )


def test_emit_alerts_for_stale_news() -> None:
    now = datetime(2026, 9, 10, 12, 0, tzinfo=UTC)  # Wednesday
    alerts = emit_alerts([_snap("finnhub.news")], now=now)
    assert len(alerts) == 1
    assert alerts[0].source_id == "finnhub.news"


def test_emit_alerts_suppresses_weekend_price() -> None:
    now = datetime(2026, 9, 12, 12, 0, tzinfo=UTC)  # Saturday
    alerts = emit_alerts(
        [_snap("mt5.prices", kind="price", age=3600)],
        now=now,
    )
    assert alerts == []


def test_kill_feed_drill_passes() -> None:
    session = get_session_factory()()
    try:
        result = run_kill_feed_drill(session, source_id="finnhub.news")
        assert result.passed
        assert any(a.source_id == "finnhub.news" for a in result.report.alerts)
    finally:
        session.close()


def test_run_check_smoke() -> None:
    session = get_session_factory()()
    try:
        record_heartbeat(session, "mt5.prices")
        report = run_check(session)
        assert len(report.sources) >= 4
        mt5 = next(s for s in report.sources if s.source_id == "mt5.prices")
        assert mt5.status == STATUS_OK
    finally:
        session.close()
