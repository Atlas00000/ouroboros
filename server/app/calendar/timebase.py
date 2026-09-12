"""UTC + MT5 server clock conversions."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone

from zoneinfo import ZoneInfo


def ensure_utc(dt: datetime) -> datetime:
    """Normalize any datetime to timezone-aware UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def mt5_server_tz(offset_hours: float) -> timezone:
    """Fixed-offset tz for MT5 server clock (offset from UTC, e.g. +2 or +3)."""
    return timezone(timedelta(hours=offset_hours))


def mt5_to_utc(dt: datetime, *, offset_hours: float) -> datetime:
    """Convert a naive/aware MT5 server-time bar timestamp to UTC."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=mt5_server_tz(offset_hours))
    return dt.astimezone(UTC)


def utc_to_mt5(dt: datetime, *, offset_hours: float) -> datetime:
    """Convert UTC (or any) datetime to MT5 server local time."""
    return ensure_utc(dt).astimezone(mt5_server_tz(offset_hours))


def infer_mt5_offset_hours(as_of: datetime | None = None) -> float:
    """
    Infer common FX broker MT5 offset (EET/EEST style): UTC+2 winter, UTC+3 summer.

    Many brokers follow Europe/Bucharest-like DST. Override with
    MT5_SERVER_UTC_OFFSET_HOURS when the broker differs.
    """
    moment = ensure_utc(as_of or datetime.now(UTC))
    local = moment.astimezone(ZoneInfo("Europe/Bucharest"))
    offset = local.utcoffset()
    return offset.total_seconds() / 3600.0 if offset else 2.0
