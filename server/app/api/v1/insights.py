"""GET /v1/insights — latest narrative Insight (insight.v1)."""

from __future__ import annotations

from typing import Annotated

from contracts.insight_v1 import Insight
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.state_store import latest_state_row, market_state_from_row
from app.api.errors import AppError
from app.api.staleness import with_feed_stale
from app.auth.dependencies import RequirePrincipal
from app.db.session import get_db
from app.intelligence.llm_client import LLMClient
from app.intelligence.narratives import (
    build_narrative_insight,
    insight_from_row,
    latest_insight_row,
    persist_insight,
)
from app.intelligence.sentiment import latest_sentiment_row, sentiment_from_row
from app.models.asset import Asset

router = APIRouter(tags=["insights"])


@router.get("/insights", response_model=Insight)
def get_insight(
    _principal: RequirePrincipal,
    db: Annotated[Session, Depends(get_db)],
    symbol: Annotated[str, Query(min_length=1)],
    refresh: Annotated[bool, Query(description="Regenerate narrative from latest state/sentiment")] = False,
) -> Insight:
    sym = symbol.upper()
    asset = db.scalar(select(Asset).where(Asset.symbol == sym))
    if asset is None:
        raise AppError(
            status=404,
            title="Not Found",
            detail=f"Unknown asset {sym}",
            type_="https://ouroboros.local/problems/not-found",
        )

    row = latest_insight_row(db, sym)
    if row is not None and not refresh:
        return with_feed_stale(insight_from_row(row), db, "insights")

    state_row = latest_state_row(db, sym, "H1")
    state = market_state_from_row(state_row) if state_row else None
    sent_row = latest_sentiment_row(db, sym)
    sentiment = sentiment_from_row(sent_row) if sent_row else None

    if state is None and sentiment is None:
        raise AppError(
            status=404,
            title="Not Found",
            detail=f"No state or sentiment inputs for {sym}",
            type_="https://ouroboros.local/problems/not-found",
        )

    insight = build_narrative_insight(
        sym, state=state, sentiment=sentiment, client=LLMClient()
    )
    if insight.type != "narrative":
        raise AppError(
            status=500,
            title="Internal Server Error",
            detail="Narrative guardrail failed",
            type_="https://ouroboros.local/problems/guardrail",
        )
    if not insight.disclaimer.text:
        raise AppError(
            status=500,
            title="Internal Server Error",
            detail="Disclaimer required on insights",
            type_="https://ouroboros.local/problems/guardrail",
        )

    persist_insight(db, insight)
    db.commit()
    return with_feed_stale(insight, db, "insights")
