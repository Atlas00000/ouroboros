"""W8 API — /metrics prometheus + stale provenance smoke."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("CLERK_TEST_JWT_SECRET", "w8-test-secret-32bytes-minimum!!")
os.environ.setdefault("OUROBOROS_API_KEY_EPG", "test-epg-key-w8")
os.environ["CLERK_JWKS_URL"] = ""

from app.auth.api_keys import BootstrapKey, upsert_bootstrap_keys
from app.config import get_settings
from app.db.session import get_session_factory
from app.main import app
from app.models.source_registry import SourceRegistry
from sqlalchemy import select


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
                    raw_key="test-epg-key-w8",
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


def test_prometheus_metrics_public(client: TestClient) -> None:
    res = client.get("/metrics")
    assert res.status_code == 200
    assert "text/plain" in res.headers["content-type"]
    body = res.text
    assert "ouroboros_http_requests_total" in body or "ouroboros_llm_spend_usd_day" in body


def test_assets_stale_flag_when_prices_stale(client: TestClient) -> None:
    session = get_session_factory()()
    try:
        row = session.scalar(select(SourceRegistry).where(SourceRegistry.source_id == "mt5.prices"))
        if row is None:
            pytest.skip("mt5.prices not seeded")
        prev = row.status
        row.status = "stale"
        session.commit()
        try:
            res = client.get("/v1/assets", headers={"X-API-Key": "test-epg-key-w8"})
            assert res.status_code == 200
            assert res.json()["provenance"]["stale"] is True
        finally:
            row.status = prev
            session.commit()
    finally:
        session.close()
