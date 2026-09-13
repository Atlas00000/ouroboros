"""GET /v1/state — latest MarketState (state.v1)."""

from __future__ import annotations

from typing import Annotated, Literal

from contracts.state_v1 import MarketState
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.bars import load_ohlcv, m1_depth_days
from app.analytics.regimes import classify_regime
from app.analytics.state_store import (
    latest_state_row,
    market_state_from_row,
    market_state_from_snapshot,
    persist_regime_state,
)
from app.api.errors import AppError
from app.auth.dependencies import RequirePrincipal
from app.db.session import get_db
from app.models.asset import Asset

router = APIRouter(tags=["state"])

TimeframeQ = Literal["M1", "M15", "H1", "H4", "D1"]


@router.get("/state", response_model=MarketState)
def get_state(
    _principal: RequirePrincipal,
    db: Annotated[Session, Depends(get_db)],
    symbol: Annotated[str, Query(min_length=1)],
    timeframe: Annotated[TimeframeQ, Query()] = "H1",
    refresh: Annotated[bool, Query(description="Recompute and persist if missing/stale path")] = False,
) -> MarketState:
    sym = symbol.upper()
    asset = db.scalar(select(Asset).where(Asset.symbol == sym))
    if asset is None:
        raise AppError(
            status=404,
            title="Not Found",
            detail=f"Unknown asset {sym}",
            type_="https://ouroboros.local/problems/not-found",
        )

    row = latest_state_row(db, sym, timeframe)
    if row is not None and not refresh:
        return market_state_from_row(row)

    df = load_ohlcv(db, sym, timeframe, lookback_days=120)
    if df.empty:
        raise AppError(
            status=404,
            title="Not Found",
            detail=f"No bars for {sym} {timeframe}",
            type_="https://ouroboros.local/problems/not-found",
        )
    snap = classify_regime(
        df,
        symbol=sym,
        timeframe=timeframe,
        m1_span_days_value=m1_depth_days(db, sym),
    )
    if snap.skipped:
        raise AppError(
            status=404,
            title="Not Found",
            detail=snap.skip_reason or "regime skipped",
            type_="https://ouroboros.local/problems/not-found",
        )
    persist_regime_state(db, snap, enqueue_outbox=True)
    db.commit()
    return market_state_from_snapshot(snap)
