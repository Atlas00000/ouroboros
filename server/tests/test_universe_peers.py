"""Class-aware peers, depth gates, and trading-hour defaults for expanded universe."""

from __future__ import annotations

import pandas as pd

from app.analytics.profiles import AssetIdentityInput, _trading_hours_default, build_asset_profile
from app.analytics.universe import (
    DEPTH_GATED_SYMBOLS,
    EQUITY_INDEX_ANCHORS,
    default_peer_symbols,
    passes_depth_gate,
)
from app.calendar.sessions import SessionName


class _ScalarResult:
    def __init__(self, values: list[str]) -> None:
        self._values = values

    def all(self) -> list[str]:
        return list(self._values)


class _OrderedSession:
    """Returns successive scalar result lists (same-class query, then all-active)."""

    def __init__(self, batches: list[list[str]]) -> None:
        self._batches = list(batches)
        self._i = 0

    def scalars(self, _stmt):  # noqa: ANN001
        if self._i >= len(self._batches):
            return _ScalarResult([])
        batch = self._batches[self._i]
        self._i += 1
        return _ScalarResult(batch)


def test_equity_depth_gated_until_history() -> None:
    assert "AAPL" in DEPTH_GATED_SYMBOLS
    assert "XTIUSD" in DEPTH_GATED_SYMBOLS
    assert "DE40" in DEPTH_GATED_SYMBOLS
    assert not passes_depth_gate("AAPL", m1_span_days_value=10.0)
    assert passes_depth_gate("AAPL", m1_span_days_value=90.0)
    assert passes_depth_gate("EURUSD", m1_span_days_value=1.0)


def test_trading_hours_equity_and_metal_index() -> None:
    eq = _trading_hours_default(asset_class="equity")
    assert eq.timezone == "America/New_York"
    assert SessionName.NEW_YORK.value in eq.sessions
    assert eq.open_utc is not None

    metal = _trading_hours_default(asset_class="metal")
    assert metal.open_utc is not None
    assert metal.notes

    idx = _trading_hours_default(asset_class="index")
    assert SessionName.LONDON.value in idx.sessions
    assert idx.notes


def test_equity_profile_uses_equity_sessions() -> None:
    identity = AssetIdentityInput(
        symbol="AAPL",
        display_name="Apple Inc.",
        asset_class="equity",
        quote_currency="USD",
    )
    profile = build_asset_profile(
        identity,
        d1_ohlcv=pd.DataFrame(),
        m1_span_by_symbol={"AAPL": 5.0},
    )
    assert profile.trading_hours.timezone == "America/New_York"
    assert all(d.share == 0.0 for d in profile.regime_distribution)


def test_default_peer_symbols_equity_includes_index_anchors() -> None:
    session = _OrderedSession(
        [
            ["MSFT", "NVDA", "AMZN"],
            ["AAPL", "MSFT", "NVDA", "AMZN", "US500", "NAS100", "EURUSD"],
        ]
    )
    peers = default_peer_symbols(session, "AAPL", asset_class="equity")
    assert "MSFT" in peers
    assert "NVDA" in peers
    assert "EURUSD" not in peers
    for anchor in EQUITY_INDEX_ANCHORS:
        assert anchor in peers


def test_default_peer_symbols_fx_stays_in_class() -> None:
    session = _OrderedSession([["GBPUSD", "USDJPY"]])
    peers = default_peer_symbols(session, "EURUSD", asset_class="fx")
    assert set(peers) == {"GBPUSD", "USDJPY"}
