"""Health endpoint smoke tests (requires local Docker services for full check)."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_liveness() -> None:
    response = client.get("/v1/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_health_shape() -> None:
    response = client.get("/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "ouroboros-server"
    assert "checks" in body
    assert {c["name"] for c in body["checks"]} >= {"postgres", "redis"}
