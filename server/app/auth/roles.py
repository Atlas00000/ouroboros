"""Auth roles and principal types (ADR-015)."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field

Role = Literal["viewer", "analyst", "admin", "ops"]
AuthMethod = Literal["clerk", "api_key"]

ROLE_ORDER: dict[Role, int] = {
    "viewer": 1,
    "analyst": 2,
    "admin": 3,
    "ops": 4,
}


class HumanPrincipal(BaseModel):
    subject_id: str = Field(description="Clerk user id")
    role: Role = "viewer"
    auth_method: Literal["clerk"] = "clerk"
    org_id: str | None = None
    email: str | None = None


class ServicePrincipal(BaseModel):
    subject_id: str = Field(description="Stable id for the key / service")
    service_name: str
    role: Role = "viewer"
    auth_method: Literal["api_key"] = "api_key"


Principal = Annotated[HumanPrincipal | ServicePrincipal, Field(discriminator="auth_method")]


def role_at_least(principal_role: Role, required: Role) -> bool:
    return ROLE_ORDER.get(principal_role, 0) >= ROLE_ORDER.get(required, 99)


def parse_role(value: object, *, default: Role = "viewer") -> Role:
    if isinstance(value, str) and value in ROLE_ORDER:
        return value  # type: ignore[return-value]
    return default
