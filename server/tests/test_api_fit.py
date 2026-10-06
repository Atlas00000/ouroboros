"""API tests for GET /v1/fit (R4)."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("CLERK_TEST_JWT_SECRET", "fit-test-secret-32bytes-minimum!!")
os.environ.setdefault("OUROBOROS_API_KEY_QUANT", "test-quant-key-fit")
os.environ["CLERK_JWKS_URL"] = ""

from app.auth.api_keys import BootstrapKey, upsert_bootstrap_keys
from app.config import get_settings
from app.db.session import get_session_factory
from app.main import app

API_KEY = "test-quant-key-fit"


@pytest.fixture(scope="module", autouse=True)
def _bootstrap() -> None:
    from sqlalchemy import text

    get_settings.cache_clear()
    try:
        session = get_session_factory()()
        session.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"database unavailable: {exc}")
    try:
        upsert_bootstrap_keys(
            session,
            [
                BootstrapKey(
                    name="quant-fit",
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


def test_fit_requires_auth(client: TestClient) -> None:
    res = client.get("/v1/fit", params={"symbol": "EURUSD", "family": "meanrev"})
    assert res.status_code == 401
    assert res.headers["content-type"].startswith("application/problem+json")


def test_fit_unknown_asset(client: TestClient) -> None:
    res = client.get(
        "/v1/fit",
        params={"symbol": "NOTAREAL", "family": "meanrev", "timeframe": "H1"},
        headers={"X-API-Key": API_KEY},
    )
    assert res.status_code == 404


def test_fit_with_api_key(client: TestClient) -> None:
    res = client.get(
        "/v1/fit",
        params={"symbol": "EURUSD", "family": "meanrev", "timeframe": "H1"},
        headers={"X-API-Key": API_KEY},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["schema_id"] == "fit.v1"
    assert body["symbol"] == "EURUSD"
    assert body["family"] == "meanrev"
    assert body["tag"] in ("MATCH", "MISMATCH", "FRAGILE")
    assert body["allow_on"] == (body["tag"] == "MATCH")
    assert body["provenance"]["model_version"] == "fit.map_v0"
    assert "provenance" in body
    assert "disclaimer" in body


def test_fit_with_board_window(client: TestClient) -> None:
    res = client.get(
        "/v1/fit",
        params={
            "symbol": "EURUSD",
            "family": "trendfollow",
            "timeframe": "H1",
            "window": "30d",
        },
        headers={"X-API-Key": API_KEY},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["window"] == "30d"
    assert body["shares"] is not None
    assert set(body["shares"]) >= {"MATCH", "MISMATCH", "FRAGILE"}


def test_openapi_includes_fit(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    assert "/v1/fit" in schema["paths"]
