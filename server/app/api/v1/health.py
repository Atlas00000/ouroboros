"""Health and readiness probes."""

from __future__ import annotations

import logging
from typing import Any

import psycopg
import redis
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


class DependencyStatus(BaseModel):
    name: str
    ok: bool
    detail: str | None = None


class HealthResponse(BaseModel):
    status: str = Field(description="'ok' if all critical deps healthy, else 'degraded'")
    service: str
    environment: str
    checks: list[DependencyStatus]


def _check_postgres(database_url: str) -> DependencyStatus:
    try:
        with psycopg.connect(database_url, connect_timeout=3) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return DependencyStatus(name="postgres", ok=True)
    except Exception as exc:  # noqa: BLE001 — surface any connectivity failure
        logger.warning("postgres_health_failed: %s", exc)
        return DependencyStatus(name="postgres", ok=False, detail=str(exc))


def _check_redis(redis_url: str) -> DependencyStatus:
    try:
        client = redis.Redis.from_url(redis_url, socket_connect_timeout=3)
        pong = client.ping()
        client.close()
        if not pong:
            return DependencyStatus(name="redis", ok=False, detail="ping returned false")
        return DependencyStatus(name="redis", ok=True)
    except Exception as exc:  # noqa: BLE001
        logger.warning("redis_health_failed: %s", exc)
        return DependencyStatus(name="redis", ok=False, detail=str(exc))


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    checks = [
        _check_postgres(settings.database_url),
        _check_redis(settings.redis_url),
    ]
    all_ok = all(c.ok for c in checks)
    return HealthResponse(
        status="ok" if all_ok else "degraded",
        service=settings.app_name,
        environment=settings.app_env,
        checks=checks,
    )


@router.get("/health/live")
def liveness() -> dict[str, Any]:
    """Process is up — no dependency checks (for orchestrators)."""
    return {"status": "alive"}
