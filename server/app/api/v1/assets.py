"""GET /v1/assets — authenticated asset universe list."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.pagination import ProvenanceEnvelope, encode_cursor, decode_cursor
from app.auth.dependencies import RequirePrincipal
from app.db.session import get_db
from app.models.asset import Asset

router = APIRouter(tags=["assets"])


class AssetListItem(BaseModel):
    symbol: str
    display_name: str
    asset_class: str
    mt5_ticker: str | None = None
    base_currency: str | None = None
    quote_currency: str | None = None
    venues: list[str] = Field(default_factory=list)
    is_active: bool = True


class AssetListResponse(BaseModel):
    items: list[AssetListItem]
    next_cursor: str | None = None
    has_more: bool = False
    provenance: ProvenanceEnvelope


def _venues_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [v.strip() for v in str(raw).split(",") if v.strip()]


@router.get("/assets", response_model=AssetListResponse)
def list_assets(
    _principal: RequirePrincipal,
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    cursor: Annotated[str | None, Query()] = None,
    active_only: Annotated[bool, Query()] = True,
) -> AssetListResponse:
    stmt = select(Asset).order_by(Asset.symbol.asc())
    if active_only:
        stmt = stmt.where(Asset.is_active.is_(True))
    if cursor:
        payload = decode_cursor(cursor)
        after = str(payload.get("symbol") or "")
        if after:
            stmt = stmt.where(Asset.symbol > after)

    rows = list(db.scalars(stmt.limit(limit + 1)).all())
    has_more = len(rows) > limit
    page = rows[:limit]
    next_cursor = encode_cursor({"symbol": page[-1].symbol}) if has_more and page else None

    items = [
        AssetListItem(
            symbol=r.symbol,
            display_name=r.display_name,
            asset_class=r.asset_class,
            mt5_ticker=r.mt5_ticker,
            base_currency=r.base_currency,
            quote_currency=r.quote_currency,
            venues=_venues_list(r.venues),
            is_active=bool(r.is_active),
        )
        for r in page
    ]
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    return AssetListResponse(
        items=items,
        next_cursor=next_cursor,
        has_more=has_more,
        provenance=ProvenanceEnvelope(
            sources=["db.assets"],
            generated_at=now,
            model_version="assets.list.v1",
            confidence=1.0,
            stale=False,
        ),
    )
