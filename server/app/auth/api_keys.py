"""Machine API key hashing and verification (X-API-Key)."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.roles import Role, ServicePrincipal
from app.models.api_key import ApiKeyRow


def hash_api_key(raw_key: str) -> str:
    """SHA-256 hex digest of the plaintext key (never store plaintext)."""
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def generate_api_key(*, prefix: str = "ob_live") -> str:
    """Generate a new plaintext key (show once to the operator)."""
    return f"{prefix}_{secrets.token_urlsafe(32)}"


@dataclass(frozen=True)
class BootstrapKey:
    name: str
    service_name: str
    raw_key: str
    role: Role = "viewer"


def verify_api_key(session: Session, raw_key: str) -> ServicePrincipal | None:
    """Look up active key by hash; constant-time compare on hash match path."""
    if not raw_key or not raw_key.strip():
        return None
    digest = hash_api_key(raw_key.strip())
    row = session.scalar(
        select(ApiKeyRow).where(ApiKeyRow.key_hash == digest, ApiKeyRow.is_active.is_(True))
    )
    if row is None:
        return None
    # Defense in depth if ORM somehow returned a mismatched row
    if not hmac.compare_digest(row.key_hash, digest):
        return None
    return ServicePrincipal(
        subject_id=f"api_key:{row.name}",
        service_name=row.service_name,
        role=row.role,  # type: ignore[arg-type]
        auth_method="api_key",
    )


def upsert_bootstrap_keys(session: Session, keys: list[BootstrapKey]) -> int:
    """Insert or update hashed keys from env bootstrap values. Returns upsert count."""
    n = 0
    for item in keys:
        if not item.raw_key.strip():
            continue
        digest = hash_api_key(item.raw_key.strip())
        existing = session.scalar(select(ApiKeyRow).where(ApiKeyRow.name == item.name))
        if existing is None:
            session.add(
                ApiKeyRow(
                    name=item.name,
                    service_name=item.service_name,
                    key_hash=digest,
                    role=item.role,
                    is_active=True,
                )
            )
            n += 1
        elif existing.key_hash != digest:
            existing.key_hash = digest
            existing.service_name = item.service_name
            existing.role = item.role
            existing.is_active = True
            n += 1
    session.commit()
    return n
