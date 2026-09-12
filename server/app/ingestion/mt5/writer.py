"""Persist price bars into Timescale `prices` hypertable."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.ingestion.mt5.rates import RawBar
from app.models.price import PriceBar

logger = logging.getLogger(__name__)

# Postgres bind limit is 65535 params; 10 cols/row → keep batches well under.
_UPSERT_BATCH = 500


def latest_bar_ts(session: Session, symbol: str) -> datetime | None:
    return session.scalar(select(func.max(PriceBar.ts)).where(PriceBar.symbol == symbol))


def upsert_bars(session: Session, symbol: str, bars: list[RawBar]) -> int:
    """Idempotent upsert in batches; returns number of rows attempted."""
    if not bars:
        return 0

    now = datetime.now(UTC)
    total = 0
    for i in range(0, len(bars), _UPSERT_BATCH):
        chunk = bars[i : i + _UPSERT_BATCH]
        rows = [
            {
                "symbol": symbol,
                "ts": bar.ts,
                "open": Decimal(str(bar.open)),
                "high": Decimal(str(bar.high)),
                "low": Decimal(str(bar.low)),
                "close": Decimal(str(bar.close)),
                "volume": Decimal(str(bar.real_volume)),
                "source": "mt5",
                "ingested_at": now,
                "tick_volume": bar.tick_volume,
            }
            for bar in chunk
        ]
        stmt = insert(PriceBar).values(rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=["symbol", "ts"],
            set_={
                "open": stmt.excluded.open,
                "high": stmt.excluded.high,
                "low": stmt.excluded.low,
                "close": stmt.excluded.close,
                "volume": stmt.excluded.volume,
                "source": stmt.excluded.source,
                "ingested_at": stmt.excluded.ingested_at,
                "tick_volume": stmt.excluded.tick_volume,
            },
        )
        session.execute(stmt)
        session.commit()
        total += len(rows)

    logger.info("upserted bars symbol=%s count=%s", symbol, total)
    return total


def count_bars(session: Session, symbol: str) -> int:
    return int(
        session.scalar(select(func.count()).select_from(PriceBar).where(PriceBar.symbol == symbol))
        or 0
    )


def heartbeat_source(session: Session, source_id: str = "mt5.prices") -> None:
    session.execute(
        text(
            "UPDATE source_registry SET last_seen_at = now(), status = 'ok', updated_at = now() "
            "WHERE source_id = :sid"
        ),
        {"sid": source_id},
    )
    session.commit()
