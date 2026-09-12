"""Unit tests for regimes.rule_v1 (W4·D3)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pandas as pd
import pytest

from app.analytics.regimes import (
    MODEL_VERSION,
    PERSISTENCE_N,
    REGIME_LABELS,
    apply_persistence,
    classify_from_snapshot_features,
    classify_raw,
    classify_regime,
    regime_feature_frame,
    soft_regime_probabilities,
)


def test_model_version() -> None:
    assert MODEL_VERSION == "regimes.rule_v1"
    assert PERSISTENCE_N == 3


def test_classify_raw_grid() -> None:
    assert classify_raw(85.0, 0.1) == "high_volatility"
    assert classify_raw(50.0, 0.5) == "trending_up"
    assert classify_raw(50.0, -0.5) == "trending_down"
    assert classify_raw(50.0, 0.1) == "ranging"
    assert classify_raw(None, 0.5) is None


def test_soft_probs_sum_to_one_and_cover_labels() -> None:
    probs = soft_regime_probabilities(85.0, 0.1)
    assert probs is not None
    assert {p.regime for p in probs} == set(REGIME_LABELS)
    total = sum(p.probability for p in probs)
    assert total == pytest.approx(1.0, abs=0.02)
    hv = next(p.probability for p in probs if p.regime == "high_volatility")
    assert hv == max(p.probability for p in probs)


def test_soft_probs_trend_up_dominates() -> None:
    probs = soft_regime_probabilities(40.0, 0.6)
    assert probs is not None
    top = max(probs, key=lambda p: p.probability)
    assert top.regime == "trending_up"


def test_persistence_requires_n_bars() -> None:
    raw: list = ["ranging", "trending_up", "trending_up", "trending_up", "trending_down"]
    # n=3: flip to trending_up only on 4th bar (3rd consecutive up)
    out = apply_persistence(raw, n=3, prior_confirmed="ranging")
    assert out[0] == "ranging"
    assert out[1] == "ranging"  # 1st up
    assert out[2] == "ranging"  # 2nd up
    assert out[3] == "trending_up"  # 3rd up confirms
    assert out[4] == "trending_up"  # single down not enough


def test_persistence_holds_on_none() -> None:
    out = apply_persistence(
        ["trending_up", None, None],
        n=3,
        prior_confirmed="trending_up",
    )
    assert out == ["trending_up", "trending_up", "trending_up"]


def test_usdchf_skipped_by_depth_gate() -> None:
    snap = classify_from_snapshot_features(
        symbol="USDCHF",
        timeframe="H1",
        as_of=datetime(2026, 9, 11, tzinfo=UTC),
        vol_percentile=40.0,
        efficiency_ratio=0.5,
        m1_span_days_value=1.0,
    )
    assert snap.skipped is True
    assert snap.skip_reason is not None


def test_eurusd_not_skipped() -> None:
    snap = classify_from_snapshot_features(
        symbol="EURUSD",
        timeframe="H1",
        as_of=datetime(2026, 9, 11, tzinfo=UTC),
        vol_percentile=40.0,
        efficiency_ratio=0.5,
        m1_span_days_value=400.0,
    )
    assert snap.skipped is False
    assert snap.regime == "trending_up"
    assert snap.raw_regime == "trending_up"


def _trend_ohlcv(n: int = 200) -> pd.DataFrame:
    start = datetime(2026, 7, 1, tzinfo=UTC)
    rows = []
    px = 1.10
    for i in range(n):
        ts = start + timedelta(hours=i)
        c = px + 0.0002
        rows.append(
            {
                "ts": ts,
                "open": px,
                "high": c + 0.0001,
                "low": px - 0.0001,
                "close": c,
                "volume": 1.0,
            }
        )
        px = c
    return pd.DataFrame(rows)


def test_regime_feature_frame_and_classify() -> None:
    df = _trend_ohlcv(250)
    features = regime_feature_frame(df, "H1")
    assert "raw_regime" in features.columns
    assert "confirmed_regime" in features.columns
    # Late bars of a steady uptrend should be trending_up (raw)
    tail = features.dropna(subset=["efficiency_ratio"]).iloc[-20:]
    assert (tail["raw_regime"] == "trending_up").mean() > 0.5

    snap = classify_regime(
        df,
        symbol="EURUSD",
        timeframe="H1",
        m1_span_days_value=400.0,
    )
    assert snap.skipped is False
    assert snap.model_version == MODEL_VERSION
    assert abs(sum(p.probability for p in snap.regime_probabilities) - 1.0) < 0.02
