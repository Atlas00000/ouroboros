"""FX session windows and trading-day helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from enum import Enum

from zoneinfo import ZoneInfo

from app.calendar.timebase import ensure_utc


class SessionName(str, Enum):
    SYDNEY = "sydney"
    TOKYO = "tokyo"
    LONDON = "london"
    NEW_YORK = "new_york"


@dataclass(frozen=True)
class SessionWindow:
    """Local-wall-clock session bounds (inclusive start, exclusive end)."""

    name: SessionName
    tz: str
    open_hour: int
    open_minute: int
    close_hour: int
    close_minute: int


DEFAULT_SESSIONS: tuple[SessionWindow, ...] = (
    SessionWindow(SessionName.SYDNEY, "Australia/Sydney", 7, 0, 16, 0),
    SessionWindow(SessionName.TOKYO, "Asia/Tokyo", 9, 0, 18, 0),
    SessionWindow(SessionName.LONDON, "Europe/London", 8, 0, 16, 30),
    SessionWindow(SessionName.NEW_YORK, "America/New_York", 8, 0, 17, 0),
)


def is_fx_weekend_closed(dt: datetime) -> bool:
    """FX approx closed Fri 22:00 UTC → Sun 22:00 UTC."""
    utc = ensure_utc(dt)
    weekday = utc.weekday()  # Mon=0 ... Sun=6
    if weekday == 5:
        return True
    if weekday == 6:
        return utc.hour < 22
    if weekday == 4:
        return utc.hour >= 22
    return False


def active_sessions(
    dt: datetime,
    sessions: tuple[SessionWindow, ...] = DEFAULT_SESSIONS,
) -> list[SessionName]:
    """Return which named sessions are open at the given UTC instant."""
    utc = ensure_utc(dt)
    open_sessions: list[SessionName] = []
    for session in sessions:
        local = utc.astimezone(ZoneInfo(session.tz))
        start = local.replace(
            hour=session.open_hour,
            minute=session.open_minute,
            second=0,
            microsecond=0,
        )
        end = local.replace(
            hour=session.close_hour,
            minute=session.close_minute,
            second=0,
            microsecond=0,
        )
        if start <= local < end:
            open_sessions.append(session.name)
    return open_sessions


def trading_day_utc(dt: datetime) -> date:
    """FX trading day: after 22:00 UTC rolls to the next calendar date."""
    utc = ensure_utc(dt)
    if utc.hour >= 22:
        return (utc + timedelta(days=1)).date()
    return utc.date()
