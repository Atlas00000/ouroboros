"""Asset universe — canonical symbols."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    asset_class: Mapped[str] = mapped_column(String(32), nullable=False, default="fx")
    mt5_ticker: Mapped[str | None] = mapped_column(String(64), nullable=True)
    base_currency: Mapped[str | None] = mapped_column(String(16), nullable=True)
    quote_currency: Mapped[str | None] = mapped_column(String(16), nullable=True)
    venues: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as text for MVP
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
