"""CLI: FRED macro series poll."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

SERVER_ROOT = Path(__file__).resolve().parents[2] / "server"
sys.path.insert(0, str(SERVER_ROOT))
os.chdir(SERVER_ROOT)

from app.config import get_settings  # noqa: E402
from app.ingestion.macro.poller import poll_once  # noqa: E402
from app.observability.logging import configure_logging  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Poll FRED macro series")
    parser.add_argument(
        "--series",
        default="",
        help="Comma-separated series IDs (default: FRED_SERIES / built-in list)",
    )
    parser.add_argument("--lookback-days", type=int, default=365 * 5)
    args = parser.parse_args()

    get_settings.cache_clear()
    settings = get_settings()
    configure_logging(settings.log_level)

    series = [s.strip().upper() for s in args.series.split(",") if s.strip()] or None
    result = poll_once(
        settings=settings,
        lookback_days=args.lookback_days,
        series_ids=series,
    )
    print(
        f"macro poll series={result.series_count} points={result.points_fetched} "
        f"written={result.rows_written}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
