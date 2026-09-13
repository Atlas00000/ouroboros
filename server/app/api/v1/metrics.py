"""GET /v1/metrics — on-demand metrics.v1 snapshot (asset metrics, not Prometheus)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.bars import load_ohlcv
from app.analytics.metrics import MODEL_VERSION, compute_metric_snapshot
from app.api.errors import AppError
from app.api.pagination import ProvenanceEnvelope
from app.api.staleness import endpoint_stale
from app.auth.dependencies import RequirePrincipal
from app.db.session import get_db
from app.models.asset import Asset

router = APIRouter(tags=["metrics"])

TimeframeQ = Literal["M1", "M15", "H1", "H4", "D1"]


class MetricsResponse(BaseModel):
    symbol: str
    timeframe: str
    as_of: datetime
    realized_vol_20: float | None = None
    realized_vol_60: float | None = None
    realized_vol_percentile_30d: float | None = None
    realized_vol_percentile_90d: float | None = None
    atr_14: float | None = None
    atr_percentile_30d: float | None = None
    atr_percentile_90d: float | None = None
    return_1: float | None = None
    return_5: float | None = None
    return_20: float | None = None
    efficiency_ratio_20: float | None = None
    range_mean_20: float | None = None
    range_percentile_30d: float | None = None
    typical_spread: float | None = None
    liquidity_note: str = ""
    model_version: str = MODEL_VERSION
    provenance: ProvenanceEnvelope


@router.get("/metrics", response_model=MetricsResponse)
def get_metrics(
    _principal: RequirePrincipal,
    db: Annotated[Session, Depends(get_db)],
    symbol: Annotated[str, Query(min_length=1)],
    timeframe: Annotated[TimeframeQ, Query()] = "H1",
    lookback_days: Annotated[int, Query(ge=30, le=400)] = 120,
) -> MetricsResponse:
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
    snap = compute_metric_snapshot(df, symbol=sym, timeframe=timeframe)
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    return MetricsResponse(
        symbol=snap.symbol,
        timeframe=snap.timeframe,
        as_of=snap.as_of,
        realized_vol_20=snap.realized_vol_20,
        realized_vol_60=snap.realized_vol_60,
        realized_vol_percentile_30d=snap.realized_vol_percentile_30d,
        realized_vol_percentile_90d=snap.realized_vol_percentile_90d,
        atr_14=snap.atr_14,
        atr_percentile_30d=snap.atr_percentile_30d,
        atr_percentile_90d=snap.atr_percentile_90d,
        return_1=snap.return_1,
        return_5=snap.return_5,
        return_20=snap.return_20,
        efficiency_ratio_20=snap.efficiency_ratio_20,
        range_mean_20=snap.range_mean_20,
        range_percentile_30d=snap.range_percentile_30d,
        typical_spread=snap.typical_spread,
        liquidity_note=snap.liquidity_note,
        model_version=snap.model_version,
        provenance=ProvenanceEnvelope(
            sources=["mt5.prices", snap.model_version],
            generated_at=now,
            model_version=snap.model_version,
            confidence=0.9 if snap.atr_14 is not None else 0.4,
            stale=endpoint_stale(db, "metrics"),
        ),
    )
