"""API smoke for /v1/sentiment and /v1/insights (W7)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import PHASE3_API_KEY


def test_sentiment_requires_auth(phase3_client: TestClient) -> None:
    res = phase3_client.get("/v1/sentiment", params={"symbol": "EURUSD"})
    assert res.status_code == 401


def test_insights_requires_auth(phase3_client: TestClient) -> None:
    res = phase3_client.get("/v1/insights", params={"symbol": "EURUSD"})
    assert res.status_code == 401


def test_sentiment_unknown_asset(phase3_client: TestClient) -> None:
    res = phase3_client.get(
        "/v1/sentiment",
        params={"symbol": "NOSUCH"},
        headers={"X-API-Key": PHASE3_API_KEY},
    )
    assert res.status_code == 404


def test_insights_unknown_asset(phase3_client: TestClient) -> None:
    res = phase3_client.get(
        "/v1/insights",
        params={"symbol": "NOSUCH"},
        headers={"X-API-Key": PHASE3_API_KEY},
    )
    assert res.status_code == 404
