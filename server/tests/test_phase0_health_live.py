"""Live dependency health — Phase 0 (Docker Postgres/Redis must be up)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_dependencies_ok() -> None:
    response = client.get("/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    by_name = {c["name"]: c for c in body["checks"]}
    assert by_name["postgres"]["ok"] is True
    assert by_name["redis"]["ok"] is True


def test_openapi_available() -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    spec = response.json()
    assert "/v1/health" in spec["paths"]
    assert "/v1/health/live" in spec["paths"]
