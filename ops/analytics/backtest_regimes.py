"""CLI: regime flip-rate backtest + optional threshold tune (W4·D4)."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

SERVER_ROOT = Path(__file__).resolve().parents[2] / "server"
sys.path.insert(0, str(SERVER_ROOT))
os.chdir(SERVER_ROOT)

from sqlalchemy import text  # noqa: E402

from app.analytics.backtest import (  # noqa: E402
    FLIP_BUDGET_D1_PER_WEEK,
    FLIP_BUDGET_H1_PER_DAY,
    measure_flip_rate,
    tune_regime_params,
)
from app.analytics.bars import load_ohlcv, m1_depth_days  # noqa: E402
from app.analytics.regimes import DEFAULT_PARAMS, RegimeParams  # noqa: E402
from app.analytics.universe import passes_depth_gate  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.db.session import get_session_factory  # noqa: E402


def _active_symbols(session) -> list[str]:
    rows = session.execute(
        text("SELECT symbol FROM assets WHERE is_active IS TRUE ORDER BY symbol")
    ).scalars().all()
    return [str(s) for s in rows]


def main() -> int:
    parser = argparse.ArgumentParser(description="Regime flip-rate backtest / tune")
    parser.add_argument("--lookback-days", type=int, default=400)
    parser.add_argument("--tune", action="store_true", help="Grid-search thresholds")
    parser.add_argument("--er-abs", type=float, default=None)
    parser.add_argument("--vol-high", type=float, default=None)
    parser.add_argument("--persistence-n", type=int, default=None)
    args = parser.parse_args()

    get_settings.cache_clear()
    session = get_session_factory()()
    try:
        symbols = _active_symbols(session)
        eligible: list[str] = []
        for sym in symbols:
            span = m1_depth_days(session, sym)
            if passes_depth_gate(sym, m1_span_days_value=span):
                eligible.append(sym)
            else:
                print(f"skip {sym} depth={span:.1f}d", flush=True)

        print(f"eligible={eligible}", flush=True)
        print(f"loading {len(eligible)} symbols lookback={args.lookback_days}d...", flush=True)
        h1_frames: dict = {}
        d1_frames: dict = {}
        for sym in eligible:
            h1_frames[sym] = load_ohlcv(session, sym, "H1", lookback_days=args.lookback_days)
            d1_frames[sym] = load_ohlcv(session, sym, "D1", lookback_days=args.lookback_days)
            print(
                f"  loaded {sym} H1={len(h1_frames[sym])} D1={len(d1_frames[sym])}",
                flush=True,
            )

        if args.tune:
            best = tune_regime_params(h1_frames, d1_frames)
            p = best.params
            print(
                f"BEST params vol_high={p.vol_high} er_abs={p.er_abs} "
                f"persistence_n={p.persistence_n}",
                flush=True,
            )
            print(
                f"  H1 avg flips/day={best.h1_avg_flips_per_day:.3f} "
                f"(budget {FLIP_BUDGET_H1_PER_DAY}) within={best.h1_within}",
                flush=True,
            )
            print(
                f"  D1 avg flips/week={best.d1_avg_flips_per_week:.3f} "
                f"(budget {FLIP_BUDGET_D1_PER_WEEK}) within={best.d1_within}",
                flush=True,
            )
            print(
                f"  mean ranging share={best.mean_ranging_share:.3f} score={best.score:.3f}",
                flush=True,
            )
            params = best.params
        else:
            params = RegimeParams(
                vol_high=args.vol_high if args.vol_high is not None else DEFAULT_PARAMS.vol_high,
                er_abs=args.er_abs if args.er_abs is not None else DEFAULT_PARAMS.er_abs,
                persistence_n=(
                    args.persistence_n
                    if args.persistence_n is not None
                    else DEFAULT_PARAMS.persistence_n
                ),
            )

        print(
            f"\nparams vol_high={params.vol_high} er_abs={params.er_abs} "
            f"persistence_n={params.persistence_n}",
            flush=True,
        )
        print("--- H1 ---", flush=True)
        h1_ok = True
        for sym, df in h1_frames.items():
            if df.empty:
                print(f"  {sym}: empty", flush=True)
                continue
            r = measure_flip_rate(df, symbol=sym, timeframe="H1", params=params)
            flag = "OK" if r.within_budget else "OVER"
            h1_ok = h1_ok and r.within_budget
            print(
                f"  {sym}: flips/day={r.flips_per_day:.3f} flips={r.flips} "
                f"days={r.span_days:.1f} ranging={r.ranging_share:.2f} [{flag}]",
                flush=True,
            )

        print("--- D1 ---", flush=True)
        d1_ok = True
        for sym, df in d1_frames.items():
            if df.empty:
                print(f"  {sym}: empty", flush=True)
                continue
            r = measure_flip_rate(df, symbol=sym, timeframe="D1", params=params)
            flag = "OK" if r.within_budget else "OVER"
            d1_ok = d1_ok and r.within_budget
            print(
                f"  {sym}: flips/week={r.flips_per_week:.3f} flips={r.flips} "
                f"days={r.span_days:.1f} ranging={r.ranging_share:.2f} [{flag}]",
                flush=True,
            )

        print(f"\nbudget_pass h1={h1_ok} d1={d1_ok}", flush=True)
        return 0 if h1_ok and d1_ok else 1
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
