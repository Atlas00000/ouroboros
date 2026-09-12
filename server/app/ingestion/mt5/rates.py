"""Fetch M1 OHLCV bars from MT5."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Iterator

from app.calendar.timebase import ensure_utc
from app.config import Settings, get_settings
from app.ingestion.mt5.connection import _import_mt5

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RawBar:
    """One M1 bar in UTC."""

    ts: datetime
    open: float
    high: float
    low: float
    close: float
    tick_volume: int
    real_volume: float


def ensure_symbol_selected(mt5_ticker: str) -> None:
    mt5 = _import_mt5()
    if not mt5.symbol_select(mt5_ticker, True):
        code, message = mt5.last_error()
        raise RuntimeError(f"symbol_select({mt5_ticker}) failed: {code} {message}")


def _row_to_bar(row: object) -> RawBar:
    # MT5 rate time is Unix epoch seconds (UTC absolute).
    ts = datetime.fromtimestamp(int(row["time"]), tz=UTC)  # type: ignore[index]
    return RawBar(
        ts=ts,
        open=float(row["open"]),  # type: ignore[index]
        high=float(row["high"]),  # type: ignore[index]
        low=float(row["low"]),  # type: ignore[index]
        close=float(row["close"]),  # type: ignore[index]
        tick_volume=int(row["tick_volume"]),  # type: ignore[index]
        real_volume=float(row["real_volume"]),  # type: ignore[index]
    )


def fetch_m1_range(
    mt5_ticker: str,
    start_utc: datetime,
    end_utc: datetime,
    *,
    settings: Settings | None = None,  # noqa: ARG001 — reserved for future knobs
    chunk_days: int = 30,
) -> Iterator[list[RawBar]]:
    """
    Yield chunks of M1 bars for [start_utc, end_utc).

    Uses monthly-ish windows for resumability and smaller IPC payloads.
    """
    _ = settings or get_settings()
    mt5 = _import_mt5()
    ensure_symbol_selected(mt5_ticker)

    start = ensure_utc(start_utc)
    end = ensure_utc(end_utc)
    if end <= start:
        return

    cursor = start
    while cursor < end:
        window_end = min(cursor + timedelta(days=chunk_days), end)
        # MT5 accepts naive UTC datetimes for range bounds.
        from_dt = cursor.replace(tzinfo=None)
        to_dt = window_end.replace(tzinfo=None)

        rates = mt5.copy_rates_range(mt5_ticker, mt5.TIMEFRAME_M1, from_dt, to_dt)
        if rates is None:
            code, message = mt5.last_error()
            logger.warning(
                "copy_rates_range empty ticker=%s window=%s..%s err=%s %s",
                mt5_ticker,
                cursor.isoformat(),
                window_end.isoformat(),
                code,
                message,
            )
            cursor = window_end
            continue

        bars = [_row_to_bar(row) for row in rates]
        bars = [b for b in bars if start <= b.ts < end]
        logger.info(
            "fetched bars ticker=%s count=%s window=%s..%s",
            mt5_ticker,
            len(bars),
            cursor.date(),
            window_end.date(),
        )
        if bars:
            yield bars
        cursor = window_end


def probe_rates(mt5_ticker: str, *, bars: int = 10) -> list[RawBar]:
    """Fetch the last N M1 bars (connectivity / symbol sanity check)."""
    mt5 = _import_mt5()
    ensure_symbol_selected(mt5_ticker)
    rates = mt5.copy_rates_from_pos(mt5_ticker, mt5.TIMEFRAME_M1, 0, bars)
    if rates is None:
        code, message = mt5.last_error()
        raise RuntimeError(f"copy_rates_from_pos failed: {code} {message}")
    return [_row_to_bar(row) for row in rates]
