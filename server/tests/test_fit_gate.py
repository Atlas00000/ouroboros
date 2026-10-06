"""Live fit gate helper tests (R2)."""

from __future__ import annotations

from datetime import UTC, datetime

from app.analytics.fit.gate import fit_from_regime_snapshot
from app.analytics.fit.mapper import MODEL_VERSION
from app.analytics.regimes import RegimeProbability, RegimeSnapshot


def _snap(
    *,
    regime: str = "ranging",
    skipped: bool = False,
    skip_reason: str | None = None,
) -> RegimeSnapshot:
    probs = tuple(
        RegimeProbability(regime=r, probability=0.25)  # type: ignore[arg-type]
        for r in ("trending_up", "trending_down", "ranging", "high_volatility")
    )
    # Put mass on confirmed regime for confidence
    probs = tuple(
        RegimeProbability(
            regime=p.regime,
            probability=0.7 if p.regime == regime else 0.1,
        )
        for p in probs
    )
    return RegimeSnapshot(
        symbol="EURUSD",
        timeframe="H1",
        regime=regime,  # type: ignore[arg-type]
        raw_regime=regime,  # type: ignore[arg-type]
        regime_probabilities=probs,
        volatility_percentile=40.0,
        trend_strength=0.1,
        as_of=datetime(2026, 10, 1, 12, 0, tzinfo=UTC),
        model_version="regimes.rule_v1",
        skipped=skipped,
        skip_reason=skip_reason,
    )


def test_meanrev_ranging_allow_on() -> None:
    fit = fit_from_regime_snapshot(_snap(regime="ranging"), "meanrev")
    assert fit.tag == "MATCH"
    assert fit.allow_on is True
    assert fit.model_version == MODEL_VERSION
    assert fit.skipped is False
    assert fit.confidence == 0.7


def test_trendfollow_ranging_off() -> None:
    fit = fit_from_regime_snapshot(_snap(regime="ranging"), "trendfollow")
    assert fit.tag == "MISMATCH"
    assert fit.allow_on is False


def test_fragile_high_vol_off() -> None:
    fit = fit_from_regime_snapshot(_snap(regime="high_volatility"), "meanrev")
    assert fit.tag == "FRAGILE"
    assert fit.allow_on is False
    assert "high_volatility" in fit.fragile_reasons


def test_skipped_depth_gate() -> None:
    fit = fit_from_regime_snapshot(
        _snap(skipped=True, skip_reason="depth gate"),
        "meanrev",
    )
    assert fit.skipped is True
    assert fit.allow_on is False
    assert fit.tag == "MISMATCH"
    assert fit.regime is None
    assert fit.skip_reason == "depth gate"
