"""Persist AssetProfile versions + retention prune (Phase 2 W5·D2)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import uuid4

from contracts.common_v1 import Provenance
from contracts.events_v1 import ProfileUpdatedEvent, ProfileUpdatedPayload
from contracts.profile_v1 import AssetProfile
from sqlalchemy import Select, delete, func, select, text
from sqlalchemy.orm import Session

from app.analytics.profiles import PROFILE_MODEL_VERSION
from app.calendar.timebase import ensure_utc
from app.models.outbox import OutboxMessage
from app.models.profile import ProfileRow

RETENTION_DAYS = 180
REFRESH_COOLDOWN = timedelta(hours=1)


@dataclass(frozen=True)
class ProfilePersistResult:
    row: ProfileRow
    outbox_event_id: str | None


def next_profile_version(session: Session, symbol: str) -> int:
    """Monotonic version per symbol (starts at 1)."""
    sym = symbol.upper()
    current = session.scalar(
        select(func.max(ProfileRow.profile_version)).where(ProfileRow.symbol == sym)
    )
    return 1 if current is None else int(current) + 1


def latest_profile_created_at(session: Session, symbol: str) -> datetime | None:
    sym = symbol.upper()
    return session.scalar(
        select(func.max(ProfileRow.created_at)).where(ProfileRow.symbol == sym)
    )


def within_refresh_cooldown(
    last_created: datetime | None,
    *,
    now: datetime | None = None,
    cooldown: timedelta = REFRESH_COOLDOWN,
) -> bool:
    """True when a refresh would violate ≤1/hour/symbol."""
    if last_created is None:
        return False
    now_utc = ensure_utc(now or datetime.now(UTC))
    last = ensure_utc(last_created)
    return (now_utc - last) < cooldown


def can_refresh_symbol(
    session: Session,
    symbol: str,
    *,
    now: datetime | None = None,
    cooldown: timedelta = REFRESH_COOLDOWN,
) -> bool:
    return not within_refresh_cooldown(
        latest_profile_created_at(session, symbol),
        now=now,
        cooldown=cooldown,
    )


def persist_asset_profile(
    session: Session,
    profile: AssetProfile,
    *,
    enqueue_outbox: bool = True,
    created_at: datetime | None = None,
) -> ProfilePersistResult:
    """
    Insert a new ``profiles`` row (and optional ``profile.updated`` outbox row).

    Caller must commit. ``profile.profile_version`` should already be the next
    monotonic version for the symbol.
    """
    sym = profile.identity.symbol.upper()
    created = ensure_utc(created_at or datetime.now(UTC))
    conf = Decimal(str(round(float(profile.provenance.confidence), 4)))
    row = ProfileRow(
        symbol=sym,
        profile_version=int(profile.profile_version),
        payload_json=profile.model_dump_json(),
        as_of=ensure_utc(profile.as_of),
        model_version=profile.provenance.model_version or PROFILE_MODEL_VERSION,
        confidence=conf,
        stale=bool(profile.provenance.stale),
        created_at=created,
    )
    session.add(row)

    event_id: str | None = None
    if enqueue_outbox:
        event_id = str(uuid4())
        envelope = ProfileUpdatedEvent(
            event_id=event_id,
            occurred_at=created,
            symbol=sym,
            provenance=Provenance(
                sources=list(profile.provenance.sources) or [PROFILE_MODEL_VERSION],
                generated_at=created,
                model_version=PROFILE_MODEL_VERSION,
                confidence=float(profile.provenance.confidence),
                stale=bool(profile.provenance.stale),
            ),
            payload=ProfileUpdatedPayload(
                symbol=sym,
                profile_version=int(profile.profile_version),
                as_of=ensure_utc(profile.as_of),
            ),
        )
        session.add(
            OutboxMessage(
                event_id=event_id,
                event="profile.updated",
                payload_json=envelope.model_dump_json(),
            )
        )

    session.flush()
    return ProfilePersistResult(row=row, outbox_event_id=event_id)


@dataclass(frozen=True)
class PruneResult:
    deleted: int
    retention_days: int
    cutoff: datetime


def ids_to_prune_beyond_retention(
    rows: list[tuple[int, str, datetime]],
    *,
    cutoff: datetime,
) -> list[int]:
    """
    Pure helper: among rows older than ``cutoff``, keep last-of-day per symbol;
    return ids of the rest (to delete).
    """
    cutoff_utc = ensure_utc(cutoff)
    by_day: dict[tuple[str, str], list[tuple[datetime, int]]] = {}
    for row_id, symbol, created_at in rows:
        created = ensure_utc(created_at)
        if created >= cutoff_utc:
            continue
        day = created.date().isoformat()
        by_day.setdefault((symbol.upper(), day), []).append((created, row_id))

    doomed: list[int] = []
    for group in by_day.values():
        group.sort(key=lambda t: (t[0], t[1]), reverse=True)
        for _, row_id in group[1:]:
            doomed.append(row_id)
    return doomed


def prune_profiles(
    session: Session,
    *,
    now: datetime | None = None,
    retention_days: int = RETENTION_DAYS,
    use_sql_function: bool = True,
) -> PruneResult:
    """
    Apply 180d then last-of-day retention.

    Prefers DB function ``prune_profiles_retention`` (migration 0006); falls back
    to ORM delete using the pure selection helper.
    """
    now_utc = ensure_utc(now or datetime.now(UTC))
    cutoff = now_utc - timedelta(days=retention_days)

    if use_sql_function:
        try:
            with session.begin_nested():
                deleted = session.scalar(
                    text("SELECT prune_profiles_retention(:days)").bindparams(
                        days=retention_days
                    )
                )
            return PruneResult(
                deleted=int(deleted or 0),
                retention_days=retention_days,
                cutoff=cutoff,
            )
        except Exception:
            # Function missing / pre-migration — ORM path below.
            pass

    rows = session.execute(
        select(ProfileRow.id, ProfileRow.symbol, ProfileRow.created_at).where(
            ProfileRow.created_at < cutoff
        )
    ).all()
    doomed = ids_to_prune_beyond_retention(
        [(int(r[0]), str(r[1]), r[2]) for r in rows],
        cutoff=cutoff,
    )
    deleted = 0
    if doomed:
        result = session.execute(delete(ProfileRow).where(ProfileRow.id.in_(doomed)))
        deleted = int(result.rowcount or 0)
        session.flush()
    return PruneResult(deleted=deleted, retention_days=retention_days, cutoff=cutoff)


def latest_profile_row(session: Session, symbol: str) -> ProfileRow | None:
    sym = symbol.upper()
    stmt: Select[Any] = (
        select(ProfileRow)
        .where(ProfileRow.symbol == sym)
        .order_by(ProfileRow.profile_version.desc())
        .limit(1)
    )
    return session.scalar(stmt)
