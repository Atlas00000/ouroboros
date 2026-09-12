"""CLI: compare regimes.hmm_v1 spike vs regimes.rule_v1 (W5·D5)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

SERVER_ROOT = Path(__file__).resolve().parents[2] / "server"
sys.path.insert(0, str(SERVER_ROOT))
os.chdir(SERVER_ROOT)

from sqlalchemy import text  # noqa: E402

from app.analytics.bars import load_ohlcv, m1_depth_days  # noqa: E402
from app.analytics.hmm_regimes import (  # noqa: E402
    compare_hmm_vs_rule,
    hmmlearn_available,
)
from app.analytics.universe import passes_depth_gate  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.db.session import get_session_factory  # noqa: E402


def _active_symbols(session) -> list[str]:
    rows = session.execute(
        text("SELECT symbol FROM assets WHERE is_active IS TRUE ORDER BY symbol")
    ).scalars().all()
    return [str(s) for s in rows]


def main() -> int:
    parser = argparse.ArgumentParser(description="HMM vs rule regime comparison")
    parser.add_argument("--lookback-days", type=int, default=400)
    parser.add_argument("--timeframe", default="H1", choices=["H1", "H4", "D1"])
    parser.add_argument("--symbols", nargs="*", default=None)
    parser.add_argument("--json-out", default=None, help="Write summary JSON path")
    args = parser.parse_args()

    if not hmmlearn_available():
        print("ERROR: hmmlearn not installed. pip install hmmlearn", flush=True)
        return 2

    get_settings.cache_clear()
    session = get_session_factory()()
    try:
        symbols = args.symbols or _active_symbols(session)
        eligible = []
        for sym in symbols:
            span = m1_depth_days(session, sym)
            if passes_depth_gate(sym, m1_span_days_value=span):
                eligible.append(sym)
            else:
                print(f"skip {sym} depth={span:.1f}d", flush=True)

        rows = []
        for sym in eligible:
            df = load_ohlcv(session, sym, args.timeframe, lookback_days=args.lookback_days)
            if df.empty or len(df) < 80:
                print(f"skip {sym} empty/short", flush=True)
                continue
            try:
                r = compare_hmm_vs_rule(df, symbol=sym, timeframe=args.timeframe)
            except Exception as exc:  # noqa: BLE001
                print(f"ERR {sym}: {exc}", flush=True)
                continue
            rows.append(r)
            print(
                f"{r.symbol} {r.timeframe}: rule={r.rule_flips_per_day:.3f}/d "
                f"hmm={r.hmm_flips_per_day:.3f}/d agree={r.agreement:.3f} "
                f"bars={r.bars_compared} hmm_budget={r.hmm_within_budget} "
                f"map={r.state_map}",
                flush=True,
            )

        if not rows:
            print("no results", flush=True)
            return 1

        avg_rule = sum(r.rule_flips_per_day for r in rows) / len(rows)
        avg_hmm = sum(r.hmm_flips_per_day for r in rows) / len(rows)
        avg_agree = sum(r.agreement for r in rows) / len(rows)
        hmm_ok = sum(1 for r in rows if r.hmm_within_budget)
        rule_ok = sum(1 for r in rows if r.rule_within_budget)
        # Promote only if HMM mean flip-rate is strictly better AND agreement stays high
        promote = (
            avg_hmm < avg_rule
            and hmm_ok >= rule_ok
            and avg_agree >= 0.55
            and all(r.hmm_within_budget for r in rows)
        )
        summary = {
            "timeframe": args.timeframe,
            "n_symbols": len(rows),
            "avg_rule_flips_per_day": avg_rule,
            "avg_hmm_flips_per_day": avg_hmm,
            "avg_agreement": avg_agree,
            "rule_within_budget": rule_ok,
            "hmm_within_budget": hmm_ok,
            "promote_hmm": promote,
            "decision": "promote" if promote else "keep_rule_v1",
        }
        print("---", flush=True)
        print(json.dumps(summary, indent=2), flush=True)
        if args.json_out:
            Path(args.json_out).write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
