"""News poll cycle — fetch → dedupe → map → upsert → heartbeat."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from app.config import Settings, get_settings
from app.db.session import get_session_factory
from app.ingestion.news.client import DEFAULT_CATEGORIES, FinnhubNewsClient
from app.ingestion.news.dedupe import filter_new
from app.ingestion.news.mapping import NewsAssetMapper
from app.ingestion.news.writer import upsert_mapped_articles
from app.ingestion.registry import mark_error, record_heartbeat

logger = logging.getLogger(__name__)

SOURCE_ID = "finnhub.news"


@dataclass(frozen=True)
class NewsPollResult:
    fetched: int
    new_articles: int
    rows_written: int
    mapped_articles: int
    unmapped_articles: int


def poll_once(
    *,
    settings: Settings | None = None,
    categories: tuple[str, ...] = DEFAULT_CATEGORIES,
) -> NewsPollResult:
    cfg = settings or get_settings()
    client = FinnhubNewsClient(cfg)
    session = get_session_factory()()
    try:
        try:
            articles = client.fetch_market_news(categories=categories)
        except Exception:
            logger.exception("news fetch failed")
            mark_error(session, SOURCE_ID)
            raise

        fresh = filter_new(session, articles)
        mapper = NewsAssetMapper.from_session(session)
        mapped = mapper.map_many(fresh)
        written = upsert_mapped_articles(session, mapped)
        record_heartbeat(session, SOURCE_ID)

        with_symbols = sum(1 for m in mapped if m.symbols)
        result = NewsPollResult(
            fetched=len(articles),
            new_articles=len(fresh),
            rows_written=written,
            mapped_articles=with_symbols,
            unmapped_articles=len(mapped) - with_symbols,
        )
        logger.info(
            "news poll done fetched=%s new=%s written=%s mapped=%s unmapped=%s",
            result.fetched,
            result.new_articles,
            result.rows_written,
            result.mapped_articles,
            result.unmapped_articles,
        )
        return result
    finally:
        session.close()
