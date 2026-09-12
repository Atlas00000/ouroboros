"""News dedupe — skip articles already stored by provider id."""

from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.ingestion.news.client import RawNewsArticle
from app.models.news import NewsItem


def external_id_base(provider: str, provider_id: str) -> str:
    return f"{provider}:{provider_id}"


def external_id_for_symbol(provider: str, provider_id: str, symbol: str | None) -> str:
    base = external_id_base(provider, provider_id)
    if symbol:
        return f"{base}:{symbol.upper()}"
    return base


def already_ingested(session: Session, article: RawNewsArticle) -> bool:
    """True if any row exists for this provider article (any symbol split)."""
    base = external_id_base(article.provider, article.provider_id)
    stmt = (
        select(NewsItem.id)
        .where(
            or_(
                NewsItem.external_id == base,
                NewsItem.external_id.like(f"{base}:%"),
            )
        )
        .limit(1)
    )
    return session.scalar(stmt) is not None


def filter_new(session: Session, articles: list[RawNewsArticle]) -> list[RawNewsArticle]:
    return [a for a in articles if not already_ingested(session, a)]
