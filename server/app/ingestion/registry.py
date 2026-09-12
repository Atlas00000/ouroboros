"""Source registry — cadence expectations and heartbeats."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.source_registry import SourceRegistry

logger = logging.getLogger(__name__)

# Age beyond this multiple of expected_cadence_seconds → status "stale".
DEFAULT_STALE_MULTIPLIER = 2.0

STATUS_OK = "ok"
STATUS_STALE = "stale"
STATUS_UNKNOWN = "unknown"
STATUS_ERROR = "error"


@dataclass(frozen=True)
class SourceSnapshot:
    source_id: str
    name: str
    kind: str
    expected_cadence_seconds: int
    last_seen_at: datetime | None
    status: str
    age_seconds: float | None
    stale: bool


def get_source(session: Session, source_id: str) -> SourceRegistry | None:
    return session.scalar(select(SourceRegistry).where(SourceRegistry.source_id == source_id))


def list_sources(session: Session) -> list[SourceRegistry]:
    return list(session.scalars(select(SourceRegistry).order_by(SourceRegistry.source_id)).all())


def compute_status(
    *,
    last_seen_at: datetime | None,
    expected_cadence_seconds: int,
    now: datetime | None = None,
    stale_multiplier: float = DEFAULT_STALE_MULTIPLIER,
) -> str:
    """Derive status from last heartbeat vs expected cadence."""
    if last_seen_at is None:
        return STATUS_UNKNOWN
    moment = now or datetime.now(UTC)
    if last_seen_at.tzinfo is None:
        last = last_seen_at.replace(tzinfo=UTC)
    else:
        last = last_seen_at.astimezone(UTC)
    age = (moment.astimezone(UTC) - last).total_seconds()
    if age <= expected_cadence_seconds * stale_multiplier:
        return STATUS_OK
    return STATUS_STALE


def snapshot(
    row: SourceRegistry,
    *,
    now: datetime | None = None,
    stale_multiplier: float = DEFAULT_STALE_MULTIPLIER,
) -> SourceSnapshot:
    moment = now or datetime.now(UTC)
    status = compute_status(
        last_seen_at=row.last_seen_at,
        expected_cadence_seconds=row.expected_cadence_seconds,
        now=moment,
        stale_multiplier=stale_multiplier,
    )
    age: float | None = None
    if row.last_seen_at is not None:
        last = row.last_seen_at
        if last.tzinfo is None:
            last = last.replace(tzinfo=UTC)
        age = (moment.astimezone(UTC) - last.astimezone(UTC)).total_seconds()
    return SourceSnapshot(
        source_id=row.source_id,
        name=row.name,
        kind=row.kind,
        expected_cadence_seconds=row.expected_cadence_seconds,
        last_seen_at=row.last_seen_at,
        status=status,
        age_seconds=age,
        stale=(status == STATUS_STALE),
    )


def record_heartbeat(
    session: Session,
    source_id: str,
    *,
    status: str = STATUS_OK,
    seen_at: datetime | None = None,
    commit: bool = True,
) -> SourceRegistry:
    """
    Update last_seen_at / status for a registered source.

    Raises KeyError if source_id is not seeded in source_registry.
    """
    row = get_source(session, source_id)
    if row is None:
        raise KeyError(f"Unknown source_id: {source_id}")

    row.last_seen_at = seen_at or datetime.now(UTC)
    row.status = status
    row.updated_at = datetime.now(UTC)
    if commit:
        session.commit()
    logger.debug("heartbeat source_id=%s status=%s", source_id, status)
    return row


def mark_error(
    session: Session,
    source_id: str,
    *,
    commit: bool = True,
) -> SourceRegistry:
    """Set status=error without advancing last_seen_at (feed failed this cycle)."""
    row = get_source(session, source_id)
    if row is None:
        raise KeyError(f"Unknown source_id: {source_id}")
    row.status = STATUS_ERROR
    row.updated_at = datetime.now(UTC)
    if commit:
        session.commit()
    logger.warning("source marked error source_id=%s", source_id)
    return row


def refresh_statuses(
    session: Session,
    *,
    now: datetime | None = None,
    stale_multiplier: float = DEFAULT_STALE_MULTIPLIER,
    commit: bool = True,
) -> list[SourceSnapshot]:
    """
    Recompute and persist status for every registered source.

    Does not change last_seen_at — only status / updated_at.
    """
    moment = now or datetime.now(UTC)
    snaps: list[SourceSnapshot] = []
    for row in list_sources(session):
        snap = snapshot(row, now=moment, stale_multiplier=stale_multiplier)
        # Preserve explicit error until a successful heartbeat clears it,
        # unless the feed is also past the stale threshold.
        if row.status == STATUS_ERROR and not snap.stale:
            snaps.append(
                SourceSnapshot(
                    source_id=snap.source_id,
                    name=snap.name,
                    kind=snap.kind,
                    expected_cadence_seconds=snap.expected_cadence_seconds,
                    last_seen_at=snap.last_seen_at,
                    status=STATUS_ERROR,
                    age_seconds=snap.age_seconds,
                    stale=False,
                )
            )
            continue
        if row.status != snap.status:
            row.status = snap.status
            row.updated_at = moment
        snaps.append(snap)
    if commit:
        session.commit()
    return snaps
