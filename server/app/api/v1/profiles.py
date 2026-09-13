"""GET /v1/assets/{symbol}/profile — latest AssetProfile (profile.v1)."""

from __future__ import annotations

from typing import Annotated

from contracts.profile_v1 import AssetProfile
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.profile_store import latest_profile_row
from app.api.errors import AppError
from app.api.staleness import endpoint_stale
from app.auth.dependencies import RequirePrincipal
from app.db.session import get_db
from app.models.asset import Asset

router = APIRouter(tags=["profiles"])


@router.get("/assets/{symbol}/profile", response_model=AssetProfile)
def get_asset_profile(
    symbol: str,
    _principal: RequirePrincipal,
    db: Annotated[Session, Depends(get_db)],
) -> AssetProfile:
    sym = symbol.upper()
    asset = db.scalar(select(Asset).where(Asset.symbol == sym))
    if asset is None:
        raise AppError(
            status=404,
            title="Not Found",
            detail=f"Unknown asset {sym}",
            type_="https://ouroboros.local/problems/not-found",
        )
    row = latest_profile_row(db, sym)
    if row is None:
        raise AppError(
            status=404,
            title="Not Found",
            detail=f"No profile stored for {sym}",
            type_="https://ouroboros.local/problems/not-found",
        )
    profile = AssetProfile.model_validate_json(row.payload_json)
    # Propagate DB/watchdog or live feed staleness onto provenance
    feed_stale = endpoint_stale(db, "profiles") or bool(row.stale)
    if feed_stale and not profile.provenance.stale:
        profile = profile.model_copy(
            update={"provenance": profile.provenance.model_copy(update={"stale": True})}
        )
    return profile
