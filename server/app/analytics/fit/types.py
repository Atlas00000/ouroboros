"""Shared types for regime fit tags (fit.map_v0)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from app.analytics.regimes import RegimeLabel

FitTag = Literal["MATCH", "MISMATCH", "FRAGILE"]
FIT_TAGS: tuple[FitTag, ...] = ("MATCH", "MISMATCH", "FRAGILE")

EdgeFamily = Literal["meanrev", "trendfollow"]
EDGE_FAMILIES: tuple[EdgeFamily, ...] = ("meanrev", "trendfollow")

# Board tie-break priority (higher wins on exact share ties).
TIE_BREAK_ORDER: tuple[FitTag, ...] = ("MISMATCH", "FRAGILE", "MATCH")


@dataclass(frozen=True)
class FitSnapshot:
    """Nowcast or board fit for symbol × timeframe × family."""

    symbol: str
    timeframe: str
    family: EdgeFamily
    tag: FitTag
    regime: RegimeLabel | None
    model_version: str
    as_of: datetime
    allow_on: bool
    confidence: float = 0.0
    skipped: bool = False
    skip_reason: str | None = None
    fragile_reasons: tuple[str, ...] = ()
    shares: dict[FitTag, float] | None = None
    window: str | None = None


@dataclass(frozen=True)
class FitBoardResult:
    """Ex-post dominant-share board over a closed window."""

    family: EdgeFamily
    tag: FitTag
    shares: dict[FitTag, float]
    window: str
    bar_count: int
    regime_shares: dict[str, float] = field(default_factory=dict)
