"""Simulated kill-feed drill without stopping live MT5 backfill."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.ingestion.registry import get_source, record_heartbeat
from app.watchdog.checker import WatchdogReport, run_check

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class KillFeedDrillResult:
    source_id: str
    passed: bool
    report: WatchdogReport
    detail: str


def run_kill_feed_drill(
    session: Session,
    *,
    source_id: str = "finnhub.news",
    age: timedelta = timedelta(hours=1),
) -> KillFeedDrillResult:
    """
    Prove watchdog detects a silenced feed.

    1. Heartbeat the target source to ok
    2. Backdate last_seen_at beyond cadence × stale multiplier
    3. Run watchdog check — expect an alert for source_id
    4. Leave source stale (realistic post-incident state for unused W3 feeds)
    """
    row = get_source(session, source_id)
    if row is None:
        return KillFeedDrillResult(source_id, False, WatchdogReport(datetime.now(UTC)), "unknown source")

    record_heartbeat(session, source_id)
    # Backdate without clearing status first — refresh_statuses will set stale.
    row = get_source(session, source_id)
    assert row is not None
    row.last_seen_at = datetime.now(UTC) - age
    session.commit()

    report = run_check(session)
    alerted = any(a.source_id == source_id for a in report.alerts)
    snap = next((s for s in report.sources if s.source_id == source_id), None)
    passed = alerted and snap is not None and snap.stale

    detail = (
        f"alerted={alerted} status={snap.status if snap else None} "
        f"age={snap.age_seconds if snap else None}"
    )
    if passed:
        logger.info("kill-feed drill PASSED source_id=%s %s", source_id, detail)
    else:
        logger.error("kill-feed drill FAILED source_id=%s %s", source_id, detail)

    return KillFeedDrillResult(source_id=source_id, passed=passed, report=report, detail=detail)
