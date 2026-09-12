"""Load OHLCV frames for analytics from prices / continuous aggregates."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.analytics.metrics import TIMEFRAMES, Timeframe

_TABLE_FOR_TF: dict[Timeframe, str] = {
    "M1": "prices",
    "M15": "prices_m15",
    "H1": "prices_h1",
    "H4": "prices_h4",
    "D1": "prices_d1",
}

_TS_COL: dict[Timeframe, str] = {
    "M1": "ts",
    "M15": "bucket",
    "H1": "bucket",
    "H4": "bucket",
    "D1": "bucket",
}


def load_ohlcv(
    session: Session,
    symbol: str,
    timeframe: Timeframe,
    *,
    lookback_days: int = 120,
    end_utc: datetime | None = None,
) -> pd.DataFrame:
    """
    Load OHLCV for ``symbol``/``timeframe`` ending at ``end_utc`` (default now).

    Returns columns: ts, open, high, low, close, volume (volume may be null on some caggs).
    """
    if timeframe not in TIMEFRAMES:
        raise ValueError(f"unsupported timeframe: {timeframe}")
    end = end_utc or datetime.now(UTC)
    if end.tzinfo is None:
        end = end.replace(tzinfo=UTC)
    start = end - timedelta(days=lookback_days)
    table = _TABLE_FOR_TF[timeframe]
    ts_col = _TS_COL[timeframe]
    sql = text(
        f"""
        SELECT {ts_col} AS ts, open, high, low, close, volume
        FROM {table}
        WHERE symbol = :symbol
          AND {ts_col} >= :start_ts
          AND {ts_col} <= :end_ts
        ORDER BY {ts_col} ASC
        """
    )
    rows = session.execute(
        sql,
        {"symbol": symbol.upper(), "start_ts": start, "end_ts": end},
    ).mappings().all()
    if not rows:
        return pd.DataFrame(columns=["ts", "open", "high", "low", "close", "volume"])
    return pd.DataFrame([dict(r) for r in rows])


def m1_depth_days(session: Session, symbol: str) -> float:
    """Calendar-day span of M1 history for ``symbol`` (0 if missing)."""
    row = session.execute(
        text(
            "SELECT min(ts) AS first_ts, max(ts) AS last_ts "
            "FROM prices WHERE symbol = :symbol"
        ),
        {"symbol": symbol.upper()},
    ).mappings().one()
    first, last = row["first_ts"], row["last_ts"]
    if first is None or last is None:
        return 0.0
    return max((last - first).total_seconds() / 86400.0, 0.0)
