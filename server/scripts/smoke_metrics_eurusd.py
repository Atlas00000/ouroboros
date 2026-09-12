"""Smoke: compute metrics.v1 for EURUSD across all v1 timeframes."""

from __future__ import annotations

import os
import sys

os.chdir(os.path.dirname(__file__))
sys.path.insert(0, os.getcwd())

from app.analytics.bars import load_ohlcv
from app.analytics.metrics import TIMEFRAMES, compute_metric_snapshot
from app.config import get_settings
from app.db.session import get_session_factory


def main() -> int:
    get_settings.cache_clear()
    session = get_session_factory()()
    try:
        for tf in TIMEFRAMES:
            df = load_ohlcv(session, "EURUSD", tf, lookback_days=120)
            if df.empty:
                print(f"{tf}: empty")
                continue
            snap = compute_metric_snapshot(df, symbol="EURUSD", timeframe=tf)
            print(
                f"{tf}: bars={len(df)} vol20={snap.realized_vol_20} "
                f"atr14={snap.atr_14} ret1={snap.return_1} as_of={snap.as_of}"
            )
    finally:
        session.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
