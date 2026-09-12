"""Unit tests for regime flip-rate backtest / tuning (W4·D4)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pandas as pd

from app.analytics.backtest import (
    FLIP_BUDGET_H1_PER_DAY,
    count_flips,
    measure_flip_rate,
    tune_regime_params,
)
from app.analytics.regimes import RegimeParams


def test_count_flips() -> None:
    assert count_flips(["ranging", "ranging", "trending_up", "trending_up", "ranging"]) == 2
    assert count_flips([None, "ranging", None, "ranging"]) == 0


def _ohlcv(n: int, *, drift: float = 0.0, noise_amp: float = 0.0) -> pd.DataFrame:
    start = datetime(2025, 1, 1, tzinfo=UTC)
    rows = []
    px = 1.0
    for i in range(n):
        shock = noise_amp * (1.0 if i % 2 == 0 else -1.0)
        c = px + drift + shock
        rows.append(
            {
                "ts": start + timedelta(hours=i),
                "open": px,
                "high": max(px, c) + 0.0001,
                "low": min(px, c) - 0.0001,
                "close": c,
                "volume": 1.0,
            }
        )
        px = c
    return pd.DataFrame(rows)


def test_measure_flip_rate_steady_trend_low_flips() -> None:
    df = _ohlcv(800, drift=0.00015)
    r = measure_flip_rate(
        df,
        symbol="EURUSD",
        timeframe="H1",
        params=RegimeParams(vol_high=80, er_abs=0.3, persistence_n=3),
        warmup_days=30,
    )
    assert r.bars_scored > 0
    assert r.flips_per_day < FLIP_BUDGET_H1_PER_DAY


def test_tune_prefers_feasible_params() -> None:
    # Mild trend + mild noise — should find a feasible grid point
    h1 = {f"S{i}": _ohlcv(600, drift=0.0001, noise_amp=0.00005) for i in range(3)}
    d1_rows = []
    start = datetime(2024, 1, 1, tzinfo=UTC)
    px = 1.0
    for i in range(400):
        c = px + 0.001
        d1_rows.append(
            {
                "ts": start + timedelta(days=i),
                "open": px,
                "high": c + 0.0005,
                "low": px - 0.0005,
                "close": c,
                "volume": 1.0,
            }
        )
        px = c
    d1_df = pd.DataFrame(d1_rows)
    d1 = {f"S{i}": d1_df.copy() for i in range(3)}

    best = tune_regime_params(
        h1,
        d1,
        er_grid=(0.3, 0.4),
        vol_grid=(80.0,),
        persistence_grid=(3, 5),
    )
    assert best.score < 2.0 or best.h1_within or best.d1_within
