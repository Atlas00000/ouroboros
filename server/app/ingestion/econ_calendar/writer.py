"""Persist economic calendar events into the news table."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.ingestion.econ_calendar.impact import FlaggedCalendarEvent
from app.models.news import NewsItem

logger = logging.getLogger(__name__)


def _external_id(provider: str, provider_id: str, symbol: str | None) -> str:
    base = f"{provider}.cal:{provider_id}"
    return f"{base}:{symbol}" if symbol else base


def upsert_calendar_events(session: Session, flagged: list[FlaggedCalendarEvent]) -> int:
    if not flagged:
        return 0

    now = datetime.now(UTC)
    rows: list[dict] = []
    for item in flagged:
        ev = item.event
        summary_parts = [
            f"country={ev.country}",
            f"impact={item.impact}",
        ]
        if ev.actual is not None:
            summary_parts.append(f"actual={ev.actual}")
        if ev.estimate is not None:
            summary_parts.append(f"estimate={ev.estimate}")
        if ev.previous is not None:
            summary_parts.append(f"prev={ev.previous}")
        if ev.unit:
            summary_parts.append(f"unit={ev.unit}")
        summary = "; ".join(summary_parts)

        targets: list[str | None] = list(item.symbols) if item.symbols else [None]
        for symbol in targets:
            rows.append(
                {
                    "external_id": _external_id(ev.provider, ev.provider_id, symbol),
                    "symbol": symbol,
                    "headline": ev.event[:4000],
                    "summary": summary,
                    "url": None,
                    "source": (
                        "finnhub.calendar"
                        if ev.provider == "finnhub"
                        else f"{ev.provider}.calendar"
                    ),
                    "event_type": "economic_calendar",
                    "impact": item.impact if item.impact != "unknown" else None,
                    "is_calendar": True,
                    "published_at": ev.scheduled_at,
                    "scheduled_at": ev.scheduled_at,
                    "ingested_at": now,
                }
            )

    before = int(session.scalar(select(func.count()).select_from(NewsItem)) or 0)
    # Chunk to stay under Postgres param limits.
    batch = 200
    for i in range(0, len(rows), batch):
        chunk = rows[i : i + batch]
        stmt = insert(NewsItem).values(chunk)
        stmt = stmt.on_conflict_do_update(
            index_elements=["external_id"],
            set_={
                "headline": stmt.excluded.headline,
                "summary": stmt.excluded.summary,
                "impact": stmt.excluded.impact,
                "scheduled_at": stmt.excluded.scheduled_at,
                "published_at": stmt.excluded.published_at,
                "ingested_at": stmt.excluded.ingested_at,
            },
        )
        session.execute(stmt)
    session.commit()
    after = int(session.scalar(select(func.count()).select_from(NewsItem)) or 0)
    # Updates don't grow count; report attempted rows for logging, return new inserts approx.
    written = max(0, after - before)
    logger.info(
        "calendar upsert attempted=%s new_rows=%s high_impact=%s",
        len(rows),
        written,
        sum(1 for f in flagged if f.high_impact),
    )
    return written
