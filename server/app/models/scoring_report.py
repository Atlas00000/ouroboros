"""Weekly regime accuracy scoring reports (W8·D1)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ScoringWeeklyReport(Base):
    __tablename__ = "scoring_weekly_reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    week_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    week_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    n_scored: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    n_correct: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    accuracy: Mapped[Decimal | None] = mapped_column(Numeric(6, 4), nullable=True)
    report_json: Mapped[str] = mapped_column(Text, nullable=False)
    email_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
