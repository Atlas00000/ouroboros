"""Trading calendar unit tests."""

from __future__ import annotations

from datetime import UTC, datetime

from app.calendar import (
    SessionName,
    active_sessions,
    ensure_utc,
    infer_mt5_offset_hours,
    is_fx_weekend_closed,
    mt5_to_utc,
    trading_day_utc,
)


def test_ensure_utc_naive_assumes_utc() -> None:
    dt = datetime(2026, 6, 15, 12, 0, 0)
    assert ensure_utc(dt).tzinfo == UTC


def test_mt5_to_utc_plus_two() -> None:
    # Server 14:00 with +2 offset → 12:00 UTC
    local = datetime(2026, 1, 15, 14, 0, 0)
    utc = mt5_to_utc(local, offset_hours=2.0)
    assert utc == datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC)


def test_fx_weekend_closed() -> None:
    friday_open = datetime(2026, 9, 11, 12, 0, tzinfo=UTC)  # Friday noon
    friday_closed = datetime(2026, 9, 11, 22, 30, tzinfo=UTC)
    saturday = datetime(2026, 9, 12, 10, 0, tzinfo=UTC)
    sunday_open = datetime(2026, 9, 13, 22, 30, tzinfo=UTC)
    assert is_fx_weekend_closed(friday_open) is False
    assert is_fx_weekend_closed(friday_closed) is True
    assert is_fx_weekend_closed(saturday) is True
    assert is_fx_weekend_closed(sunday_open) is False


def test_trading_day_rolls_after_22_utc() -> None:
    before = datetime(2026, 9, 11, 21, 0, tzinfo=UTC)
    after = datetime(2026, 9, 11, 22, 30, tzinfo=UTC)
    assert trading_day_utc(before).isoformat() == "2026-09-11"
    assert trading_day_utc(after).isoformat() == "2026-09-12"


def test_active_sessions_london_window() -> None:
    # 10:00 UTC in winter ≈ 10:00 London
    dt = datetime(2026, 1, 15, 10, 0, tzinfo=UTC)
    sessions = active_sessions(dt)
    assert SessionName.LONDON in sessions


def test_infer_offset_summer_or_winter() -> None:
    winter = infer_mt5_offset_hours(datetime(2026, 1, 15, tzinfo=UTC))
    summer = infer_mt5_offset_hours(datetime(2026, 7, 15, tzinfo=UTC))
    assert winter in (2.0, 3.0)
    assert summer in (2.0, 3.0)
    assert summer >= winter
