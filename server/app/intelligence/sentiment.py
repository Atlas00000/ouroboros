"""News → per-asset decay-weighted sentiment (W7·D2/D3).

Per-article scores are cached in ``article_scores`` so the same headline is
never re-scored. Aggregate scores live in ``sentiment``; spikes and high-impact
news go to the transactional outbox.
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import NAMESPACE_URL, uuid4, uuid5

from contracts.common_v1 import Disclaimer, Provenance
from contracts.events_v1 import (
    NewsHighImpactEvent,
    NewsHighImpactPayload,
    SentimentSpikeEvent,
    SentimentSpikePayload,
)
from contracts.sentiment_v1 import SentimentDriver, SentimentSnapshot
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.calendar.timebase import ensure_utc
from app.config import get_settings
from app.intelligence.llm_client import LLMClient, MODEL_VERSION as LLM_MODEL_VERSION
from app.models.article_score import ArticleScoreRow
from app.models.news import NewsItem
from app.models.outbox import OutboxMessage
from app.models.sentiment import SentimentRow

logger = logging.getLogger(__name__)

SENTIMENT_MODEL_VERSION = "sentiment.v1"
WINDOW_HOURS = 24
HALF_LIFE_HOURS = 12.0
TOP_DRIVERS = 5
MAX_SCORE_PER_TICK = 40  # batch cap per scheduler tick


@dataclass
class SentimentTickReport:
    articles_scored: int = 0
    articles_cached: int = 0
    symbols_updated: int = 0
    spikes: int = 0
    high_impact: int = 0
    errors: list[str] = field(default_factory=list)


def _driver_url(raw: str | None) -> str | None:
    if not raw or not str(raw).strip():
        return None
    u = str(raw).strip()
    if u.startswith(("http://", "https://")):
        return u
    return None


def decay_weight(age_hours: float, *, half_life: float = HALF_LIFE_HOURS) -> float:
    if age_hours < 0:
        age_hours = 0.0
    return float(0.5 ** (age_hours / half_life))


def latest_sentiment_row(session: Session, symbol: str) -> SentimentRow | None:
    sym = symbol.upper()
    return session.scalar(
        select(SentimentRow)
        .where(SentimentRow.symbol == sym)
        .order_by(SentimentRow.as_of.desc(), SentimentRow.id.desc())
        .limit(1)
    )


def sentiment_from_row(row: SentimentRow) -> SentimentSnapshot:
    drivers_raw = json.loads(row.top_drivers_json) if row.top_drivers_json else []
    drivers: list[SentimentDriver] = []
    for d in drivers_raw:
        try:
            drivers.append(SentimentDriver(**d))
        except ValidationError:
            continue
    return SentimentSnapshot(
        symbol=row.symbol,
        score=float(row.score),
        item_count=int(row.item_count),
        window_hours=int(row.window_hours),
        top_drivers=drivers,
        as_of=ensure_utc(row.as_of),
        provenance=Provenance(
            sources=json.loads(row.sources_json) if row.sources_json else [row.model_version],
            generated_at=ensure_utc(row.created_at),
            model_version=row.model_version,
            confidence=float(row.confidence),
            stale=bool(row.stale),
        ),
        disclaimer=Disclaimer(),
    )


def _cached_scores(session: Session, external_ids: list[str]) -> dict[str, float]:
    if not external_ids:
        return {}
    rows = session.scalars(
        select(ArticleScoreRow).where(ArticleScoreRow.external_id.in_(external_ids))
    ).all()
    return {r.external_id: float(r.score) for r in rows}


def score_unseen_articles(
    session: Session,
    items: list[NewsItem],
    client: LLMClient | None = None,
    *,
    max_new: int = MAX_SCORE_PER_TICK,
) -> tuple[int, int]:
    """Score headlines missing from article_scores. Returns (scored, already_cached)."""
    client = client or LLMClient()
    ids = [i.external_id for i in items]
    cached = _cached_scores(session, ids)
    already = 0
    scored = 0
    for item in items:
        if item.external_id in cached:
            already += 1
            continue
        if scored >= max_new:
            break
        try:
            score, resp = client.score_headline(item.headline, symbol=item.symbol)
            session.add(
                ArticleScoreRow(
                    external_id=item.external_id,
                    headline=item.headline[:2000],
                    score=Decimal(str(round(score, 4))),
                    provider=resp.provider,
                    model_version=f"{LLM_MODEL_VERSION}:{resp.model}",
                )
            )
            cached[item.external_id] = score
            scored += 1
        except Exception as exc:  # noqa: BLE001
            logger.warning("article_score_failed id=%s err=%s", item.external_id, exc)
    session.flush()
    return scored, already


def aggregate_symbol_sentiment(
    session: Session,
    symbol: str,
    *,
    now: datetime | None = None,
    scores: dict[str, float] | None = None,
) -> SentimentSnapshot | None:
    """Decay-weighted aggregate over 24h news for one symbol."""
    now = ensure_utc(now or datetime.now(UTC))
    sym = symbol.upper()
    cutoff = now - timedelta(hours=WINDOW_HOURS)
    items = list(
        session.scalars(
            select(NewsItem)
            .where(
                NewsItem.symbol == sym,
                NewsItem.published_at.is_not(None),
                NewsItem.published_at >= cutoff,
            )
            .order_by(NewsItem.published_at.desc())
        ).all()
    )
    if not items:
        return None

    score_map = scores if scores is not None else _cached_scores(session, [i.external_id for i in items])
    weighted_sum = 0.0
    weight_total = 0.0
    drivers: list[tuple[float, SentimentDriver]] = []

    for item in items:
        if item.external_id not in score_map:
            continue
        art_score = float(score_map[item.external_id])
        published = ensure_utc(item.published_at) if item.published_at else now
        age_h = max(0.0, (now - published).total_seconds() / 3600.0)
        w = decay_weight(age_h)
        weighted_sum += art_score * w
        weight_total += w
        drivers.append(
            (
                abs(art_score * w),
                SentimentDriver(
                    title=item.headline[:500],
                    url=_driver_url(item.url),
                    published_at=published,
                    contribution=float(max(-1.0, min(1.0, art_score))),
                    source=item.source,
                ),
            )
        )

    if weight_total <= 0:
        return None

    agg = float(max(-1.0, min(1.0, weighted_sum / weight_total)))
    drivers.sort(key=lambda t: t[0], reverse=True)
    top = [d for _, d in drivers[:TOP_DRIVERS]]
    conf = float(min(1.0, math.sqrt(len(top) / TOP_DRIVERS)))

    return SentimentSnapshot(
        symbol=sym,
        score=agg,
        item_count=len([i for i in items if i.external_id in score_map]),
        window_hours=WINDOW_HOURS,
        top_drivers=top,
        as_of=now,
        provenance=Provenance(
            sources=["db.news", "article_scores", SENTIMENT_MODEL_VERSION],
            generated_at=now,
            model_version=SENTIMENT_MODEL_VERSION,
            confidence=conf,
            stale=False,
        ),
        disclaimer=Disclaimer(),
    )


def persist_sentiment(
    session: Session,
    snap: SentimentSnapshot,
    *,
    enqueue_spike: bool = True,
) -> tuple[SentimentRow, bool]:
    """Insert sentiment row; enqueue sentiment.spike when |delta| >= threshold."""
    settings = get_settings()
    threshold = float(settings.sentiment_spike_threshold)
    prev = latest_sentiment_row(session, snap.symbol)
    prev_score = float(prev.score) if prev is not None else None
    delta = snap.score - prev_score if prev_score is not None else snap.score
    spiked = prev_score is not None and abs(delta) >= threshold

    drivers_json = json.dumps(
        [d.model_dump(mode="json") for d in snap.top_drivers],
        separators=(",", ":"),
        default=str,
    )
    row = SentimentRow(
        symbol=snap.symbol,
        score=Decimal(str(round(snap.score, 4))),
        item_count=snap.item_count,
        window_hours=snap.window_hours,
        top_drivers_json=drivers_json,
        as_of=ensure_utc(snap.as_of),
        model_version=snap.provenance.model_version,
        confidence=Decimal(str(round(snap.provenance.confidence, 4))),
        stale=bool(snap.provenance.stale),
        sources_json=json.dumps(snap.provenance.sources),
    )
    session.add(row)

    if enqueue_spike and spiked and prev is not None:
        event_id = str(uuid4())
        occurred = ensure_utc(snap.as_of)
        envelope = SentimentSpikeEvent(
            event_id=event_id,
            occurred_at=occurred,
            symbol=snap.symbol,
            provenance=snap.provenance,
            payload=SentimentSpikePayload(
                symbol=snap.symbol,
                previous_score=prev_score,
                score=snap.score,
                delta=float(delta),
                as_of=occurred,
            ),
        )
        session.add(
            OutboxMessage(
                event_id=event_id,
                event="sentiment.spike",
                payload_json=envelope.model_dump_json(),
            )
        )

    session.flush()
    return row, bool(spiked and prev is not None)


def enqueue_high_impact_news(
    session: Session,
    *,
    lookback_hours: float = 6.0,
    now: datetime | None = None,
) -> int:
    """Emit news.high_impact for calendar/high-impact items not yet in outbox."""
    now = ensure_utc(now or datetime.now(UTC))
    cutoff = now - timedelta(hours=lookback_hours)
    items = list(
        session.scalars(
            select(NewsItem).where(
                NewsItem.impact == "high",
                NewsItem.published_at.is_not(None),
                NewsItem.published_at >= cutoff,
            )
        ).all()
    )
    emitted = 0
    for item in items:
        event_id = str(uuid5(NAMESPACE_URL, f"news.high_impact:{item.external_id}"))
        exists = session.scalar(
            select(OutboxMessage.id).where(OutboxMessage.event_id == event_id).limit(1)
        )
        if exists is not None:
            continue
        occurred = ensure_utc(item.published_at or now)
        envelope = NewsHighImpactEvent(
            event_id=event_id,
            occurred_at=occurred,
            symbol=item.symbol,
            provenance=Provenance(
                sources=["db.news", item.source],
                generated_at=now,
                model_version="news.high_impact.v1",
                confidence=1.0,
                stale=False,
            ),
            payload=NewsHighImpactPayload(
                symbol=item.symbol,
                headline=item.headline[:500],
                event_type=item.event_type,
                impact="high",
                scheduled_at=ensure_utc(item.scheduled_at) if item.scheduled_at else None,
                published_at=ensure_utc(item.published_at) if item.published_at else None,
                source=item.source,
            ),
        )
        session.add(
            OutboxMessage(
                event_id=event_id,
                event="news.high_impact",
                payload_json=envelope.model_dump_json(),
            )
        )
        emitted += 1
    session.flush()
    return emitted


def run_sentiment_tick(
    session: Session,
    *,
    client: LLMClient | None = None,
    commit: bool = True,
    now: datetime | None = None,
) -> SentimentTickReport:
    """Score unseen articles, refresh symbol aggregates, emit events."""
    report = SentimentTickReport()
    now = ensure_utc(now or datetime.now(UTC))
    client = client or LLMClient()
    cutoff = now - timedelta(hours=WINDOW_HOURS)

    try:
        items = list(
            session.scalars(
                select(NewsItem)
                .where(
                    NewsItem.published_at.is_not(None),
                    NewsItem.published_at >= cutoff,
                    NewsItem.symbol.is_not(None),
                )
                .order_by(NewsItem.published_at.desc())
            ).all()
        )
        scored, cached = score_unseen_articles(session, items, client)
        report.articles_scored = scored
        report.articles_cached = cached

        symbols = sorted({(i.symbol or "").upper() for i in items if i.symbol})
        score_map = _cached_scores(session, [i.external_id for i in items])
        for sym in symbols:
            snap = aggregate_symbol_sentiment(session, sym, now=now, scores=score_map)
            if snap is None:
                continue
            _, spiked = persist_sentiment(session, snap, enqueue_spike=True)
            report.symbols_updated += 1
            if spiked:
                report.spikes += 1

        report.high_impact = enqueue_high_impact_news(session, now=now)

        if commit:
            session.commit()
        else:
            session.flush()
    except Exception as exc:  # noqa: BLE001
        report.errors.append(str(exc))
        if commit:
            session.rollback()
        logger.exception("sentiment_tick_failed")
        raise

    return report
