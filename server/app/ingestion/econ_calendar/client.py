"""Finnhub economic calendar API client."""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Any

import httpx

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

FINNHUB_CALENDAR_URL = "https://finnhub.io/api/v1/calendar/economic"


@dataclass(frozen=True)
class RawCalendarEvent:
    provider: str
    provider_id: str
    country: str
    event: str
    impact_raw: str | None
    scheduled_at: datetime | None
    actual: str | None
    estimate: str | None
    previous: str | None
    unit: str | None
    raw: dict[str, Any]


class FinnhubCalendarClient:
    def __init__(self, settings: Settings | None = None, *, timeout: float = 30.0) -> None:
        self._settings = settings or get_settings()
        self._timeout = timeout

    @property
    def api_key(self) -> str:
        key = self._settings.news_api_key
        if not key:
            raise RuntimeError("NEWS_API_KEY is not set")
        return key

    def fetch_range(self, start: date, end: date) -> list[RawCalendarEvent]:
        params = {
            "from": start.isoformat(),
            "to": end.isoformat(),
        }
        headers = {"X-Finnhub-Token": self.api_key}
        with httpx.Client(timeout=self._timeout) as client:
            resp = client.get(FINNHUB_CALENDAR_URL, params=params, headers=headers)
            resp.raise_for_status()
            payload = resp.json()

        items = payload.get("economicCalendar", payload) if isinstance(payload, dict) else payload
        if not isinstance(items, list):
            raise RuntimeError(f"unexpected calendar payload: {type(payload)}")

        events: list[RawCalendarEvent] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            parsed = self._parse(item)
            if parsed is not None:
                events.append(parsed)

        logger.info(
            "finnhub calendar fetched from=%s to=%s count=%s",
            start,
            end,
            len(events),
        )
        return events

    def fetch_upcoming(self, *, days_back: int = 1, days_forward: int = 7) -> list[RawCalendarEvent]:
        today = datetime.now(UTC).date()
        return self.fetch_range(today - timedelta(days=days_back), today + timedelta(days=days_forward))

    @staticmethod
    def _parse(item: dict[str, Any]) -> RawCalendarEvent | None:
        event = (item.get("event") or "").strip()
        country = (item.get("country") or "").strip().upper()
        if not event or not country:
            return None

        scheduled: datetime | None = None
        time_raw = item.get("time")
        if isinstance(time_raw, str) and time_raw:
            # Finnhub uses "YYYY-MM-DD HH:MM:SS" (often UTC or local-naive).
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    scheduled = datetime.strptime(time_raw, fmt).replace(tzinfo=UTC)
                    break
                except ValueError:
                    continue

        key = f"{country}|{event}|{time_raw or ''}"
        provider_id = hashlib.sha1(key.encode("utf-8")).hexdigest()[:24]

        impact = item.get("impact")
        return RawCalendarEvent(
            provider="finnhub",
            provider_id=provider_id,
            country=country,
            event=event,
            impact_raw=str(impact).strip().lower() if impact else None,
            scheduled_at=scheduled,
            actual=_str_or_none(item.get("actual")),
            estimate=_str_or_none(item.get("estimate")),
            previous=_str_or_none(item.get("prev") or item.get("previous")),
            unit=_str_or_none(item.get("unit")),
            raw=item,
        )


def _str_or_none(value: object) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    return s or None
