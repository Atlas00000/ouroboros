"""FastAPI auth dependencies — dual auth (Clerk JWT | X-API-Key)."""

from __future__ import annotations

import logging
from typing import Annotated

import jwt
from fastapi import Depends, Header, Request
from sqlalchemy.orm import Session

from app.api.errors import AppError
from app.auth.api_keys import verify_api_key
from app.auth.clerk_jwt import verify_clerk_jwt
from app.auth.roles import HumanPrincipal, Principal, Role, ServicePrincipal, role_at_least
from app.config import Settings, get_settings
from app.db.session import get_db

logger = logging.getLogger(__name__)


def get_principal(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    authorization: Annotated[str | None, Header()] = None,
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> HumanPrincipal | ServicePrincipal:
    """
    Resolve Clerk Bearer JWT or machine API key into a principal.

    Prefer API key when both are present (machine clients).
    """
    if x_api_key:
        principal = verify_api_key(db, x_api_key)
        if principal is None:
            raise AppError(
                status=401,
                title="Unauthorized",
                detail="Invalid API key",
                type_="https://ouroboros.local/problems/unauthorized",
            )
        request.state.auth_method = principal.auth_method
        request.state.subject_id = principal.subject_id
        return principal

    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        try:
            principal = verify_clerk_jwt(token, settings)
        except jwt.PyJWTError as exc:
            logger.info("clerk_jwt_rejected: %s", exc)
            raise AppError(
                status=401,
                title="Unauthorized",
                detail="Invalid or expired bearer token",
                type_="https://ouroboros.local/problems/unauthorized",
            ) from exc
        request.state.auth_method = principal.auth_method
        request.state.subject_id = principal.subject_id
        return principal

    raise AppError(
        status=401,
        title="Unauthorized",
        detail="Provide Authorization: Bearer <jwt> or X-API-Key",
        type_="https://ouroboros.local/problems/unauthorized",
    )


RequirePrincipal = Annotated[HumanPrincipal | ServicePrincipal, Depends(get_principal)]


def require_role(minimum: Role):
    """Dependency factory: principal must have at least ``minimum`` role."""

    def _dep(principal: RequirePrincipal) -> HumanPrincipal | ServicePrincipal:
        if not role_at_least(principal.role, minimum):
            raise AppError(
                status=403,
                title="Forbidden",
                detail=f"Requires role >= {minimum}",
                type_="https://ouroboros.local/problems/forbidden",
            )
        return principal

    return _dep
