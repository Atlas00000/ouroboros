"""GBPJPY BMRG M15 P1 — raise WR first, then re-score Leak.

Hard rules:
  - SL/TP frozen at 160/200 (never widen TP or shrink SL)
  - never emit TP < SL
  - selectivity only: BBDev, cooldown, fade-confirm, buy gate, MaxSpread
Framework: docs/framework/unified_edge_framework.md Stage 0–1.
Blotter prior (magic 26101825): WR 41.3% < BWR 44.4% · spread≈29pt · E_N<0.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

from app.analytics.bars import load_ohlcv
from app.config import get_settings
from app.db.session import get_session_factory

SYMBOL = "GBPJPY"
POINT = 0.001
# Frozen geometry (P0) — do not change
SL_PTS = 160.0
TP_PTS = 200.0
# Measured blotter round-trip prior (~29pt mean spread × 2)
COST_RT_BLOTTER = 58.0
# Tight MaxSpread sleeve prior (target MaxSpread≈25)
COST_RT_TIGHT = 40.0


def _resample_m15(m1: pd.DataFrame) -> pd.DataFrame:
    df = m1.copy()
    df["ts"] = pd.to_datetime(df["ts"], utc=True)
    df = df.set_index("ts").sort_index()
    return (
        df.resample("15min")
        .agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            }
        )
        .dropna(subset=["open", "close"])
        .reset_index()
    )


def _bb(close: pd.Series, n: int = 20, k: float = 2.2) -> tuple[pd.Series, pd.Series, pd.Series]:
    mid = close.rolling(n).mean()
    sd = close.rolling(n).std(ddof=0)
    return mid + k * sd, mid, mid - k * sd


def _atr_wilder(df: pd.DataFrame, n: int = 14) -> pd.Series:
    h, l, c = df["high"], df["low"], df["close"]
    prev_c = c.shift(1)
    tr = pd.concat([(h - l), (h - prev_c).abs(), (l - prev_c).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1.0 / n, adjust=False).mean()


def _resolve(
    g: pd.DataFrame,
    i_entry: int,
    side: str,
    sl_pts: float,
    tp_pts: float,
    point: float,
) -> str | None:
    entry = float(g.iloc[i_entry]["open"])
    sl_dist = sl_pts * point
    tp_dist = tp_pts * point
    if tp_dist + 1e-12 < sl_dist:
        return None
    if side == "long":
        sl, tp = entry - sl_dist, entry + tp_dist
    else:
        sl, tp = entry + sl_dist, entry - tp_dist
    for j in range(i_entry, min(i_entry + 96, len(g))):
        hi = float(g.iloc[j]["high"])
        lo = float(g.iloc[j]["low"])
        if side == "long":
            hit_sl, hit_tp = lo <= sl, hi >= tp
        else:
            hit_sl, hit_tp = hi >= sl, lo <= tp
        if hit_sl and hit_tp:
            return "loss"
        if hit_tp:
            return "win"
        if hit_sl:
            return "loss"
    return None


def _probe(
    g: pd.DataFrame,
    *,
    bb_dev: float,
    sl_pts: float = SL_PTS,
    tp_pts: float = TP_PTS,
    session: tuple[int, int] = (12, 20),
    skip_tue: bool = True,
    atr_max_pts: float | None = 126.0,
    cooldown_bars: int = 2,
    fade_confirm: bool = False,
    fade_max_bars: int = 3,
    fade_inside_mid: bool = True,
    allow_buy: bool = True,
    allow_sell: bool = True,
    cost_rt_pts: float = COST_RT_BLOTTER,
) -> dict:
    """P0-style fade, optional reclaim confirm + cooldown. SL/TP frozen."""
    upper, mid, lower = _bb(g["close"], 20, bb_dev)
    atr = _atr_wilder(g, 14)
    g = g.copy()
    g["upper"], g["mid"], g["lower"] = upper, mid, lower
    g["atr_pts"] = atr / POINT

    wins = losses = 0
    blocked_regime = 0
    blocked_side = 0
    setups = 0
    i = 25
    cool_until = -1
    while i < len(g) - 40:
        if i < cool_until:
            i += 1
            continue
        row = g.iloc[i]
        if pd.isna(row["upper"]) or pd.isna(row["lower"]) or pd.isna(row["atr_pts"]):
            i += 1
            continue
        ts = pd.to_datetime(row["ts"], utc=True)
        if skip_tue and int(ts.dayofweek) == 1:
            i += 1
            continue
        h0, h1 = session
        if not (h0 <= int(ts.hour) < h1):
            i += 1
            continue
        atr_pts = float(row["atr_pts"])
        if atr_max_pts is not None and atr_pts > atr_max_pts:
            blocked_regime += 1
            i += 1
            continue

        c = float(row["close"])
        u, m, lo = float(row["upper"]), float(row["mid"]), float(row["lower"])
        side = None
        if c <= lo:
            side = "long"
        elif c >= u:
            side = "short"
        else:
            i += 1
            continue

        if side == "long" and not allow_buy:
            blocked_side += 1
            i += 1
            continue
        if side == "short" and not allow_sell:
            blocked_side += 1
            i += 1
            continue

        entry_i: int | None = None
        if not fade_confirm:
            entry_i = i + 1
        else:
            # Arm on extreme; enter on reclaim toward mid within fade_max_bars
            for k in range(1, fade_max_bars + 1):
                j = i + k
                if j >= len(g) - 1:
                    break
                cj = float(g.iloc[j]["close"])
                uj, mj, loj = (
                    float(g.iloc[j]["upper"]),
                    float(g.iloc[j]["mid"]),
                    float(g.iloc[j]["lower"]),
                )
                if side == "long":
                    reclaimed = cj > loj
                    side_ok = (cj < mj) if fade_inside_mid else True
                else:
                    reclaimed = cj < uj
                    side_ok = (cj > mj) if fade_inside_mid else True
                if reclaimed and side_ok:
                    entry_i = j + 1
                    break
            if entry_i is None:
                i += 1
                continue

        if entry_i >= len(g) - 1:
            break

        # Session check on entry bar
        ets = pd.to_datetime(g.iloc[entry_i]["ts"], utc=True)
        if skip_tue and int(ets.dayofweek) == 1:
            i = entry_i + 1
            continue
        if not (h0 <= int(ets.hour) < h1):
            i = entry_i + 1
            continue

        setups += 1
        design_rr = tp_pts / sl_pts
        if design_rr < 1.0 - 1e-12:
            i = entry_i + 1
            continue

        outcome = _resolve(g, entry_i, side, sl_pts, tp_pts, POINT)
        if outcome == "win":
            wins += 1
        elif outcome == "loss":
            losses += 1
        # cooldown after attempt
        cool_until = entry_i + max(1, cooldown_bars)
        i = cool_until
        continue

    n = wins + losses
    wr = wins / n if n else 0.0
    r = tp_pts / sl_pts
    bwr = 1.0 / (1.0 + r)
    bm = wr - bwr
    c_r = cost_rt_pts / sl_pts
    leak = c_r / (r + 1.0)
    ef = bm - leak
    e_n = wr * (r + 1.0) - 1.0
    return {
        "n_resolved": n,
        "wins": wins,
        "losses": losses,
        "setups": setups,
        "WR": wr,
        "RR_design": r,
        "BWR": bwr,
        "BM": bm,
        "c_R": c_r,
        "Leak": leak,
        "EF": ef,
        "E_N": e_n,
        "blocked_regime": blocked_regime,
        "blocked_side": blocked_side,
        "sl_pts": sl_pts,
        "tp_pts": tp_pts,
        "cost_rt_pts": cost_rt_pts,
        "wr_gt_bwr": wr > bwr,
        "design_ok": n >= 25 and wr > bwr and e_n > 0 and r >= 1.0,
        "stage1_ok": n >= 25 and wr > bwr and e_n > 0 and r >= 1.0 and ef > 0,
    }


def main() -> int:
    get_settings.cache_clear()
    session = get_session_factory()()
    try:
        df_m1 = load_ohlcv(session, SYMBOL, "M1", lookback_days=220)
        m15 = _resample_m15(df_m1)
        end = pd.to_datetime(m15["ts"].iloc[-1], utc=True)
        # Design tip window (exclude Oct blotter tip)
        start = pd.Timestamp("2026-05-01", tz="UTC")
        end_design = min(end, pd.Timestamp("2026-09-11 23:59", tz="UTC"))
        m15w = m15[(m15["ts"] >= start) & (m15["ts"] <= end_design)].reset_index(drop=True)
        # Full tip matching Tester May→Oct (for comparison)
        m15_full = m15[(m15["ts"] >= start) & (m15["ts"] <= end)].reset_index(drop=True)

        candidates: list[tuple[str, pd.DataFrame, dict]] = []

        def add(name: str, frame: pd.DataFrame, **kw) -> None:
            candidates.append((name, frame, _probe(frame, **kw)))

        # --- P0 baseline on design window + blotter cost ---
        add(
            "P0_base_BB2.2_CD2_ATR126_cost58",
            m15w,
            bb_dev=2.2,
            cooldown_bars=2,
            fade_confirm=False,
            cost_rt_pts=COST_RT_BLOTTER,
        )
        add(
            "P0_base_BB2.2_CD2_ATR126_cost58_fullTip",
            m15_full,
            bb_dev=2.2,
            cooldown_bars=2,
            fade_confirm=False,
            cost_rt_pts=COST_RT_BLOTTER,
        )

        # --- WR lift ladder (SL/TP frozen) ---
        for bb, cd, fade, buy, cost, tag in (
            (2.3, 3, False, True, COST_RT_BLOTTER, "light_BB2.3_CD3"),
            (2.3, 3, True, True, COST_RT_BLOTTER, "fade_BB2.3_CD3"),
            (2.2, 3, True, True, COST_RT_BLOTTER, "fade_BB2.2_CD3"),
            (2.3, 2, True, True, COST_RT_BLOTTER, "fade_BB2.3_CD2"),
            (2.3, 3, True, False, COST_RT_BLOTTER, "fade_BB2.3_CD3_sellOnly"),
            (2.3, 3, True, True, COST_RT_TIGHT, "fade_BB2.3_CD3_cost40"),
            (2.4, 3, True, True, COST_RT_BLOTTER, "fade_BB2.4_CD3"),
            (2.3, 3, True, True, COST_RT_TIGHT, "light_BB2.3_CD3_cost40"),
        ):
            add(
                f"P1_{tag}",
                m15w,
                bb_dev=bb,
                cooldown_bars=cd,
                fade_confirm=fade,
                allow_buy=buy,
                cost_rt_pts=cost,
            )

        # Rank: WR>BWR first, then Stage-1 EF, then E_N, then n
        ranked = sorted(
            candidates,
            key=lambda t: (
                t[2]["wr_gt_bwr"],
                t[2]["stage1_ok"],
                t[2]["design_ok"],
                t[2]["EF"],
                t[2]["E_N"],
                t[2]["n_resolved"],
            ),
            reverse=True,
        )

        summary = {}
        for name, _, p in candidates:
            summary[name] = {
                "n": p["n_resolved"],
                "WR": round(p["WR"], 4),
                "BWR": round(p["BWR"], 4),
                "E_N": round(p["E_N"], 4),
                "EF": round(p["EF"], 4),
                "BM": round(p["BM"], 4),
                "Leak": round(p["Leak"], 4),
                "c_R": round(p["c_R"], 4),
                "cost_rt": p["cost_rt_pts"],
                "wr_gt_bwr": p["wr_gt_bwr"],
                "stage1_ok": p["stage1_ok"],
                "sl": p["sl_pts"],
                "tp": p["tp_pts"],
            }

        best_name, _, best = ranked[0]
        out = {
            "symbol": SYMBOL,
            "generated_at": datetime.now(UTC).isoformat(),
            "hard_rule": "SL/TP frozen 160/200 — raise WR via selectivity only",
            "window_design": {"start": str(start), "end": str(end_design)},
            "window_full_tip": {"start": str(start), "end": str(end)},
            "frozen_geometry": {"sl": SL_PTS, "tp": TP_PTS, "rr": TP_PTS / SL_PTS},
            "cost_priors": {
                "blotter_rt_pts": COST_RT_BLOTTER,
                "tight_rt_pts": COST_RT_TIGHT,
            },
            "blotter_p0_ref": {
                "magic": 26101825,
                "WR": 0.413,
                "BWR": 0.444,
                "E_N": -0.071,
                "spread_mean_pts": 28.9,
            },
            "probe_summary": summary,
            "recommended": best_name,
            "recommended_metrics": summary[best_name],
            "top": [
                {
                    "name": n,
                    "WR": round(p["WR"], 4),
                    "E_N": round(p["E_N"], 4),
                    "EF": round(p["EF"], 4),
                    "Leak": round(p["Leak"], 4),
                    "n": p["n_resolved"],
                    "wr_gt_bwr": p["wr_gt_bwr"],
                    "stage1": p["stage1_ok"],
                }
                for n, _, p in ranked[:12]
            ],
        }

        dest = Path(__file__).resolve().parents[2] / "research" / "assets" / "GBPJPY"
        dest.mkdir(parents=True, exist_ok=True)
        path = dest / "bmrg_m15_p1_wr_lift.json"
        path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
        print(json.dumps({"wrote": str(path), **{k: out[k] for k in ("recommended", "recommended_metrics", "top")}}, indent=2))
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
