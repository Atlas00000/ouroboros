"""Macro series observations (FRED and future providers)."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Index, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MacroObservation(Base):
    __tablename__ = "macro_observations"
    __table_args__ = (
        UniqueConstraint("series_id", "obs_date", name="uq_macro_series_date"),
        Index("ix_macro_series_date", "series_id", "obs_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    series_id: Mapped[str] = mapped_column(String(64), nullable=False)
    obs_date: Mapped[date] = mapped_column(Date, nullable=False)
    value: Mapped[Decimal | None] = mapped_column(Numeric(24, 8), nullable=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="fred")
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
