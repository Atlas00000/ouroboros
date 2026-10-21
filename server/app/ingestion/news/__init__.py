"""News ingestion package."""

from app.ingestion.news.client import FinnhubNewsClient, RawNewsArticle
from app.ingestion.news.company_poller import (
    CompanyNewsPollResult,
    poll_company_equities,
)
from app.ingestion.news.dedupe import already_ingested, filter_new
from app.ingestion.news.mapping import MappedArticle, NewsAssetMapper
from app.ingestion.news.poller import NewsPollResult, poll_once
from app.ingestion.news.writer import upsert_mapped_articles

__all__ = [
    "CompanyNewsPollResult",
    "FinnhubNewsClient",
    "MappedArticle",
    "NewsAssetMapper",
    "NewsPollResult",
    "RawNewsArticle",
    "already_ingested",
    "filter_new",
    "poll_company_equities",
    "poll_once",
    "upsert_mapped_articles",
]
