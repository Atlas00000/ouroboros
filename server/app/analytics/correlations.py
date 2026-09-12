"""Rolling correlation matrix — metrics.v1 (H1, 30d, depth-gated)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import numpy as np
import pandas as pd

from app.analytics.metrics import MODEL_VERSION, Timeframe, gap_aware_log_returns
from app.analytics.universe import MIN_CORR_REGIME_DEPTH_DAYS, filter_corr_eligible
from app.calendar.timebase import ensure_utc

CORR_TIMEFRAME: Timeframe = "H1"
CORR_WINDOW_DAYS = 30
# ~24 H1 bars/day × 30d
CORR_H1_BARS = CORR_WINDOW_DAYS * 24


@dataclass(frozen=True)
class CorrelationEntry:
    symbol_a: str
    symbol_b: str
    coefficient: float
    window_days: int = CORR_WINDOW_DAYS


@dataclass(frozen=True)
class CorrelationMatrixResult:
    """Pairwise Pearson correlations on gap-aware H1 log returns."""

    timeframe: Timeframe
    window_days: int
    symbols: tuple[str, ...]
    excluded: tuple[str, ...]
    entries: tuple[CorrelationEntry, ...]
    as_of: datetime
    model_version: str = MODEL_VERSION


def _align_return_panel(
    ohlcv_by_symbol: dict[str, pd.DataFrame],
    *,
    timeframe: Timeframe = CORR_TIMEFRAME,
) -> tuple[pd.DataFrame, datetime | None]:
    """Build a wide returns panel (columns=symbols) aligned on timestamp."""
    series: dict[str, pd.Series] = {}
    as_of: datetime | None = None
    for symbol, df in ohlcv_by_symbol.items():
        if df is None or df.empty:
            continue
        frame = df.sort_values("ts").reset_index(drop=True)
        rets = gap_aware_log_returns(frame["ts"], frame["close"], timeframe)
        idx = pd.to_datetime(frame["ts"], utc=True)
        s = pd.Series(rets.to_numpy(), index=idx, name=symbol.upper())
        series[symbol.upper()] = s
        last_ts = ensure_utc(idx.iloc[-1].to_pydatetime())
        as_of = last_ts if as_of is None else max(as_of, last_ts)
    if not series:
        return pd.DataFrame(), None
    panel = pd.concat(series, axis=1, join="outer").sort_index()
    return panel, as_of


def compute_correlation_matrix(
    ohlcv_by_symbol: dict[str, pd.DataFrame],
    *,
    m1_span_by_symbol: dict[str, float] | None = None,
    window_days: int = CORR_WINDOW_DAYS,
    min_depth_days: int = MIN_CORR_REGIME_DEPTH_DAYS,
) -> CorrelationMatrixResult:
    """
    Pearson correlation on the last ``window_days`` of H1 gap-aware log returns.

    ``m1_span_by_symbol`` gates DEPTH_GATED_SYMBOLS (e.g. USDCHF). If omitted,
    gated symbols are treated as span=0 (excluded).
    """
    symbols = [s.upper() for s in ohlcv_by_symbol]
    spans = {s.upper(): float(v) for s, v in (m1_span_by_symbol or {}).items()}
    eligible, excluded = filter_corr_eligible(
        symbols,
        m1_span_by_symbol=spans,
        min_days=min_depth_days,
    )
    by_upper = {s.upper(): df for s, df in ohlcv_by_symbol.items()}
    filtered = {s: by_upper[s] for s in eligible if s in by_upper}

    panel, as_of = _align_return_panel(filtered, timeframe=CORR_TIMEFRAME)
    if as_of is None:
        as_of = datetime(1970, 1, 1, tzinfo=UTC)
    if panel.empty or len(panel.columns) < 2:
        return CorrelationMatrixResult(
            timeframe=CORR_TIMEFRAME,
            window_days=window_days,
            symbols=tuple(eligible),
            excluded=tuple(excluded),
            entries=(),
            as_of=as_of,
        )

    # Trailing window by calendar days on the index
    cutoff = as_of - pd.Timedelta(days=window_days)
    window = panel.loc[panel.index >= cutoff]
    # Drop rows that are all-NaN; pairwise corr handles remaining NaNs
    window = window.dropna(how="all")
    if len(window) < 2:
        return CorrelationMatrixResult(
            timeframe=CORR_TIMEFRAME,
            window_days=window_days,
            symbols=tuple(sorted(window.columns.astype(str))),
            excluded=tuple(excluded),
            entries=(),
            as_of=as_of,
        )

    corr = window.corr(method="pearson", min_periods=max(10, window_days // 2))
    entries: list[CorrelationEntry] = []
    cols = list(corr.columns.astype(str))
    for i, a in enumerate(cols):
        for b in cols[i + 1 :]:
            val = corr.loc[a, b]
            if val is None or (isinstance(val, float) and not np.isfinite(val)):
                continue
            entries.append(
                CorrelationEntry(
                    symbol_a=a,
                    symbol_b=b,
                    coefficient=float(val),
                    window_days=window_days,
                )
            )

    return CorrelationMatrixResult(
        timeframe=CORR_TIMEFRAME,
        window_days=window_days,
        symbols=tuple(cols),
        excluded=tuple(excluded),
        entries=tuple(entries),
        as_of=as_of,
        model_version=MODEL_VERSION,
    )
