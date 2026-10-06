"""Composite entry gate (live MATCH + session anti-drift)."""

from __future__ import annotations

from datetime import UTC, datetime

from app.analytics.fit.entry_gate import (
    evaluate_entry_gate,
    session_drift_allows_side,
)
from app.analytics.fit.gate import fit_from_regime_snapshot
from app.analytics.regimes import RegimeProbability, RegimeSnapshot


def _fit(regime: str = "ranging"):
    probs = tuple(
        RegimeProbability(regime=r, probability=0.7 if r == regime else 0.1)  # type: ignore[arg-type]
        for r in ("trending_up", "trending_down", "ranging", "high_volatility")
    )
    snap = RegimeSnapshot(
        symbol="NAS100",
        timeframe="H1",
        regime=regime,  # type: ignore[arg-type]
        raw_regime=regime,  # type: ignore[arg-type]
        regime_probabilities=probs,
        volatility_percentile=40.0,
        trend_strength=0.1,
        as_of=datetime(2026, 4, 7, 10, 0, tzinfo=UTC),
        model_version="regimes.rule_v1",
    )
    return fit_from_regime_snapshot(snap, "meanrev")


def test_match_and_calm_session_allows() -> None:
    d = evaluate_entry_gate(
        fit=_fit("ranging"),
        side="sell",
        session_drift_pts=100.0,
        stop_target_pts=2500.0,
    )
    assert d.allow is True
    assert d.reason == "allow"


def test_trending_blocks_even_calm_drift() -> None:
    d = evaluate_entry_gate(
        fit=_fit("trending_up"),
        side="buy",
        session_drift_pts=0.0,
        stop_target_pts=2500.0,
    )
    assert d.allow is False
    assert d.reason == "fit_mismatch"
    assert d.fit_tag == "MISMATCH"


def test_fragile_blocks() -> None:
    d = evaluate_entry_gate(
        fit=_fit("high_volatility"),
        side="buy",
        session_drift_pts=0.0,
        stop_target_pts=2500.0,
    )
    assert d.allow is False
    assert d.reason == "fit_fragile"


def test_drift_blocks_sell_into_up() -> None:
    ok, reason = session_drift_allows_side("sell", 3000.0, 2500.0)
    assert ok is False
    assert reason == "drift_block_sell_into_up"

    d = evaluate_entry_gate(
        fit=_fit("ranging"),
        side="sell",
        session_drift_pts=3000.0,
        stop_target_pts=2500.0,
    )
    assert d.allow is False
    assert d.reason == "drift_block_sell_into_up"


def test_drift_allows_buy_with_up_move() -> None:
    d = evaluate_entry_gate(
        fit=_fit("ranging"),
        side="buy",
        session_drift_pts=3000.0,
        stop_target_pts=2500.0,
    )
    assert d.allow is True


def test_missing_fit_blocks() -> None:
    d = evaluate_entry_gate(
        fit=None,
        side="buy",
        stop_target_pts=2500.0,
    )
    assert d.allow is False
    assert d.reason == "fit_missing"
