"""API-facing staleness helpers (W8·D2).

Reads ``source_registry`` so list/metrics/news provenance can flip ``stale: true``
when upstream feeds are past cadence (aligned with watchdog targets).
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.source_registry import SourceRegistry

# Endpoint → feeds that should mark the response stale when any is status=stale
ENDPOINT_FEED_MAP: dict[str, tuple[str, ...]] = {
    "assets": ("mt5.prices",),
    "metrics": ("mt5.prices",),
    "state": ("mt5.prices",),
    "profiles": ("mt5.prices",),
    "news": ("finnhub.news", "finnhub.calendar"),
    "sentiment": ("finnhub.news",),
    "insights": ("finnhub.news", "mt5.prices"),
}


def source_statuses(session: Session, source_ids: tuple[str, ...] | list[str]) -> dict[str, str]:
    if not source_ids:
        return {}
    rows = session.scalars(
        select(SourceRegistry).where(SourceRegistry.source_id.in_(list(source_ids)))
    ).all()
    return {r.source_id: r.status for r in rows}


def any_feed_stale(
    session: Session,
    source_ids: tuple[str, ...] | list[str],
) -> bool:
    statuses = source_statuses(session, source_ids)
    return any(statuses.get(sid) == "stale" for sid in source_ids)


def endpoint_stale(session: Session, endpoint: str) -> bool:
    feeds = ENDPOINT_FEED_MAP.get(endpoint, ())
    return any_feed_stale(session, feeds) if feeds else False


def with_feed_stale(model, session: Session, endpoint: str):
    """Return a copy of a contract model with provenance.stale=True when feeds are stale."""
    if endpoint_stale(session, endpoint) and not model.provenance.stale:
        return model.model_copy(
            update={"provenance": model.provenance.model_copy(update={"stale": True})}
        )
    return model
