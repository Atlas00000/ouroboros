"""Auth + assets/profiles API tests (W6·D1)."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

# Configure test auth before app settings are cached
os.environ.setdefault("CLERK_TEST_JWT_SECRET", "w6d1-test-secret-32bytes-minimum!")
os.environ.setdefault("OUROBOROS_API_KEY_EPG", "test-epg-key-w6d1")
os.environ["CLERK_JWKS_URL"] = ""  # force HS256 test path

from app.auth.api_keys import BootstrapKey, hash_api_key, upsert_bootstrap_keys
from app.auth.clerk_jwt import mint_test_jwt
from app.config import get_settings
from app.db.session import get_session_factory
from app.main import app


@pytest.fixture(scope="module", autouse=True)
def _bootstrap_test_key() -> None:
    get_settings.cache_clear()
    session = get_session_factory()()
    try:
        upsert_bootstrap_keys(
            session,
            [
                BootstrapKey(
                    name="epg",
                    service_name="epg",
                    raw_key="test-epg-key-w6d1",
                    role="viewer",
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


def test_assets_requires_auth(client: TestClient) -> None:
    res = client.get("/v1/assets")
    assert res.status_code == 401
    assert res.headers["content-type"].startswith("application/problem+json")
    body = res.json()
    assert body["status"] == 401
    assert "title" in body


def test_assets_with_api_key(client: TestClient) -> None:
    res = client.get("/v1/assets", headers={"X-API-Key": "test-epg-key-w6d1"})
    assert res.status_code == 200
    body = res.json()
    assert "items" in body
    assert "provenance" in body
    assert body["provenance"]["model_version"] == "assets.list.v1"
    assert any(i["symbol"] == "EURUSD" for i in body["items"])


def test_assets_with_clerk_test_jwt(client: TestClient) -> None:
    token = mint_test_jwt(secret="w6d1-test-secret-32bytes-minimum!", role="analyst")
    res = client.get("/v1/assets", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["provenance"]["sources"] == ["db.assets"]


def test_profile_with_api_key(client: TestClient) -> None:
    res = client.get(
        "/v1/assets/EURUSD/profile",
        headers={"X-API-Key": "test-epg-key-w6d1"},
    )
    # 200 if smoke profile exists from W5; 404 if empty DB profile table
    assert res.status_code in (200, 404)
    if res.status_code == 404:
        assert res.headers["content-type"].startswith("application/problem+json")
    else:
        body = res.json()
        assert body["schema_id"] == "profile.v1"
        assert body["identity"]["symbol"] == "EURUSD"
        assert "provenance" in body


def test_hash_api_key_stable() -> None:
    assert hash_api_key("abc") == hash_api_key("abc")
    assert hash_api_key("abc") != hash_api_key("abcd")
