"""Forex Factory weekly calendar fallback (free JSON feed)."""

from __future__ import annotations

import hashlib
import logging
from datetime import UTC, datetime
from typing import Any

import httpx

from app.ingestion.econ_calendar.client import RawCalendarEvent
from app.ingestion.httputil import FF_LIMITER, get_json

logger = logging.getLogger(__name__)

# Unofficial but widely used public FF calendar JSON (this-week window).
FF_CALENDAR_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

# FF uses currency codes as "country".
_CURRENCY_TO_COUNTRY = {
    "USD": "US",
    "EUR": "EU",
    "GBP": "GB",
    "JPY": "JP",
    "CHF": "CH",
    "AUD": "AU",
    "CAD": "CA",
    "NZD": "NZ",
    "CNY": "CN",
}


class ForexFactoryCalendarClient:
    """Best-effort free calendar when Finnhub economic calendar is plan-locked."""

    def __init__(
        self,
        *,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._timeout = timeout
        self._transport = transport

    def fetch_this_week(self) -> list[RawCalendarEvent]:
        payload = get_json(
            FF_CALENDAR_URL,
            timeout=self._timeout,
            rate_limiter=FF_LIMITER,
            transport=self._transport,
        )

        if not isinstance(payload, list):
            raise RuntimeError(f"unexpected FF calendar payload: {type(payload)}")

        events: list[RawCalendarEvent] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            parsed = self._parse(item)
            if parsed is not None:
                events.append(parsed)

        logger.info("forexfactory calendar fetched count=%s", len(events))
        return events

    @staticmethod
    def _parse(item: dict[str, Any]) -> RawCalendarEvent | None:
        title = (item.get("title") or "").strip()
        currency = (item.get("country") or "").strip().upper()
        if not title or not currency:
            return None

        country = _CURRENCY_TO_COUNTRY.get(currency, currency[:2])
        date_raw = item.get("date")
        scheduled: datetime | None = None
        if isinstance(date_raw, str) and date_raw:
            try:
                scheduled = datetime.fromisoformat(date_raw.replace("Z", "+00:00"))
                if scheduled.tzinfo is None:
                    scheduled = scheduled.replace(tzinfo=UTC)
                else:
                    scheduled = scheduled.astimezone(UTC)
            except ValueError:
                scheduled = None

        key = f"ff|{country}|{title}|{date_raw or ''}"
        provider_id = hashlib.sha1(key.encode("utf-8")).hexdigest()[:24]
        impact = item.get("impact")
        return RawCalendarEvent(
            provider="forexfactory",
            provider_id=provider_id,
            country=country,
            event=title,
            impact_raw=str(impact).strip().lower() if impact else None,
            scheduled_at=scheduled,
            actual=_s(item.get("actual")),
            estimate=_s(item.get("forecast")),
            previous=_s(item.get("previous")),
            unit=None,
            raw=item,
        )


def _s(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
