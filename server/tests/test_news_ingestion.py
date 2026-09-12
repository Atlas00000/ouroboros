"""Tests for news mapping + dedupe (no live API required)."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import text

from app.db.session import get_session_factory
from app.ingestion.news.client import RawNewsArticle
from app.ingestion.news.dedupe import already_ingested, filter_new
from app.ingestion.news.mapping import NewsAssetMapper
from app.ingestion.news.writer import upsert_mapped_articles


def _article(
    provider_id: str,
    headline: str,
    *,
    summary: str | None = None,
    related: str | None = None,
) -> RawNewsArticle:
    return RawNewsArticle(
        provider="finnhub",
        provider_id=provider_id,
        headline=headline,
        summary=summary,
        url="https://example.com/n",
        source_name="test",
        published_at=datetime(2026, 9, 12, tzinfo=UTC),
        related=related,
        category="forex",
        raw={},
    )


def test_mapper_keywords_and_pairs() -> None:
    mapper = NewsAssetMapper(
        {
            "EURUSD",
            "GBPUSD",
            "XAUUSD",
            "US500",
            "USDJPY",
        }
    )
    m = mapper.map_article(_article("1", "ECB holds rates as euro rises vs dollar"))
    assert "EURUSD" in m.symbols

    m2 = mapper.map_article(_article("2", "Gold rallies on safe-haven demand"))
    assert m2.symbols == ("XAUUSD",)

    m3 = mapper.map_article(_article("3", "Markets steady", related="OANDA:EUR_USD,FX:GBPUSD"))
    assert "EURUSD" in m3.symbols
    assert "GBPUSD" in m3.symbols

    m4 = mapper.map_article(_article("4", "EUR/USD slips ahead of data"))
    assert "EURUSD" in m4.symbols


def test_dedupe_and_upsert() -> None:
    session = get_session_factory()()
    try:
        pid = "w3d1-test-article-001"
        session.execute(
            text("DELETE FROM news WHERE external_id LIKE :p"),
            {"p": f"finnhub:{pid}%"},
        )
        session.commit()

        article = _article(pid, "Fed signals pause; dollar soft", related="EURUSD")
        assert already_ingested(session, article) is False

        mapper = NewsAssetMapper({"EURUSD", "GBPUSD", "USDJPY"})
        mapped = [mapper.map_article(article)]
        n = upsert_mapped_articles(session, mapped)
        assert n >= 1
        assert already_ingested(session, article) is True
        assert filter_new(session, [article]) == []

        # Second upsert is no-op
        n2 = upsert_mapped_articles(session, mapped)
        assert n2 == 0
    finally:
        session.execute(
            text("DELETE FROM news WHERE external_id LIKE :p"),
            {"p": "finnhub:w3d1-test-article-001%"},
        )
        session.commit()
        session.close()
