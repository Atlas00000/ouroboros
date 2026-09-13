"""Auth + assets/profiles API tests (W6·D1)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.auth.api_keys import hash_api_key
from app.auth.clerk_jwt import mint_test_jwt
from app.config import get_settings
from tests.conftest import PHASE3_API_KEY, PHASE3_JWT_SECRET


def test_assets_requires_auth(phase3_client: TestClient) -> None:
    res = phase3_client.get("/v1/assets")
    assert res.status_code == 401
    assert res.headers["content-type"].startswith("application/problem+json")
    body = res.json()
    assert body["status"] == 401
    assert "title" in body


def test_assets_with_api_key(phase3_client: TestClient) -> None:
    res = phase3_client.get("/v1/assets", headers={"X-API-Key": PHASE3_API_KEY})
    assert res.status_code == 200
    body = res.json()
    assert "items" in body
    assert "provenance" in body
    assert body["provenance"]["model_version"] == "assets.list.v1"
    assert any(i["symbol"] == "EURUSD" for i in body["items"])


def test_assets_with_clerk_test_jwt(phase3_client: TestClient) -> None:
    secret = get_settings().clerk_test_jwt_secret or PHASE3_JWT_SECRET
    token = mint_test_jwt(secret=secret, role="analyst")
    res = phase3_client.get("/v1/assets", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["provenance"]["sources"] == ["db.assets"]


def test_profile_with_api_key(phase3_client: TestClient) -> None:
    res = phase3_client.get(
        "/v1/assets/EURUSD/profile",
        headers={"X-API-Key": PHASE3_API_KEY},
    )
    # 200 if profile exists, 404 if not yet built — both prove auth works
    assert res.status_code in (200, 404)


def test_hash_api_key_stable() -> None:
    assert hash_api_key("abc") == hash_api_key("abc")
    assert hash_api_key("abc") != hash_api_key("abd")
