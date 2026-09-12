"""CLI: classify latest regimes and append immutable forecast_log rows."""

from __future__ import annotations

import argparse
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_SERVER = os.path.join(_REPO, "server")
if _SERVER not in sys.path:
    sys.path.insert(0, _SERVER)
os.chdir(_SERVER)

from app.analytics.forecast_log import (  # noqa: E402
    DEFAULT_LOG_TIMEFRAMES,
    classify_and_log_regimes,
)
from app.config import get_settings  # noqa: E402
from app.db.session import get_session_factory  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Append regime calls to forecast_log")
    parser.add_argument("--symbols", nargs="*", default=None)
    parser.add_argument(
        "--timeframes",
        nargs="*",
        default=list(DEFAULT_LOG_TIMEFRAMES),
        help="Default: H1 H4 D1",
    )
    args = parser.parse_args()

    get_settings.cache_clear()
    session = get_session_factory()()
    try:
        report = classify_and_log_regimes(
            session,
            symbols=args.symbols,
            timeframes=tuple(args.timeframes),  # type: ignore[arg-type]
            commit=True,
        )
        print(
            f"inserted={report.inserted} dupes={report.skipped_dupes} "
            f"errors={len(report.errors)}"
        )
        for r in report.results:
            print(f"  {r.symbol} {r.timeframe} inserted={r.inserted}")
        for sym, tf, err in report.errors:
            print(f"  ERR {sym} {tf}: {err}")
    finally:
        session.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
