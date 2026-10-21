"""CLI: poll Finnhub market news (+ optional equity company-news) into TimescaleDB."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

SERVER_ROOT = Path(__file__).resolve().parents[2] / "server"
sys.path.insert(0, str(SERVER_ROOT))
os.chdir(SERVER_ROOT)

from app.config import get_settings  # noqa: E402
from app.ingestion.news.company_poller import poll_company_equities  # noqa: E402
from app.ingestion.news.poller import poll_once  # noqa: E402
from app.observability.logging import configure_logging  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Poll Finnhub market + company news")
    parser.add_argument(
        "--categories",
        default="forex,general,merger",
        help="Comma-separated Finnhub /news categories (empty string skips market poll)",
    )
    parser.add_argument(
        "--company-equities",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Also poll Finnhub /company-news for active equities (default: on)",
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=14,
        help="Company-news lookback window in days (default: 14)",
    )
    parser.add_argument(
        "--symbols",
        default="",
        help="Optional comma-separated equity symbols for company-news (default: all active equities)",
    )
    args = parser.parse_args()

    get_settings.cache_clear()
    settings = get_settings()
    configure_logging(settings.log_level)

    exit_code = 0
    categories = tuple(c.strip() for c in args.categories.split(",") if c.strip())
    if categories:
        result = poll_once(settings=settings, categories=categories)
        print(
            f"market news poll fetched={result.fetched} new={result.new_articles} "
            f"written={result.rows_written} mapped={result.mapped_articles} "
            f"unmapped={result.unmapped_articles}"
        )

    if args.company_equities:
        symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()] or None
        cre = poll_company_equities(
            settings=settings,
            lookback_days=args.lookback_days,
            symbols=symbols,
        )
        print(
            f"company-news poll symbols={cre.symbols_polled} fetched={cre.fetched} "
            f"new={cre.new_articles} written={cre.rows_written} mapped={cre.mapped_articles} "
            f"errors={len(cre.errors)}"
        )
        for err in cre.errors:
            print(f"  error: {err}")
        if cre.errors:
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
