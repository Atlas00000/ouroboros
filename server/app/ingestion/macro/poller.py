"""FRED macro poll cycle."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.config import Settings, get_settings
from app.db.session import get_session_factory
from app.ingestion.macro.client import FredClient
from app.ingestion.macro.writer import upsert_macro_points
from app.ingestion.registry import mark_error, record_heartbeat

logger = logging.getLogger(__name__)

SOURCE_ID = "fred.macro"


@dataclass(frozen=True)
class MacroPollResult:
    series_count: int
    points_fetched: int
    rows_written: int


def poll_once(
    *,
    settings: Settings | None = None,
    lookback_days: int = 365 * 5,
    series_ids: list[str] | None = None,
) -> MacroPollResult:
    """
    Pull configured FRED series from `observation_start` through today.

    Default lookback ~5y is enough for analytics without dumping full history.
    """
    cfg = settings or get_settings()
    client = FredClient(cfg)
    ids = series_ids or cfg.fred_series_list
    start = datetime.now(UTC).date() - timedelta(days=lookback_days)

    session = get_session_factory()()
    try:
        total_points = 0
        total_written = 0
        try:
            for series_id in ids:
                points = client.fetch_series(series_id, observation_start=start)
                total_points += len(points)
                total_written += upsert_macro_points(session, points)
        except Exception:
            logger.exception("fred macro fetch failed")
            mark_error(session, SOURCE_ID)
            raise

        record_heartbeat(session, SOURCE_ID)
        result = MacroPollResult(
            series_count=len(ids),
            points_fetched=total_points,
            rows_written=total_written,
        )
        logger.info(
            "macro poll done series=%s points=%s written=%s",
            result.series_count,
            result.points_fetched,
            result.rows_written,
        )
        return result
    finally:
        session.close()
