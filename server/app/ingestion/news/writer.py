"""Persist mapped news articles into the news table."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.ingestion.news.dedupe import external_id_for_symbol
from app.ingestion.news.mapping import MappedArticle
from app.models.news import NewsItem

logger = logging.getLogger(__name__)


def upsert_mapped_articles(session: Session, mapped: list[MappedArticle]) -> int:
    """
    Insert one row per (article, symbol); symbol=NULL when unmapped.

    Idempotent on external_id.
    """
    if not mapped:
        return 0

    now = datetime.now(UTC)
    rows: list[dict] = []
    for item in mapped:
        targets: list[str | None] = list(item.symbols) if item.symbols else [None]
        for symbol in targets:
            rows.append(
                {
                    "external_id": external_id_for_symbol(
                        item.article.provider,
                        item.article.provider_id,
                        symbol,
                    ),
                    "symbol": symbol,
                    "headline": item.article.headline[:4000],
                    "summary": item.article.summary,
                    "url": item.article.url,
                    "source": item.article.source_name[:64],
                    "event_type": item.article.category,
                    "impact": None,
                    "is_calendar": False,
                    "published_at": item.article.published_at,
                    "scheduled_at": None,
                    "ingested_at": now,
                }
            )

    before = int(session.scalar(select(func.count()).select_from(NewsItem)) or 0)
    stmt = insert(NewsItem).values(rows)
    stmt = stmt.on_conflict_do_nothing(index_elements=["external_id"])
    session.execute(stmt)
    session.commit()
    after = int(session.scalar(select(func.count()).select_from(NewsItem)) or 0)
    written = max(0, after - before)
    logger.info("news upsert attempted=%s written=%s", len(rows), written)
    return written
