"""HTTP metrics middleware + GET /metrics (Prometheus text)."""

from __future__ import annotations

import logging
from typing import Callable

from fastapi import FastAPI, Request, Response
from sqlalchemy import func, select
from starlette.middleware.base import BaseHTTPMiddleware

from app.db.session import get_session_factory
from app.intelligence.llm_client import get_daily_spend_usd
from app.models.outbox import OutboxMessage
from app.models.source_registry import SourceRegistry
from app.observability.prom_metrics import Timer, observe_request, render_prometheus_text

logger = logging.getLogger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path == "/metrics":
            return await call_next(request)
        timer = Timer()
        response: Response | None = None
        try:
            response = await call_next(request)
            return response
        finally:
            auth = getattr(request.state, "auth_method", None)
            status = response.status_code if response is not None else 500
            observe_request(
                method=request.method,
                path=request.url.path,
                status=status,
                duration_sec=timer.seconds(),
                auth_method=str(auth) if auth else None,
            )


def _collect_runtime_gauges() -> dict[str, tuple[str, dict]]:
    gauges: dict[str, tuple[str, dict]] = {}
    session = get_session_factory()()
    try:
        from datetime import UTC, datetime

        now = datetime.now(UTC)
        lag_values: dict[tuple[tuple[str, str], ...], float] = {}
        rows = list(session.scalars(select(SourceRegistry)).all())
        for r in rows:
            if r.last_seen_at is None:
                continue
            seen = r.last_seen_at
            if seen.tzinfo is None:
                seen = seen.replace(tzinfo=UTC)
            age = max(0.0, (now - seen).total_seconds())
            lag_values[(("source_id", r.source_id),)] = float(age)
        gauges["ouroboros_ingestion_lag_seconds"] = (
            "Seconds since last_seen_at per source_registry feed",
            lag_values,
        )

        unpublished = session.scalar(
            select(func.count())
            .select_from(OutboxMessage)
            .where(OutboxMessage.published_at.is_(None))
        )
        published = session.scalar(
            select(func.count())
            .select_from(OutboxMessage)
            .where(OutboxMessage.published_at.is_not(None))
        )
        gauges["ouroboros_outbox_unpublished"] = (
            "Outbox rows not yet published to Redis Streams",
            {(): float(unpublished or 0)},
        )
        gauges["ouroboros_outbox_published_total"] = (
            "Outbox rows with published_at set (approx lifetime)",
            {(): float(published or 0)},
        )
    except Exception:
        logger.exception("metrics_gauge_collect_failed")
    finally:
        session.close()

    spend = get_daily_spend_usd()
    gauges["ouroboros_llm_spend_usd_day"] = (
        "Estimated LLM spend USD for the current UTC day",
        {(): float(spend)},
    )
    return gauges


def mount_metrics(app: FastAPI) -> None:
    app.add_middleware(MetricsMiddleware)

    @app.get("/metrics", include_in_schema=False)
    def prometheus_metrics() -> Response:
        body = render_prometheus_text(extra_gauges=_collect_runtime_gauges())
        return Response(content=body, media_type="text/plain; version=0.0.4; charset=utf-8")
