"""Economic calendar poll cycle."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx
from sqlalchemy import select

from app.config import Settings, get_settings
from app.db.session import get_session_factory
from app.ingestion.econ_calendar.client import FinnhubCalendarClient, RawCalendarEvent
from app.ingestion.econ_calendar.ff_client import ForexFactoryCalendarClient
from app.ingestion.econ_calendar.impact import flag_event
from app.ingestion.econ_calendar.writer import upsert_calendar_events
from app.ingestion.registry import mark_error, record_heartbeat
from app.models.asset import Asset

logger = logging.getLogger(__name__)

SOURCE_ID = "finnhub.calendar"


@dataclass(frozen=True)
class CalendarPollResult:
    fetched: int
    high_impact: int
    rows_written: int
    provider: str


def _fetch_events(
    settings: Settings,
    *,
    days_back: int,
    days_forward: int,
) -> tuple[list[RawCalendarEvent], str]:
    """Prefer Finnhub; fall back to Forex Factory JSON on 401/403 (free-tier lock)."""
    try:
        events = FinnhubCalendarClient(settings).fetch_upcoming(
            days_back=days_back,
            days_forward=days_forward,
        )
        return events, "finnhub"
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code not in (401, 403):
            raise
        logger.warning(
            "finnhub calendar HTTP %s — falling back to Forex Factory weekly JSON",
            exc.response.status_code,
        )
        events = ForexFactoryCalendarClient().fetch_this_week()
        return events, "forexfactory"


def poll_once(
    *,
    settings: Settings | None = None,
    days_back: int = 1,
    days_forward: int = 7,
) -> CalendarPollResult:
    cfg = settings or get_settings()
    session = get_session_factory()()
    try:
        try:
            events, provider = _fetch_events(
                cfg, days_back=days_back, days_forward=days_forward
            )
        except Exception:
            logger.exception("calendar fetch failed")
            mark_error(session, SOURCE_ID)
            raise

        active = set(session.scalars(select(Asset.symbol).where(Asset.is_active.is_(True))).all())
        flagged = [flag_event(e, active_symbols=active) for e in events]
        written = upsert_calendar_events(session, flagged)
        record_heartbeat(session, SOURCE_ID)

        high = sum(1 for f in flagged if f.high_impact)
        result = CalendarPollResult(
            fetched=len(events),
            high_impact=high,
            rows_written=written,
            provider=provider,
        )
        logger.info(
            "calendar poll done provider=%s fetched=%s high_impact=%s written=%s",
            result.provider,
            result.fetched,
            result.high_impact,
            result.rows_written,
        )
        return result
    finally:
        session.close()
