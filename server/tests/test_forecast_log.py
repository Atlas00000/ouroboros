"""Unit tests for forecast / regime-call log writer (W5·D3)."""

from __future__ import annotations

from datetime import UTC, datetime

from app.analytics.forecast_log import (
    HORIZON_MINUTES,
    confidence_from_snapshot,
    regime_prediction_payload,
)
from app.analytics.regimes import MODEL_VERSION, RegimeProbability, RegimeSnapshot


def _snap(**kwargs: object) -> RegimeSnapshot:
    base = dict(
        symbol="EURUSD",
        timeframe="H1",
        regime="ranging",
        raw_regime="ranging",
        regime_probabilities=(
            RegimeProbability("trending_up", 0.1),
            RegimeProbability("trending_down", 0.15),
            RegimeProbability("ranging", 0.55),
            RegimeProbability("high_volatility", 0.2),
        ),
        volatility_percentile=40.0,
        trend_strength=0.12,
        as_of=datetime(2026, 9, 12, 10, 0, tzinfo=UTC),
        model_version=MODEL_VERSION,
        skipped=False,
        skip_reason=None,
    )
    base.update(kwargs)
    return RegimeSnapshot(**base)  # type: ignore[arg-type]


def test_regime_prediction_payload_includes_model_fields() -> None:
    snap = _snap()
    payload = regime_prediction_payload(snap)
    assert payload["regime"] == "ranging"
    assert payload["raw_regime"] == "ranging"
    assert len(payload["probabilities"]) == 4
    assert payload["skipped"] is False
    assert "2026-09-12" in payload["as_of"]


def test_confidence_uses_confirmed_regime_probability() -> None:
    assert abs(confidence_from_snapshot(_snap()) - 0.55) < 1e-9
    skipped = _snap(skipped=True, skip_reason="depth gate")
    assert confidence_from_snapshot(skipped) == 0.0


def test_horizon_minutes_cover_v1_timeframes() -> None:
    assert HORIZON_MINUTES["H1"] == 60
    assert HORIZON_MINUTES["H4"] == 240
    assert HORIZON_MINUTES["D1"] == 1440
