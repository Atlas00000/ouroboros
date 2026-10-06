"""Replay composite entry gate against a DV US100 blotter (agent log).

Usage (from repo root):

  py -3.12 ops/analytics/dv_entry_gate_replay.py
  py -3.12 ops/analytics/dv_entry_gate_replay.py --run 4 --broker-utc-offset 3
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_SERVER = os.path.join(_REPO, "server")
if _SERVER not in sys.path:
    sys.path.insert(0, _SERVER)
os.chdir(_SERVER)

import pandas as pd  # noqa: E402

from app.analytics.bars import load_ohlcv  # noqa: E402
from app.analytics.fit.entry_gate import evaluate_entry_gate  # noqa: E402
from app.analytics.fit.mapper import map_regime_to_fit  # noqa: E402
from app.analytics.fit.types import FitSnapshot  # noqa: E402
from app.analytics.regimes import MODEL_VERSION as REGIME_MODEL  # noqa: E402
from app.analytics.regimes import regime_feature_frame  # noqa: E402
from app.analytics.fit.mapper import MODEL_VERSION as FIT_MODEL  # noqa: E402
from app.calendar.timebase import ensure_utc  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.db.session import get_session_factory  # noqa: E402

DEFAULT_LOG = Path(
    r"C:\Users\emili\AppData\Roaming\MetaQuotes\Tester"
    r"\D0E8209F77C8CF37AD8BF550E51FF075\Agent-127.0.0.1-3000\logs\20261003.log"
)

STOP_PTS = 2500.0
POINT = 0.01


def _decode(path: Path) -> str:
    raw = path.read_bytes()
    if b"\x00" in raw[:200]:
        return raw.decode("utf-16le", errors="replace")
    return raw.decode("utf-8", errors="replace")


def parse_run_trades(text: str, run_index: int) -> tuple[tuple[str, str], list[dict]]:
    lines = text.splitlines()
    starts = [
        i
        for i, ln in enumerate(lines)
        if "testing of Experts" in ln and "started with inputs" in ln
    ]
    if run_index < 1 or run_index > len(starts):
        raise SystemExit(f"run {run_index} out of range 1..{len(starts)}")
    s = starts[run_index - 1]
    e = starts[run_index] if run_index < len(starts) else len(lines)
    block = lines[s:e]
    wm = re.search(r"from (\d{4}\.\d{2}\.\d{2}).*to (\d{4}\.\d{2}\.\d{2})", block[0])
    window = (wm.group(1), wm.group(2)) if wm else ("?", "?")

    deal_re = re.compile(r"deal #(\d+) (buy|sell) ([\d.]+) US100 at ([\d.]+)")
    close_re = re.compile(r"close #(\d+)")
    ts_re = re.compile(r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2})")
    opens: dict = {}
    pending = None
    trades: list[dict] = []
    for ln in block:
        mclose = close_re.search(ln)
        if mclose:
            pending = int(mclose.group(1))
        md = deal_re.search(ln)
        if not md:
            continue
        did = int(md.group(1))
        side = md.group(2)
        lots = float(md.group(3))
        price = float(md.group(4))
        tsv = ts_re.search(ln).group(1) if ts_re.search(ln) else ""
        if pending is not None:
            op = opens.get(pending)
            if op:
                o_side, o_lots, o_price, o_ts = op
                if o_side == "buy" and side == "sell":
                    pts = price - o_price
                elif o_side == "sell" and side == "buy":
                    pts = o_price - price
                else:
                    pts = None
                if pts is not None:
                    trades.append(
                        {
                            "ts": o_ts,
                            "side": o_side,
                            "pts": pts,
                            "entry": o_price,
                            "money": pts * o_lots,
                        }
                    )
                opens.pop(pending, None)
            pending = None
        else:
            opens[did] = (side, lots, price, tsv)
    return window, trades


def broker_ts_to_utc(ts: str, offset_hours: int) -> datetime:
    local = datetime.strptime(ts, "%Y.%m.%d %H:%M:%S")
    return (local - timedelta(hours=offset_hours)).replace(tzinfo=timezone.utc)


def main() -> int:
    p = argparse.ArgumentParser(description="Replay DV entry gate on tester blotter")
    p.add_argument("--log", type=Path, default=DEFAULT_LOG)
    p.add_argument("--run", type=int, default=4, help="1-based run index in agent log")
    p.add_argument("--broker-utc-offset", type=int, default=3)
    p.add_argument("--stop-pts", type=float, default=STOP_PTS)
    args = p.parse_args()

    text = _decode(args.log)
    window, trades = parse_run_trades(text, args.run)
    print(f"run=#{args.run} window={window[0]}->{window[1]} trades={len(trades)}")
    if not trades:
        return 2

    get_settings.cache_clear()
    session = get_session_factory()()
    try:
        h1 = load_ohlcv(session, "NAS100", "H1", lookback_days=400)
        m5 = load_ohlcv(session, "NAS100", "M1", lookback_days=400)
        for df in (h1, m5):
            df.sort_values("ts", inplace=True)
            df["ts"] = df["ts"].map(ensure_utc)
            for c in ("open", "high", "low", "close"):
                df[c] = df[c].astype(float)
        feats = regime_feature_frame(h1, "H1").dropna(subset=["confirmed_regime"])
        feats["ts"] = pd.to_datetime(feats["ts"], utc=True)
        feats = feats.set_index("ts").sort_index()

        m1 = m5.set_index(pd.to_datetime(m5["ts"], utc=True)).sort_index()
        m5o = (
            m1.resample("5min")
            .agg({"open": "first", "high": "max", "low": "min", "close": "last"})
            .dropna()
        )

        kept = []
        blocked = defaultdict(int)
        for t in trades:
            utc = broker_ts_to_utc(t["ts"], args.broker_utc_offset)
            # last H1 feature at/before entry
            idx = feats.index[feats.index <= utc]
            if len(idx) == 0:
                blocked["no_h1"] += 1
                continue
            row = feats.loc[idx[-1]]
            reg = str(row["confirmed_regime"])
            tag = map_regime_to_fit(reg, "meanrev")
            fit = FitSnapshot(
                symbol="NAS100",
                timeframe="H1",
                family="meanrev",
                tag=tag,
                regime=reg,  # type: ignore[arg-type]
                model_version=FIT_MODEL,
                as_of=utc,
                allow_on=(tag == "MATCH"),
            )
            # session open at broker start hour 08:00 → UTC
            local_day = datetime.strptime(t["ts"][:10], "%Y.%m.%d")
            sess_local = local_day.replace(hour=8, minute=0, second=0)
            sess_utc = (sess_local - timedelta(hours=args.broker_utc_offset)).replace(
                tzinfo=timezone.utc
            )
            sess_bars = m5o.loc[m5o.index >= sess_utc]
            if sess_bars.empty:
                blocked["no_sess"] += 1
                continue
            sess_open = float(sess_bars.iloc[0]["open"])
            drift_pts = (float(t["entry"]) - sess_open) / POINT
            decision = evaluate_entry_gate(
                fit=fit,
                side=t["side"],
                session_drift_pts=drift_pts,
                stop_target_pts=args.stop_pts,
            )
            if decision.allow:
                kept.append(t)
            else:
                blocked[decision.reason] += 1

        def score(sub: list[dict], label: str) -> None:
            if not sub:
                print(f"{label}: empty")
                return
            w = [x for x in sub if x["pts"] > 0]
            wr = len(w) / len(sub)
            aw = sum(x["pts"] for x in w) / len(w) if w else 0.0
            losses = [x for x in sub if x["pts"] <= 0]
            al = sum(abs(x["pts"]) for x in losses) / len(losses) if losses else 0.0
            rr = aw / al if al else 0.0
            be = 1 / (1 + rr) if rr else 0.0
            er = wr * rr - (1 - wr)
            net = sum(x["money"] for x in sub)
            print(
                f"{label}: n={len(sub)} WR={wr:.3f} RR={rr:.3f} BE={be:.3f} "
                f"E_R={er:.4f} net={net:.1f} avgW={aw:.2f}"
            )

        score(trades, "RAW")
        score(kept, "GATED")
        print("blocked_reasons", dict(blocked))
        print(
            f"models regime={REGIME_MODEL} fit={FIT_MODEL} "
            f"broker_utc_offset={args.broker_utc_offset}"
        )
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
