"""Deterministic price metrics — model tag ``metrics.v1`` (Phase 2 W4·D1–D2).

Pure functions over OHLCV frames. No LLM / no DB I/O here.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal

import numpy as np
import pandas as pd

from app.calendar.sessions import is_fx_weekend_closed
from app.calendar.timebase import ensure_utc

MODEL_VERSION = "metrics.v1"

Timeframe = Literal["M1", "M15", "H1", "H4", "D1"]
TIMEFRAMES: tuple[Timeframe, ...] = ("M1", "M15", "H1", "H4", "D1")

ER_PERIOD = 20
RANGE_MEAN_PERIOD = 20
LIQUIDITY_NOTE = (
    "true bid/ask spread deferred until quote ingestion; "
    "range proxies (high-low) only"
)

# Expected bar length and max allowed gap before nulling a return.
_BAR_DELTA: dict[Timeframe, timedelta] = {
    "M1": timedelta(minutes=1),
    "M15": timedelta(minutes=15),
    "H1": timedelta(hours=1),
    "H4": timedelta(hours=4),
    "D1": timedelta(days=1),
}
# Multiples of bar length; D1 allows Fri→Mon (~3d).
_MAX_GAP_MULTIPLIER: dict[Timeframe, float] = {
    "M1": 3.0,
    "M15": 3.0,
    "H1": 3.0,
    "H4": 2.5,
    "D1": 5.0,  # Fri→Mon + short holidays
}

# FX-style annualization (~252 trading days × bars/day).
_PERIODS_PER_YEAR: dict[Timeframe, float] = {
    "M1": 252 * 24 * 60,
    "M15": 252 * 24 * 4,
    "H1": 252 * 24,
    "H4": 252 * 6,
    "D1": 252,
}


@dataclass(frozen=True)
class MetricSnapshot:
    """Latest metrics for one symbol/timeframe (metrics.v1)."""

    symbol: str
    timeframe: Timeframe
    as_of: datetime
    realized_vol_20: float | None
    realized_vol_60: float | None
    realized_vol_percentile_30d: float | None
    realized_vol_percentile_90d: float | None
    atr_14: float | None
    atr_percentile_30d: float | None
    atr_percentile_90d: float | None
    return_1: float | None
    return_5: float | None
    return_20: float | None
    efficiency_ratio_20: float | None
    range_mean_20: float | None
    range_percentile_30d: float | None
    typical_spread: float | None
    liquidity_note: str
    model_version: str = MODEL_VERSION


def _require_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    need = {"ts", "open", "high", "low", "close"}
    missing = need - set(df.columns)
    if missing:
        raise ValueError(f"OHLCV frame missing columns: {sorted(missing)}")
    out = df.sort_values("ts").reset_index(drop=True).copy()
    out["ts"] = out["ts"].map(ensure_utc)
    return out


def gap_aware_log_returns(ts: pd.Series, close: pd.Series, timeframe: Timeframe) -> pd.Series:
    """
    Log returns with weekend / oversized gaps nulled.

    A return at index i uses close[i-1] → close[i]. If the wall-clock gap exceeds
    the timeframe budget, or the prior bar is in the FX weekend while the current
    bar is not (Fri→Sun open), the return is NaN.
    """
    close_f = pd.to_numeric(close, errors="coerce").astype(float)
    raw = np.log(close_f / close_f.shift(1))
    max_gap = _BAR_DELTA[timeframe] * _MAX_GAP_MULTIPLIER[timeframe]

    ts_utc = pd.to_datetime(ts, utc=True)
    deltas = ts_utc.diff()
    oversized = deltas > max_gap

    weekend_cross = pd.Series(False, index=ts.index)
    for i in range(1, len(ts_utc)):
        prev = ts_utc.iloc[i - 1].to_pydatetime()
        cur = ts_utc.iloc[i].to_pydatetime()
        if is_fx_weekend_closed(prev) and not is_fx_weekend_closed(cur):
            weekend_cross.iloc[i] = True
        if (
            timeframe != "D1"
            and not pd.isna(deltas.iloc[i])
            and deltas.iloc[i] >= timedelta(hours=36)
        ):
            weekend_cross.iloc[i] = True

    masked = raw.where(~(oversized | weekend_cross))
    masked.iloc[0] = np.nan
    return masked


def realized_vol(returns: pd.Series, window: int, timeframe: Timeframe) -> pd.Series:
    """Annualized realized vol = std(log returns, ddof=0) * sqrt(periods/year).

    ``min_periods`` is slightly below ``window`` so FX weekend-nulls (esp. D1)
    do not leave the entire series NaN when ~1 return/week is gap-masked.
    """
    if window < 2:
        raise ValueError("window must be >= 2")
    scale = float(np.sqrt(_PERIODS_PER_YEAR[timeframe]))
    min_p = max(2, window - max(1, window // 5))
    return returns.rolling(window, min_periods=min_p).std(ddof=0) * scale


def wilder_atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14,
) -> pd.Series:
    """Wilder ATR(period)."""
    high_f = pd.to_numeric(high, errors="coerce").astype(float)
    low_f = pd.to_numeric(low, errors="coerce").astype(float)
    close_f = pd.to_numeric(close, errors="coerce").astype(float)
    prev_close = close_f.shift(1)
    tr = pd.concat(
        [
            (high_f - low_f).abs(),
            (high_f - prev_close).abs(),
            (low_f - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    # Wilder smoothing = EWM alpha = 1/period
    return tr.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()


def kaufman_efficiency_ratio(close: pd.Series, period: int = ER_PERIOD) -> pd.Series:
    """
    Kaufman Efficiency Ratio, signed by net-change direction.

    ER = |close_t - close_{t-n}| / sum |Δclose| over n steps ∈ [0, 1].
    Signed value ∈ [-1, 1]: positive = net up, negative = net down.
    """
    if period < 1:
        raise ValueError("period must be >= 1")
    close_f = pd.to_numeric(close, errors="coerce").astype(float)
    net = close_f - close_f.shift(period)
    path = close_f.diff().abs().rolling(period, min_periods=period).sum()
    er = net.abs() / path.replace(0.0, np.nan)
    signed = np.sign(net.to_numpy(dtype=float)) * er.to_numpy(dtype=float)
    return pd.Series(signed, index=close.index, dtype=float)


def bar_range(high: pd.Series, low: pd.Series) -> pd.Series:
    """Per-bar high − low range (liquidity proxy; not bid/ask spread)."""
    high_f = pd.to_numeric(high, errors="coerce").astype(float)
    low_f = pd.to_numeric(low, errors="coerce").astype(float)
    return (high_f - low_f).abs()


def bars_for_calendar_days(timeframe: Timeframe, days: int) -> int:
    """Approximate bar count for a calendar-day lookback (used for percentiles)."""
    per_day = {
        "M1": 24 * 60,
        "M15": 24 * 4,
        "H1": 24,
        "H4": 6,
        "D1": 1,
    }[timeframe]
    return max(days * per_day, 2)


def percentile_of_last(series: pd.Series, lookback: int) -> float | None:
    """Percentile rank of the last value within the trailing lookback window [0, 100]."""
    clean = series.dropna()
    if clean.empty:
        return None
    window = clean.iloc[-lookback:] if len(clean) >= lookback else clean
    if len(window) < 2:
        return None
    last = float(window.iloc[-1])
    # Percentile rank: fraction of values <= last
    rank = float((window <= last).sum()) / float(len(window))
    return rank * 100.0


def rolling_simple_return(close: pd.Series, periods: int) -> float | None:
    """Simple return over ``periods`` bars: close_t / close_{t-n} - 1."""
    close_f = pd.to_numeric(close, errors="coerce").astype(float)
    if len(close_f) <= periods:
        return None
    a = float(close_f.iloc[-1])
    b = float(close_f.iloc[-(periods + 1)])
    if not np.isfinite(a) or not np.isfinite(b) or b == 0.0:
        return None
    return a / b - 1.0


def _finite_or_none(value: float | None) -> float | None:
    if value is None:
        return None
    if not np.isfinite(value):
        return None
    return float(value)


def compute_metric_snapshot(
    df: pd.DataFrame,
    *,
    symbol: str,
    timeframe: Timeframe,
) -> MetricSnapshot:
    """
    Compute metrics.v1 snapshot from an OHLCV frame (columns: ts, open, high, low, close).

    Uses the last row as ``as_of``. Requires enough history for windows where possible;
    insufficient history yields None fields rather than raising.
    """
    if timeframe not in TIMEFRAMES:
        raise ValueError(f"unsupported timeframe: {timeframe}")
    frame = _require_ohlcv(df)
    if frame.empty:
        raise ValueError("empty OHLCV frame")

    as_of = ensure_utc(frame["ts"].iloc[-1].to_pydatetime())
    rets = gap_aware_log_returns(frame["ts"], frame["close"], timeframe)
    vol20 = realized_vol(rets, 20, timeframe)
    vol60 = realized_vol(rets, 60, timeframe)
    atr = wilder_atr(frame["high"], frame["low"], frame["close"], period=14)
    er = kaufman_efficiency_ratio(frame["close"], period=ER_PERIOD)
    ranges = bar_range(frame["high"], frame["low"])
    range_mean = ranges.rolling(RANGE_MEAN_PERIOD, min_periods=RANGE_MEAN_PERIOD).mean()

    lookback_30 = bars_for_calendar_days(timeframe, 30)
    lookback_90 = bars_for_calendar_days(timeframe, 90)

    return MetricSnapshot(
        symbol=symbol.upper(),
        timeframe=timeframe,
        as_of=as_of,
        realized_vol_20=_finite_or_none(float(vol20.iloc[-1]) if len(vol20) else None),
        realized_vol_60=_finite_or_none(float(vol60.iloc[-1]) if len(vol60) else None),
        realized_vol_percentile_30d=percentile_of_last(vol20, lookback_30),
        realized_vol_percentile_90d=percentile_of_last(vol20, lookback_90),
        atr_14=_finite_or_none(float(atr.iloc[-1]) if len(atr) else None),
        atr_percentile_30d=percentile_of_last(atr, lookback_30),
        atr_percentile_90d=percentile_of_last(atr, lookback_90),
        return_1=rolling_simple_return(frame["close"], 1),
        return_5=rolling_simple_return(frame["close"], 5),
        return_20=rolling_simple_return(frame["close"], 20),
        efficiency_ratio_20=_finite_or_none(float(er.iloc[-1]) if len(er) else None),
        range_mean_20=_finite_or_none(float(range_mean.iloc[-1]) if len(range_mean) else None),
        range_percentile_30d=percentile_of_last(ranges, lookback_30),
        typical_spread=None,
        liquidity_note=LIQUIDITY_NOTE,
        model_version=MODEL_VERSION,
    )
