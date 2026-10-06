"""CLI: print ex-post regime fit board for symbol × family × TF.

Usage (from repo root, server deps installed):

  py -3.12 ops/analytics/fit_board.py --symbol EURUSD --family meanrev --tf H1 --window 30d
"""

from __future__ import annotations

import argparse
import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_SERVER = os.path.join(_REPO, "server")
if _SERVER not in sys.path:
    sys.path.insert(0, _SERVER)
os.chdir(_SERVER)

from app.analytics.bars import load_ohlcv  # noqa: E402
from app.analytics.fit.boards import BOARD_WINDOWS, board_from_ohlcv  # noqa: E402
from app.analytics.fit.mapper import MODEL_VERSION  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.db.session import get_session_factory  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Ex-post regime fit board")
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--family", choices=("meanrev", "trendfollow"), required=True)
    parser.add_argument("--tf", default="H1", choices=("M1", "M15", "H1", "H4", "D1"))
    parser.add_argument("--window", default="30d", choices=list(BOARD_WINDOWS))
    parser.add_argument("--lookback-days", type=int, default=120)
    args = parser.parse_args()

    get_settings.cache_clear()
    session = get_session_factory()()
    try:
        df = load_ohlcv(
            session,
            args.symbol.upper(),
            args.tf,
            lookback_days=args.lookback_days,
        )
        board = board_from_ohlcv(
            df,
            args.family,
            timeframe=args.tf,
            window=args.window,
        )
        out = {
            "model_version": MODEL_VERSION,
            "symbol": args.symbol.upper(),
            "timeframe": args.tf,
            "family": board.family,
            "window": board.window,
            "tag": board.tag,
            "bar_count": board.bar_count,
            "shares": board.shares,
            "regime_shares": board.regime_shares,
        }
        print(json.dumps(out, indent=2, default=str))
        return 0 if board.bar_count > 0 else 2
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
