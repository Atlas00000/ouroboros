"""API smoke for /v1/sentiment and /v1/insights (W7)."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("CLERK_TEST_JWT_SECRET", "w7-test-secret-32bytes-minimum!!")
os.environ.setdefault("OUROBOROS_API_KEY_EPG", "test-epg-key-w7")
os.environ.setdefault("LLM_PROVIDERS", "mock")
os.environ["CLERK_JWKS_URL"] = ""

from app.auth.api_keys import BootstrapKey, upsert_bootstrap_keys
from app.config import get_settings
from app.db.session import get_session_factory
from app.main import app


@pytest.fixture(scope="module", autouse=True)
def _bootstrap() -> None:
    get_settings.cache_clear()
    session = get_session_factory()()
    try:
        upsert_bootstrap_keys(
            session,
            [
                BootstrapKey(
                    name="epg",
                    service_name="epg",
                    raw_key="test-epg-key-w7",
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


def test_sentiment_requires_auth(client: TestClient) -> None:
    res = client.get("/v1/sentiment", params={"symbol": "EURUSD"})
    assert res.status_code == 401


def test_insights_requires_auth(client: TestClient) -> None:
    res = client.get("/v1/insights", params={"symbol": "EURUSD"})
    assert res.status_code == 401


def test_sentiment_unknown_asset(client: TestClient) -> None:
    res = client.get(
        "/v1/sentiment",
        params={"symbol": "NOSUCH"},
        headers={"X-API-Key": "test-epg-key-w7"},
    )
    assert res.status_code == 404


def test_insights_unknown_asset(client: TestClient) -> None:
    res = client.get(
        "/v1/insights",
        params={"symbol": "NOSUCH"},
        headers={"X-API-Key": "test-epg-key-w7"},
    )
    assert res.status_code == 404
