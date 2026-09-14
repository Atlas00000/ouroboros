"""W11 ops / scoring / admin key API smoke tests."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("CLERK_TEST_JWT_SECRET", "w11-test-secret-32bytes-minimum!!")
os.environ.setdefault("OUROBOROS_API_KEY_CLIENT", "test-client-admin-w11")
os.environ["CLERK_JWKS_URL"] = ""

from app.auth.api_keys import BootstrapKey, upsert_bootstrap_keys
from app.auth.clerk_jwt import mint_test_jwt
from app.config import get_settings
from app.db.session import get_session_factory
from app.main import app

ADMIN_KEY = "test-client-admin-w11"
JWT_SECRET = "w11-test-secret-32bytes-minimum!!"


@pytest.fixture(scope="module", autouse=True)
def _bootstrap() -> None:
    get_settings.cache_clear()
    os.environ["OUROBOROS_API_KEY_CLIENT"] = ADMIN_KEY
    session = get_session_factory()()
    try:
        upsert_bootstrap_keys(
            session,
            [
                BootstrapKey(
                    name="client",
                    service_name="client",
                    raw_key=ADMIN_KEY,
                    role="admin",
                )
            ],
        )
    finally:
        session.close()


@pytest.fixture
def client() -> TestClient:
    get_settings.cache_clear()
    with TestClient(app) as c:
        yield c


def test_ops_registry_requires_admin(client: TestClient) -> None:
    secret = get_settings().clerk_test_jwt_secret or JWT_SECRET
    viewer = mint_test_jwt(secret=secret, role="viewer")
    res = client.get("/v1/ops/registry", headers={"Authorization": f"Bearer {viewer}"})
    assert res.status_code == 403


def test_ops_registry_ok_for_admin_key(client: TestClient) -> None:
    res = client.get("/v1/ops/registry", headers={"X-API-Key": ADMIN_KEY})
    assert res.status_code == 200
    body = res.json()
    assert "sources" in body
    assert "checked_at" in body


def test_ops_watchdog_and_summary(client: TestClient) -> None:
    h = {"X-API-Key": ADMIN_KEY}
    w = client.get("/v1/ops/watchdog", headers=h)
    assert w.status_code == 200
    assert "alerts" in w.json()
    s = client.get("/v1/ops/summary", headers=h)
    assert s.status_code == 200
    assert "outbox_unpublished" in s.json()


def test_scoring_weekly_list(client: TestClient) -> None:
    res = client.get("/v1/scoring/weekly", headers={"X-API-Key": ADMIN_KEY})
    assert res.status_code == 200
    assert "items" in res.json()


def test_admin_keys_mint_list_revoke(client: TestClient) -> None:
    h = {"X-API-Key": ADMIN_KEY}
    name = "w11_smoke_key"
    # cleanup if prior run left it
    listed = client.get("/v1/admin/keys", headers=h)
    assert listed.status_code == 200
    for item in listed.json()["items"]:
        if item["name"] == name and item["is_active"]:
            client.post(f"/v1/admin/keys/{item['id']}/revoke", headers=h)

    minted = client.post(
        "/v1/admin/keys",
        headers=h,
        json={"name": name, "service_name": "quant", "role": "viewer"},
    )
    assert minted.status_code == 201, minted.text
    body = minted.json()
    assert body["plaintext"].startswith("ob_live_")
    kid = body["key"]["id"]

    again = client.post(
        "/v1/admin/keys",
        headers=h,
        json={"name": name, "service_name": "quant", "role": "viewer"},
    )
    assert again.status_code == 409

    rev = client.post(f"/v1/admin/keys/{kid}/revoke", headers=h)
    assert rev.status_code == 200
    assert rev.json()["is_active"] is False
