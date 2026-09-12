"""Smoke: dual-auth against /v1/assets (API key + test Clerk JWT)."""

from __future__ import annotations

import os
import sys

os.chdir(os.path.dirname(__file__))
sys.path.insert(0, os.getcwd())

from fastapi.testclient import TestClient

from app.auth.api_keys import BootstrapKey, upsert_bootstrap_keys
from app.auth.clerk_jwt import mint_test_jwt
from app.config import get_settings
from app.db.session import get_session_factory
from app.main import app


def main() -> int:
    # Prefer env; fall back to local smoke secrets
    os.environ.setdefault("CLERK_TEST_JWT_SECRET", "w6d1-smoke-secret")
    if not os.environ.get("OUROBOROS_API_KEY_EPG"):
        os.environ["OUROBOROS_API_KEY_EPG"] = "smoke-epg-key"
    os.environ["CLERK_JWKS_URL"] = ""
    get_settings.cache_clear()
    settings = get_settings()

    session = get_session_factory()()
    try:
        raw = settings.ouroboros_api_key_epg or "smoke-epg-key"
        upsert_bootstrap_keys(
            session,
            [BootstrapKey(name="epg", service_name="epg", raw_key=raw, role="viewer")],
        )
    finally:
        session.close()

    client = TestClient(app)
    r1 = client.get("/v1/assets", headers={"X-API-Key": raw})
    print(f"api_key status={r1.status_code} items={len(r1.json().get('items', []))}")

    secret = settings.clerk_test_jwt_secret or "w6d1-smoke-secret"
    token = mint_test_jwt(secret=secret, role="analyst")
    r2 = client.get("/v1/assets", headers={"Authorization": f"Bearer {token}"})
    print(f"clerk_jwt status={r2.status_code} items={len(r2.json().get('items', []))}")

    r3 = client.get("/v1/assets/EURUSD/profile", headers={"X-API-Key": raw})
    print(f"profile status={r3.status_code}")
    return 0 if r1.status_code == 200 and r2.status_code == 200 else 1


if __name__ == "__main__":
    raise SystemExit(main())
