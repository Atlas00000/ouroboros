"""Universe gates for analytics (depth filters, exclusions, peer sets)."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pandas as pd

from app.calendar.timebase import ensure_utc

# Roadmap: exclude from correlations/regimes until ≥90 days M1 depth.
MIN_CORR_REGIME_DEPTH_DAYS = 90

# Cap default peer matrices so expanding the universe does not N² stampede.
MAX_DEFAULT_PEERS = 12

# Index anchors included when building equity peer sets.
EQUITY_INDEX_ANCHORS: tuple[str, ...] = ("US500", "NAS100")

# Symbols that need the depth gate before joining correlation / regime panels.
# New equities / energy / extra indices stay gated until backfill clears ≥90d.
DEPTH_GATED_SYMBOLS: frozenset[str] = frozenset(
    {
        "USDCHF",
        # Equities (0011)
        "AAPL",
        "MSFT",
        "NVDA",
        "AMZN",
        "META",
        "GOOGL",
        "TSLA",
        "JPM",
        "AVGO",
        "XOM",
        # Energy materials (0012)
        "XTIUSD",
        "XBRUSD",
        # Extra indices (0013)
        "DE40",
        "UK100",
        "JP225",
    }
)


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


def default_peer_symbols(
    session: Any,
    symbol: str,
    *,
    asset_class: str,
    max_peers: int = MAX_DEFAULT_PEERS,
) -> list[str]:
    """
    Class-aware peer set for profile correlations.

    Same ``asset_class`` first (excluding self). Equities also pull US index anchors.
    Capped so a 30-symbol universe does not load every peer frame.
    """
    from sqlalchemy import select

    from app.models.asset import Asset

    sym = symbol.upper()
    klass = (asset_class or "").lower()
    same_class = [
        str(s).upper()
        for s in session.scalars(
            select(Asset.symbol).where(
                Asset.is_active.is_(True),
                Asset.asset_class == klass,
                Asset.symbol != sym,
            )
        ).all()
    ]
    peers: list[str] = []
    seen: set[str] = {sym}
    for candidate in same_class:
        if candidate not in seen:
            peers.append(candidate)
            seen.add(candidate)
        if len(peers) >= max_peers:
            return peers

    if klass == "equity":
        active = {
            str(s).upper()
            for s in session.scalars(select(Asset.symbol).where(Asset.is_active.is_(True))).all()
        }
        for anchor in EQUITY_INDEX_ANCHORS:
            if anchor in active and anchor not in seen:
                peers.append(anchor)
                seen.add(anchor)
            if len(peers) >= max_peers:
                break

    return peers[:max_peers]
