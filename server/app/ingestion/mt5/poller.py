"""Live M1 price poller — gap detection + re-fetch, then upsert."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.calendar.sessions import is_fx_weekend_closed
from app.calendar.timebase import ensure_utc
from app.config import Settings, get_settings
from app.db.session import get_session_factory
from app.ingestion.mt5.connection import disconnect, ensure_connected
from app.ingestion.mt5.rates import RawBar, fetch_m1_range
from app.ingestion.mt5.symbols import SymbolMapper
from app.ingestion.mt5.writer import heartbeat_source, latest_bar_ts, upsert_bars

logger = logging.getLogger(__name__)

# If DB lags live clock by more than this during market hours, treat as a gap.
DEFAULT_GAP_THRESHOLD = timedelta(minutes=3)
# When a symbol has never been seen, only pull a short recent window (backfill owns history).
DEFAULT_COLD_LOOKBACK = timedelta(hours=6)


@dataclass(frozen=True)
class GapWindow:
    symbol: str
    from_ts: datetime
    to_ts: datetime
    missing_minutes: int


@dataclass(frozen=True)
class SymbolPollResult:
    symbol: str
    mt5_ticker: str
    bars_written: int
    from_ts: datetime | None
    to_ts: datetime | None
    gap: GapWindow | None


def floor_minute(dt: datetime) -> datetime:
    utc = ensure_utc(dt)
    return utc.replace(second=0, microsecond=0)


def closed_bar_exclusive_end(now: datetime | None = None) -> datetime:
    """Exclusive end for fetch: start of current UTC minute (last closed bar is prior)."""
    return floor_minute(now or datetime.now(UTC))


def detect_gap(
    *,
    symbol: str,
    last_ts: datetime | None,
    end_exclusive: datetime,
    threshold: timedelta = DEFAULT_GAP_THRESHOLD,
) -> GapWindow | None:
    """
    Detect a staleness gap between DB latest and the closed-bar frontier.

    Weekend FX closure is ignored so Friday→Sunday reopen is not a false gap.
    """
    if last_ts is None:
        return None

    last = ensure_utc(last_ts)
    end = ensure_utc(end_exclusive)
    expected_next = last + timedelta(minutes=1)
    if expected_next >= end:
        return None

    lag = end - expected_next
    if lag < threshold:
        return None

    # Sample midpoint of the hole; skip if that instant is weekend-closed.
    mid = expected_next + (end - expected_next) / 2
    if is_fx_weekend_closed(mid):
        return None

    missing = int(lag.total_seconds() // 60)
    return GapWindow(symbol=symbol, from_ts=expected_next, to_ts=end, missing_minutes=missing)


def _fetch_window(mt5_ticker: str, start: datetime, end: datetime) -> list[RawBar]:
    bars: list[RawBar] = []
    for chunk in fetch_m1_range(mt5_ticker, start, end, chunk_days=7):
        bars.extend(chunk)
    return bars


def poll_symbol(
    session: Session,
    *,
    symbol: str,
    mt5_ticker: str,
    now: datetime | None = None,
    lookback: timedelta = DEFAULT_COLD_LOOKBACK,
    gap_threshold: timedelta = DEFAULT_GAP_THRESHOLD,
    settings: Settings | None = None,
) -> SymbolPollResult:
    """Pull closed M1 bars since last DB ts (or lookback), re-fetch on gap, upsert."""
    _ = settings or get_settings()
    end = closed_bar_exclusive_end(now)
    last = latest_bar_ts(session, symbol)

    if last is None:
        start = end - lookback
    else:
        start = ensure_utc(last) + timedelta(minutes=1)

    gap = detect_gap(symbol=symbol, last_ts=last, end_exclusive=end, threshold=gap_threshold)
    if gap is not None:
        logger.warning(
            "gap detected symbol=%s missing_minutes=%s from=%s to=%s — re-fetching",
            symbol,
            gap.missing_minutes,
            gap.from_ts.isoformat(),
            gap.to_ts.isoformat(),
        )
        start = min(start, gap.from_ts)

    if start >= end:
        return SymbolPollResult(symbol, mt5_ticker, 0, last, last, gap)

    bars = _fetch_window(mt5_ticker, start, end)
    written = upsert_bars(session, symbol, bars) if bars else 0
    heartbeat_source(session)

    first = bars[0].ts if bars else None
    last_written = bars[-1].ts if bars else None
    return SymbolPollResult(
        symbol=symbol,
        mt5_ticker=mt5_ticker,
        bars_written=written,
        from_ts=first,
        to_ts=last_written,
        gap=gap,
    )


def poll_once(
    *,
    symbols: list[str] | None = None,
    settings: Settings | None = None,
    lookback: timedelta = DEFAULT_COLD_LOOKBACK,
    gap_threshold: timedelta = DEFAULT_GAP_THRESHOLD,
) -> list[SymbolPollResult]:
    """One poll cycle across the active universe (or subset)."""
    cfg = settings or get_settings()
    ensure_connected(cfg)
    session = get_session_factory()()
    results: list[SymbolPollResult] = []
    try:
        mapper = SymbolMapper.from_session(session)
        targets = [s.upper() for s in symbols] if symbols else mapper.all_symbols()
        for symbol in targets:
            ticker = mapper.to_mt5(symbol)
            result = poll_symbol(
                session,
                symbol=symbol,
                mt5_ticker=ticker,
                lookback=lookback,
                gap_threshold=gap_threshold,
                settings=cfg,
            )
            logger.info(
                "poll symbol=%s written=%s gap=%s",
                symbol,
                result.bars_written,
                result.gap.missing_minutes if result.gap else None,
            )
            results.append(result)
    finally:
        session.close()
    return results


def run_poll_loop(
    *,
    interval_seconds: float = 60.0,
    symbols: list[str] | None = None,
    settings: Settings | None = None,
    max_cycles: int | None = None,
) -> None:
    """
    Continuously poll until interrupted.

    Keeps a single MT5 connection for the process lifetime.
    """
    cfg = settings or get_settings()
    ensure_connected(cfg)
    cycles = 0
    try:
        while max_cycles is None or cycles < max_cycles:
            started = time.monotonic()
            results = poll_once(symbols=symbols, settings=cfg)
            total = sum(r.bars_written for r in results)
            gaps = sum(1 for r in results if r.gap is not None)
            logger.info(
                "poll cycle done symbols=%s bars_written=%s gaps=%s",
                len(results),
                total,
                gaps,
            )
            cycles += 1
            if max_cycles is not None and cycles >= max_cycles:
                break
            elapsed = time.monotonic() - started
            sleep_for = max(0.0, interval_seconds - elapsed)
            time.sleep(sleep_for)
    finally:
        disconnect()
