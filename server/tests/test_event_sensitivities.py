"""Unit tests for event sensitivity classification / ATR windows."""

from __future__ import annotations

from app.analytics.event_sensitivities import classify_event_type, event_types_for_symbol


def test_classify_event_type_nfp_cpi_fomc() -> None:
    assert classify_event_type("US Non-Farm Payrolls") == "NFP"
    assert classify_event_type("US CPI YoY") == "CPI"
    assert classify_event_type("FOMC Rate Decision") == "FOMC"
    assert classify_event_type("ECB Interest Rate Decision") == "central_bank"


def test_event_types_for_eurusd() -> None:
    types = event_types_for_symbol("EURUSD")
    assert "NFP" in types
    assert "FOMC" in types
