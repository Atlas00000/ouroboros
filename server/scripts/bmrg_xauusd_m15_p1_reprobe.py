"""Quick P0 vs P1 selectivity re-probe for XAUUSD M15 BMRG (design prior only)."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from app.analytics.bars import load_ohlcv
from app.config import get_settings
from app.db.session import get_session_factory

# Local helpers (keep self-contained; mirror bmrg_xauusd_m15_6m_audit)
POINT = 0.01
COST_RT_POINTS = 35.0


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


def _bb(close: pd.Series, n: int = 20, k: float = 2.2):
    mid = close.rolling(n).mean()
    sd = close.rolling(n).std(ddof=0)
    return mid + k * sd, mid, mid - k * sd


def _atr_wilder(df: pd.DataFrame, n: int = 14) -> pd.Series:
    h, l, c = df["high"], df["low"], df["close"]
    prev_c = c.shift(1)
    tr = pd.concat([(h - l), (h - prev_c).abs(), (l - prev_c).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1.0 / n, adjust=False).mean()


def _probe_with_cooldown(
    g: pd.DataFrame,
    *,
    bb_dev: float,
    sl_pts: float,
    tp_pts: float,
    cooldown_bars: int,
    atr_max_pts: float | None,
    bb_width_min_pct: float | None,
    session: tuple[int, int] = (12, 20),
) -> dict:
    """Same FIXED_RR fade as audit, with explicit cooldown after each armed setup."""
    upper, mid, lower = _bb(g["close"], 20, bb_dev)
    atr = _atr_wilder(g, 14)
    g = g.copy()
    g["upper"], g["mid"], g["lower"] = upper, mid, lower
    g["atr"] = atr
    g["atr_pts"] = atr / POINT
    g["bb_width_pct"] = 100.0 * (upper - lower) / mid.abs()

    wins = losses = 0
    blocked = 0
    i = 25
    while i < len(g) - 40:
        row = g.iloc[i]
        if pd.isna(row["upper"]) or pd.isna(row["lower"]) or pd.isna(row["atr"]):
            i += 1
            continue
        ts = pd.to_datetime(row["ts"], utc=True)
        if int(ts.dayofweek) == 1:
            i += 1
            continue
        h0, h1 = session
        if not (h0 <= int(ts.hour) < h1):
            i += 1
            continue

        atr_pts = float(row["atr_pts"])
        bbw = float(row["bb_width_pct"])
        if atr_max_pts is not None and atr_pts > atr_max_pts:
            blocked += 1
            i += 1
            continue
        if bb_width_min_pct is not None and bbw < bb_width_min_pct:
            blocked += 1
            i += 1
            continue

        side = None
        if float(row["close"]) <= float(row["lower"]):
            side = "long"
        elif float(row["close"]) >= float(row["upper"]):
            side = "short"
        else:
            i += 1
            continue

        entry = float(g.iloc[i + 1]["open"])
        sl_dist = sl_pts * POINT
        tp_dist = tp_pts * POINT
        if side == "long":
            sl, tp = entry - sl_dist, entry + tp_dist
        else:
            sl, tp = entry + sl_dist, entry - tp_dist

        outcome = None
        for j in range(i + 1, min(i + 1 + 96, len(g))):
            hi = float(g.iloc[j]["high"])
            lo = float(g.iloc[j]["low"])
            if side == "long":
                hit_sl, hit_tp = lo <= sl, hi >= tp
            else:
                hit_sl, hit_tp = hi >= sl, lo <= tp
            if hit_sl and hit_tp:
                outcome = "loss"
                break
            if hit_tp:
                outcome = "win"
                break
            if hit_sl:
                outcome = "loss"
                break
        if outcome == "win":
            wins += 1
        elif outcome == "loss":
            losses += 1
        i += max(cooldown_bars, 1)
        continue

    n = wins + losses
    wr = wins / n if n else 0.0
    rr = tp_pts / sl_pts
    bwr = 1.0 / (1.0 + rr)
    bm = wr - bwr
    c_r = COST_RT_POINTS / sl_pts
    leak = c_r / (rr + 1.0)
    return {
        "n": n,
        "wins": wins,
        "losses": losses,
        "WR": wr,
        "RR": rr,
        "BWR": bwr,
        "BM": bm,
        "Leak": leak,
        "EF": bm - leak,
        "E_N": wr * (rr + 1.0) - 1.0,
        "blocked": blocked,
        "bb_dev": bb_dev,
        "cooldown": cooldown_bars,
        "bb_width_min": bb_width_min_pct,
        "atr_max": atr_max_pts,
    }


def main() -> int:
    get_settings.cache_clear()
    session = get_session_factory()()
    try:
        m1 = load_ohlcv(session, "XAUUSD", "M1", lookback_days=220)
        m15 = _resample_m15(m1)
        end = pd.to_datetime(m15["ts"].iloc[-1], utc=True)
        start = pd.Timestamp(year=end.year, month=end.month, day=1, tz="UTC") - pd.DateOffset(
            months=5
        )
        start = pd.Timestamp(year=start.year, month=start.month, day=1, tz="UTC")
        g = m15[(m15["ts"] >= start) & (m15["ts"] <= end)].reset_index(drop=True)

        candidates = {
            "P0_baseline_bb2.2_cd2_noBBw": _probe_with_cooldown(
                g,
                bb_dev=2.2,
                sl_pts=1200,
                tp_pts=1500,
                cooldown_bars=2,
                atr_max_pts=1000,
                bb_width_min_pct=None,
            ),
            "P1a_bb2.4_cd3_bbw0.35": _probe_with_cooldown(
                g,
                bb_dev=2.4,
                sl_pts=1200,
                tp_pts=1500,
                cooldown_bars=3,
                atr_max_pts=1000,
                bb_width_min_pct=0.35,
            ),
            "P1_bb2.5_cd3_bbw0.35": _probe_with_cooldown(
                g,
                bb_dev=2.5,
                sl_pts=1200,
                tp_pts=1500,
                cooldown_bars=3,
                atr_max_pts=1000,
                bb_width_min_pct=0.35,
            ),
            "P1b_bb2.5_cd4_bbw0.40": _probe_with_cooldown(
                g,
                bb_dev=2.5,
                sl_pts=1200,
                tp_pts=1500,
                cooldown_bars=4,
                atr_max_pts=1000,
                bb_width_min_pct=0.40,
            ),
        }

        # Prefer E_N>0, EF>0, WR>BWR, n>=30; then EF, E_N
        ranked = sorted(
            candidates.items(),
            key=lambda kv: (
                kv[1]["n"] >= 30
                and kv[1]["E_N"] > 0
                and kv[1]["EF"] > 0
                and kv[1]["WR"] > kv[1]["BWR"],
                kv[1]["EF"],
                kv[1]["E_N"],
                kv[1]["n"],
            ),
            reverse=True,
        )
        best = ranked[0][0]
        out = {
            "generated_at": datetime.now(UTC).isoformat(),
            "window": {"start": str(start), "end": str(end)},
            "note": "Design prior only — P0 Tester blotter was WR~43% < BWR. Re-test P1 on every-tick.",
            "recommended": best,
            "candidates": {
                k: {
                    **{kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items()},
                    "WR_pct": round(100 * v["WR"], 1),
                    "BWR_pct": round(100 * v["BWR"], 1),
                    "EF_pp": round(100 * v["EF"], 2),
                }
                for k, v in candidates.items()
            },
        }
        dest = (
            Path(__file__).resolve().parents[2]
            / "research"
            / "assets"
            / "XAUUSD"
            / "bmrg_m15_p1_reprobe.json"
        )
        dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(json.dumps(out, indent=2))
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
