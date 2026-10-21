"""EURUSD M5 FBRG geometry + meanrev fit audit (last ~6 months).

Research-only. Resamples M1→M5, scans false-breakout setups, scores designed
RR (mid TP / invalidation SL), and builds monthly meanrev boards from H1.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

from app.analytics.bars import load_ohlcv
from app.analytics.fit.boards import board_from_regimes
from app.analytics.regimes import regime_feature_frame
from app.config import get_settings
from app.db.session import get_session_factory

SYMBOL = "EURUSD"
LOOKBACK_DAYS = 200
RANGE_BARS = 40
BREAK_K = 0.20
INV_K = 0.75
FAIL_MAX = 6
MIN_RR = 1.5
GRID_LEVELS = 3
GRID_ATR = 0.30


def _f(x: object) -> float:
    return float(x)


def main() -> int:
    get_settings.cache_clear()
    session = get_session_factory()()
    try:
        df_m1 = load_ohlcv(session, SYMBOL, "M1", lookback_days=LOOKBACK_DAYS)
        df_h1 = load_ohlcv(session, SYMBOL, "H1", lookback_days=LOOKBACK_DAYS)

        m1 = df_m1.copy()
        m1["ts"] = pd.to_datetime(m1["ts"], utc=True)
        m1 = m1.set_index("ts").sort_index()
        end = m1.index.max()
        start_6m = end - pd.Timedelta(days=183)
        m1 = m1.loc[m1.index >= start_6m]

        o = m1["open"].astype(float).resample("5min").first()
        h = m1["high"].astype(float).resample("5min").max()
        l = m1["low"].astype(float).resample("5min").min()
        c = m1["close"].astype(float).resample("5min").last()
        m5 = pd.DataFrame({"open": o, "high": h, "low": l, "close": c}).dropna()
        m5 = m5.reset_index().rename(columns={"index": "ts"})

        tr = pd.concat(
            [
                m5["high"] - m5["low"],
                (m5["high"] - m5["close"].shift(1)).abs(),
                (m5["low"] - m5["close"].shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)
        m5["atr"] = tr.rolling(14).mean()

        setups: list[dict] = []
        i = RANGE_BARS + 20
        n = len(m5)
        while i < n - 2:
            atr = _f(m5["atr"].iloc[i])
            if not np.isfinite(atr) or atr <= 0:
                i += 1
                continue
            window = m5.iloc[i - RANGE_BARS : i]
            rh = _f(window["high"].max())
            rl = _f(window["low"].min())
            mid = 0.5 * (rh + rl)
            w = rh - rl
            bar = m5.iloc[i]
            bull = _f(bar["high"]) >= rh + BREAK_K * atr
            bear = _f(bar["low"]) <= rl - BREAK_K * atr
            if not bull and not bear:
                i += 1
                continue

            direction = None
            fail_i = None
            for j in range(i, min(i + FAIL_MAX + 1, n)):
                b = m5.iloc[j]
                if bull and _f(b["close"]) < rh:
                    direction = "short"
                    fail_i = j
                    break
                if bear and _f(b["close"]) > rl:
                    direction = "long"
                    fail_i = j
                    break
            if direction is None or fail_i is None or fail_i + 1 >= n:
                i += 1
                continue

            entry = _f(m5["open"].iloc[fail_i + 1])
            if direction == "short":
                tp = mid
                sl = rh + INV_K * atr
                reward = entry - tp
                risk = sl - entry
                break_atr = (_f(m5["high"].iloc[i]) - rh) / atr
            else:
                tp = mid
                sl = rl - INV_K * atr
                reward = tp - entry
                risk = entry - sl
                break_atr = (rl - _f(m5["low"].iloc[i])) / atr

            rr = reward / risk if risk > 0 else 0.0
            setups.append(
                {
                    "ts": str(m5["ts"].iloc[fail_i]),
                    "month": pd.Timestamp(m5["ts"].iloc[fail_i]).strftime("%Y-%m"),
                    "dir": direction,
                    "rh": rh,
                    "rl": rl,
                    "mid": mid,
                    "w": w,
                    "atr": atr,
                    "entry": entry,
                    "tp": tp,
                    "sl": sl,
                    "reward": reward,
                    "risk": risk,
                    "rr": rr,
                    "tp_lt_sl": bool(reward < risk),
                    "pass_floor": bool(rr + 1e-12 >= MIN_RR and risk > 0 and reward > 0),
                    "break_atr": break_atr,
                }
            )
            i = fail_i + 3

        rrs = np.array([s["rr"] for s in setups]) if setups else np.array([0.0])
        hits: list[str] = []
        ts_index = {pd.Timestamp(t): idx for idx, t in enumerate(m5["ts"])}
        for s in setups:
            if not s["pass_floor"]:
                continue
            i0 = ts_index.get(pd.Timestamp(s["ts"]))
            if i0 is None:
                continue
            start = i0 + 1
            endj = min(start + 48, len(m5) - 1)
            outcome = "timeout"
            for j in range(start, endj + 1):
                hi = _f(m5["high"].iloc[j])
                lo = _f(m5["low"].iloc[j])
                if s["dir"] == "short":
                    if hi >= s["sl"]:
                        outcome = "SL"
                        break
                    if lo <= s["tp"]:
                        outcome = "TP"
                        break
                else:
                    if lo <= s["sl"]:
                        outcome = "SL"
                        break
                    if hi >= s["tp"]:
                        outcome = "TP"
                        break
            hits.append(outcome)

        hc = Counter(hits)
        n_scored = hc["TP"] + hc["SL"]
        wr = hc["TP"] / n_scored if n_scored else 0.0
        passed_rr = [s["rr"] for s in setups if s["pass_floor"]]
        r_des = float(np.median(passed_rr)) if passed_rr else 0.0
        bwr = 1.0 / (1.0 + r_des) if r_des > 0 else 1.0
        en = wr * (r_des + 1.0) - 1.0 if n_scored else None
        bm = wr - bwr if n_scored else None

        # H1 meanrev monthly boards
        feat = regime_feature_frame(df_h1, "H1")
        ts = pd.to_datetime(feat["ts"], utc=True)
        feat = feat.loc[ts >= pd.Timestamp(start_6m)].copy()
        ts = pd.to_datetime(feat["ts"], utc=True)
        months = sorted(ts.dt.strftime("%Y-%m").unique())
        boards = []
        for ym in months:
            mask = ts.dt.strftime("%Y-%m") == ym
            regs = [str(r) for r in feat.loc[mask, "confirmed_regime"].dropna()]
            b = board_from_regimes(regs, "meanrev", window="calendar_month")
            dom = (
                max(b.regime_shares, key=b.regime_shares.get) if b.regime_shares else None
            )
            boards.append(
                {
                    "month": ym,
                    "tag": b.tag,
                    "bars": b.bar_count,
                    "dominant_regime": dom,
                    "shares": b.shares,
                    "regime_shares": b.regime_shares,
                }
            )

        all_regs = [str(r) for r in feat["confirmed_regime"].dropna()]
        ball = board_from_regimes(all_regs, "meanrev", window="30d")

        out = {
            "generated_at": datetime.now(UTC).isoformat(),
            "symbol": SYMBOL,
            "edge_family": "meanrev",
            "disclaimer": (
                "Research only. Path proxy is Level-0 mid-TP vs invalidation SL "
                "(no grid fills, no costs). Designed RR ≠ realised R. Never emit TP < SL."
            ),
            "window": {"start": str(start_6m), "end": str(end)},
            "m5_bars": int(len(m5)),
            "params": {
                "range_bars": RANGE_BARS,
                "break_atr_mult": BREAK_K,
                "invalidation_atr_mult": INV_K,
                "break_max_bars": FAIL_MAX,
                "min_design_rr": MIN_RR,
                "design_tp": "MID",
                "grid_levels": GRID_LEVELS,
                "grid_atr_mult": GRID_ATR,
            },
            "geometry": {
                "setups_n": len(setups),
                "rr_percentiles": {
                    k: float(v)
                    for k, v in zip(
                        ["p25", "p50", "p75"],
                        np.percentile(rrs, [25, 50, 75]) if len(setups) else [0, 0, 0],
                    )
                },
                "tp_lt_sl_count": int(sum(1 for s in setups if s["tp_lt_sl"])),
                "tp_lt_sl_pct": 100
                * sum(1 for s in setups if s["tp_lt_sl"])
                / max(len(setups), 1),
                "pass_rr15_count": int(sum(1 for s in setups if s["pass_floor"])),
                "pass_rr15_pct": 100
                * sum(1 for s in setups if s["pass_floor"])
                / max(len(setups), 1),
                "hard_rule": "Basket_Activate blocks reward < risk and RR < MinDesignRR",
            },
            "path_proxy_level0": {
                "outcomes": dict(hc),
                "n_scored": int(n_scored),
                "WR": wr,
                "R_design_med": r_des,
                "BWR": bwr,
                "BM": bm,
                "E_N": en,
                "note": "Level0-only; ignores grid averaging & costs (Leak not subtracted)",
            },
            "monthly_meanrev_h1": boards,
            "overall_meanrev_shares": ball.shares,
            "overall_regime_shares": ball.regime_shares,
            "tag_summary": dict(Counter(b["tag"] for b in boards if b["bars"] > 0)),
        }

        repo = Path(__file__).resolve().parents[2]
        out_dir = repo / "research" / "presets" / "FBRG"
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "eurusd-m5-6m-audit.json"
        path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
        print(json.dumps({k: out[k] for k in (
            "window", "m5_bars", "geometry", "path_proxy_level0", "tag_summary",
            "overall_meanrev_shares"
        )}, indent=2, default=str))
        print("wrote", path)
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
