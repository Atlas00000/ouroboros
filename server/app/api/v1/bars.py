"""GET /v1/bars — OHLCV series for charts (W10)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.bars import load_ohlcv
from app.api.errors import AppError
from app.api.pagination import ProvenanceEnvelope
from app.api.staleness import endpoint_stale
from app.auth.dependencies import RequirePrincipal
from app.calendar.timebase import ensure_utc
from app.db.session import get_db
from app.models.asset import Asset

router = APIRouter(tags=["bars"])

TimeframeQ = Literal["M1", "M15", "H1", "H4", "D1"]


class BarPoint(BaseModel):
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None


class BarsResponse(BaseModel):
    symbol: str
    timeframe: str
    bars: list[BarPoint]
    provenance: ProvenanceEnvelope


@router.get("/bars", response_model=BarsResponse)
def get_bars(
    _principal: RequirePrincipal,
    db: Annotated[Session, Depends(get_db)],
    symbol: Annotated[str, Query(min_length=1)],
    timeframe: Annotated[TimeframeQ, Query()] = "H1",
    lookback_days: Annotated[int, Query(ge=1, le=400)] = 60,
) -> BarsResponse:
    sym = symbol.upper()
    asset = db.scalar(select(Asset).where(Asset.symbol == sym))
    if asset is None:
        raise AppError(
            status=404,
            title="Not Found",
            detail=f"Unknown asset {sym}",
            type_="https://ouroboros.local/problems/not-found",
        )
    df = load_ohlcv(db, sym, timeframe, lookback_days=lookback_days)
    if df.empty:
        raise AppError(
            status=404,
            title="Not Found",
            detail=f"No bars for {sym} {timeframe}",
            type_="https://ouroboros.local/problems/not-found",
        )

    bars: list[BarPoint] = []
    for _, row in df.iterrows():
        raw_ts = row["ts"]
        if hasattr(raw_ts, "to_pydatetime"):
            ts = ensure_utc(raw_ts.to_pydatetime())
        else:
            ts = ensure_utc(raw_ts)
        vol = row["volume"] if "volume" in row and row["volume"] == row["volume"] else None
        bars.append(
            BarPoint(
                ts=ts,
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=float(vol) if vol is not None else None,
            )
        )

    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    return BarsResponse(
        symbol=sym,
        timeframe=timeframe,
        bars=bars,
        provenance=ProvenanceEnvelope(
            sources=["mt5.prices", "bars.v1"],
            generated_at=now,
            model_version="bars.v1",
            confidence=1.0 if bars else 0.0,
            stale=endpoint_stale(db, "bars"),
        ),
    )
