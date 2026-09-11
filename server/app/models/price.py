"""M1 OHLCV bars — Timescale hypertable on `ts`."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PriceBar(Base):
    """1-minute OHLCV. Composite PK (symbol, ts) required for hypertable."""

    __tablename__ = "prices"
    __table_args__ = (Index("ix_prices_symbol_ts", "symbol", "ts"),)

    symbol: Mapped[str] = mapped_column(String(32), ForeignKey("assets.symbol"), primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    open: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    high: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    low: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    close: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    volume: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False, default=0)
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="mt5")
    ingested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    tick_volume: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
