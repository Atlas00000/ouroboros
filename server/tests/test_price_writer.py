"""Unit tests for price writer upsert (DB required)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select, text

from app.db.session import get_session_factory
from app.ingestion.mt5.rates import RawBar
from app.ingestion.mt5.writer import count_bars, upsert_bars
from app.models.price import PriceBar


def test_upsert_bars_idempotent() -> None:
    session = get_session_factory()()
    try:
        # Ensure asset exists (seeded)
        symbol = "EURUSD"
        exists = session.execute(
            text("SELECT 1 FROM assets WHERE symbol = :s"), {"s": symbol}
        ).scalar()
        assert exists == 1

        ts = datetime(2020, 1, 2, 10, 0, tzinfo=UTC)
        bar = RawBar(ts=ts, open=1.1, high=1.2, low=1.0, close=1.15, tick_volume=10, real_volume=0)
        upsert_bars(session, symbol, [bar])
        upsert_bars(
            session,
            symbol,
            [RawBar(ts=ts, open=1.11, high=1.21, low=1.01, close=1.16, tick_volume=11, real_volume=0)],
        )

        rows = session.scalars(
            select(PriceBar).where(PriceBar.symbol == symbol, PriceBar.ts == ts)
        ).all()
        assert len(rows) == 1
        assert rows[0].close == Decimal("1.16000000") or float(rows[0].close) == 1.16
        assert count_bars(session, symbol) >= 1

        # cleanup test row
        session.execute(
            text("DELETE FROM prices WHERE symbol = :s AND ts = :ts"),
            {"s": symbol, "ts": ts},
        )
        session.commit()
    finally:
        session.close()
