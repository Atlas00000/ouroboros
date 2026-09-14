"""Ops routes — registry, watchdog, pipe summary (W11)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.auth.roles import HumanPrincipal, ServicePrincipal
from app.db.session import get_db
from app.ingestion.registry import SourceSnapshot, refresh_statuses
from app.intelligence.llm_client import get_daily_spend_usd
from app.models.outbox import OutboxMessage
from app.models.source_registry import SourceRegistry
from app.watchdog.checker import run_check

router = APIRouter(tags=["ops"])

RequireOps = Annotated[
    HumanPrincipal | ServicePrincipal,
    Depends(require_role("admin")),  # admin + ops (role_at_least)
]


class SourceRow(BaseModel):
    source_id: str
    name: str
    kind: str
    expected_cadence_seconds: int
    last_seen_at: datetime | None
    status: str
    age_seconds: float | None
    stale: bool


class RegistryResponse(BaseModel):
    checked_at: datetime
    sources: list[SourceRow]


class WatchdogAlertRow(BaseModel):
    source_id: str
    status: str
    age_seconds: float | None
    message: str


class WatchdogResponse(BaseModel):
    checked_at: datetime
    ok: bool
    stale_count: int
    alerts: list[WatchdogAlertRow]
    sources: list[SourceRow] = Field(default_factory=list)
    rows_marked_stale: dict[str, int] = Field(default_factory=dict)


class LagRow(BaseModel):
    source_id: str
    age_seconds: float | None


class OpsSummaryResponse(BaseModel):
    as_of: datetime
    outbox_unpublished: int
    outbox_published: int
    llm_spend_usd_day: float
    ingestion_lag: list[LagRow]
    health_hint: str


def _snap_to_row(s: SourceSnapshot) -> SourceRow:
    return SourceRow(
        source_id=s.source_id,
        name=s.name,
        kind=s.kind,
        expected_cadence_seconds=s.expected_cadence_seconds,
        last_seen_at=s.last_seen_at,
        status=s.status,
        age_seconds=s.age_seconds,
        stale=s.stale,
    )


@router.get("/ops/ping")
def ops_ping(
    principal: Annotated[
        HumanPrincipal | ServicePrincipal,
        Depends(require_role("ops")),
    ],
) -> dict[str, str]:
    """Strict ops-only stub — returns 403 for viewer/analyst/admin."""
    return {
        "status": "ok",
        "role": principal.role,
        "auth_method": principal.auth_method,
        "subject_id": principal.subject_id,
    }


@router.get("/ops/registry", response_model=RegistryResponse)
def ops_registry(
    _principal: RequireOps,
    db: Annotated[Session, Depends(get_db)],
) -> RegistryResponse:
    """Feed registry with live cadence status (admin+)."""
    now = datetime.now(UTC)
    snaps = refresh_statuses(db, now=now)
    return RegistryResponse(checked_at=now, sources=[_snap_to_row(s) for s in snaps])


@router.get("/ops/watchdog", response_model=WatchdogResponse)
def ops_watchdog(
    _principal: RequireOps,
    db: Annotated[Session, Depends(get_db)],
) -> WatchdogResponse:
    """Run a lightweight watchdog check (no email notify)."""
    report = run_check(db, propagate=False, notify=False)
    return WatchdogResponse(
        checked_at=report.checked_at,
        ok=report.ok,
        stale_count=report.stale_count,
        alerts=[
            WatchdogAlertRow(
                source_id=a.source_id,
                status=a.status,
                age_seconds=a.age_seconds,
                message=a.message,
            )
            for a in report.alerts
        ],
        sources=[_snap_to_row(s) for s in report.sources],
        rows_marked_stale=report.rows_marked_stale,
    )


@router.get("/ops/summary", response_model=OpsSummaryResponse)
def ops_summary(
    _principal: RequireOps,
    db: Annotated[Session, Depends(get_db)],
) -> OpsSummaryResponse:
    """Human-readable pipe health (not raw Prometheus)."""
    now = datetime.now(UTC)
    unpublished = db.scalar(
        select(func.count())
        .select_from(OutboxMessage)
        .where(OutboxMessage.published_at.is_(None))
    )
    published = db.scalar(
        select(func.count())
        .select_from(OutboxMessage)
        .where(OutboxMessage.published_at.is_not(None))
    )
    lags: list[LagRow] = []
    for r in db.scalars(select(SourceRegistry).order_by(SourceRegistry.source_id)).all():
        age: float | None = None
        if r.last_seen_at is not None:
            seen = r.last_seen_at
            if seen.tzinfo is None:
                seen = seen.replace(tzinfo=UTC)
            age = max(0.0, (now - seen.astimezone(UTC)).total_seconds())
        lags.append(LagRow(source_id=r.source_id, age_seconds=age))

    spend = float(get_daily_spend_usd())
    stale_lags = sum(1 for L in lags if L.age_seconds is not None and L.age_seconds > 3600)
    if (unpublished or 0) > 100:
        hint = "outbox backlog elevated"
    elif stale_lags:
        hint = "some feeds lagging >1h"
    else:
        hint = "pipe nominal"

    return OpsSummaryResponse(
        as_of=now,
        outbox_unpublished=int(unpublished or 0),
        outbox_published=int(published or 0),
        llm_spend_usd_day=spend,
        ingestion_lag=lags,
        health_hint=hint,
    )
