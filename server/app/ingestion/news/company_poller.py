"""Poll Finnhub company-news for active equities and upsert into ``news``."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select

from app.config import Settings, get_settings
from app.db.session import get_session_factory
from app.ingestion.news.client import FinnhubNewsClient, RawNewsArticle
from app.ingestion.news.dedupe import filter_new
from app.ingestion.news.mapping import MappedArticle, NewsAssetMapper
from app.ingestion.news.writer import upsert_mapped_articles
from app.ingestion.registry import mark_error, record_heartbeat
from app.models.asset import Asset

logger = logging.getLogger(__name__)

SOURCE_ID = "finnhub.news"
DEFAULT_LOOKBACK_DAYS = 14


@dataclass(frozen=True)
class CompanyNewsPollResult:
    symbols_polled: int
    fetched: int
    new_articles: int
    rows_written: int
    mapped_articles: int
    errors: tuple[str, ...] = ()


def _force_map(
    mapper: NewsAssetMapper,
    articles: list[RawNewsArticle],
    *,
    forced_symbol: str,
) -> list[MappedArticle]:
    """Map articles and always include the polled equity ticker."""
    forced = forced_symbol.upper()
    out: list[MappedArticle] = []
    for article in articles:
        mapped = mapper.map_article(article)
        symbols = set(mapped.symbols)
        if forced in mapper.active_symbols:
            symbols.add(forced)
        out.append(MappedArticle(article=article, symbols=tuple(sorted(symbols))))
    return out


def active_equity_symbols(session) -> list[str]:  # noqa: ANN001
    rows = session.scalars(
        select(Asset.symbol).where(
            Asset.is_active.is_(True),
            Asset.asset_class == "equity",
        )
    ).all()
    return [str(s).upper() for s in rows]


def poll_company_equities(
    *,
    settings: Settings | None = None,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
    symbols: list[str] | None = None,
    as_of: date | None = None,
) -> CompanyNewsPollResult:
    """
    Fetch last ``lookback_days`` of company-news for each active equity.

    Canonical ticker == Finnhub ``symbol`` query param (AAPL, MSFT, …).
    """
    cfg = settings or get_settings()
    client = FinnhubNewsClient(cfg)
    session = get_session_factory()()
    errors: list[str] = []
    try:
        targets = symbols or active_equity_symbols(session)
        if not targets:
            return CompanyNewsPollResult(0, 0, 0, 0, 0)

        end = as_of or datetime.now(UTC).date()
        start = end - timedelta(days=max(1, lookback_days))
        mapper = NewsAssetMapper.from_session(session)

        all_fresh: list[RawNewsArticle] = []
        mapped_batch: list[MappedArticle] = []
        fetched = 0

        for sym in targets:
            try:
                articles = client.fetch_company_news(sym, from_date=start, to_date=end)
            except Exception as exc:  # noqa: BLE001 — per-symbol continue
                logger.exception("company-news fetch failed symbol=%s", sym)
                errors.append(f"{sym}:{exc}"[:200])
                mark_error(session, SOURCE_ID)
                continue

            fetched += len(articles)
            fresh = filter_new(session, articles)
            all_fresh.extend(fresh)
            mapped_batch.extend(_force_map(mapper, fresh, forced_symbol=sym))

        written = upsert_mapped_articles(session, mapped_batch)
        if not errors:
            record_heartbeat(session, SOURCE_ID)

        with_symbols = sum(1 for m in mapped_batch if m.symbols)
        result = CompanyNewsPollResult(
            symbols_polled=len(targets),
            fetched=fetched,
            new_articles=len(all_fresh),
            rows_written=written,
            mapped_articles=with_symbols,
            errors=tuple(errors),
        )
        logger.info(
            "company-news poll done symbols=%s fetched=%s new=%s written=%s mapped=%s errors=%s",
            result.symbols_polled,
            result.fetched,
            result.new_articles,
            result.rows_written,
            result.mapped_articles,
            len(result.errors),
        )
        return result
    finally:
        session.close()
