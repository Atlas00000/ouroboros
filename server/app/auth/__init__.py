"""Auth package — dual Clerk JWT + hashed API keys (ADR-015)."""

from app.auth.api_keys import generate_api_key, hash_api_key, upsert_bootstrap_keys, verify_api_key
from app.auth.clerk_jwt import mint_test_jwt, verify_clerk_jwt
from app.auth.dependencies import RequirePrincipal, get_principal, require_role
from app.auth.roles import HumanPrincipal, Principal, Role, ServicePrincipal, role_at_least

__all__ = [
    "HumanPrincipal",
    "Principal",
    "RequirePrincipal",
    "Role",
    "ServicePrincipal",
    "generate_api_key",
    "get_principal",
    "hash_api_key",
    "mint_test_jwt",
    "require_role",
    "role_at_least",
    "upsert_bootstrap_keys",
    "verify_api_key",
    "verify_clerk_jwt",
]
