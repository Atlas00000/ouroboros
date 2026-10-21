"""Economic calendar impact + FRED writer tests."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import text

from app.db.session import get_session_factory
from app.ingestion.econ_calendar.client import RawCalendarEvent
from app.ingestion.econ_calendar.impact import flag_event, normalize_impact
from app.ingestion.econ_calendar.writer import upsert_calendar_events
from app.ingestion.macro.client import RawMacroPoint
from app.ingestion.macro.writer import upsert_macro_points


def test_normalize_impact_and_high_events() -> None:
    assert normalize_impact("medium", "Retail Sales") == "medium"
    assert normalize_impact("low", "Non-Farm Payrolls") == "high"
    assert normalize_impact(None, "FOMC Rate Decision") == "high"
    assert normalize_impact("3", "Something") == "high"


def test_flag_event_country_map() -> None:
    ev = RawCalendarEvent(
        provider="finnhub",
        provider_id="abc",
        country="US",
        event="CPI",
        impact_raw="high",
        scheduled_at=datetime(2026, 9, 12, tzinfo=UTC),
        actual=None,
        estimate=None,
        previous=None,
        unit="%",
        raw={},
    )
    flagged = flag_event(ev, active_symbols={"EURUSD", "XAUUSD", "GBPUSD", "AAPL"})
    assert flagged.high_impact is True
    assert flagged.impact == "high"
    assert "EURUSD" in flagged.symbols
    assert "XAUUSD" in flagged.symbols
    # Equities must not auto-attach to every US macro print
    assert "AAPL" not in flagged.symbols


def test_flag_event_regional_indices() -> None:
    de = RawCalendarEvent(
        provider="finnhub",
        provider_id="de1",
        country="DE",
        event="GDP",
        impact_raw="high",
        scheduled_at=datetime(2026, 9, 12, tzinfo=UTC),
        actual=None,
        estimate=None,
        previous=None,
        unit="%",
        raw={},
    )
    flagged = flag_event(de, active_symbols={"EURUSD", "DE40", "UK100", "JP225"})
    assert "DE40" in flagged.symbols
    assert "UK100" not in flagged.symbols

    jp = RawCalendarEvent(
        provider="finnhub",
        provider_id="jp1",
        country="JP",
        event="BoJ Interest Rate Decision",
        impact_raw="medium",
        scheduled_at=datetime(2026, 9, 12, tzinfo=UTC),
        actual=None,
        estimate=None,
        previous=None,
        unit="%",
        raw={},
    )
    flagged_jp = flag_event(jp, active_symbols={"USDJPY", "JP225"})
    assert "JP225" in flagged_jp.symbols
    assert flagged_jp.high_impact is True


def test_calendar_and_macro_upsert() -> None:
    session = get_session_factory()()
    try:
        ev = RawCalendarEvent(
            provider="finnhub",
            provider_id="w3d2testcal001",
            country="GB",
            event="BoE Interest Rate Decision",
            impact_raw="medium",
            scheduled_at=datetime(2026, 9, 15, 11, 0, tzinfo=UTC),
            actual=None,
            estimate="4.00",
            previous="4.25",
            unit="%",
            raw={},
        )
        flagged = flag_event(ev, active_symbols={"GBPUSD", "EURGBP"})
        assert flagged.high_impact is True  # BoE keyword

        session.execute(
            text("DELETE FROM news WHERE external_id LIKE :p"),
            {"p": "finnhub.cal:w3d2testcal001%"},
        )
        session.commit()
        n = upsert_calendar_events(session, [flagged])
        assert n >= 1

        session.execute(
            text("DELETE FROM macro_observations WHERE series_id = 'TESTDFF'")
        )
        session.commit()
        points = [
            RawMacroPoint("TESTDFF", date(2026, 1, 1), Decimal("5.25")),
            RawMacroPoint("TESTDFF", date(2026, 1, 2), Decimal("5.33")),
        ]
        m = upsert_macro_points(session, points)
        assert m == 2
        m2 = upsert_macro_points(session, points)
        assert m2 == 0
    finally:
        session.execute(
            text("DELETE FROM news WHERE external_id LIKE :p"),
            {"p": "finnhub.cal:w3d2testcal001%"},
        )
        session.execute(text("DELETE FROM macro_observations WHERE series_id = 'TESTDFF'"))
        session.commit()
        session.close()
