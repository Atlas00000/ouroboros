"""Historical M1 backfill — idempotent and resumable."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db.session import get_session_factory
from app.ingestion.mt5.connection import disconnect, ensure_connected
from app.ingestion.mt5.rates import fetch_m1_range
from app.ingestion.mt5.symbols import SymbolMapper
from app.ingestion.mt5.writer import count_bars, heartbeat_source, latest_bar_ts, upsert_bars

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BackfillResult:
    symbol: str
    mt5_ticker: str
    bars_written: int
    from_ts: datetime | None
    to_ts: datetime | None
    resumed: bool
    error: str | None = None


def backfill_symbol(
    session: Session,
    *,
    symbol: str,
    mt5_ticker: str,
    years: float = 2.0,
    end_utc: datetime | None = None,
    chunk_days: int = 14,
    settings: Settings | None = None,
    no_resume: bool = False,
) -> BackfillResult:
    """
    Backfill one symbol.

    Resume: if bars already exist, continue from last ts + 1 minute.
    Use no_resume=True to re-fetch the full years window (upserts are idempotent).
    """
    cfg = settings or get_settings()
    end = end_utc or datetime.now(UTC)
    start = end - timedelta(days=int(years * 365.25))

    last = latest_bar_ts(session, symbol)
    resumed = False
    if not no_resume and last is not None and last > start:
        start = last + timedelta(minutes=1)
        resumed = True

    if start >= end:
        logger.info("symbol=%s already up to date last=%s", symbol, last)
        return BackfillResult(symbol, mt5_ticker, 0, last, last, resumed=True)

    written = 0
    first_ts: datetime | None = None
    last_ts: datetime | None = None
    for chunk in fetch_m1_range(
        mt5_ticker,
        start,
        end,
        settings=cfg,
        chunk_days=chunk_days,
    ):
        n = upsert_bars(session, symbol, chunk)
        written += n
        if chunk:
            first_ts = first_ts or chunk[0].ts
            last_ts = chunk[-1].ts
        heartbeat_source(session)

    return BackfillResult(
        symbol=symbol,
        mt5_ticker=mt5_ticker,
        bars_written=written,
        from_ts=first_ts or start,
        to_ts=last_ts or end,
        resumed=resumed,
    )


def backfill_universe(
    *,
    years: float = 2.0,
    symbols: list[str] | None = None,
    chunk_days: int = 14,
    settings: Settings | None = None,
    no_resume: bool = False,
) -> list[BackfillResult]:
    """Connect to MT5 and backfill active universe (or a symbol subset)."""
    cfg = settings or get_settings()
    ensure_connected(cfg)
    session = get_session_factory()()
    results: list[BackfillResult] = []
    try:
        mapper = SymbolMapper.from_session(session)
        targets = [s.upper() for s in symbols] if symbols else mapper.all_symbols()
        for symbol in targets:
            ticker = mapper.to_mt5(symbol)
            logger.info("backfill start symbol=%s ticker=%s years=%s", symbol, ticker, years)
            try:
                result = backfill_symbol(
                    session,
                    symbol=symbol,
                    mt5_ticker=ticker,
                    years=years,
                    chunk_days=chunk_days,
                    settings=cfg,
                    no_resume=no_resume,
                )
            except Exception as exc:  # noqa: BLE001 — continue universe on per-symbol MT5 failures
                logger.exception("backfill failed symbol=%s ticker=%s", symbol, ticker)
                results.append(
                    BackfillResult(
                        symbol=symbol,
                        mt5_ticker=ticker,
                        bars_written=0,
                        from_ts=None,
                        to_ts=None,
                        resumed=False,
                        error=str(exc),
                    )
                )
                continue
            total = count_bars(session, symbol)
            logger.info(
                "backfill done symbol=%s written=%s total_in_db=%s resumed=%s",
                symbol,
                result.bars_written,
                total,
                result.resumed,
            )
            results.append(result)
    finally:
        session.close()
        disconnect()
    return results
