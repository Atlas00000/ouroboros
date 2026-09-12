"""Unit tests for analytics metrics.v1 (W4·D1)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import numpy as np
import pandas as pd
import pytest

from app.analytics.metrics import (
    MODEL_VERSION,
    compute_metric_snapshot,
    gap_aware_log_returns,
    percentile_of_last,
    realized_vol,
    rolling_simple_return,
    wilder_atr,
)


def _m1_frame(
    start: datetime,
    n: int,
    *,
    start_price: float = 1.1000,
    step: float = 0.0001,
) -> pd.DataFrame:
    rows = []
    px = start_price
    for i in range(n):
        ts = start + timedelta(minutes=i)
        o = px
        h = px + step
        low = px - step
        c = px + step * 0.5
        rows.append({"ts": ts, "open": o, "high": h, "low": low, "close": c, "volume": 1.0})
        px = c
    return pd.DataFrame(rows)


def test_model_version_tag() -> None:
    assert MODEL_VERSION == "metrics.v1"


def test_gap_aware_nulls_weekend_jump() -> None:
    # Friday 21:00 then Sunday 22:30 — must not produce a synthetic return
    friday = datetime(2026, 9, 11, 21, 0, tzinfo=UTC)
    sunday = datetime(2026, 9, 13, 22, 30, tzinfo=UTC)
    ts = pd.Series([friday, sunday])
    close = pd.Series([1.10, 1.12])
    rets = gap_aware_log_returns(ts, close, "M1")
    assert np.isnan(rets.iloc[1])


def test_gap_aware_keeps_adjacent_m1() -> None:
    start = datetime(2026, 9, 10, 12, 0, tzinfo=UTC)
    ts = pd.Series([start, start + timedelta(minutes=1)])
    close = pd.Series([1.10, 1.101])
    rets = gap_aware_log_returns(ts, close, "M1")
    assert np.isfinite(rets.iloc[1])
    assert rets.iloc[1] == pytest.approx(np.log(1.101 / 1.10))


def test_wilder_atr_positive() -> None:
    df = _m1_frame(datetime(2026, 9, 8, 10, 0, tzinfo=UTC), 40)
    atr = wilder_atr(df["high"], df["low"], df["close"], period=14)
    assert atr.iloc[-1] > 0


def test_realized_vol_annualized() -> None:
    df = _m1_frame(datetime(2026, 9, 8, 10, 0, tzinfo=UTC), 80)
    rets = gap_aware_log_returns(df["ts"], df["close"], "M1")
    vol = realized_vol(rets, 20, "M1")
    assert np.isfinite(vol.iloc[-1])
    assert vol.iloc[-1] > 0


def test_realized_vol_tolerates_sparse_d1_weekend_nulls() -> None:
    """D1 FX series nulls ~1 return/week; vol20 must still resolve."""
    start = datetime(2025, 1, 6, tzinfo=UTC)  # Monday
    rows_ts = []
    closes = []
    px = 1.10
    for i in range(80):
        ts = start + timedelta(days=i)
        if ts.weekday() >= 5:
            continue
        rows_ts.append(ts)
        closes.append(px)
        px *= 1.0 + (0.001 if i % 3 else -0.0005)
    ts = pd.Series(rows_ts)
    close = pd.Series(closes)
    rets = gap_aware_log_returns(ts, close, "D1")
    vol = realized_vol(rets, 20, "D1")
    assert np.isfinite(vol.iloc[-1])


def test_percentile_of_last_bounds() -> None:
    s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    p = percentile_of_last(s, 5)
    assert p == pytest.approx(100.0)


def test_rolling_simple_return() -> None:
    close = pd.Series([100.0, 101.0, 102.0, 103.0])
    assert rolling_simple_return(close, 1) == pytest.approx(103 / 102 - 1)
    assert rolling_simple_return(close, 3) == pytest.approx(103 / 100 - 1)


def test_compute_metric_snapshot_smoke() -> None:
    df = _m1_frame(datetime(2026, 9, 1, 0, 0, tzinfo=UTC), 200)
    snap = compute_metric_snapshot(df, symbol="eurusd", timeframe="M1")
    assert snap.symbol == "EURUSD"
    assert snap.timeframe == "M1"
    assert snap.model_version == "metrics.v1"
    assert snap.realized_vol_20 is not None
    assert snap.atr_14 is not None
    assert snap.return_1 is not None
    assert 0.0 <= (snap.atr_percentile_30d or 0.0) <= 100.0


def test_d1_allows_friday_to_monday_gap() -> None:
    friday = datetime(2026, 9, 11, 21, 0, tzinfo=UTC)
    monday = datetime(2026, 9, 14, 21, 0, tzinfo=UTC)
    ts = pd.Series([friday, monday])
    close = pd.Series([1.10, 1.11])
    rets = gap_aware_log_returns(ts, close, "D1")
    # 3 calendar days < 4*1d budget → kept
    assert np.isfinite(rets.iloc[1])
