"""Watchdog v1 — cadence check, stale propagation, log alerts."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.calendar.sessions import is_fx_weekend_closed
from app.ingestion.registry import (
    STATUS_STALE,
    STATUS_UNKNOWN,
    SourceSnapshot,
    refresh_statuses,
)

logger = logging.getLogger(__name__)

# When a feed is stale, flip stale=true on these derived tables (v1: whole table).
SOURCE_STALE_TARGETS: dict[str, tuple[str, ...]] = {
    "mt5.prices": ("states", "profiles"),
    "finnhub.news": ("sentiment", "insights"),
    "finnhub.calendar": (),
    "fred.macro": (),
}


@dataclass(frozen=True)
class WatchdogAlert:
    source_id: str
    status: str
    age_seconds: float | None
    message: str


@dataclass
class WatchdogReport:
    checked_at: datetime
    sources: list[SourceSnapshot] = field(default_factory=list)
    alerts: list[WatchdogAlert] = field(default_factory=list)
    rows_marked_stale: dict[str, int] = field(default_factory=dict)

    @property
    def stale_count(self) -> int:
        return sum(1 for s in self.sources if s.stale)

    @property
    def ok(self) -> bool:
        return len(self.alerts) == 0


def _should_suppress_price_alert(snap: SourceSnapshot, now: datetime) -> bool:
    """FX weekend: price silence is expected — do not alert."""
    if snap.kind != "price":
        return False
    return is_fx_weekend_closed(now)


def propagate_stale_flags(session: Session, stale_source_ids: list[str]) -> dict[str, int]:
    """Mark derived output rows stale=true for each stale source's target tables."""
    updated: dict[str, int] = {}
    for source_id in stale_source_ids:
        for table in SOURCE_STALE_TARGETS.get(source_id, ()):
            result = session.execute(
                text(f"UPDATE {table} SET stale = true WHERE stale = false")  # noqa: S608
            )
            n = result.rowcount or 0
            if n:
                updated[table] = updated.get(table, 0) + n
                logger.warning(
                    "stale propagation source_id=%s table=%s rows=%s",
                    source_id,
                    table,
                    n,
                )
    session.commit()
    return updated


def emit_alerts(snaps: list[SourceSnapshot], *, now: datetime) -> list[WatchdogAlert]:
    alerts: list[WatchdogAlert] = []
    for snap in snaps:
        if snap.status == STATUS_UNKNOWN:
            # Not yet wired — informational only at DEBUG (feeds come online in W3).
            logger.debug(
                "watchdog source never seen source_id=%s cadence=%ss",
                snap.source_id,
                snap.expected_cadence_seconds,
            )
            continue
        if not snap.stale and snap.status != STATUS_STALE:
            continue
        if _should_suppress_price_alert(snap, now):
            logger.info(
                "watchdog suppress weekend price silence source_id=%s age=%s",
                snap.source_id,
                snap.age_seconds,
            )
            continue
        msg = (
            f"FEED STALE source_id={snap.source_id} age_seconds={snap.age_seconds} "
            f"cadence={snap.expected_cadence_seconds}s"
        )
        logger.error(msg)
        alerts.append(
            WatchdogAlert(
                source_id=snap.source_id,
                status=snap.status,
                age_seconds=snap.age_seconds,
                message=msg,
            )
        )
    return alerts


def run_check(
    session: Session,
    *,
    now: datetime | None = None,
    propagate: bool = True,
) -> WatchdogReport:
    """
    Cadence checker → persist registry status → propagate stale flags → log alerts.
    """
    moment = now or datetime.now(UTC)
    snaps = refresh_statuses(session, now=moment)
    alerts = emit_alerts(snaps, now=moment)
    marked: dict[str, int] = {}
    if propagate:
        stale_ids = [s.source_id for s in snaps if s.stale]
        # Also propagate for sources we alerted on (status may be stale).
        alert_ids = [a.source_id for a in alerts]
        targets = sorted(set(stale_ids + alert_ids))
        if targets:
            marked = propagate_stale_flags(session, targets)

    report = WatchdogReport(
        checked_at=moment,
        sources=snaps,
        alerts=alerts,
        rows_marked_stale=marked,
    )
    logger.info(
        "watchdog check done sources=%s stale=%s alerts=%s propagated=%s",
        len(snaps),
        report.stale_count,
        len(alerts),
        marked,
    )
    return report
