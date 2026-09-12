"""Unit tests for W4·D2 — ER, liquidity proxies, correlations, depth gate."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import numpy as np
import pandas as pd
import pytest

from app.analytics.correlations import compute_correlation_matrix
from app.analytics.metrics import (
    LIQUIDITY_NOTE,
    compute_metric_snapshot,
    kaufman_efficiency_ratio,
)
from app.analytics.universe import (
    filter_corr_eligible,
    m1_span_days,
    passes_depth_gate,
)


def _ohlcv(
    start: datetime,
    n: int,
    *,
    start_price: float = 1.1,
    drift: float = 0.0001,
    noise: float = 0.00005,
) -> pd.DataFrame:
    rows = []
    px = start_price
    rng = np.random.default_rng(42)
    for i in range(n):
        ts = start + timedelta(hours=i)
        shock = float(rng.normal(0, noise))
        o = px
        c = px + drift + shock
        h = max(o, c) + abs(shock)
        low = min(o, c) - abs(shock)
        rows.append({"ts": ts, "open": o, "high": h, "low": low, "close": c, "volume": 1.0})
        px = c
    return pd.DataFrame(rows)


def test_kaufman_er_trending_up_near_one() -> None:
    # Pure uptrend: path == net → |ER| ≈ 1, sign +.
    close = pd.Series([1.0 + 0.01 * i for i in range(30)])
    er = kaufman_efficiency_ratio(close, period=20)
    assert er.iloc[-1] == pytest.approx(1.0, abs=1e-9)


def test_kaufman_er_noisy_lower_than_trend() -> None:
    trend = pd.Series([1.0 + 0.01 * i for i in range(40)])
    noisy = trend + pd.Series([0.05 if i % 2 else -0.05 for i in range(40)])
    er_trend = float(kaufman_efficiency_ratio(trend, 20).iloc[-1])
    er_noisy = float(kaufman_efficiency_ratio(noisy, 20).iloc[-1])
    assert abs(er_trend) > abs(er_noisy)


def test_metric_snapshot_includes_er_and_liquidity() -> None:
    df = _ohlcv(datetime(2026, 8, 1, tzinfo=UTC), 80)
    snap = compute_metric_snapshot(df, symbol="EURUSD", timeframe="H1")
    assert snap.efficiency_ratio_20 is not None
    assert -1.0 <= snap.efficiency_ratio_20 <= 1.0
    assert snap.range_mean_20 is not None and snap.range_mean_20 > 0
    assert snap.typical_spread is None
    assert snap.liquidity_note == LIQUIDITY_NOTE
    assert 0.0 <= (snap.range_percentile_30d or 0.0) <= 100.0


def test_usdchf_depth_gate() -> None:
    assert passes_depth_gate("EURUSD", m1_span_days_value=1.0) is True
    assert passes_depth_gate("USDCHF", m1_span_days_value=10.0) is False
    assert passes_depth_gate("USDCHF", m1_span_days_value=90.0) is True


def test_m1_span_days() -> None:
    ts = pd.Series(
        [
            datetime(2026, 1, 1, tzinfo=UTC),
            datetime(2026, 4, 1, tzinfo=UTC),
        ]
    )
    assert m1_span_days(ts) == pytest.approx(90.0, abs=0.1)


def test_filter_corr_eligible_excludes_thin_usdchf() -> None:
    eligible, excluded = filter_corr_eligible(
        ["EURUSD", "USDCHF", "GBPUSD"],
        m1_span_by_symbol={"EURUSD": 400.0, "USDCHF": 1.0, "GBPUSD": 400.0},
    )
    assert eligible == ["EURUSD", "GBPUSD"]
    assert excluded == ["USDCHF"]


def test_correlation_matrix_excludes_usdchf_and_has_pair() -> None:
    start = datetime(2026, 8, 1, tzinfo=UTC)
    eurusd = _ohlcv(start, 40 * 24, start_price=1.10, drift=0.00005)
    gbpusd = _ohlcv(start, 40 * 24, start_price=1.25, drift=0.00004)
    # Correlated noise: reuse EUR path scaled
    usdjpy = eurusd.copy()
    usdjpy["close"] = 150 + (eurusd["close"] - 1.10) * 50
    usdjpy["open"] = usdjpy["close"]
    usdjpy["high"] = usdjpy["close"] + 0.01
    usdjpy["low"] = usdjpy["close"] - 0.01
    usdchf = _ohlcv(start, 40 * 24, start_price=0.90, drift=0.00002)

    result = compute_correlation_matrix(
        {
            "EURUSD": eurusd,
            "GBPUSD": gbpusd,
            "USDJPY": usdjpy,
            "USDCHF": usdchf,
        },
        m1_span_by_symbol={
            "EURUSD": 400.0,
            "GBPUSD": 400.0,
            "USDJPY": 400.0,
            "USDCHF": 1.0,
        },
    )
    assert "USDCHF" in result.excluded
    assert "USDCHF" not in result.symbols
    assert len(result.entries) >= 1
    assert all(e.symbol_a != "USDCHF" and e.symbol_b != "USDCHF" for e in result.entries)
    assert all(-1.0 <= e.coefficient <= 1.0 for e in result.entries)
