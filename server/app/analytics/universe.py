"""Universe gates for analytics (depth filters, exclusions)."""

from __future__ import annotations

from datetime import timedelta

import pandas as pd

from app.calendar.timebase import ensure_utc

# Roadmap: exclude from correlations/regimes until ≥90 days M1 depth.
MIN_CORR_REGIME_DEPTH_DAYS = 90

# Symbols that need the depth gate before joining correlation / regime panels.
DEPTH_GATED_SYMBOLS: frozenset[str] = frozenset({"USDCHF"})


def m1_span_days(ts: pd.Series) -> float:
    """Calendar-day span of an M1 timestamp series (0 if empty / single point)."""
    if ts is None or len(ts) < 2:
        return 0.0
    t = pd.to_datetime(ts, utc=True).sort_values()
    first = ensure_utc(t.iloc[0].to_pydatetime())
    last = ensure_utc(t.iloc[-1].to_pydatetime())
    return max((last - first) / timedelta(days=1), 0.0)


def passes_depth_gate(
    symbol: str,
    *,
    m1_span_days_value: float,
    min_days: int = MIN_CORR_REGIME_DEPTH_DAYS,
) -> bool:
    """
    Return True if ``symbol`` may enter correlations / regimes.

    Non-gated symbols always pass. Gated symbols need ``m1_span_days_value >= min_days``.
    """
    sym = symbol.upper()
    if sym not in DEPTH_GATED_SYMBOLS:
        return True
    return m1_span_days_value >= float(min_days)


def filter_corr_eligible(
    symbols: list[str],
    *,
    m1_span_by_symbol: dict[str, float],
    min_days: int = MIN_CORR_REGIME_DEPTH_DAYS,
) -> tuple[list[str], list[str]]:
    """Split symbols into (eligible, excluded_by_depth)."""
    eligible: list[str] = []
    excluded: list[str] = []
    for raw in symbols:
        sym = raw.upper()
        span = float(m1_span_by_symbol.get(sym, 0.0))
        if passes_depth_gate(sym, m1_span_days_value=span, min_days=min_days):
            eligible.append(sym)
        else:
            excluded.append(sym)
    return eligible, excluded
