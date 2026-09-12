"""CLI: Finnhub economic calendar poll."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

SERVER_ROOT = Path(__file__).resolve().parents[2] / "server"
sys.path.insert(0, str(SERVER_ROOT))
os.chdir(SERVER_ROOT)

from app.config import get_settings  # noqa: E402
from app.ingestion.econ_calendar.poller import poll_once  # noqa: E402
from app.observability.logging import configure_logging  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Poll Finnhub economic calendar")
    parser.add_argument("--days-back", type=int, default=1)
    parser.add_argument("--days-forward", type=int, default=7)
    args = parser.parse_args()

    get_settings.cache_clear()
    settings = get_settings()
    configure_logging(settings.log_level)

    result = poll_once(
        settings=settings,
        days_back=args.days_back,
        days_forward=args.days_forward,
    )
    print(
        f"calendar poll provider={result.provider} fetched={result.fetched} "
        f"high_impact={result.high_impact} written={result.rows_written}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
