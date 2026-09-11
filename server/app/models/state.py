"""Persisted market state / regime classifications."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MarketStateRow(Base):
    __tablename__ = "states"
    __table_args__ = (Index("ix_states_symbol_tf_as_of", "symbol", "timeframe", "as_of"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(32), ForeignKey("assets.symbol"), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(8), nullable=False)
    regime: Mapped[str] = mapped_column(String(32), nullable=False)
    probabilities_json: Mapped[str] = mapped_column(Text, nullable=False)
    volatility_percentile: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    trend_strength: Mapped[Decimal | None] = mapped_column(Numeric(6, 4), nullable=True)
    as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    model_version: Mapped[str] = mapped_column(String(64), nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False, default=0)
    stale: Mapped[bool] = mapped_column(default=False, nullable=False)
    sources_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
