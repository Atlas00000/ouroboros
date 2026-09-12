"""Regime classifier backtest + flip-rate tuning (Phase 2 W4·D4)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from app.analytics.metrics import Timeframe, bars_for_calendar_days
from app.analytics.regimes import (
    DEFAULT_PARAMS,
    FLIP_BUDGET_D1_PER_WEEK,
    FLIP_BUDGET_H1_PER_DAY,
    RegimeLabel,
    RegimeParams,
    apply_persistence,
    classify_raw,
    regime_feature_frame,
)
from app.calendar.timebase import ensure_utc

__all__ = [
    "FLIP_BUDGET_D1_PER_WEEK",
    "FLIP_BUDGET_H1_PER_DAY",
    "FlipRateResult",
    "TuneResult",
    "count_flips",
    "measure_flip_rate",
    "precompute_regime_features",
    "tune_regime_params",
]


@dataclass(frozen=True)
class FlipRateResult:
    symbol: str
    timeframe: Timeframe
    flips: int
    span_days: float
    flips_per_day: float
    flips_per_week: float
    bars_scored: int
    ranging_share: float
    regime_counts: dict[str, int]
    within_budget: bool
    params: RegimeParams


@dataclass(frozen=True)
class TuneResult:
    params: RegimeParams
    h1_avg_flips_per_day: float
    d1_avg_flips_per_week: float
    h1_within: bool
    d1_within: bool
    mean_ranging_share: float
    score: float


def count_flips(labels: list[RegimeLabel | None] | pd.Series) -> int:
    """Count confirmed-label transitions (ignoring None)."""
    flips = 0
    prev: str | None = None
    for lab in labels:
        if lab is None or (isinstance(lab, float) and pd.isna(lab)):
            continue
        label = str(lab)
        if prev is not None and label != prev:
            flips += 1
        prev = label
    return flips


def _span_days(ts: pd.Series) -> float:
    if len(ts) < 2:
        return 0.0
    first = ensure_utc(pd.to_datetime(ts.iloc[0], utc=True).to_pydatetime())
    last = ensure_utc(pd.to_datetime(ts.iloc[-1], utc=True).to_pydatetime())
    return max((last - first).total_seconds() / 86400.0, 1.0 / 24.0)


def precompute_regime_features(df: pd.DataFrame, timeframe: Timeframe) -> pd.DataFrame:
    """Compute vol percentile + ER once (expensive); labels applied later per params."""
    # Uses default params only for structure; raw/confirmed columns ignored by tuners.
    feats = regime_feature_frame(df, timeframe, params=DEFAULT_PARAMS)
    return feats[["ts", "vol_percentile", "efficiency_ratio"]].copy()


def _flip_rate_from_features(
    features: pd.DataFrame,
    *,
    symbol: str,
    timeframe: Timeframe,
    params: RegimeParams,
    warmup_days: int = 30,
) -> FlipRateResult:
    if features.empty:
        return FlipRateResult(
            symbol=symbol.upper(),
            timeframe=timeframe,
            flips=0,
            span_days=0.0,
            flips_per_day=0.0,
            flips_per_week=0.0,
            bars_scored=0,
            ranging_share=1.0,
            regime_counts={},
            within_budget=True,
            params=params,
        )

    raw: list[RegimeLabel | None] = []
    for i in range(len(features)):
        vp = features["vol_percentile"].iloc[i]
        er = features["efficiency_ratio"].iloc[i]
        raw.append(
            classify_raw(
                float(vp) if np.isfinite(vp) else None,
                float(er) if np.isfinite(er) else None,
                vol_high=params.vol_high,
                er_abs=params.er_abs,
            )
        )
    confirmed = apply_persistence(raw, n=params.persistence_n)
    work = features.copy()
    work["confirmed_regime"] = confirmed

    warmup_bars = bars_for_calendar_days(timeframe, warmup_days)
    scored = work.iloc[warmup_bars:]
    scored = scored[scored["confirmed_regime"].notna()]
    labels = list(scored["confirmed_regime"])
    flips = count_flips(labels)
    span = _span_days(scored["ts"]) if len(scored) else 0.0
    per_day = flips / span if span > 0 else 0.0
    per_week = per_day * 7.0

    counts: dict[str, int] = {}
    for lab in labels:
        key = str(lab)
        counts[key] = counts.get(key, 0) + 1
    total = sum(counts.values()) or 1
    ranging_share = counts.get("ranging", 0) / total

    if timeframe == "D1":
        within = per_week <= FLIP_BUDGET_D1_PER_WEEK
    else:
        within = per_day <= FLIP_BUDGET_H1_PER_DAY

    return FlipRateResult(
        symbol=symbol.upper(),
        timeframe=timeframe,
        flips=flips,
        span_days=span,
        flips_per_day=per_day,
        flips_per_week=per_week,
        bars_scored=len(scored),
        ranging_share=ranging_share,
        regime_counts=counts,
        within_budget=within,
        params=params,
    )


def measure_flip_rate(
    df: pd.DataFrame,
    *,
    symbol: str,
    timeframe: Timeframe,
    params: RegimeParams = DEFAULT_PARAMS,
    warmup_days: int = 30,
) -> FlipRateResult:
    """Run classifier over ``df`` and measure confirmed-regime flip rate after warmup."""
    features = precompute_regime_features(df, timeframe)
    return _flip_rate_from_features(
        features,
        symbol=symbol,
        timeframe=timeframe,
        params=params,
        warmup_days=warmup_days,
    )


def tune_regime_params(
    h1_frames: dict[str, pd.DataFrame],
    d1_frames: dict[str, pd.DataFrame],
    *,
    er_grid: tuple[float, ...] = (0.25, 0.30, 0.35, 0.40, 0.45),
    vol_grid: tuple[float, ...] = (75.0, 80.0, 85.0),
    persistence_grid: tuple[int, ...] = (3, 4, 5),
) -> TuneResult:
    """
    Grid-search params that satisfy flip budgets while minimizing ranging share.

    Precomputes features once per symbol/timeframe, then only re-labels per candidate.
    """
    print("precomputing H1 features...", flush=True)
    h1_feats = {
        sym: precompute_regime_features(df, "H1")
        for sym, df in h1_frames.items()
        if df is not None and not df.empty
    }
    print(f"  H1 symbols={len(h1_feats)}", flush=True)
    print("precomputing D1 features...", flush=True)
    d1_feats = {
        sym: precompute_regime_features(df, "D1")
        for sym, df in d1_frames.items()
        if df is not None and not df.empty
    }
    print(f"  D1 symbols={len(d1_feats)}", flush=True)

    best: TuneResult | None = None
    for er_abs in er_grid:
        for vol_high in vol_grid:
            for n in persistence_grid:
                params = RegimeParams(vol_high=vol_high, er_abs=er_abs, persistence_n=n)
                h1_rates = [
                    _flip_rate_from_features(feats, symbol=sym, timeframe="H1", params=params)
                    for sym, feats in h1_feats.items()
                ]
                d1_rates = [
                    _flip_rate_from_features(feats, symbol=sym, timeframe="D1", params=params)
                    for sym, feats in d1_feats.items()
                ]
                if not h1_rates or not d1_rates:
                    continue

                h1_avg = sum(r.flips_per_day for r in h1_rates) / len(h1_rates)
                d1_avg = sum(r.flips_per_week for r in d1_rates) / len(d1_rates)
                h1_ok = all(r.within_budget for r in h1_rates)
                d1_ok = all(r.within_budget for r in d1_rates)
                ranging = (
                    sum(r.ranging_share for r in h1_rates + d1_rates)
                    / (len(h1_rates) + len(d1_rates))
                )

                if h1_ok and d1_ok:
                    score = ranging
                else:
                    over_h1 = max(0.0, h1_avg - FLIP_BUDGET_H1_PER_DAY)
                    over_d1 = max(0.0, d1_avg - FLIP_BUDGET_D1_PER_WEEK)
                    score = 2.0 + over_h1 + over_d1 + ranging

                cand = TuneResult(
                    params=params,
                    h1_avg_flips_per_day=h1_avg,
                    d1_avg_flips_per_week=d1_avg,
                    h1_within=h1_ok,
                    d1_within=d1_ok,
                    mean_ranging_share=ranging,
                    score=score,
                )
                if best is None or cand.score < best.score:
                    best = cand
                    print(
                        f"  candidate vol={vol_high} er={er_abs} n={n} "
                        f"h1={h1_avg:.3f}/d d1={d1_avg:.3f}/w ranging={ranging:.3f} "
                        f"ok={h1_ok and d1_ok}",
                        flush=True,
                    )

    if best is None:
        return TuneResult(
            params=DEFAULT_PARAMS,
            h1_avg_flips_per_day=0.0,
            d1_avg_flips_per_week=0.0,
            h1_within=False,
            d1_within=False,
            mean_ranging_share=1.0,
            score=99.0,
        )
    return best
