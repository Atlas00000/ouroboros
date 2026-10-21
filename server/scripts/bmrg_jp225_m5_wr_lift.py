"""JP225 BMRG M5 — Stage-1 WR/EF lift after lean grid returned viable_count=0.

Lean bmrg_m5_6m_audit.json: all EF < 0; best Growth 21180/31770 ATR≤p75
  WR≈39.7% · BWR=40% · EF≈−5.0pp under cost RT 2500.

Hypothesis: fat-spread Nikkei M5 needs either (a) higher R to cut BWR+Leak,
or (b) BB/ATR-band/fade selectivity to lift WR ~5pp — without TP < SL.

Hard rules: never emit TP < SL · deposit unchanged · regime filter kept.
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

SYMBOL = "JP225"
POINT = 0.01
COST_RT = 2500.0
SESSION = (8, 17)


def _resample_m5(m1: pd.DataFrame) -> pd.DataFrame:
    df = m1.copy()
    df["ts"] = pd.to_datetime(df["ts"], utc=True)
    df = df.set_index("ts").sort_index()
    return (
        df.resample("5min")
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


def _probe(
    g: pd.DataFrame,
    *,
    bb_dev: float,
    sl_pts: float,
    tp_pts: float,
    atr_max_pts: float | None,
    atr_min_pts: float | None = None,
    cooldown_bars: int = 3,
    fade_confirm: bool = False,
    fade_max_bars: int = 3,
    skip_tue: bool = True,
    session: tuple[int, int] | None = SESSION,
) -> dict:
    upper, mid, lower = _bb(g["close"], 20, bb_dev)
    atr = _atr_wilder(g, 14)
    g = g.copy()
    g["upper"], g["mid"], g["lower"] = upper, mid, lower
    g["atr_pts"] = atr / POINT

    wins = losses = 0
    blocked = 0
    rrs: list[float] = []
    i = 25
    while i < len(g) - 40:
        row = g.iloc[i]
        if pd.isna(row["upper"]) or pd.isna(row["atr_pts"]):
            i += 1
            continue
        ts = pd.to_datetime(row["ts"], utc=True)
        if skip_tue and int(ts.dayofweek) == 1:
            i += 1
            continue
        if session is not None:
            h0, h1 = session
            if not (h0 <= int(ts.hour) < h1):
                i += 1
                continue
        atr_pts = float(row["atr_pts"])
        if atr_min_pts is not None and atr_pts < atr_min_pts:
            blocked += 1
            i += 1
            continue
        if atr_max_pts is not None and atr_pts > atr_max_pts:
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

        if fade_confirm:
            ok = False
            for k in range(1, fade_max_bars + 1):
                if i + k >= len(g):
                    break
                c = float(g.iloc[i + k]["close"])
                if side == "long" and c > float(row["lower"]):
                    ok = True
                    i = i + k
                    break
                if side == "short" and c < float(row["upper"]):
                    ok = True
                    i = i + k
                    break
            if not ok:
                i += 1
                continue

        entry_i = i + 1
        if entry_i >= len(g) - 2:
            break
        entry = float(g.iloc[entry_i]["open"])
        sl_dist = sl_pts * POINT
        tp_dist = tp_pts * POINT
        design_rr = tp_dist / sl_dist if sl_dist > 0 else 0.0
        if design_rr < 1.0 - 1e-12:
            i += cooldown_bars
            continue
        rrs.append(design_rr)

        if side == "long":
            sl, tp = entry - sl_dist, entry + tp_dist
        else:
            sl, tp = entry + sl_dist, entry - tp_dist

        outcome = None
        for j in range(entry_i, min(entry_i + 144, len(g))):
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
        i = entry_i + cooldown_bars

    n = wins + losses
    wr = wins / n if n else 0.0
    rr = float(np.median(rrs)) if rrs else 0.0
    bwr = 1.0 / (1.0 + rr) if rr > 0 else 1.0
    bm = wr - bwr
    c_r = COST_RT / sl_pts if sl_pts else 0.15
    leak = c_r / (rr + 1.0) if rr > 0 else 0.0
    ef = bm - leak
    e_n = wr * (rr + 1.0) - 1.0
    return {
        "n_resolved": n,
        "wins": wins,
        "losses": losses,
        "WR": wr,
        "RR_design": rr,
        "BWR": bwr,
        "BM": bm,
        "c_R_prior": c_r,
        "Leak": leak,
        "EF": ef,
        "E_N": e_n,
        "blocked_regime": blocked,
        "sl_pts": sl_pts,
        "tp_pts": tp_pts,
        "tp_lt_sl_blocked": int(sum(1 for x in rrs if x < 1.0)),
        "wr_clears_bwr_leak": wr > (bwr + leak),
    }


def main() -> int:
    print("JP225 M5 WR-lift: load…", flush=True)
    get_settings.cache_clear()
    session = get_session_factory()()
    try:
        df_m1 = load_ohlcv(session, SYMBOL, "M1", lookback_days=220)
        m5 = _resample_m5(df_m1)
        end = pd.to_datetime(m5["ts"].iloc[-1], utc=True)
        start = pd.Timestamp(year=end.year, month=end.month, day=1, tz="UTC") - pd.DateOffset(
            months=5
        )
        start = pd.Timestamp(year=start.year, month=start.month, day=1, tz="UTC")
        m5w = m5[(m5["ts"] >= start) & (m5["ts"] <= end)].reset_index(drop=True)
        atr = _atr_wilder(m5w, 14)
        atr_pts = (atr / POINT).dropna()
        p40 = float(atr_pts.quantile(0.40))
        p50 = float(atr_pts.quantile(0.50))
        p75 = float(atr_pts.quantile(0.75))
        p90 = float(atr_pts.quantile(0.90))
        print(
            f"window {start.date()}->{end.date()} bars={len(m5w)} "
            f"atr p40={p40:.0f} p50={p50:.0f} p75={p75:.0f} p90={p90:.0f}",
            flush=True,
        )

        # Focused fat-SL × higher-R × selectivity (lean grid already killed thin RR)
        geometries = [
            (21180, 31770, 1.50),
            (21180, 37065, 1.75),
            (21180, 42360, 2.00),
            (23260, 34890, 1.50),  # M15 P0 geometry on M5
            (23260, 40705, 1.75),
            (25000, 37500, 1.50),
            (25000, 43750, 1.75),
            (25000, 50000, 2.00),
        ]

        candidates: list[tuple[str, dict]] = []

        def add(name: str, **kw) -> None:
            print(f"  {name} …", flush=True)
            candidates.append((name, _probe(m5w, **kw)))

        for sl, tp, rrm in geometries:
            for bb in (2.2, 2.4, 2.5):
                add(
                    f"sl{sl}_tp{tp}_RR{rrm}_bb{bb}_atrMax",
                    bb_dev=bb,
                    sl_pts=sl,
                    tp_pts=tp,
                    atr_max_pts=p75,
                    cooldown_bars=3,
                )

        # ATR band + fade on RR≥1.75 fat sleeves (closest to clearing Leak)
        for sl, tp, rrm in (
            (21180, 37065, 1.75),
            (21180, 42360, 2.00),
            (23260, 40705, 1.75),
            (25000, 50000, 2.00),
        ):
            for bb in (2.4, 2.5):
                add(
                    f"sl{sl}_tp{tp}_RR{rrm}_bb{bb}_atrBand",
                    bb_dev=bb,
                    sl_pts=sl,
                    tp_pts=tp,
                    atr_min_pts=p40,
                    atr_max_pts=p75,
                    cooldown_bars=3,
                )
                add(
                    f"sl{sl}_tp{tp}_RR{rrm}_bb{bb}_atrMax_fade",
                    bb_dev=bb,
                    sl_pts=sl,
                    tp_pts=tp,
                    atr_max_pts=p75,
                    cooldown_bars=3,
                    fade_confirm=True,
                )

        for sl, tp, rrm in ((21180, 42360, 2.0), (25000, 50000, 2.0)):
            add(
                f"sl{sl}_tp{tp}_RR{rrm}_bb2.5_atrMax_cd6",
                bb_dev=2.5,
                sl_pts=sl,
                tp_pts=tp,
                atr_max_pts=p75,
                cooldown_bars=6,
            )

        ranked = []
        for name, p in candidates:
            ok = (
                p["n_resolved"] >= 40
                and p["RR_design"] + 1e-12 >= 1.0
                and p["E_N"] > 0
                and p["EF"] > 0
                and p["WR"] > p["BWR"]
                and p["wr_clears_bwr_leak"]
                and p["tp_lt_sl_blocked"] == 0
            )
            # Prefer mix RR 1.25–1.75 over lottery 2.0 when tied
            rr_pref = (
                1.0
                if 1.2 <= p["RR_design"] <= 1.55
                else (0.7 if 1.55 < p["RR_design"] <= 1.8 else 0.3)
            )
            ranked.append((ok, rr_pref, p["EF"], p["E_N"], p["n_resolved"], name, p))
        ranked.sort(key=lambda t: (t[0], t[1], t[2], t[3], t[4]), reverse=True)

        summary = {
            name: {
                "n": p["n_resolved"],
                "WR": round(p["WR"], 4),
                "RR": round(p["RR_design"], 3),
                "BWR": round(p["BWR"], 4),
                "BM": round(p["BM"], 4),
                "Leak": round(p["Leak"], 4),
                "EF": round(p["EF"], 4),
                "E_N": round(p["E_N"], 4),
                "sl": p["sl_pts"],
                "tp": p["tp_pts"],
                "blocked": p["blocked_regime"],
                "clears": p["wr_clears_bwr_leak"],
            }
            for name, p in candidates
        }
        viable = [r for r in ranked if r[0]]
        best_name = ranked[0][5] if ranked else None

        out = {
            "symbol": SYMBOL,
            "tf": "M5*",
            "generated_at": datetime.now(UTC).isoformat(),
            "window": {"start": str(start), "end": str(end)},
            "cost_rt_points_prior": COST_RT,
            "atr_m5": {"p40": p40, "p50": p50, "p75": p75, "p90": p90},
            "probe_summary": summary,
            "recommended": best_name,
            "recommended_metrics": summary.get(best_name),
            "viable_count": len(viable),
            "top_viable": [
                {
                    "name": r[5],
                    "EF": round(r[6]["EF"], 4),
                    "E_N": round(r[6]["E_N"], 4),
                    "WR": round(r[6]["WR"], 4),
                    "RR": round(r[6]["RR_design"], 3),
                    "n": r[6]["n_resolved"],
                    "sl": r[6]["sl_pts"],
                    "tp": r[6]["tp_pts"],
                }
                for r in viable[:15]
            ],
            "top_overall": [
                {
                    "name": r[5],
                    "ok": r[0],
                    "EF": round(r[6]["EF"], 4),
                    "E_N": round(r[6]["E_N"], 4),
                    "WR": round(r[6]["WR"], 4),
                    "RR": round(r[6]["RR_design"], 3),
                    "n": r[6]["n_resolved"],
                    "sl": r[6]["sl_pts"],
                    "tp": r[6]["tp_pts"],
                }
                for r in ranked[:12]
            ],
            "hard_rule": "never emit TP < SL",
            "note": "RESEARCH / UNTESTED design prior after lean-grid EF fail",
        }
        dest = Path(__file__).resolve().parents[2] / "research" / "assets" / "JP225"
        path = dest / "bmrg_m5_wr_lift.json"
        path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
        print(
            json.dumps(
                {
                    "wrote": str(path),
                    "viable_count": len(viable),
                    "recommended": best_name,
                    "recommended_metrics": summary.get(best_name),
                    "top_viable": out["top_viable"][:8],
                    "top_overall": out["top_overall"][:8],
                },
                indent=2,
            ),
            flush=True,
        )
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
