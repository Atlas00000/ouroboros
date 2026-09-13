"""W8 API — /metrics prometheus + stale provenance smoke."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.session import get_session_factory
from app.models.source_registry import SourceRegistry
from tests.conftest import PHASE3_API_KEY


def test_prometheus_metrics_public(phase3_client: TestClient) -> None:
    res = phase3_client.get("/metrics")
    assert res.status_code == 200
    assert "text/plain" in res.headers["content-type"]
    body = res.text
    assert "ouroboros_http_requests_total" in body or "ouroboros_llm_spend_usd_day" in body


def test_assets_stale_flag_when_prices_stale(phase3_client: TestClient) -> None:
    session = get_session_factory()()
    try:
        row = session.scalar(select(SourceRegistry).where(SourceRegistry.source_id == "mt5.prices"))
        if row is None:
            pytest.skip("mt5.prices not seeded")
        prev = row.status
        row.status = "stale"
        session.commit()
        try:
            res = phase3_client.get("/v1/assets", headers={"X-API-Key": PHASE3_API_KEY})
            assert res.status_code == 200
            assert res.json()["provenance"]["stale"] is True
        finally:
            row.status = prev
            session.commit()
    finally:
        session.close()
