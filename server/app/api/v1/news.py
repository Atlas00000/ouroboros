"""GET /v1/news — authenticated news / calendar list."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.pagination import ProvenanceEnvelope, decode_cursor, encode_cursor
from app.api.staleness import endpoint_stale
from app.auth.dependencies import RequirePrincipal
from app.db.session import get_db
from app.models.news import NewsItem

router = APIRouter(tags=["news"])


class NewsListItem(BaseModel):
    id: int
    external_id: str
    symbol: str | None = None
    headline: str
    summary: str | None = None
    url: str | None = None
    source: str
    event_type: str | None = None
    impact: str | None = None
    is_calendar: bool = False
    published_at: datetime | None = None
    scheduled_at: datetime | None = None
    ingested_at: datetime


class NewsListResponse(BaseModel):
    items: list[NewsListItem]
    next_cursor: str | None = None
    has_more: bool = False
    provenance: ProvenanceEnvelope


@router.get("/news", response_model=NewsListResponse)
def list_news(
    _principal: RequirePrincipal,
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    cursor: Annotated[str | None, Query()] = None,
    symbol: Annotated[str | None, Query()] = None,
    is_calendar: Annotated[bool | None, Query()] = None,
    impact: Annotated[str | None, Query()] = None,
) -> NewsListResponse:
    stmt = select(NewsItem).order_by(NewsItem.id.desc())
    if symbol:
        stmt = stmt.where(NewsItem.symbol == symbol.upper())
    if is_calendar is not None:
        stmt = stmt.where(NewsItem.is_calendar.is_(is_calendar))
    if impact:
        stmt = stmt.where(NewsItem.impact == impact.lower())
    if cursor:
        payload = decode_cursor(cursor)
        after_id = int(payload.get("id") or 0)
        if after_id:
            stmt = stmt.where(NewsItem.id < after_id)

    rows = list(db.scalars(stmt.limit(limit + 1)).all())
    has_more = len(rows) > limit
    page = rows[:limit]
    next_cursor = encode_cursor({"id": page[-1].id}) if has_more and page else None

    items = [
        NewsListItem(
            id=r.id,
            external_id=r.external_id,
            symbol=r.symbol,
            headline=r.headline,
            summary=r.summary,
            url=r.url,
            source=r.source,
            event_type=r.event_type,
            impact=r.impact,
            is_calendar=bool(r.is_calendar),
            published_at=r.published_at,
            scheduled_at=r.scheduled_at,
            ingested_at=r.ingested_at,
        )
        for r in page
    ]
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    return NewsListResponse(
        items=items,
        next_cursor=next_cursor,
        has_more=has_more,
        provenance=ProvenanceEnvelope(
            sources=["db.news"],
            generated_at=now,
            model_version="news.list.v1",
            confidence=1.0,
            stale=endpoint_stale(db, "news"),
        ),
    )
