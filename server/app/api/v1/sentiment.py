"""GET /v1/sentiment — latest SentimentSnapshot (sentiment.v1)."""

from __future__ import annotations

from typing import Annotated

from contracts.sentiment_v1 import SentimentSnapshot
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.errors import AppError
from app.api.staleness import with_feed_stale
from app.auth.dependencies import RequirePrincipal
from app.db.session import get_db
from app.intelligence.llm_client import LLMClient
from app.intelligence.sentiment import (
    aggregate_symbol_sentiment,
    latest_sentiment_row,
    persist_sentiment,
    run_sentiment_tick,
    sentiment_from_row,
)
from app.models.asset import Asset

router = APIRouter(tags=["sentiment"])


@router.get("/sentiment", response_model=SentimentSnapshot)
def get_sentiment(
    _principal: RequirePrincipal,
    db: Annotated[Session, Depends(get_db)],
    symbol: Annotated[str, Query(min_length=1)],
    refresh: Annotated[bool, Query(description="Re-aggregate from cached article scores")] = False,
) -> SentimentSnapshot:
    sym = symbol.upper()
    asset = db.scalar(select(Asset).where(Asset.symbol == sym))
    if asset is None:
        raise AppError(
            status=404,
            title="Not Found",
            detail=f"Unknown asset {sym}",
            type_="https://ouroboros.local/problems/not-found",
        )

    row = latest_sentiment_row(db, sym)
    if row is not None and not refresh:
        return with_feed_stale(sentiment_from_row(row), db, "sentiment")

    if refresh:
        # Score any unseen headlines then re-aggregate (mock-friendly).
        run_sentiment_tick(db, client=LLMClient(), commit=False)
        row = latest_sentiment_row(db, sym)
        if row is not None:
            db.commit()
            return with_feed_stale(sentiment_from_row(row), db, "sentiment")

    snap = aggregate_symbol_sentiment(db, sym)
    if snap is None:
        raise AppError(
            status=404,
            title="Not Found",
            detail=f"No sentiment for {sym} (need scored news in 24h window)",
            type_="https://ouroboros.local/problems/not-found",
        )
    persist_sentiment(db, snap, enqueue_spike=True)
    db.commit()
    return with_feed_stale(snap, db, "sentiment")
