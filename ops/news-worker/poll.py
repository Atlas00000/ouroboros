"""CLI: poll Finnhub market news into TimescaleDB."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

SERVER_ROOT = Path(__file__).resolve().parents[2] / "server"
sys.path.insert(0, str(SERVER_ROOT))
os.chdir(SERVER_ROOT)

from app.config import get_settings  # noqa: E402
from app.ingestion.news.poller import poll_once  # noqa: E402
from app.observability.logging import configure_logging  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Poll Finnhub market news")
    parser.add_argument(
        "--categories",
        default="forex,general",
        help="Comma-separated Finnhub news categories",
    )
    args = parser.parse_args()

    get_settings.cache_clear()
    settings = get_settings()
    configure_logging(settings.log_level)

    categories = tuple(c.strip() for c in args.categories.split(",") if c.strip())
    result = poll_once(settings=settings, categories=categories)
    print(
        f"news poll fetched={result.fetched} new={result.new_articles} "
        f"written={result.rows_written} mapped={result.mapped_articles} "
        f"unmapped={result.unmapped_articles}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
