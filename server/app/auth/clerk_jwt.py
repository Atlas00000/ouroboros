"""Clerk JWT verification via JWKS (humans)."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

import jwt
from jwt import PyJWKClient

from app.auth.roles import HumanPrincipal, parse_role
from app.config import Settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=4)
def _jwks_client(jwks_url: str) -> PyJWKClient:
    return PyJWKClient(jwks_url, cache_keys=True, lifespan=3600)


def verify_clerk_jwt(token: str, settings: Settings) -> HumanPrincipal:
    """
    Verify Bearer JWT.

    Production: Clerk JWKS (RS256).
    Local/test: when ``CLERK_TEST_JWT_SECRET`` is set and JWKS URL is empty,
    accept HS256 tokens signed with that secret (smoke / unit tests only).
    """
    if not token or not token.strip():
        raise jwt.InvalidTokenError("empty token")

    raw = token.strip()
    if settings.clerk_jwks_url:
        client = _jwks_client(settings.clerk_jwks_url)
        signing_key = client.get_signing_key_from_jwt(raw)
        claims = jwt.decode(
            raw,
            signing_key.key,
            algorithms=["RS256"],
            audience=None,
            options={"verify_aud": False},
            leeway=30,
        )
    elif settings.clerk_test_jwt_secret:
        claims = jwt.decode(
            raw,
            settings.clerk_test_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
            leeway=30,
        )
    else:
        raise jwt.InvalidTokenError("Clerk JWKS / test secret not configured")

    _validate_authorized_party(claims, settings)
    if settings.clerk_allowed_org_id:
        org = _claim_org_id(claims)
        if org != settings.clerk_allowed_org_id:
            raise jwt.InvalidTokenError("org not allowed")

    sub = str(claims.get("sub") or "")
    if not sub:
        raise jwt.InvalidTokenError("missing sub")

    role = parse_role(
        (claims.get("public_metadata") or {}).get("role")
        if isinstance(claims.get("public_metadata"), dict)
        else claims.get("role"),
        default="viewer",
    )
    email = claims.get("email")
    return HumanPrincipal(
        subject_id=sub,
        role=role,
        org_id=_claim_org_id(claims),
        email=str(email) if email else None,
    )


def _claim_org_id(claims: dict[str, Any]) -> str | None:
    if claims.get("org_id"):
        return str(claims["org_id"])
    nested = claims.get("o")
    if isinstance(nested, dict) and nested.get("id"):
        return str(nested["id"])
    return None


def _validate_authorized_party(claims: dict[str, Any], settings: Settings) -> None:
    allowed = settings.clerk_authorized_parties_list
    if not allowed:
        return
    azp = claims.get("azp")
    if azp is None:
        return
    if str(azp) not in allowed:
        raise jwt.InvalidTokenError("authorized party not allowed")


def mint_test_jwt(
    *,
    secret: str,
    sub: str = "user_test_w6d1",
    role: str = "analyst",
    hours: int = 1,
) -> str:
    """Mint an HS256 JWT for local smoke tests (requires CLERK_TEST_JWT_SECRET)."""
    from datetime import UTC, datetime, timedelta

    now = datetime.now(UTC)
    payload = {
        "sub": sub,
        "role": role,
        "iat": now,
        "exp": now + timedelta(hours=hours),
        "iss": "ouroboros-test",
    }
    return jwt.encode(payload, secret, algorithm="HS256")
