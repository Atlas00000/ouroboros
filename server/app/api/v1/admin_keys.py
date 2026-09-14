"""Admin API key mint / list / revoke (W11)."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.errors import AppError
from app.auth.api_keys import generate_api_key, hash_api_key
from app.auth.dependencies import require_role
from app.auth.roles import HumanPrincipal, Role, ServicePrincipal, parse_role
from app.db.session import get_db
from app.models.api_key import ApiKeyRow

router = APIRouter(tags=["admin"])

RequireAdmin = Annotated[
    HumanPrincipal | ServicePrincipal,
    Depends(require_role("admin")),
]

KeyRole = Literal["viewer", "analyst", "admin", "ops"]


class ApiKeyPublic(BaseModel):
    id: int
    name: str
    service_name: str
    role: str
    is_active: bool
    created_at: datetime


class ApiKeyListResponse(BaseModel):
    items: list[ApiKeyPublic]


class MintKeyRequest(BaseModel):
    name: str = Field(min_length=2, max_length=64, pattern=r"^[a-zA-Z0-9_\-]+$")
    service_name: str = Field(min_length=2, max_length=64)
    role: KeyRole = "viewer"


class MintKeyResponse(BaseModel):
    key: ApiKeyPublic
    plaintext: str = Field(description="Show once — never stored or returned again")


class RevokeKeyResponse(BaseModel):
    id: int
    name: str
    is_active: bool


def _public(row: ApiKeyRow) -> ApiKeyPublic:
    return ApiKeyPublic(
        id=row.id,
        name=row.name,
        service_name=row.service_name,
        role=row.role,
        is_active=row.is_active,
        created_at=row.created_at,
    )


@router.get("/admin/keys", response_model=ApiKeyListResponse)
def list_keys(
    _principal: RequireAdmin,
    db: Annotated[Session, Depends(get_db)],
) -> ApiKeyListResponse:
    rows = list(db.scalars(select(ApiKeyRow).order_by(ApiKeyRow.created_at.desc())).all())
    return ApiKeyListResponse(items=[_public(r) for r in rows])


@router.post("/admin/keys", response_model=MintKeyResponse, status_code=201)
def mint_key(
    body: MintKeyRequest,
    _principal: RequireAdmin,
    db: Annotated[Session, Depends(get_db)],
) -> MintKeyResponse:
    existing = db.scalar(select(ApiKeyRow).where(ApiKeyRow.name == body.name))
    if existing is not None:
        raise AppError(
            status=409,
            title="Conflict",
            detail=f"Key name already exists: {body.name}",
            type_="https://ouroboros.local/problems/conflict",
        )
    role: Role = parse_role(body.role)
    plaintext = generate_api_key(prefix="ob_live")
    row = ApiKeyRow(
        name=body.name,
        service_name=body.service_name,
        key_hash=hash_api_key(plaintext),
        role=role,
        is_active=True,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return MintKeyResponse(key=_public(row), plaintext=plaintext)


@router.post("/admin/keys/{key_id}/revoke", response_model=RevokeKeyResponse)
def revoke_key(
    key_id: int,
    _principal: RequireAdmin,
    db: Annotated[Session, Depends(get_db)],
) -> RevokeKeyResponse:
    row = db.get(ApiKeyRow, key_id)
    if row is None:
        raise AppError(
            status=404,
            title="Not Found",
            detail=f"Unknown key id {key_id}",
            type_="https://ouroboros.local/problems/not-found",
        )
    row.is_active = False
    db.commit()
    return RevokeKeyResponse(id=row.id, name=row.name, is_active=row.is_active)
