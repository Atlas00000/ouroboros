"""FRED series observations client."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx

from app.config import Settings, get_settings
from app.ingestion.httputil import FRED_LIMITER, get_json

logger = logging.getLogger(__name__)

FRED_OBS_URL = "https://api.stlouisfed.org/fred/series/observations"


@dataclass(frozen=True)
class RawMacroPoint:
    series_id: str
    obs_date: date
    value: Decimal | None


class FredClient:
    def __init__(
        self,
        settings: Settings | None = None,
        *,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._timeout = timeout
        self._transport = transport

    @property
    def api_key(self) -> str:
        key = self._settings.fred_api_key
        if not key:
            raise RuntimeError("FRED_API_KEY is not set")
        return key

    def fetch_series(
        self,
        series_id: str,
        *,
        observation_start: date | None = None,
        limit: int | None = None,
    ) -> list[RawMacroPoint]:
        params: dict[str, Any] = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "sort_order": "asc",
        }
        if observation_start is not None:
            params["observation_start"] = observation_start.isoformat()
        if limit is not None:
            params["limit"] = limit

        payload = get_json(
            FRED_OBS_URL,
            timeout=self._timeout,
            params=params,
            rate_limiter=FRED_LIMITER,
            transport=self._transport,
        )

        observations = payload.get("observations") if isinstance(payload, dict) else None
        if not isinstance(observations, list):
            raise RuntimeError(f"unexpected FRED payload for {series_id}")

        points: list[RawMacroPoint] = []
        for item in observations:
            if not isinstance(item, dict):
                continue
            d_raw = item.get("date")
            v_raw = item.get("value")
            if not d_raw:
                continue
            try:
                obs_date = date.fromisoformat(str(d_raw))
            except ValueError:
                continue
            value: Decimal | None
            if v_raw in (None, ".", ""):
                value = None
            else:
                try:
                    value = Decimal(str(v_raw))
                except (InvalidOperation, ValueError):
                    value = None
            points.append(RawMacroPoint(series_id=series_id.upper(), obs_date=obs_date, value=value))

        logger.info("fred fetched series=%s points=%s", series_id, len(points))
        return points
