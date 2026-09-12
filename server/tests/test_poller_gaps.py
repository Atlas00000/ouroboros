"""Unit tests for live poller gap detection (no MT5 required)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.ingestion.mt5.poller import closed_bar_exclusive_end, detect_gap, floor_minute


def test_floor_minute() -> None:
    dt = datetime(2026, 9, 12, 10, 15, 42, 123456, tzinfo=UTC)
    assert floor_minute(dt) == datetime(2026, 9, 12, 10, 15, tzinfo=UTC)


def test_closed_bar_exclusive_end() -> None:
    now = datetime(2026, 9, 12, 10, 15, 42, tzinfo=UTC)
    assert closed_bar_exclusive_end(now) == datetime(2026, 9, 12, 10, 15, tzinfo=UTC)


def test_detect_gap_none_when_fresh() -> None:
    last = datetime(2026, 9, 10, 12, 0, tzinfo=UTC)  # Wednesday
    end = last + timedelta(minutes=2)
    assert detect_gap(symbol="EURUSD", last_ts=last, end_exclusive=end) is None


def test_detect_gap_when_stale_weekday() -> None:
    last = datetime(2026, 9, 10, 12, 0, tzinfo=UTC)  # Wednesday
    end = last + timedelta(minutes=10)
    gap = detect_gap(symbol="EURUSD", last_ts=last, end_exclusive=end)
    assert gap is not None
    assert gap.symbol == "EURUSD"
    assert gap.from_ts == last + timedelta(minutes=1)
    assert gap.to_ts == end
    assert gap.missing_minutes == 9


def test_detect_gap_ignores_weekend() -> None:
    # Friday 21:00 → Sunday 23:00 hole should not count (FX weekend).
    last = datetime(2026, 9, 11, 21, 0, tzinfo=UTC)  # Friday
    end = datetime(2026, 9, 13, 23, 0, tzinfo=UTC)  # Sunday after reopen window mid
    # Midpoint falls in Saturday → weekend closed → no gap.
    gap = detect_gap(symbol="EURUSD", last_ts=last, end_exclusive=end)
    assert gap is None


def test_detect_gap_none_without_history() -> None:
    end = datetime(2026, 9, 10, 12, 0, tzinfo=UTC)
    assert detect_gap(symbol="EURUSD", last_ts=None, end_exclusive=end) is None
