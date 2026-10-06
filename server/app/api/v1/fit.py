"""GET /v1/fit — regime fit tags (fit.v1)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, Literal

from contracts.common_v1 import Disclaimer, Provenance
from contracts.fit_v1 import FitSnapshot
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.bars import load_ohlcv
from app.analytics.fit.boards import BOARD_WINDOWS, board_from_ohlcv
from app.analytics.fit.gate import live_fit
from app.analytics.fit.mapper import MODEL_VERSION
from app.api.errors import AppError
from app.api.staleness import endpoint_stale
from app.auth.dependencies import RequirePrincipal
from app.db.session import get_db
from app.models.asset import Asset

router = APIRouter(tags=["fit"])

TimeframeQ = Literal["M1", "M15", "H1", "H4", "D1"]
FamilyQ = Literal["meanrev", "trendfollow"]
WindowQ = Literal["7d", "30d", "calendar_month"]

RESEARCH_DISCLAIMER = Disclaimer(
    text=(
        "Ouroboros fit tags are internal research context only "
        "(MATCH/MISMATCH/FRAGILE vs an edge family). "
        "They are not investment advice, not execution signals, "
        "and do not authorize disabling survival geometry."
    ),
)


@router.get("/fit", response_model=FitSnapshot)
def get_fit(
    _principal: RequirePrincipal,
    db: Annotated[Session, Depends(get_db)],
    symbol: Annotated[str, Query(min_length=1)],
    family: Annotated[FamilyQ, Query()],
    timeframe: Annotated[TimeframeQ, Query()] = "H1",
    window: Annotated[
        WindowQ | None,
        Query(description="Optional ex-post board window; adds shares"),
    ] = None,
) -> FitSnapshot:
    sym = symbol.upper()
    asset = db.scalar(select(Asset).where(Asset.symbol == sym))
    if asset is None:
        raise AppError(
            status=404,
            title="Not Found",
            detail=f"Unknown asset {sym}",
            type_="https://ouroboros.local/problems/not-found",
        )

    snap = live_fit(db, sym, timeframe, family)
    if snap.skipped and snap.skip_reason == "empty ohlcv":
        raise AppError(
            status=404,
            title="Not Found",
            detail=f"No bars for {sym} {timeframe}",
            type_="https://ouroboros.local/problems/not-found",
        )

    shares = None
    win = None
    if window is not None:
        if window not in BOARD_WINDOWS:
            raise AppError(
                status=422,
                title="Validation Error",
                detail=f"Unsupported window {window}",
                type_="https://ouroboros.local/problems/validation",
            )
        df = load_ohlcv(db, sym, timeframe, lookback_days=120)
        board = board_from_ohlcv(df, family, timeframe=timeframe, window=window)
        shares = {k: float(v) for k, v in board.shares.items()}
        win = board.window

    stale = endpoint_stale(db, "fit")
    return FitSnapshot(
        schema_id="fit.v1",
        symbol=sym,
        timeframe=timeframe,
        family=family,
        tag=snap.tag,
        regime=snap.regime,
        allow_on=snap.allow_on,
        shares=shares,
        window=win,
        fragile_reasons=list(snap.fragile_reasons),
        as_of=snap.as_of if not snap.skipped else datetime.now(UTC),
        provenance=Provenance(
            sources=["mt5.prices", "regimes.rule_v1", MODEL_VERSION],
            generated_at=datetime.now(UTC),
            model_version=MODEL_VERSION,
            confidence=float(snap.confidence),
            stale=stale or snap.skipped,
        ),
        disclaimer=RESEARCH_DISCLAIMER,
    )
