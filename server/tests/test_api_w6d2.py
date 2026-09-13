"""W6·D2 API tests — state, metrics, news, ops role stub."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("CLERK_TEST_JWT_SECRET", "w6d2-test-secret-32bytes-minimum!")
os.environ.setdefault("OUROBOROS_API_KEY_QUANT", "test-quant-key-w6d2")
os.environ["CLERK_JWKS_URL"] = ""

from app.auth.api_keys import BootstrapKey, upsert_bootstrap_keys
from app.auth.clerk_jwt import mint_test_jwt
from app.config import get_settings
from app.db.session import get_session_factory
from app.main import app

API_KEY = "test-quant-key-w6d2"
JWT_SECRET = "w6d2-test-secret-32bytes-minimum!"


@pytest.fixture(scope="module", autouse=True)
def _bootstrap() -> None:
    get_settings.cache_clear()
    session = get_session_factory()()
    try:
        upsert_bootstrap_keys(
            session,
            [
                BootstrapKey(
                    name="quant",
                    service_name="quant",
                    raw_key=API_KEY,
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


def test_state_metrics_news_require_auth(client: TestClient) -> None:
    for path in ("/v1/state?symbol=EURUSD", "/v1/metrics?symbol=EURUSD", "/v1/news"):
        res = client.get(path)
        assert res.status_code == 401
        assert res.headers["content-type"].startswith("application/problem+json")


def test_metrics_with_api_key(client: TestClient) -> None:
    res = client.get(
        "/v1/metrics",
        params={"symbol": "EURUSD", "timeframe": "H1"},
        headers={"X-API-Key": API_KEY},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["symbol"] == "EURUSD"
    assert body["model_version"] == "metrics.v1"
    assert "provenance" in body


def test_state_with_api_key(client: TestClient) -> None:
    res = client.get(
        "/v1/state",
        params={"symbol": "EURUSD", "timeframe": "H1", "refresh": True},
        headers={"X-API-Key": API_KEY},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["schema_id"] == "state.v1"
    assert body["symbol"] == "EURUSD"
    assert "regime" in body
    assert "provenance" in body


def test_news_list_with_jwt(client: TestClient) -> None:
    secret = get_settings().clerk_test_jwt_secret or JWT_SECRET
    token = mint_test_jwt(secret=secret, role="analyst")
    res = client.get("/v1/news", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    body = res.json()
    assert "items" in body
    assert body["provenance"]["model_version"] == "news.list.v1"


def test_ops_ping_forbidden_for_viewer(client: TestClient) -> None:
    res = client.get("/v1/ops/ping", headers={"X-API-Key": API_KEY})
    assert res.status_code == 403


def test_ops_ping_ok_for_ops_jwt(client: TestClient) -> None:
    secret = get_settings().clerk_test_jwt_secret or JWT_SECRET
    token = mint_test_jwt(secret=secret, role="ops")
    res = client.get("/v1/ops/ping", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["role"] == "ops"
