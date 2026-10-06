"""Composite entry gate for meanrev research books (DV / Preset Factory).

Combines:
  1. Live fit nowcast — ON only while family tag == MATCH (FRAGILE/MISMATCH off)
  2. Session drift — block fades against a one-way session move ≥ threshold

Payoff geometry (TP/SL) stays outside this module. Monthly boards are not a gate.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.analytics.fit.types import FitSnapshot, FitTag

TradeSide = Literal["buy", "sell"]


@dataclass(frozen=True)
class EntryGateDecision:
    """Whether a new entry (or grid add) is allowed."""

    allow: bool
    reason: str
    fit_tag: FitTag | None = None
    regime: str | None = None
    session_drift_pts: float | None = None
    drift_threshold_pts: float | None = None


def drift_threshold_pts(
    *,
    stop_target_pts: float,
    override_pts: float | None = None,
) -> float:
    """Default drift block distance = StopTarget points (1R path)."""
    if override_pts is not None and override_pts > 0:
        return float(override_pts)
    return float(stop_target_pts)


def session_drift_allows_side(
    side: TradeSide,
    session_drift_pts: float,
    threshold_pts: float,
    *,
    block_both_sides: bool = False,
) -> tuple[bool, str]:
    """
    Anti-drift fade filter.

    ``session_drift_pts`` = (price_now - session_open) / point  (signed).
    When |drift| >= threshold:
      - block_both_sides → block all new entries
      - else block sells into up-drift / buys into down-drift
    """
    thr = float(threshold_pts)
    if thr <= 0:
        return True, "drift_disabled"
    d = float(session_drift_pts)
    if abs(d) < thr:
        return True, "drift_ok"
    if block_both_sides:
        return False, "drift_block_both"
    if d >= thr and side == "sell":
        return False, "drift_block_sell_into_up"
    if d <= -thr and side == "buy":
        return False, "drift_block_buy_into_down"
    return True, "drift_ok_with_trend"


def fit_allows_entry(fit: FitSnapshot) -> tuple[bool, str]:
    """Research live gate: MATCH only (same contract as ``live_fit.allow_on``)."""
    if fit.skipped:
        return False, fit.skip_reason or "fit_skipped"
    if fit.tag == "MATCH" and fit.allow_on:
        return True, "fit_match"
    if fit.tag == "FRAGILE":
        return False, "fit_fragile"
    return False, "fit_mismatch"


def evaluate_entry_gate(
    *,
    fit: FitSnapshot | None,
    side: TradeSide,
    session_drift_pts: float = 0.0,
    stop_target_pts: float = 0.0,
    drift_override_pts: float | None = None,
    require_fit: bool = True,
    enable_drift: bool = True,
    block_both_on_drift: bool = False,
) -> EntryGateDecision:
    """
    Composite gate for a proposed buy/sell entry.

    ``require_fit=True`` (default): missing/skipped/non-MATCH fit → block.
    ``enable_drift=True``: apply session anti-drift after fit passes.
    """
    fit_tag: FitTag | None = None
    regime: str | None = None

    if require_fit:
        if fit is None:
            return EntryGateDecision(False, "fit_missing")
        fit_tag = fit.tag
        regime = str(fit.regime) if fit.regime is not None else None
        ok, reason = fit_allows_entry(fit)
        if not ok:
            return EntryGateDecision(
                False,
                reason,
                fit_tag=fit_tag,
                regime=regime,
                session_drift_pts=session_drift_pts,
            )

    thr = drift_threshold_pts(
        stop_target_pts=stop_target_pts,
        override_pts=drift_override_pts,
    )
    if enable_drift:
        ok, reason = session_drift_allows_side(
            side,
            session_drift_pts,
            thr,
            block_both_sides=block_both_on_drift,
        )
        if not ok:
            return EntryGateDecision(
                False,
                reason,
                fit_tag=fit_tag,
                regime=regime,
                session_drift_pts=session_drift_pts,
                drift_threshold_pts=thr,
            )

    return EntryGateDecision(
        True,
        "allow",
        fit_tag=fit_tag,
        regime=regime,
        session_drift_pts=session_drift_pts,
        drift_threshold_pts=thr if enable_drift else None,
    )
