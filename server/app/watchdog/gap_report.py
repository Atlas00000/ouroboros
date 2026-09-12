"""Backfill integrity — M1 gap scan over prices (weekday / session-aware)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.calendar.sessions import is_fx_weekend_closed
from app.calendar.timebase import ensure_utc

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PriceGap:
    symbol: str
    from_ts: datetime
    to_ts: datetime
    missing_minutes: int


@dataclass(frozen=True)
class SymbolGapReport:
    symbol: str
    bar_count: int
    min_ts: datetime | None
    max_ts: datetime | None
    gaps: list[PriceGap]

    @property
    def gap_count(self) -> int:
        return len(self.gaps)

    @property
    def missing_minutes_total(self) -> int:
        return sum(g.missing_minutes for g in self.gaps)


@dataclass(frozen=True)
class GapReport:
    generated_at: datetime
    symbols: list[SymbolGapReport]

    @property
    def symbols_with_gaps(self) -> int:
        return sum(1 for s in self.symbols if s.gap_count)


def _scan_symbol_gaps(
    session: Session,
    symbol: str,
    *,
    min_hole_minutes: int = 2,
    max_gaps: int = 50,
) -> SymbolGapReport:
    """
    Find M1 holes using lag(ts). Skips holes whose midpoint falls in FX weekend.
    """
    row = session.execute(
        text(
            "SELECT count(*)::int, min(ts), max(ts) FROM prices WHERE symbol = :s"
        ),
        {"s": symbol},
    ).one()
    bar_count, min_ts, max_ts = int(row[0]), row[1], row[2]
    if bar_count < 2 or min_ts is None or max_ts is None:
        return SymbolGapReport(symbol, bar_count, min_ts, max_ts, [])

    # Windowed lag in SQL — only emit candidate holes >= min_hole_minutes.
    rows = session.execute(
        text(
            """
            WITH ordered AS (
              SELECT ts,
                     lag(ts) OVER (ORDER BY ts) AS prev_ts
              FROM prices
              WHERE symbol = :s
            )
            SELECT prev_ts, ts,
                   EXTRACT(EPOCH FROM (ts - prev_ts)) / 60.0 AS delta_min
            FROM ordered
            WHERE prev_ts IS NOT NULL
              AND EXTRACT(EPOCH FROM (ts - prev_ts)) >= :min_secs
            ORDER BY prev_ts
            LIMIT :lim
            """
        ),
        {
            "s": symbol,
            "min_secs": min_hole_minutes * 60,
            "lim": max_gaps * 3,  # filter weekend after
        },
    ).fetchall()

    gaps: list[PriceGap] = []
    for prev_ts, ts, delta_min in rows:
        prev = ensure_utc(prev_ts)
        cur = ensure_utc(ts)
        mid = prev + (cur - prev) / 2
        if is_fx_weekend_closed(mid):
            continue
        missing = int(delta_min) - 1  # expected contiguous minutes between bars
        if missing < min_hole_minutes:
            continue
        gaps.append(
            PriceGap(
                symbol=symbol,
                from_ts=prev + timedelta(minutes=1),
                to_ts=cur,
                missing_minutes=missing,
            )
        )
        if len(gaps) >= max_gaps:
            break

    return SymbolGapReport(symbol, bar_count, min_ts, max_ts, gaps)


def build_gap_report(
    session: Session,
    *,
    symbols: list[str] | None = None,
    min_hole_minutes: int = 2,
    max_gaps_per_symbol: int = 50,
) -> GapReport:
    if symbols is None:
        symbols = [
            r[0]
            for r in session.execute(
                text("SELECT symbol FROM assets WHERE is_active = true ORDER BY symbol")
            ).fetchall()
        ]

    reports: list[SymbolGapReport] = []
    for symbol in symbols:
        rep = _scan_symbol_gaps(
            session,
            symbol,
            min_hole_minutes=min_hole_minutes,
            max_gaps=max_gaps_per_symbol,
        )
        logger.info(
            "gap scan symbol=%s bars=%s gaps=%s missing_min=%s",
            symbol,
            rep.bar_count,
            rep.gap_count,
            rep.missing_minutes_total,
        )
        reports.append(rep)

    return GapReport(generated_at=datetime.now(UTC), symbols=reports)
