"""JP225 BMRG M15 P1 — raise WR first (frozen geometry), re-score Leak.

Hard rules:
  - SL/TP frozen at 23260/34890 (RR=1.50) — never widen TP or shrink SL
  - never emit TP < SL
  - selectivity only: BBDev, cooldown, fade-confirm, ATR max, MaxSpread prior
  - deposit unchanged — edge before capital
Framework: docs/framework/unified_edge_framework.md Stage 0–1.
Blotter prior (magic 26101903): tip WR 42.4% · BWR 39.4% · EF −1.1pp · E_N +0.08R.
Target: WR ≳ BWR + Leak ≈ 44%+ (prefer 45–48%) with EF>0, n≥40.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from app.analytics.bars import load_ohlcv
from app.config import get_settings
from app.db.session import get_session_factory

SYMBOL = "JP225"
POINT = 0.01
# Frozen P0 growth geometry
SL_PTS = 23260.0
TP_PTS = 34890.0
COST_RT = 2500.0  # spread~2300 + slip prior
ATR_MAX_P0 = 19670.0  # ≈ p75
SESSION = (8, 17)


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
) -> str | None:
    entry = float(g.iloc[i_entry]["open"])
    sl_dist = sl_pts * POINT
    tp_dist = tp_pts * POINT
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
    session: tuple[int, int] = SESSION,
    skip_tue: bool = True,
    atr_max_pts: float | None = ATR_MAX_P0,
    cooldown_bars: int = 2,
    fade_confirm: bool = False,
    fade_max_bars: int = 3,
    cost_rt_pts: float = COST_RT,
) -> dict:
    upper, mid, lower = _bb(g["close"], 20, bb_dev)
    atr = _atr_wilder(g, 14)
    g = g.copy()
    g["upper"], g["mid"], g["lower"] = upper, mid, lower
    g["atr_pts"] = atr / POINT

    wins = losses = 0
    blocked_regime = 0
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

        entry_i: int | None = None
        if not fade_confirm:
            entry_i = i + 1
        else:
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
                    reclaimed = cj > loj and cj < mj
                else:
                    reclaimed = cj < uj and cj > mj
                if reclaimed:
                    entry_i = j + 1
                    break
            if entry_i is None:
                i += 1
                continue

        if entry_i is None or entry_i >= len(g) - 1:
            break

        ets = pd.to_datetime(g.iloc[entry_i]["ts"], utc=True)
        if skip_tue and int(ets.dayofweek) == 1:
            i = entry_i + 1
            continue
        if not (h0 <= int(ets.hour) < h1):
            i = entry_i + 1
            continue

        setups += 1
        if tp_pts / sl_pts < 1.0 - 1e-12:
            i = entry_i + 1
            continue

        outcome = _resolve(g, entry_i, side, sl_pts, tp_pts)
        if outcome == "win":
            wins += 1
        elif outcome == "loss":
            losses += 1
        cool_until = entry_i + max(1, cooldown_bars)
        i = cool_until

    n = wins + losses
    wr = wins / n if n else 0.0
    r = tp_pts / sl_pts
    bwr = 1.0 / (1.0 + r)
    bm = wr - bwr
    c_r = cost_rt_pts / sl_pts
    leak = c_r / (r + 1.0)
    ef = bm - leak
    e_n = wr * (r + 1.0) - 1.0
    # Need BM > Leak ≈ WR > BWR + Leak
    wr_clear = wr - bwr - leak
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
        "WR_minus_BWR_Leak": wr_clear,
        "blocked_regime": blocked_regime,
        "sl_pts": sl_pts,
        "tp_pts": tp_pts,
        "bb_dev": bb_dev,
        "cooldown_bars": cooldown_bars,
        "fade_confirm": fade_confirm,
        "atr_max_pts": atr_max_pts,
        "stage0_ok": n >= 40 and wr > bwr and e_n > 0 and r >= 1.0,
        "stage1_ok": n >= 40 and wr > bwr and e_n > 0 and r >= 1.0 and ef > 0,
    }


def main() -> int:
    get_settings.cache_clear()
    session = get_session_factory()()
    try:
        df_m1 = load_ohlcv(session, SYMBOL, "M1", lookback_days=220)
        m15 = _resample_m15(df_m1)
        end = pd.to_datetime(m15["ts"].iloc[-1], utc=True)
        start = pd.Timestamp("2026-05-01", tz="UTC")
        # Match blotter tip end (Aug) + full available tip
        tip_aug = min(end, pd.Timestamp("2026-08-31 23:59", tz="UTC"))
        m15_aug = m15[(m15["ts"] >= start) & (m15["ts"] <= tip_aug)].reset_index(drop=True)
        m15_full = m15[(m15["ts"] >= start) & (m15["ts"] <= end)].reset_index(drop=True)

        atr = _atr_wilder(m15_full, 14)
        atr_pts = (atr / POINT).dropna()
        atr_p60 = float(atr_pts.quantile(0.60))
        atr_p70 = float(atr_pts.quantile(0.70))
        atr_p75 = float(atr_pts.quantile(0.75))

        candidates: list[tuple[str, dict]] = []

        def add(name: str, frame: pd.DataFrame, **kw) -> None:
            candidates.append((name, _probe(frame, **kw)))

        # P0 baseline (blotter window)
        add("P0_BB2.2_CD2_ATRp75_aug", m15_aug, bb_dev=2.2, cooldown_bars=2, atr_max_pts=ATR_MAX_P0)
        add("P0_BB2.2_CD2_ATRp75_full", m15_full, bb_dev=2.2, cooldown_bars=2, atr_max_pts=ATR_MAX_P0)

        # WR-lift ladder — frozen SL/TP
        for bb in (2.3, 2.4, 2.5):
            for cd in (2, 3, 4):
                for atr_cap, tag in (
                    (ATR_MAX_P0, "p75"),
                    (atr_p70, "p70"),
                    (atr_p60, "p60"),
                ):
                    add(
                        f"BB{bb}_CD{cd}_ATR{tag}_aug",
                        m15_aug,
                        bb_dev=bb,
                        cooldown_bars=cd,
                        atr_max_pts=atr_cap,
                        fade_confirm=False,
                    )
                    add(
                        f"BB{bb}_CD{cd}_ATR{tag}_full",
                        m15_full,
                        bb_dev=bb,
                        cooldown_bars=cd,
                        atr_max_pts=atr_cap,
                        fade_confirm=False,
                    )

        # Fade-confirm light (risk of starve — keep CD=2)
        for bb in (2.3, 2.4):
            add(
                f"BB{bb}_CD2_ATRp75_fade_aug",
                m15_aug,
                bb_dev=bb,
                cooldown_bars=2,
                atr_max_pts=ATR_MAX_P0,
                fade_confirm=True,
            )
            add(
                f"BB{bb}_CD2_ATRp75_fade_full",
                m15_full,
                bb_dev=bb,
                cooldown_bars=2,
                atr_max_pts=ATR_MAX_P0,
                fade_confirm=True,
            )

        # Prefer stage1 on tip-aug (matches scored blotter), then full
        ranked = sorted(
            candidates,
            key=lambda t: (
                t[1]["stage1_ok"],
                t[1]["stage0_ok"],
                t[1]["EF"],
                t[1]["WR_minus_BWR_Leak"],
                t[1]["n_resolved"],
            ),
            reverse=True,
        )

        summary = {
            name: {
                "n": p["n_resolved"],
                "WR": round(p["WR"], 4),
                "BWR": round(p["BWR"], 4),
                "BM_pp": round(100 * p["BM"], 2),
                "Leak_pp": round(100 * p["Leak"], 2),
                "EF_pp": round(100 * p["EF"], 2),
                "E_N": round(p["E_N"], 4),
                "clear_pp": round(100 * p["WR_minus_BWR_Leak"], 2),
                "bb": p["bb_dev"],
                "cd": p["cooldown_bars"],
                "fade": p["fade_confirm"],
                "atr_max": round(p["atr_max_pts"] or 0, 0),
                "stage0": p["stage0_ok"],
                "stage1": p["stage1_ok"],
            }
            for name, p in candidates
        }

        best = ranked[0] if ranked else (None, None)
        # Prefer a non-starve full-tip stage1 if available
        best_full = next(
            (r for r in ranked if r[0].endswith("_full") and r[1]["stage1_ok"]),
            None,
        )
        best_aug = next(
            (r for r in ranked if r[0].endswith("_aug") and r[1]["stage1_ok"]),
            None,
        )
        recommended = best_aug or best_full or best

        out = {
            "symbol": SYMBOL,
            "mt5_ticker": "JPN225",
            "generated_at": datetime.now(UTC).isoformat(),
            "frozen_geometry": {"sl": SL_PTS, "tp": TP_PTS, "rr": TP_PTS / SL_PTS},
            "cost_rt_prior": COST_RT,
            "atr_caps": {"p60": atr_p60, "p70": atr_p70, "p75": atr_p75},
            "blotter_prior_magic": 26101903,
            "blotter_prior": {
                "WR": 0.424,
                "BWR": 0.394,
                "EF_pp": -1.1,
                "E_N": 0.078,
                "n": 99,
            },
            "target": "WR > BWR + Leak (~44%+) · EF>0 · n>=40 · deposit unchanged",
            "probe_summary": summary,
            "recommended": recommended[0] if recommended else None,
            "recommended_metrics": summary.get(recommended[0]) if recommended else None,
            "top_stage1": [
                {
                    "name": n,
                    **summary[n],
                }
                for n, p in ranked
                if p["stage1_ok"]
            ][:12],
            "top_overall": [
                {"name": n, **summary[n]} for n, _ in ranked[:15]
            ],
        }

        dest = Path(__file__).resolve().parents[2] / "research" / "assets" / "JP225"
        dest.mkdir(parents=True, exist_ok=True)
        path = dest / "bmrg_m15_p1_wr_lift.json"
        path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
        print(
            json.dumps(
                {
                    "wrote": str(path),
                    "atr_caps": {k: round(v, 1) for k, v in out["atr_caps"].items()},
                    "recommended": out["recommended"],
                    "recommended_metrics": out["recommended_metrics"],
                    "stage1_count": len(out["top_stage1"]),
                    "top_stage1": out["top_stage1"][:8],
                    "top_overall": out["top_overall"][:8],
                },
                indent=2,
            )
        )
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
