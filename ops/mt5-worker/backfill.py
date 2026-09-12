"""CLI: historical M1 backfill from MT5 into TimescaleDB."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

SERVER_ROOT = Path(__file__).resolve().parents[2] / "server"
sys.path.insert(0, str(SERVER_ROOT))
os.chdir(SERVER_ROOT)

from app.config import get_settings  # noqa: E402
from app.ingestion.mt5.backfill import backfill_universe  # noqa: E402
from app.observability.logging import configure_logging  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill M1 OHLCV from MT5")
    parser.add_argument("--years", type=float, default=2.0, help="History depth in years")
    parser.add_argument(
        "--symbols",
        type=str,
        default="",
        help="Comma-separated canonical symbols (default: full active universe)",
    )
    parser.add_argument("--chunk-days", type=int, default=14, help="MT5 fetch window size")
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Ignore latest bar; re-fetch full --years window (idempotent upserts)",
    )
    args = parser.parse_args()

    get_settings.cache_clear()
    settings = get_settings()
    configure_logging(settings.log_level)

    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()] or None
    results = backfill_universe(
        years=args.years,
        symbols=symbols,
        chunk_days=args.chunk_days,
        settings=settings,
        no_resume=args.no_resume,
    )
    total = sum(r.bars_written for r in results)
    print(f"backfill complete symbols={len(results)} bars_written={total}")
    for r in results:
        err = f" ERROR={r.error}" if r.error else ""
        print(
            f"  {r.symbol} ticker={r.mt5_ticker} written={r.bars_written} "
            f"resumed={r.resumed} from={r.from_ts} to={r.to_ts}{err}"
        )
    failed = [r for r in results if r.error]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
