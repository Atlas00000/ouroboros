"""Unit tests for AssetProfile builder (W5·D1)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pandas as pd

from app.analytics.profiles import (
    PROFILE_MODEL_VERSION,
    AssetIdentityInput,
    build_asset_profile,
)
from app.analytics.regimes import REGIME_LABELS
from contracts.profile_v1 import AssetProfile


def _d1(n: int = 120, *, drift: float = 0.001) -> pd.DataFrame:
    start = datetime(2025, 1, 1, tzinfo=UTC)
    rows = []
    px = 1.10
    for i in range(n):
        ts = start + timedelta(days=i)
        if ts.weekday() >= 5:
            continue
        c = px + drift
        rows.append(
            {
                "ts": ts,
                "open": px,
                "high": max(px, c) + 0.0005,
                "low": min(px, c) - 0.0005,
                "close": c,
                "volume": 1.0,
            }
        )
        px = c
    return pd.DataFrame(rows)


def _h1(n: int = 800, *, drift: float = 0.00005, start_price: float = 1.10) -> pd.DataFrame:
    start = datetime(2025, 6, 2, tzinfo=UTC)
    rows = []
    px = start_price
    for i in range(n):
        ts = start + timedelta(hours=i)
        if ts.weekday() >= 5:
            continue
        c = px + drift
        rows.append(
            {
                "ts": ts,
                "open": px,
                "high": max(px, c) + 0.0001,
                "low": min(px, c) - 0.0001,
                "close": c,
                "volume": 1.0,
            }
        )
        px = c
    return pd.DataFrame(rows)


def test_build_asset_profile_validates_contract() -> None:
    identity = AssetIdentityInput(
        symbol="EURUSD",
        display_name="Euro / US Dollar",
        asset_class="fx",
        mt5_ticker="EURUSD",
        base_currency="EUR",
        quote_currency="USD",
        venues=("YWO-Trade",),
    )
    eurusd_h1 = _h1(start_price=1.10)
    gbpusd_h1 = _h1(start_price=1.25, drift=0.00004)
    profile = build_asset_profile(
        identity,
        d1_ohlcv=_d1(),
        h1_ohlcv=eurusd_h1,
        peer_h1_ohlcv={"EURUSD": eurusd_h1, "GBPUSD": gbpusd_h1},
        m1_span_by_symbol={"EURUSD": 400.0, "GBPUSD": 400.0},
        profile_version=1,
    )
    # Round-trip through contract validator
    restored = AssetProfile.model_validate(profile.model_dump(mode="json"))
    assert restored.schema_id == "profile.v1"
    assert restored.identity.symbol == "EURUSD"
    assert restored.provenance.model_version == PROFILE_MODEL_VERSION
    assert "metrics.v1" in restored.provenance.sources
    assert restored.volatility.typical_daily_range is not None
    assert restored.liquidity.typical_spread is None
    assert {d.regime for d in restored.regime_distribution} == set(REGIME_LABELS)
    assert abs(sum(d.share for d in restored.regime_distribution) - 1.0) < 0.05
    assert any(c.symbol == "GBPUSD" for c in restored.correlations)


def test_usdchf_depth_gate_zeros_regime_shares() -> None:
    identity = AssetIdentityInput(
        symbol="USDCHF",
        display_name="USD/CHF",
        asset_class="fx",
    )
    profile = build_asset_profile(
        identity,
        d1_ohlcv=_d1(60),
        h1_ohlcv=_h1(200),
        m1_span_by_symbol={"USDCHF": 1.0},
    )
    assert all(d.share == 0.0 for d in profile.regime_distribution)
