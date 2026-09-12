"""Map news articles onto canonical asset symbols."""

from __future__ import annotations

import re
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ingestion.news.client import RawNewsArticle
from app.models.asset import Asset

# Keyword → symbols (FX/metals/indices universe). Order does not matter; unioned.
_KEYWORD_SYMBOLS: dict[str, tuple[str, ...]] = {
    "euro": ("EURUSD", "EURGBP", "EURJPY"),
    "ecb": ("EURUSD", "EURGBP", "EURJPY"),
    "lagarde": ("EURUSD", "EURGBP", "EURJPY"),
    "sterling": ("GBPUSD", "EURGBP", "GBPJPY"),
    "pound": ("GBPUSD", "EURGBP", "GBPJPY"),
    "boe": ("GBPUSD", "EURGBP", "GBPJPY"),
    "yen": ("USDJPY", "EURJPY", "GBPJPY"),
    "boj": ("USDJPY", "EURJPY", "GBPJPY"),
    "swiss": ("USDCHF",),
    "snb": ("USDCHF",),
    "aussie": ("AUDUSD",),
    "australia": ("AUDUSD",),
    "rba": ("AUDUSD",),
    "loonie": ("USDCAD",),
    "canada": ("USDCAD",),
    "boc": ("USDCAD",),
    "kiwi": ("NZDUSD",),
    "zealand": ("NZDUSD",),
    "rbnz": ("NZDUSD",),
    "fed": ("EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD"),
    "fomc": ("EURUSD", "GBPUSD", "USDJPY", "XAUUSD"),
    "powell": ("EURUSD", "GBPUSD", "USDJPY", "XAUUSD"),
    "dollar": ("EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD"),
    "gold": ("XAUUSD",),
    "xau": ("XAUUSD",),
    "silver": ("XAGUSD",),
    "xag": ("XAGUSD",),
    "s&p": ("US500",),
    "spx": ("US500",),
    "s&p 500": ("US500",),
    "dow": ("US30",),
    "nasdaq": ("NAS100",),
}

_PAIR_RE = re.compile(
    r"\b(EUR|GBP|USD|JPY|CHF|AUD|CAD|NZD)[/\-]?(EUR|GBP|USD|JPY|CHF|AUD|CAD|NZD)\b"
    r"|\b(EURUSD|GBPUSD|USDJPY|USDCHF|AUDUSD|USDCAD|NZDUSD|EURGBP|EURJPY|GBPJPY|XAUUSD|XAGUSD)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class MappedArticle:
    article: RawNewsArticle
    symbols: tuple[str, ...]  # empty → store with symbol=NULL


class NewsAssetMapper:
    """Resolve Finnhub articles to active canonical symbols."""

    def __init__(self, active_symbols: set[str]) -> None:
        self._active = {s.upper() for s in active_symbols}

    @classmethod
    def from_session(cls, session: Session) -> NewsAssetMapper:
        rows = session.scalars(select(Asset.symbol).where(Asset.is_active.is_(True))).all()
        return cls(set(rows))

    def map_article(self, article: RawNewsArticle) -> MappedArticle:
        found: set[str] = set()
        found.update(self._from_related(article.related))
        text = f"{article.headline} {article.summary or ''}"
        found.update(self._from_pair_tokens(text))
        found.update(self._from_keywords(text))
        symbols = tuple(sorted(s for s in found if s in self._active))
        return MappedArticle(article=article, symbols=symbols)

    def map_many(self, articles: list[RawNewsArticle]) -> list[MappedArticle]:
        return [self.map_article(a) for a in articles]

    def _from_related(self, related: str | None) -> set[str]:
        if not related:
            return set()
        out: set[str] = set()
        for token in re.split(r"[,;\s]+", related.upper()):
            token = token.strip()
            if not token:
                continue
            # OANDA:EUR_USD / FX:EURUSD / plain EURUSD
            token = token.replace("OANDA:", "").replace("FX:", "").replace("_", "")
            if token in self._active:
                out.add(token)
            if len(token) == 6 and token[:3].isalpha() and token[3:].isalpha():
                if token in self._active:
                    out.add(token)
        return out

    def _from_pair_tokens(self, text: str) -> set[str]:
        out: set[str] = set()
        for match in _PAIR_RE.finditer(text):
            token = match.group(0).upper().replace("/", "").replace("-", "").replace(" ", "")
            if len(token) == 6 and token.isalpha():
                out.add(token)
        return out

    @staticmethod
    def _from_keywords(text: str) -> set[str]:
        lower = text.lower()
        out: set[str] = set()
        for key, symbols in _KEYWORD_SYMBOLS.items():
            if key in lower:
                out.update(symbols)
        return out
