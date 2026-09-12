"""CLI: live M1 poller from MT5 into TimescaleDB."""

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
from app.ingestion.mt5.connection import disconnect  # noqa: E402
from app.ingestion.mt5.poller import poll_once, run_poll_loop  # noqa: E402
from app.observability.logging import configure_logging  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Live M1 poller from MT5")
    parser.add_argument(
        "--symbols",
        type=str,
        default="",
        help="Comma-separated canonical symbols (default: full active universe)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single poll cycle and exit",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=60.0,
        help="Seconds between poll cycles (loop mode)",
    )
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=0,
        help="Stop after N cycles in loop mode (0 = forever)",
    )
    args = parser.parse_args()

    get_settings.cache_clear()
    settings = get_settings()
    configure_logging(settings.log_level)

    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()] or None

    if args.once:
        try:
            results = poll_once(symbols=symbols, settings=settings)
        finally:
            disconnect()
        total = sum(r.bars_written for r in results)
        gaps = sum(1 for r in results if r.gap is not None)
        print(f"poll complete symbols={len(results)} bars_written={total} gaps={gaps}")
        for r in results:
            gap_info = (
                f" gap_missing={r.gap.missing_minutes}m"
                if r.gap is not None
                else ""
            )
            print(
                f"  {r.symbol} ticker={r.mt5_ticker} written={r.bars_written} "
                f"from={r.from_ts} to={r.to_ts}{gap_info}"
            )
        return 0

    max_cycles = args.max_cycles if args.max_cycles > 0 else None
    logging.getLogger(__name__).info(
        "starting poll loop interval=%ss max_cycles=%s",
        args.interval,
        max_cycles,
    )
    run_poll_loop(
        interval_seconds=args.interval,
        symbols=symbols,
        settings=settings,
        max_cycles=max_cycles,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
