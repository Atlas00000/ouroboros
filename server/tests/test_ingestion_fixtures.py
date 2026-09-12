"""Integration tests against recorded provider fixtures (no live network)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import httpx

from app.config import Settings
from app.ingestion.econ_calendar.client import FinnhubCalendarClient
from app.ingestion.econ_calendar.ff_client import ForexFactoryCalendarClient
from app.ingestion.econ_calendar.impact import flag_event
from app.ingestion.macro.client import FredClient
from app.ingestion.news.client import FinnhubNewsClient
from app.ingestion.news.mapping import NewsAssetMapper

FIXTURES = Path(__file__).parent / "fixtures" / "ingestion"


def _load(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


def _settings() -> Settings:
    return Settings(
        NEWS_API_KEY="test-finnhub-key",
        FRED_API_KEY="test-fred-key",
    )


def _transport_for(mapping: dict[str, bytes]) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        for needle, body in mapping.items():
            if needle in path or needle in str(request.url):
                return httpx.Response(200, content=body, request=request)
        return httpx.Response(404, json={"error": f"no fixture for {request.url}"}, request=request)

    return httpx.MockTransport(handler)


def test_finnhub_news_fixture_parse_and_map() -> None:
    body = _load("finnhub_news_forex.json")
    transport = _transport_for({"/api/v1/news": body})
    client = FinnhubNewsClient(settings=_settings(), transport=transport)
    articles = client.fetch_category("forex")
    assert len(articles) == 2
    assert articles[0].provider_id == "9001001"

    mapper = NewsAssetMapper({"EURUSD", "XAUUSD", "GBPUSD"})
    mapped = mapper.map_many(articles)
    symbols = {s for m in mapped for s in m.symbols}
    assert "EURUSD" in symbols
    assert "XAUUSD" in symbols


def test_finnhub_calendar_fixture_high_impact() -> None:
    body = _load("finnhub_calendar.json")
    transport = _transport_for({"/api/v1/calendar/economic": body})
    client = FinnhubCalendarClient(settings=_settings(), transport=transport)
    events = client.fetch_range(date(2026, 9, 11), date(2026, 9, 12))
    assert len(events) == 2
    flagged = [flag_event(e, active_symbols={"EURUSD", "GBPUSD", "XAUUSD"}) for e in events]
    assert any(f.high_impact and "Non-Farm" in f.event.event for f in flagged)
    assert any(f.high_impact and "BoE" in f.event.event for f in flagged)


def test_ff_calendar_fixture() -> None:
    body = _load("ff_calendar_thisweek.json")
    transport = _transport_for({"ff_calendar_thisweek.json": body})
    events = ForexFactoryCalendarClient(transport=transport).fetch_this_week()
    assert len(events) == 2
    assert events[0].country == "US"
    assert events[1].country == "EU"
    assert flag_event(events[0]).high_impact is True


def test_fred_fixture_skips_missing_values() -> None:
    body = _load("fred_dff_observations.json")
    transport = _transport_for({"/fred/series/observations": body})
    points = FredClient(settings=_settings(), transport=transport).fetch_series("DFF")
    assert len(points) == 3
    assert points[0].value is not None
    assert points[-1].value is None  # "." sentinel
    assert json.loads(body.decode())["observations"][0]["date"] == "2026-09-10"
