"""Rule-based regime classifier — model tag ``regimes.rule_v1`` (Phase 2 W4·D3).

Grid (regimes.rule_v1, tuned W4·D4):
  vol_percentile_30d >= 75              → high_volatility
  else |ER_20| >= 0.25 and ER > 0       → trending_up
  else |ER_20| >= 0.25 and ER < 0       → trending_down
  else                                  → ranging

Soft probabilities from distance-to-threshold (sum ≈ 1).
Confirmed label uses hysteresis with N-bar persistence (default 3).
USDCHF (and other depth-gated symbols) excluded until M1 depth gate passes.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal

import numpy as np
import pandas as pd

from app.analytics.metrics import (
    ER_PERIOD,
    Timeframe,
    bars_for_calendar_days,
    gap_aware_log_returns,
    kaufman_efficiency_ratio,
    realized_vol,
)
from app.analytics.universe import MIN_CORR_REGIME_DEPTH_DAYS, passes_depth_gate
from app.calendar.timebase import ensure_utc

MODEL_VERSION = "regimes.rule_v1"

RegimeLabel = Literal["trending_up", "trending_down", "ranging", "high_volatility"]
REGIME_LABELS: tuple[RegimeLabel, ...] = (
    "trending_up",
    "trending_down",
    "ranging",
    "high_volatility",
)

VOL_HIGH_PCT = 75.0
ER_TREND_ABS = 0.25
PERSISTENCE_N = 3

# Flip-rate budgets (roadmap Phase 2 locked baseline).
FLIP_BUDGET_H1_PER_DAY = 2.0
FLIP_BUDGET_D1_PER_WEEK = 1.0

# Soft-score ramps (aligned to hard thresholds after W4·D4 tune).
_VOL_SOFT_LO = 65.0
_VOL_SOFT_HI = 85.0
_ER_SOFT_LO = 0.10
_ER_SOFT_HI = 0.40


@dataclass(frozen=True)
class RegimeParams:
    """Tunable classifier knobs (W4·D4)."""

    vol_high: float = VOL_HIGH_PCT
    er_abs: float = ER_TREND_ABS
    persistence_n: int = PERSISTENCE_N


DEFAULT_PARAMS = RegimeParams()


@dataclass(frozen=True)
class RegimeProbability:
    regime: RegimeLabel
    probability: float


@dataclass(frozen=True)
class RegimeSnapshot:
    """Latest confirmed regime for one symbol/timeframe."""

    symbol: str
    timeframe: Timeframe
    regime: RegimeLabel
    raw_regime: RegimeLabel
    regime_probabilities: tuple[RegimeProbability, ...]
    volatility_percentile: float | None
    trend_strength: float | None
    as_of: datetime
    model_version: str = MODEL_VERSION
    skipped: bool = False
    skip_reason: str | None = None


def _clamp01(x: float) -> float:
    return float(min(1.0, max(0.0, x)))


def _ramp(value: float, lo: float, hi: float) -> float:
    """Linear 0→1 between lo and hi."""
    if hi <= lo:
        return 1.0 if value >= hi else 0.0
    return _clamp01((value - lo) / (hi - lo))


def classify_raw(
    vol_percentile: float | None,
    efficiency_ratio: float | None,
    *,
    vol_high: float = VOL_HIGH_PCT,
    er_abs: float = ER_TREND_ABS,
) -> RegimeLabel | None:
    """Hard grid classification. Returns None if features are missing."""
    if vol_percentile is None or efficiency_ratio is None:
        return None
    if not np.isfinite(vol_percentile) or not np.isfinite(efficiency_ratio):
        return None
    if vol_percentile >= vol_high:
        return "high_volatility"
    if efficiency_ratio >= er_abs:
        return "trending_up"
    if efficiency_ratio <= -er_abs:
        return "trending_down"
    return "ranging"


def soft_regime_probabilities(
    vol_percentile: float | None,
    efficiency_ratio: float | None,
) -> tuple[RegimeProbability, ...] | None:
    """
    Soft distance-to-threshold probabilities for all four regimes (sum ≈ 1).

    High-vol score ramps vol 70→90; trend scores ramp |ER| 0.15→0.45 and are
    attenuated by high-vol score; ranging fills residual mass when |ER| is low.
    """
    if vol_percentile is None or efficiency_ratio is None:
        return None
    if not np.isfinite(vol_percentile) or not np.isfinite(efficiency_ratio):
        return None

    s_hv = _ramp(float(vol_percentile), _VOL_SOFT_LO, _VOL_SOFT_HI)
    atten = 1.0 - s_hv
    s_up = _ramp(float(efficiency_ratio), _ER_SOFT_LO, _ER_SOFT_HI) * atten
    s_dn = _ramp(float(-efficiency_ratio), _ER_SOFT_LO, _ER_SOFT_HI) * atten
    s_rg = _ramp(ER_TREND_ABS + 0.05 - abs(float(efficiency_ratio)), 0.0, ER_TREND_ABS + 0.05)
    s_rg *= atten

    scores: dict[RegimeLabel, float] = {
        "high_volatility": s_hv,
        "trending_up": s_up,
        "trending_down": s_dn,
        "ranging": s_rg,
    }
    # Ensure hard-grid winner has meaningful mass, then floor + renormalize.
    hard = classify_raw(vol_percentile, efficiency_ratio)
    if hard is not None:
        scores[hard] = max(scores[hard], 0.4)
    for key in REGIME_LABELS:
        scores[key] = max(scores[key], 0.02)

    total = sum(scores.values())
    probs = {k: scores[k] / total for k in REGIME_LABELS}
    return tuple(RegimeProbability(regime=k, probability=float(probs[k])) for k in REGIME_LABELS)


def apply_persistence(
    raw_labels: list[RegimeLabel | None],
    *,
    n: int = PERSISTENCE_N,
    prior_confirmed: RegimeLabel | None = None,
) -> list[RegimeLabel | None]:
    """
    Confirm a regime change only after ``n`` consecutive raw labels agree.

    ``None`` raw bars hold the prior confirmed label (no flip).
    """
    if n < 1:
        raise ValueError("n must be >= 1")
    confirmed: list[RegimeLabel | None] = []
    current = prior_confirmed
    pending: RegimeLabel | None = None
    streak = 0

    for raw in raw_labels:
        if raw is None:
            confirmed.append(current)
            pending = None
            streak = 0
            continue
        if current is None:
            current = raw
            confirmed.append(current)
            pending = None
            streak = 0
            continue
        if raw == current:
            pending = None
            streak = 0
            confirmed.append(current)
            continue
        if raw == pending:
            streak += 1
        else:
            pending = raw
            streak = 1
        if streak >= n:
            current = pending
            pending = None
            streak = 0
        confirmed.append(current)
    return confirmed


def _rolling_percentile_rank(series: pd.Series, window: int) -> pd.Series:
    min_p = max(2, min(window, max(window // 5, 2)))
    # Percentile of the current value within the trailing window (0–100).
    return series.rolling(window, min_periods=min_p).rank(pct=True) * 100.0


def regime_feature_frame(
    df: pd.DataFrame,
    timeframe: Timeframe,
    *,
    params: RegimeParams = DEFAULT_PARAMS,
) -> pd.DataFrame:
    """Build per-bar vol percentile, ER, raw + confirmed regime for an OHLCV frame."""
    need = {"ts", "open", "high", "low", "close"}
    missing = need - set(df.columns)
    if missing:
        raise ValueError(f"OHLCV frame missing columns: {sorted(missing)}")
    frame = df.sort_values("ts").reset_index(drop=True).copy()
    frame["ts"] = frame["ts"].map(ensure_utc)

    rets = gap_aware_log_returns(frame["ts"], frame["close"], timeframe)
    vol20 = realized_vol(rets, 20, timeframe)
    lookback = bars_for_calendar_days(timeframe, 30)
    vol_pct = _rolling_percentile_rank(vol20, lookback)
    er = kaufman_efficiency_ratio(frame["close"], period=ER_PERIOD)

    raw: list[RegimeLabel | None] = [
        classify_raw(
            float(vol_pct.iloc[i]) if np.isfinite(vol_pct.iloc[i]) else None,
            float(er.iloc[i]) if np.isfinite(er.iloc[i]) else None,
            vol_high=params.vol_high,
            er_abs=params.er_abs,
        )
        for i in range(len(frame))
    ]
    out = pd.DataFrame(
        {
            "ts": frame["ts"],
            "vol_percentile": vol_pct,
            "efficiency_ratio": er,
            "raw_regime": raw,
        }
    )
    out["confirmed_regime"] = apply_persistence(
        list(out["raw_regime"]),
        n=params.persistence_n,
    )
    return out


def classify_regime(
    df: pd.DataFrame,
    *,
    symbol: str,
    timeframe: Timeframe,
    m1_span_days_value: float | None = None,
    prior_confirmed: RegimeLabel | None = None,
    min_depth_days: int = MIN_CORR_REGIME_DEPTH_DAYS,
) -> RegimeSnapshot:
    """
    Classify the latest bar for ``symbol``/``timeframe``.

    If depth-gated and span is insufficient, returns ``skipped=True`` (no regime).
    """
    sym = symbol.upper()
    span = 0.0 if m1_span_days_value is None else float(m1_span_days_value)
    # Only apply gate when span was provided (or symbol is gated — missing span ⇒ 0)
    if not passes_depth_gate(sym, m1_span_days_value=span, min_days=min_depth_days):
        as_of = (
            ensure_utc(pd.to_datetime(df["ts"].iloc[-1], utc=True).to_pydatetime())
            if len(df)
            else datetime.now(UTC)
        )
        return RegimeSnapshot(
            symbol=sym,
            timeframe=timeframe,
            regime="ranging",
            raw_regime="ranging",
            regime_probabilities=tuple(
                RegimeProbability(regime=r, probability=0.25) for r in REGIME_LABELS
            ),
            volatility_percentile=None,
            trend_strength=None,
            as_of=as_of,
            skipped=True,
            skip_reason=f"depth gate: need >={min_depth_days}d M1 history",
        )

    features = regime_feature_frame(df, timeframe)
    if prior_confirmed is not None:
        features["confirmed_regime"] = apply_persistence(
            list(features["raw_regime"]),
            n=PERSISTENCE_N,
            prior_confirmed=prior_confirmed,
        )

    last = features.iloc[-1]
    vol_p = float(last["vol_percentile"]) if np.isfinite(last["vol_percentile"]) else None
    er_v = float(last["efficiency_ratio"]) if np.isfinite(last["efficiency_ratio"]) else None
    raw = last["raw_regime"]
    confirmed = last["confirmed_regime"]
    if raw is None or confirmed is None:
        # Fall back: use latest available metric snapshot-style percentile
        raw = classify_raw(vol_p, er_v) or "ranging"
        confirmed = prior_confirmed or raw

    probs = soft_regime_probabilities(vol_p, er_v)
    if probs is None:
        probs = tuple(RegimeProbability(regime=r, probability=0.25) for r in REGIME_LABELS)

    as_of = ensure_utc(pd.to_datetime(last["ts"], utc=True).to_pydatetime())
    return RegimeSnapshot(
        symbol=sym,
        timeframe=timeframe,
        regime=confirmed,  # type: ignore[arg-type]
        raw_regime=raw,  # type: ignore[arg-type]
        regime_probabilities=probs,
        volatility_percentile=vol_p if vol_p is None else float(vol_p),
        trend_strength=er_v if er_v is None else float(er_v),
        as_of=as_of,
        skipped=False,
        skip_reason=None,
    )


def classify_from_snapshot_features(
    *,
    symbol: str,
    timeframe: Timeframe,
    as_of: datetime,
    vol_percentile: float | None,
    efficiency_ratio: float | None,
    prior_confirmed: RegimeLabel | None = None,
    raw_history: list[RegimeLabel | None] | None = None,
    m1_span_days_value: float | None = None,
    min_depth_days: int = MIN_CORR_REGIME_DEPTH_DAYS,
) -> RegimeSnapshot:
    """Classify from precomputed features (e.g. MetricSnapshot fields) + optional history."""
    sym = symbol.upper()
    span = 0.0 if m1_span_days_value is None else float(m1_span_days_value)
    if not passes_depth_gate(sym, m1_span_days_value=span, min_days=min_depth_days):
        return RegimeSnapshot(
            symbol=sym,
            timeframe=timeframe,
            regime="ranging",
            raw_regime="ranging",
            regime_probabilities=tuple(
                RegimeProbability(regime=r, probability=0.25) for r in REGIME_LABELS
            ),
            volatility_percentile=vol_percentile,
            trend_strength=efficiency_ratio,
            as_of=ensure_utc(as_of),
            skipped=True,
            skip_reason=f"depth gate: need >={min_depth_days}d M1 history",
        )

    raw = classify_raw(vol_percentile, efficiency_ratio) or "ranging"
    history = list(raw_history or [])
    history.append(raw)
    confirmed_series = apply_persistence(
        history,
        n=PERSISTENCE_N,
        prior_confirmed=prior_confirmed,
    )
    confirmed = confirmed_series[-1] or prior_confirmed or raw
    probs = soft_regime_probabilities(vol_percentile, efficiency_ratio)
    if probs is None:
        probs = tuple(RegimeProbability(regime=r, probability=0.25) for r in REGIME_LABELS)

    return RegimeSnapshot(
        symbol=sym,
        timeframe=timeframe,
        regime=confirmed,
        raw_regime=raw,
        regime_probabilities=probs,
        volatility_percentile=vol_percentile,
        trend_strength=efficiency_ratio,
        as_of=ensure_utc(as_of),
    )
