"""Finnhub market + company news API client."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Any

import httpx

from app.config import Settings, get_settings
from app.ingestion.httputil import FINNHUB_LIMITER, get_json

logger = logging.getLogger(__name__)

FINNHUB_NEWS_URL = "https://finnhub.io/api/v1/news"
FINNHUB_COMPANY_NEWS_URL = "https://finnhub.io/api/v1/company-news"
# Finnhub /news categories. "merger" is the equity-adjacent market feed;
# per-ticker depth comes from /company-news (see fetch_company_news).
DEFAULT_CATEGORIES = ("forex", "general", "merger")


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

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._timeout = timeout
        self._transport = transport

    @property
    def api_key(self) -> str:
        key = self._settings.news_api_key
        if not key:
            raise RuntimeError("NEWS_API_KEY is not set")
        return key

    def fetch_category(self, category: str) -> list[RawNewsArticle]:
        params = {"category": category}
        headers = {"X-Finnhub-Token": self.api_key}
        payload = get_json(
            FINNHUB_NEWS_URL,
            timeout=self._timeout,
            headers=headers,
            params=params,
            rate_limiter=FINNHUB_LIMITER,
            transport=self._transport,
        )

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

    def fetch_company_news(
        self,
        symbol: str,
        *,
        from_date: date,
        to_date: date,
    ) -> list[RawNewsArticle]:
        """
        Fetch Finnhub company-news for one equity ticker.

        ``related`` is forced to the canonical symbol so downstream mapping
        always attaches the polled equity even when headlines omit the ticker.
        """
        sym = symbol.upper().strip()
        params = {
            "symbol": sym,
            "from": from_date.isoformat(),
            "to": to_date.isoformat(),
        }
        headers = {"X-Finnhub-Token": self.api_key}
        payload = get_json(
            FINNHUB_COMPANY_NEWS_URL,
            timeout=self._timeout,
            headers=headers,
            params=params,
            rate_limiter=FINNHUB_LIMITER,
            transport=self._transport,
        )
        if not isinstance(payload, list):
            raise RuntimeError(f"unexpected Finnhub company-news payload type: {type(payload)}")

        articles: list[RawNewsArticle] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            parsed = self._parse_item(item, category="company", force_related=sym)
            if parsed is not None:
                articles.append(parsed)

        logger.info(
            "finnhub company-news fetched symbol=%s count=%s from=%s to=%s",
            sym,
            len(articles),
            from_date.isoformat(),
            to_date.isoformat(),
        )
        return articles

    @staticmethod
    def _parse_item(
        item: dict[str, Any],
        *,
        category: str,
        force_related: str | None = None,
    ) -> RawNewsArticle | None:
        provider_id = item.get("id")
        headline = (item.get("headline") or "").strip()
        if provider_id is None or not headline:
            return None

        published: datetime | None = None
        ts = item.get("datetime")
        if isinstance(ts, (int, float)) and ts > 0:
            published = datetime.fromtimestamp(int(ts), tz=UTC)

        related = force_related or (item.get("related") or None)
        if related is not None:
            related = str(related)

        return RawNewsArticle(
            provider="finnhub",
            provider_id=str(provider_id),
            headline=headline,
            summary=(item.get("summary") or None),
            url=(item.get("url") or None),
            source_name=str(item.get("source") or "finnhub"),
            published_at=published,
            related=related,
            category=str(item.get("category") or category),
            raw=item,
        )
