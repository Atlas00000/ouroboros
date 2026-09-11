"""Persisted sentiment snapshots."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SentimentRow(Base):
    __tablename__ = "sentiment"
    __table_args__ = (Index("ix_sentiment_symbol_as_of", "symbol", "as_of"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(32), ForeignKey("assets.symbol"), nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    item_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    window_hours: Mapped[int] = mapped_column(Integer, nullable=False, default=24)
    top_drivers_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    model_version: Mapped[str] = mapped_column(String(64), nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False, default=0)
    stale: Mapped[bool] = mapped_column(default=False, nullable=False)
    sources_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
