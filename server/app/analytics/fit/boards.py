"""Ex-post fit boards — dominant-share tag over a closed window."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime, timedelta
from typing import Literal

import pandas as pd

from app.analytics.fit.mapper import MODEL_VERSION, map_regime_to_fit
from app.analytics.fit.types import (
    TIE_BREAK_ORDER,
    EdgeFamily,
    FitBoardResult,
    FitTag,
)
from app.analytics.regimes import regime_feature_frame
from app.calendar.timebase import ensure_utc

BoardWindow = Literal["7d", "30d", "calendar_month"]
BOARD_WINDOWS: tuple[BoardWindow, ...] = ("7d", "30d", "calendar_month")


def _tie_break(shares: dict[FitTag, float]) -> FitTag:
    """On exact share ties, prefer MISMATCH > FRAGILE > MATCH (safety)."""
    if not shares:
        raise ValueError("empty shares")
    best = max(shares.values())
    tied = [t for t, s in shares.items() if abs(s - best) < 1e-12]
    for pref in TIE_BREAK_ORDER:
        if pref in tied:
            return pref
    return tied[0]


def _window_start(end: datetime, window: BoardWindow) -> datetime:
    end = ensure_utc(end)
    if window == "7d":
        return end - timedelta(days=7)
    if window == "30d":
        return end - timedelta(days=30)
    if window == "calendar_month":
        return end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    raise ValueError(f"unknown window: {window}")


def board_from_regimes(
    regimes: list[str],
    family: EdgeFamily | str,
    *,
    window: BoardWindow = "30d",
) -> FitBoardResult:
    """
    Build a fit board from an ordered list of confirmed regime labels.

    Empty input → MISMATCH with zero shares (safe default for research gate).
    """
    fam: EdgeFamily = family if family in ("meanrev", "trendfollow") else str(family)  # type: ignore[assignment]
    if fam not in ("meanrev", "trendfollow"):
        raise ValueError(f"unknown edge family: {family}")

    if not regimes:
        empty_shares: dict[FitTag, float] = {
            "MATCH": 0.0,
            "MISMATCH": 0.0,
            "FRAGILE": 0.0,
        }
        return FitBoardResult(
            family=fam,
            tag="MISMATCH",
            shares=empty_shares,
            window=window,
            bar_count=0,
            regime_shares={},
        )

    tags = [map_regime_to_fit(r, fam) for r in regimes]
    tag_counts = Counter(tags)
    n = len(tags)
    shares: dict[FitTag, float] = {
        "MATCH": tag_counts.get("MATCH", 0) / n,
        "MISMATCH": tag_counts.get("MISMATCH", 0) / n,
        "FRAGILE": tag_counts.get("FRAGILE", 0) / n,
    }
    regime_counts = Counter(regimes)
    regime_shares = {k: v / n for k, v in sorted(regime_counts.items())}
    return FitBoardResult(
        family=fam,
        tag=_tie_break(shares),
        shares=shares,
        window=window,
        bar_count=n,
        regime_shares=regime_shares,
    )


def board_from_ohlcv(
    df: pd.DataFrame,
    family: EdgeFamily | str,
    *,
    timeframe: str,
    window: BoardWindow = "30d",
    end: datetime | None = None,
) -> FitBoardResult:
    """
    Classify confirmed regimes on OHLCV then aggregate fit shares in ``window``.

    Requires columns used by ``regime_feature_frame`` (ts/open/high/low/close/…).
    """
    if df is None or df.empty:
        return board_from_regimes([], family, window=window)

    features = regime_feature_frame(df, timeframe)  # type: ignore[arg-type]
    if features.empty or "confirmed_regime" not in features.columns:
        return board_from_regimes([], family, window=window)

    end_ts = ensure_utc(end or datetime.now(UTC))
    # Prefer last bar time as end when available
    if "ts" in features.columns and len(features):
        last_ts = features["ts"].iloc[-1]
        if hasattr(last_ts, "to_pydatetime"):
            end_ts = ensure_utc(last_ts.to_pydatetime())
        elif isinstance(last_ts, datetime):
            end_ts = ensure_utc(last_ts)

    start = _window_start(end_ts, window)
    if "ts" in features.columns:
        ts = pd.to_datetime(features["ts"], utc=True)
        mask = (ts >= pd.Timestamp(start)) & (ts <= pd.Timestamp(end_ts))
        sliced = features.loc[mask]
    else:
        sliced = features

    regimes = [str(r) for r in sliced["confirmed_regime"].tolist()]
    return board_from_regimes(regimes, family, window=window)


def board_model_version() -> str:
    return MODEL_VERSION
