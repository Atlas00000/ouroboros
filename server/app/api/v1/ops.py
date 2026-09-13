"""Ops-only stub routes (W6·D2 role check)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth.dependencies import require_role
from app.auth.roles import HumanPrincipal, ServicePrincipal

router = APIRouter(tags=["ops"])


@router.get("/ops/ping")
def ops_ping(
    principal: Annotated[
        HumanPrincipal | ServicePrincipal,
        Depends(require_role("ops")),
    ],
) -> dict[str, str]:
    """Stub ops-only route — returns 403 for viewer/analyst/admin."""
    return {
        "status": "ok",
        "role": principal.role,
        "auth_method": principal.auth_method,
        "subject_id": principal.subject_id,
    }
