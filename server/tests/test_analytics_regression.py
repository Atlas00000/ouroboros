"""Regression fixtures pinning regimes.rule_v1 + metrics.v1 surface (W4·D5)."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd
import pytest

from app.analytics.metrics import (
    MODEL_VERSION as METRICS_MODEL_VERSION,
)
from app.analytics.metrics import (
    TIMEFRAMES,
    compute_metric_snapshot,
)
from app.analytics.regimes import (
    DEFAULT_PARAMS,
    PERSISTENCE_N,
    REGIME_LABELS,
    apply_persistence,
    classify_raw,
    soft_regime_probabilities,
)
from app.analytics.regimes import (
    MODEL_VERSION as REGIME_MODEL_VERSION,
)

FIXTURE = Path(__file__).parent / "fixtures" / "analytics" / "regime_rule_v1.json"


def _load_regime_fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_fixture_params_match_defaults() -> None:
    data = _load_regime_fixture()
    assert data["model_version"] == REGIME_MODEL_VERSION
    assert data["params"]["vol_high"] == DEFAULT_PARAMS.vol_high
    assert data["params"]["er_abs"] == DEFAULT_PARAMS.er_abs
    assert data["params"]["persistence_n"] == DEFAULT_PARAMS.persistence_n == PERSISTENCE_N


@pytest.mark.parametrize(
    "case",
    json.loads(FIXTURE.read_text(encoding="utf-8"))["grid_cases"],
    ids=lambda c: c["id"],
)
def test_grid_cases_pinned(case: dict) -> None:
    raw = classify_raw(case["vol_percentile"], case["efficiency_ratio"])
    assert raw == case["expected_raw"]


@pytest.mark.parametrize(
    "case",
    json.loads(FIXTURE.read_text(encoding="utf-8"))["persistence_cases"],
    ids=lambda c: c["id"],
)
def test_persistence_cases_pinned(case: dict) -> None:
    out = apply_persistence(
        case["raw"],
        n=PERSISTENCE_N,
        prior_confirmed=case["prior"],
    )
    assert out == case["expected_confirmed"]


@pytest.mark.parametrize(
    "case",
    json.loads(FIXTURE.read_text(encoding="utf-8"))["probability_cases"],
    ids=lambda c: c["id"],
)
def test_probability_cases_pinned(case: dict) -> None:
    probs = soft_regime_probabilities(case["vol_percentile"], case["efficiency_ratio"])
    assert probs is not None
    assert {p.regime for p in probs} == set(REGIME_LABELS)
    assert abs(sum(p.probability for p in probs) - 1.0) < 0.02
    top = max(probs, key=lambda p: p.probability)
    assert top.regime == case["expected_top"]
    assert top.probability >= case["min_top_probability"]


def _ohlcv(n: int, *, drift: float, timeframe_hours: float = 1.0) -> pd.DataFrame:
    start = datetime(2025, 6, 2, 0, 0, tzinfo=UTC)  # Monday
    rows = []
    px = 1.2
    step = timedelta(hours=timeframe_hours)
    for i in range(n):
        ts = start + step * i
        # Skip FX weekend for H1-like series
        if ts.weekday() >= 5:
            continue
        c = px + drift
        rows.append(
            {
                "ts": ts,
                "open": px,
                "high": max(px, c) + 0.0002,
                "low": min(px, c) - 0.0002,
                "close": c,
                "volume": 1.0,
            }
        )
        px = c
    return pd.DataFrame(rows)


@pytest.mark.parametrize("timeframe", TIMEFRAMES)
def test_metrics_snapshot_all_timeframes(timeframe: str) -> None:
    hours = {"M1": 1 / 60, "M15": 0.25, "H1": 1.0, "H4": 4.0, "D1": 24.0}[timeframe]
    n = {"M1": 2000, "M15": 800, "H1": 400, "H4": 200, "D1": 120}[timeframe]
    df = _ohlcv(n, drift=0.00005, timeframe_hours=hours)
    snap = compute_metric_snapshot(df, symbol="EURUSD", timeframe=timeframe)  # type: ignore[arg-type]
    assert snap.model_version == METRICS_MODEL_VERSION
    assert snap.timeframe == timeframe
    assert snap.typical_spread is None
    assert snap.liquidity_note
    # Core fields populated on a long enough series
    assert snap.atr_14 is not None and snap.atr_14 > 0
    assert snap.efficiency_ratio_20 is not None
    assert snap.range_mean_20 is not None and snap.range_mean_20 > 0
    assert snap.return_1 is not None


def test_metrics_v1_field_surface_complete() -> None:
    df = _ohlcv(300, drift=0.0001)
    snap = compute_metric_snapshot(df, symbol="GBPUSD", timeframe="H1")
    # Pin the public surface so profile builders can rely on it
    required = {
        "symbol",
        "timeframe",
        "as_of",
        "realized_vol_20",
        "realized_vol_60",
        "realized_vol_percentile_30d",
        "realized_vol_percentile_90d",
        "atr_14",
        "atr_percentile_30d",
        "atr_percentile_90d",
        "return_1",
        "return_5",
        "return_20",
        "efficiency_ratio_20",
        "range_mean_20",
        "range_percentile_30d",
        "typical_spread",
        "liquidity_note",
        "model_version",
    }
    assert set(snap.__dataclass_fields__) == required
