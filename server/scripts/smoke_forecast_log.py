"""Smoke: classify + append regime calls to forecast_log (EURUSD)."""

from __future__ import annotations

import os
import sys

os.chdir(os.path.dirname(__file__))
sys.path.insert(0, os.getcwd())

from sqlalchemy import func, select

from app.analytics.forecast_log import classify_and_log_regimes
from app.config import get_settings
from app.db.session import get_session_factory
from app.models.forecast_log import ForecastLog


def main() -> int:
    get_settings.cache_clear()
    session = get_session_factory()()
    try:
        report = classify_and_log_regimes(
            session,
            symbols=["EURUSD"],
            timeframes=("H1", "H4", "D1"),
            commit=True,
        )
        print(
            f"inserted={report.inserted} dupes={report.skipped_dupes} "
            f"errors={len(report.errors)}"
        )
        for r in report.results:
            print(
                f"  {r.symbol} {r.timeframe} inserted={r.inserted} "
                f"id={getattr(r.row, 'id', None)} model={getattr(r.row, 'model_version', None)}"
            )
        for err in report.errors:
            print(f"  ERR {err}")

        # Re-run should be all dupes
        again = classify_and_log_regimes(
            session,
            symbols=["EURUSD"],
            timeframes=("H1", "H4", "D1"),
            commit=True,
        )
        print(f"rerun inserted={again.inserted} dupes={again.skipped_dupes}")

        count = session.scalar(
            select(func.count()).select_from(ForecastLog).where(ForecastLog.symbol == "EURUSD")
        )
        print(f"forecast_log EURUSD rows={count}")
    finally:
        session.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
