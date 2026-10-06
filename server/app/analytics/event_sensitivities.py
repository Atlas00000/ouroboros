"""Event sensitivity estimates for profile.v1 dossiers.

Uses econ-calendar taxonomy + post-event H1 range vs ATR when enough history exists.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import numpy as np
import pandas as pd
from contracts.profile_v1 import EventSensitivity
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.metrics import wilder_atr
from app.calendar.timebase import ensure_utc
from app.ingestion.econ_calendar.impact import _COUNTRY_SYMBOLS, _HIGH_IMPACT_EVENTS
from app.models.news import NewsItem

# Minimum post-event samples before we emit a typical ATR multiple.
MIN_EVENT_SAMPLES = 3
# H1 bars after scheduled_at used for move estimate.
POST_EVENT_BARS = 4

# Headline / token → canonical event_type for profile.v1.
_EVENT_TYPE_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("NFP", ("non-farm", "nonfarm", "nfp", "payroll")),
    ("CPI", ("cpi", "consumer price", "pce")),
    ("FOMC", ("fomc", "fed interest", "federal reserve")),
    ("GDP", ("gdp",)),
    (
        "central_bank",
        (
            "interest rate decision",
            "ecb",
            "boe",
            "boj",
            "rba",
            "snb",
            "ism manufacturing",
            "unemployment rate",
        ),
    ),
)

# Symbol → event types that typically matter (from country→symbol map).
_SYMBOL_EVENT_TYPES: dict[str, tuple[str, ...]] = {
    "EURUSD": ("NFP", "CPI", "FOMC", "GDP", "central_bank"),
    "GBPUSD": ("NFP", "CPI", "FOMC", "GDP", "central_bank"),
    "USDJPY": ("NFP", "CPI", "FOMC", "GDP", "central_bank"),
    "USDCHF": ("NFP", "CPI", "FOMC", "central_bank"),
    "AUDUSD": ("NFP", "CPI", "FOMC", "central_bank"),
    "USDCAD": ("NFP", "CPI", "FOMC", "central_bank"),
    "NZDUSD": ("NFP", "CPI", "FOMC", "central_bank"),
    "EURGBP": ("CPI", "GDP", "central_bank"),
    "EURJPY": ("CPI", "GDP", "central_bank"),
    "GBPJPY": ("CPI", "GDP", "central_bank"),
    "XAUUSD": ("NFP", "CPI", "FOMC"),
    "XAGUSD": ("NFP", "CPI", "FOMC"),
    "US500": ("NFP", "CPI", "FOMC", "GDP"),
    "US30": ("NFP", "CPI", "FOMC", "GDP"),
    "NAS100": ("NFP", "CPI", "FOMC", "GDP"),
}


def classify_event_type(headline: str) -> str | None:
    """Map a calendar headline onto a profile event_type label."""
    name = (headline or "").lower()
    for event_type, tokens in _EVENT_TYPE_RULES:
        if any(tok in name for tok in tokens):
            return event_type
    # Fallback: any high-impact token → central_bank bucket
    if any(tok in name for tok in _HIGH_IMPACT_EVENTS):
        return "central_bank"
    return None


def event_types_for_symbol(symbol: str) -> tuple[str, ...]:
    sym = symbol.upper()
    if sym in _SYMBOL_EVENT_TYPES:
        return _SYMBOL_EVENT_TYPES[sym]
    # Any symbol appearing in country maps gets a conservative default set.
    for symbols in _COUNTRY_SYMBOLS.values():
        if sym in symbols:
            return ("NFP", "CPI", "FOMC", "central_bank")
    return ("NFP", "CPI", "FOMC")


def _frame_atr_series(h1: pd.DataFrame) -> pd.Series:
    atr = wilder_atr(h1["high"], h1["low"], h1["close"], period=14)
    return atr


def _post_event_atr_multiple(
    h1: pd.DataFrame,
    atr: pd.Series,
    event_at: datetime,
) -> float | None:
    """Max H1 range over POST_EVENT_BARS after event, divided by pre-event ATR."""
    if h1.empty or "ts" not in h1.columns:
        return None
    ts = pd.to_datetime(h1["ts"], utc=True)
    moment = ensure_utc(event_at)
    after = h1.loc[ts >= pd.Timestamp(moment)].head(POST_EVENT_BARS)
    if len(after) < 1:
        return None
    # ATR as of last bar before event (or first after if none).
    before_mask = ts < pd.Timestamp(moment)
    if before_mask.any():
        atr_val = float(atr.loc[before_mask].iloc[-1])
    else:
        atr_val = float(atr.iloc[after.index[0]]) if len(atr) else float("nan")
    if not np.isfinite(atr_val) or atr_val <= 0:
        return None
    high = pd.to_numeric(after["high"], errors="coerce").astype(float)
    low = pd.to_numeric(after["low"], errors="coerce").astype(float)
    move = float((high - low).abs().max())
    if not np.isfinite(move):
        return None
    return move / atr_val


def compute_event_sensitivities(
    symbol: str,
    *,
    h1_ohlcv: pd.DataFrame | None,
    events: list[tuple[str, datetime]],
) -> list[EventSensitivity]:
    """
    Build EventSensitivity rows for a symbol.

    ``events`` is a list of ``(event_type, scheduled_at)`` samples.
    Emits one row per relevant event_type; ATR multiple only when ≥ MIN_EVENT_SAMPLES.
    """
    sym = symbol.upper()
    types = event_types_for_symbol(sym)
    by_type: dict[str, list[datetime]] = {t: [] for t in types}
    for etype, when in events:
        if etype in by_type:
            by_type[etype].append(ensure_utc(when))

    atr: pd.Series | None = None
    frame = h1_ohlcv
    if frame is not None and not frame.empty and len(frame) >= 20:
        atr = _frame_atr_series(frame)

    out: list[EventSensitivity] = []
    for etype in types:
        samples = sorted(by_type.get(etype, []))
        multiples: list[float] = []
        if atr is not None and frame is not None:
            for when in samples:
                m = _post_event_atr_multiple(frame, atr, when)
                if m is not None:
                    multiples.append(m)

        if len(multiples) >= MIN_EVENT_SAMPLES:
            typical = float(np.median(multiples))
            out.append(
                EventSensitivity(
                    event_type=etype,
                    typical_move_atr_multiple=round(typical, 3),
                    notes=f"Median H1 range / ATR over {len(multiples)} events ({POST_EVENT_BARS}h window).",
                )
            )
        else:
            n = len(samples)
            note = (
                f"Relevant for {sym}; need ≥{MIN_EVENT_SAMPLES} scored windows "
                f"(have {len(multiples)} moves from {n} calendar hits)."
            )
            out.append(
                EventSensitivity(
                    event_type=etype,
                    typical_move_atr_multiple=None,
                    notes=note,
                )
            )
    return out


def load_calendar_events_for_symbol(
    session: Session,
    symbol: str,
    *,
    lookback_days: int = 400,
) -> list[tuple[str, datetime]]:
    """Load high-impact calendar headlines for symbol and classify event types."""
    sym = symbol.upper()
    cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
    rows = list(
        session.scalars(
            select(NewsItem)
            .where(
                NewsItem.is_calendar.is_(True),
                NewsItem.symbol == sym,
                NewsItem.impact == "high",
                NewsItem.scheduled_at.is_not(None),
                NewsItem.scheduled_at >= cutoff,
            )
            .order_by(NewsItem.scheduled_at.desc())
            .limit(200)
        ).all()
    )
    out: list[tuple[str, datetime]] = []
    for row in rows:
        etype = classify_event_type(row.headline or "")
        if etype is None or row.scheduled_at is None:
            continue
        out.append((etype, ensure_utc(row.scheduled_at)))
    return out


def event_sensitivities_from_session(
    session: Session,
    symbol: str,
    *,
    h1_ohlcv: pd.DataFrame | None,
) -> list[EventSensitivity]:
    events = load_calendar_events_for_symbol(session, symbol)
    return compute_event_sensitivities(symbol, h1_ohlcv=h1_ohlcv, events=events)
