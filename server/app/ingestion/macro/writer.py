"""Upsert FRED macro observations."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.ingestion.macro.client import RawMacroPoint
from app.models.macro import MacroObservation

logger = logging.getLogger(__name__)


def upsert_macro_points(session: Session, points: list[RawMacroPoint]) -> int:
    if not points:
        return 0

    now = datetime.now(UTC)
    rows = [
        {
            "series_id": p.series_id,
            "obs_date": p.obs_date,
            "value": p.value,
            "source": "fred",
            "ingested_at": now,
        }
        for p in points
        if p.value is not None
    ]
    if not rows:
        return 0

    before = int(session.scalar(select(func.count()).select_from(MacroObservation)) or 0)
    batch = 500
    for i in range(0, len(rows), batch):
        chunk = rows[i : i + batch]
        stmt = insert(MacroObservation).values(chunk)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_macro_series_date",
            set_={
                "value": stmt.excluded.value,
                "source": stmt.excluded.source,
                "ingested_at": stmt.excluded.ingested_at,
            },
        )
        session.execute(stmt)
    session.commit()
    after = int(session.scalar(select(func.count()).select_from(MacroObservation)) or 0)
    written = max(0, after - before)
    logger.info("macro upsert attempted=%s new_rows=%s", len(rows), written)
    return written
