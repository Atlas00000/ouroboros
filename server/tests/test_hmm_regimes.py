"""Unit tests for HMM regime spike helpers (W5·D5)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import numpy as np
import pandas as pd
import pytest

from app.analytics.hmm_regimes import (
    hmmlearn_available,
    map_state_means_to_labels,
)


def test_map_state_means_covers_four_labels() -> None:
    means = np.array(
        [
            [80.0, 0.0],
            [40.0, 0.5],
            [40.0, -0.5],
            [30.0, 0.0],
        ]
    )
    mapping = map_state_means_to_labels(
        means,
        train_mu=np.array([0.0, 0.0]),
        train_sigma=np.array([1.0, 1.0]),
    )
    assert set(mapping.values()) == {
        "high_volatility",
        "trending_up",
        "trending_down",
        "ranging",
    }


@pytest.mark.skipif(not hmmlearn_available(), reason="hmmlearn not installed")
def test_fit_and_compare_on_synthetic() -> None:
    from app.analytics.hmm_regimes import compare_hmm_vs_rule

    # Continuous H1 series (no weekend gaps) so vol percentiles resolve.
    start = datetime(2025, 6, 2, tzinfo=UTC)
    rows = []
    px = 1.10
    rng = np.random.default_rng(0)
    for i in range(800):
        ts = start + timedelta(hours=i)
        regime = (i // 100) % 4
        if regime == 0:
            shock = float(rng.normal(0.0003, 0.00005))
        elif regime == 1:
            shock = float(rng.normal(-0.0003, 0.00005))
        elif regime == 2:
            shock = float(rng.normal(0.0, 0.00008))
        else:
            shock = float(rng.normal(0.0, 0.0012))
        c = px + shock
        rows.append(
            {
                "ts": ts,
                "open": px,
                "high": max(px, c) + abs(shock),
                "low": min(px, c) - abs(shock),
                "close": c,
                "volume": 1.0,
            }
        )
        px = c
    df = pd.DataFrame(rows)
    result = compare_hmm_vs_rule(df, symbol="EURUSD", timeframe="H1")
    assert result.bars_compared > 50
    assert 0.0 <= result.agreement <= 1.0
    assert result.hmm_model == "regimes.hmm_v1"
    assert len(result.state_map) == 4
