"""Finnhub market news API client."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import httpx

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

FINNHUB_NEWS_URL = "https://finnhub.io/api/v1/news"
DEFAULT_CATEGORIES = ("forex", "general")


@dataclass(frozen=True)
class RawNewsArticle:
    """Provider-normalized news article (pre-persist)."""

    provider: str
    provider_id: str
    headline: str
    summary: str | None
    url: str | None
    source_name: str
    published_at: datetime | None
    related: str | None
    category: str | None
    raw: dict[str, Any]


class FinnhubNewsClient:
    """Thin client for Finnhub market news (`/news`)."""

    def __init__(self, settings: Settings | None = None, *, timeout: float = 30.0) -> None:
        self._settings = settings or get_settings()
        self._timeout = timeout

    @property
    def api_key(self) -> str:
        key = self._settings.news_api_key
        if not key:
            raise RuntimeError("NEWS_API_KEY is not set")
        return key

    def fetch_category(self, category: str) -> list[RawNewsArticle]:
        params = {"category": category}
        headers = {"X-Finnhub-Token": self.api_key}
        with httpx.Client(timeout=self._timeout) as client:
            resp = client.get(FINNHUB_NEWS_URL, params=params, headers=headers)
            resp.raise_for_status()
            payload = resp.json()

        if not isinstance(payload, list):
            raise RuntimeError(f"unexpected Finnhub news payload type: {type(payload)}")

        articles: list[RawNewsArticle] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            parsed = self._parse_item(item, category=category)
            if parsed is not None:
                articles.append(parsed)

        logger.info(
            "finnhub news fetched category=%s count=%s",
            category,
            len(articles),
        )
        return articles

    def fetch_market_news(
        self,
        categories: tuple[str, ...] = DEFAULT_CATEGORIES,
    ) -> list[RawNewsArticle]:
        """Fetch several categories; de-dupe by provider_id within the batch."""
        by_id: dict[str, RawNewsArticle] = {}
        for category in categories:
            for article in self.fetch_category(category):
                by_id.setdefault(article.provider_id, article)
        return list(by_id.values())

    @staticmethod
    def _parse_item(item: dict[str, Any], *, category: str) -> RawNewsArticle | None:
        provider_id = item.get("id")
        headline = (item.get("headline") or "").strip()
        if provider_id is None or not headline:
            return None

        published: datetime | None = None
        ts = item.get("datetime")
        if isinstance(ts, (int, float)) and ts > 0:
            published = datetime.fromtimestamp(int(ts), tz=UTC)

        return RawNewsArticle(
            provider="finnhub",
            provider_id=str(provider_id),
            headline=headline,
            summary=(item.get("summary") or None),
            url=(item.get("url") or None),
            source_name=str(item.get("source") or "finnhub"),
            published_at=published,
            related=(item.get("related") or None),
            category=str(item.get("category") or category),
            raw=item,
        )
