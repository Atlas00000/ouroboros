"""GBPJPY ~6m regime + BMRG M5* geometry probe (lean grid).

Hard rules:
  - never emit TP < SL (RR_design >= 1.0)
  - target mix of functional WR and returns
  - regime filters when they protect EF without starving fire-count
Framework: docs/framework/unified_edge_framework.md Stage 0–1.

Yen Digits=3 → Point=0.001. Scale from M5 ATR — not M15 160pt floors.
Cost prior ≈ 2× measured spr (~29) from M15 blotter.
"""

from __future__ import annotations

import calendar
import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

from app.analytics.bars import load_ohlcv
from app.analytics.fit.boards import board_from_ohlcv, board_from_regimes
from app.analytics.fit.mapper import MODEL_VERSION as FIT_MODEL
from app.analytics.profiles import build_asset_profile_from_session
from app.analytics.regimes import MODEL_VERSION as REGIME_MODEL, regime_feature_frame
from app.config import get_settings
from app.db.session import get_session_factory

SYMBOL = "GBPJPY"
POINT = 0.001
COST_RT_POINTS = 58.0  # blotter prior; replace with M5 blotter
SESSION = (12, 20)


def _month_ends(start: pd.Timestamp, end: pd.Timestamp) -> list[tuple[str, pd.Timestamp]]:
    cur = pd.Timestamp(year=start.year, month=start.month, day=1, tz="UTC")
    out: list[tuple[str, pd.Timestamp]] = []
    while cur <= end:
        last = calendar.monthrange(cur.year, cur.month)[1]
        me = pd.Timestamp(
            year=cur.year, month=cur.month, day=last, hour=23, minute=59, tz="UTC"
        )
        out.append((f"{cur.year:04d}-{cur.month:02d}", me))
        if cur.month == 12:
            cur = pd.Timestamp(year=cur.year + 1, month=1, day=1, tz="UTC")
        else:
            cur = pd.Timestamp(year=cur.year, month=cur.month + 1, day=1, tz="UTC")
    return out


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


def _bb(close: pd.Series, n: int = 20, k: float = 2.2) -> tuple[pd.Series, pd.Series, pd.Series]:
    mid = close.rolling(n).mean()
    sd = close.rolling(n).std(ddof=0)
    return mid + k * sd, mid, mid - k * sd


def _atr_wilder(df: pd.DataFrame, n: int = 14) -> pd.Series:
    h, l, c = df["high"], df["low"], df["close"]
    prev_c = c.shift(1)
    tr = pd.concat([(h - l), (h - prev_c).abs(), (l - prev_c).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1.0 / n, adjust=False).mean()


def _round_pts(x: float, step: int = 10) -> int:
    return int(round(x / step) * step)


def _probe(
    g: pd.DataFrame,
    *,
    bb_dev: float,
    sl_pts: float,
    tp_pts: float,
    atr_max_pts: float | None = None,
    session: tuple[int, int] | None = SESSION,
    skip_tue: bool = True,
    cost_rt_pts: float = COST_RT_POINTS,
    hold_bars: int = 192,  # ~16h on M5
    cooldown: int = 3,
) -> dict:
    upper, mid, lower = _bb(g["close"], 20, bb_dev)
    atr = _atr_wilder(g, 14)
    g = g.copy()
    g["upper"], g["mid"], g["lower"] = upper, mid, lower
    g["atr_pts"] = atr / POINT

    wins = losses = 0
    blocked_regime = 0
    rrs: list[float] = []
    i = 25
    while i < len(g) - hold_bars - 2:
        row = g.iloc[i]
        if pd.isna(row["upper"]) or pd.isna(row["lower"]) or pd.isna(row["atr_pts"]):
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
        if atr_max_pts is not None and atr_pts > atr_max_pts:
            blocked_regime += 1
            i += 1
            continue

        c = float(row["close"])
        side = None
        if c <= float(row["lower"]):
            side = "long"
        elif c >= float(row["upper"]):
            side = "short"
        else:
            i += 1
            continue

        entry = float(g.iloc[i + 1]["open"])
        sl_dist = sl_pts * POINT
        tp_dist = tp_pts * POINT
        design_rr = tp_dist / sl_dist if sl_dist > 0 else 0.0
        rrs.append(design_rr)
        if design_rr < 1.0 - 1e-12:
            i += 2
            continue

        if side == "long":
            sl, tp = entry - sl_dist, entry + tp_dist
        else:
            sl, tp = entry + sl_dist, entry - tp_dist

        outcome = None
        for j in range(i + 1, min(i + 1 + hold_bars, len(g))):
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
        i += max(3, cooldown)
        continue

    n = wins + losses
    wr = wins / n if n else 0.0
    r = float(np.median(rrs)) if rrs else 0.0
    bwr = 1.0 / (1.0 + r) if r > 0 else 1.0
    bm = wr - bwr
    c_r = cost_rt_pts / sl_pts if sl_pts else 0.15
    leak = c_r / (r + 1.0) if r > 0 else 0.0
    ef = bm - leak
    e_n = wr * (r + 1.0) - 1.0
    return {
        "n_resolved": n,
        "wins": wins,
        "losses": losses,
        "setups": len(rrs),
        "WR": wr,
        "RR_design": r,
        "BWR": bwr,
        "BM": bm,
        "c_R": c_r,
        "Leak": leak,
        "EF": ef,
        "E_N": e_n,
        "blocked_regime": blocked_regime,
        "sl_pts": sl_pts,
        "tp_pts": tp_pts,
        "tp_lt_sl_blocked": int(sum(1 for x in rrs if x < 1.0)),
    }


def main() -> int:
    get_settings.cache_clear()
    session = get_session_factory()()
    try:
        print("loading bars…", flush=True)
        df_h1 = load_ohlcv(session, SYMBOL, "H1", lookback_days=220)
        df_m1 = load_ohlcv(session, SYMBOL, "M1", lookback_days=220)
        m5 = _resample_m5(df_m1)
        end = pd.to_datetime(m5["ts"].iloc[-1], utc=True)
        start = pd.Timestamp(year=end.year, month=end.month, day=1, tz="UTC") - pd.DateOffset(
            months=5
        )
        start = pd.Timestamp(year=start.year, month=start.month, day=1, tz="UTC")
        m5w = m5[(m5["ts"] >= start) & (m5["ts"] <= end)].reset_index(drop=True)
        print(f"window {start.date()} -> {end}  m5_bars={len(m5w)}", flush=True)

        atr = _atr_wilder(m5w, 14)
        atr_pts = (atr / POINT).dropna()
        atr_stats = {
            "p25": float(atr_pts.quantile(0.25)),
            "p50": float(atr_pts.quantile(0.50)),
            "p75": float(atr_pts.quantile(0.75)),
            "p90": float(atr_pts.quantile(0.90)),
            "mean": float(atr_pts.mean()),
        }
        sl_floor = max(_round_pts(atr_stats["p50"] * 1.2), 40)
        sl_16 = max(_round_pts(atr_stats["p50"] * 1.6), sl_floor)
        sl_20 = max(_round_pts(atr_stats["p50"] * 2.0), sl_floor)
        sl_25 = max(_round_pts(atr_stats["p50"] * 2.5), sl_floor)
        atr_p75 = float(atr_stats["p75"])
        atr_p90 = float(atr_stats["p90"])
        atr_tight = float(atr_stats["p50"]) + 0.15 * (atr_p75 - atr_stats["p50"])
        print(
            f"ATR pts p50={atr_stats['p50']:.1f} p75={atr_p75:.1f} p90={atr_p90:.1f} "
            f"sl_cands={sl_16}/{sl_20}/{sl_25}",
            flush=True,
        )

        feat_h1 = regime_feature_frame(df_h1, "H1")
        months = _month_ends(start, end)
        monthly = []
        ts = pd.to_datetime(feat_h1["ts"], utc=True)
        for mk, me in months:
            ms = me.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if ms < start:
                ms = start
            mask = (ts >= ms) & (ts <= me) & (ts >= start)
            regimes = [
                str(r) for r in feat_h1.loc[mask, "confirmed_regime"].dropna().tolist()
            ]
            b = board_from_regimes(regimes, "meanrev", window="calendar_month")
            monthly.append(
                {
                    "month": mk,
                    "tag": b.tag,
                    "shares": b.shares,
                    "regime_shares": b.regime_shares,
                    "bars": b.bar_count,
                }
            )
        overall_mask = (ts >= start) & (ts <= end)
        regimes_all = [
            str(r)
            for r in feat_h1.loc[overall_mask, "confirmed_regime"].dropna().tolist()
        ]
        overall = board_from_regimes(regimes_all, "meanrev", window="30d")
        fit30 = board_from_ohlcv(df_h1, "meanrev", timeframe="H1", window="30d")
        prof = build_asset_profile_from_session(session, SYMBOL, lookback_days=220)

        # Lean candidate set — all enforce TP >= SL
        candidates: list[tuple[str, dict]] = []

        def add(name: str, **kw) -> None:
            print(f"  probe {name}...", flush=True)
            p = _probe(m5w, **kw)
            print(
                f"    n={p['n_resolved']} WR={p['WR']:.1%} E_N={p['E_N']:+.3f} "
                f"EF={p['EF']:+.3f}",
                flush=True,
            )
            candidates.append((name, p))

        for sl in (sl_16, sl_20, sl_25):
            tp125 = max(_round_pts(sl * 1.25), sl)
            tp130 = max(_round_pts(sl * 1.30), sl)
            tp150 = max(_round_pts(sl * 1.50), sl)
            # no gate
            add(f"bal_RR1.25_sl{sl}_tp{tp125}", bb_dev=2.2, sl_pts=sl, tp_pts=tp125)
            add(f"bal_RR1.30_sl{sl}_tp{tp130}", bb_dev=2.2, sl_pts=sl, tp_pts=tp130)
            # ATR p75 gate (Sep FRAGILE cut from M15 dossier)
            add(
                f"bal_RR1.25_sl{sl}_tp{tp125}_atrMax{int(atr_p75)}",
                bb_dev=2.2,
                sl_pts=sl,
                tp_pts=tp125,
                atr_max_pts=atr_p75,
            )
            add(
                f"bal_RR1.30_sl{sl}_tp{tp130}_atrMax{int(atr_p75)}",
                bb_dev=2.2,
                sl_pts=sl,
                tp_pts=tp130,
                atr_max_pts=atr_p75,
            )
            add(
                f"growth_RR1.5_sl{sl}_tp{tp150}_atrMax{int(atr_p75)}",
                bb_dev=2.2,
                sl_pts=sl,
                tp_pts=tp150,
                atr_max_pts=atr_p75,
            )
            # light selectivity BB 2.3
            add(
                f"light_BB2.3_RR1.25_sl{sl}_tp{tp125}_atrMax{int(atr_p75)}",
                bb_dev=2.3,
                sl_pts=sl,
                tp_pts=tp125,
                atr_max_pts=atr_p75,
                cooldown=4,
            )

        # ATR p90 ablation on mid SL
        tp = max(_round_pts(sl_20 * 1.25), sl_20)
        add(
            f"bal_RR1.25_sl{sl_20}_tp{tp}_atrMax{int(atr_p90)}_p90",
            bb_dev=2.2,
            sl_pts=sl_20,
            tp_pts=tp,
            atr_max_pts=atr_p90,
        )
        add(
            f"bal_RR1.25_sl{sl_20}_tp{tp}_atrMax{int(atr_tight)}_tight",
            bb_dev=2.2,
            sl_pts=sl_20,
            tp_pts=tp,
            atr_max_pts=atr_tight,
        )
        # session / no-regime ablations
        add(
            f"bal_RR1.25_sl{sl_20}_tp{tp}_noAtr",
            bb_dev=2.2,
            sl_pts=sl_20,
            tp_pts=tp,
            atr_max_pts=None,
        )
        add(
            f"bal_RR1.25_sl{sl_20}_tp{tp}_atrMax_sess08_20",
            bb_dev=2.2,
            sl_pts=sl_20,
            tp_pts=tp,
            atr_max_pts=atr_p75,
            session=(8, 20),
        )

        probes = {n: p for n, p in candidates}
        ranked = []
        for name, p in probes.items():
            design_ok = (
                p["n_resolved"] >= 40
                and p["RR_design"] + 1e-12 >= 1.0
                and p["E_N"] > 0
                and p["WR"] > p["BWR"]
                and p["tp_lt_sl_blocked"] == 0
            )
            stage1_ok = design_ok and p["EF"] > 0
            rr_pref = 1.0 if 1.2 <= p["RR_design"] <= 1.35 else 0.0
            regime_pref = 1.0 if "atrMax" in name and p["blocked_regime"] > 0 else 0.0
            ranked.append(
                (
                    stage1_ok,
                    design_ok,
                    rr_pref,
                    regime_pref,
                    p["EF"],
                    p["E_N"],
                    p["n_resolved"],
                    name,
                    p,
                )
            )
        ranked.sort(key=lambda t: (t[0], t[1], t[2], t[3], t[4], t[5], t[6]), reverse=True)
        best_name = ranked[0][7]
        best = probes[best_name]

        summary = {
            n: {
                "n": p["n_resolved"],
                "WR": round(p["WR"], 4),
                "RR": round(p["RR_design"], 3),
                "E_N": round(p["E_N"], 4),
                "EF": round(p["EF"], 4),
                "BM": round(p["BM"], 4),
                "Leak": round(p["Leak"], 4),
                "sl": p["sl_pts"],
                "tp": p["tp_pts"],
                "blocked": p["blocked_regime"],
            }
            for n, p in probes.items()
        }

        out = {
            "symbol": SYMBOL,
            "tf_probe": "M5*",
            "point": POINT,
            "cost_rt_points_prior": COST_RT_POINTS,
            "generated_at": datetime.now(UTC).isoformat(),
            "window": {"start": str(start), "end": str(end)},
            "models": {"regime": REGIME_MODEL, "fit": FIT_MODEL},
            "atr_m5_points": atr_stats,
            "sl_candidates": {"x1.6": sl_16, "x2.0": sl_20, "x2.5": sl_25},
            "atr_cap_p75": atr_p75,
            "atr_cap_p90": atr_p90,
            "atr_cap_tight": atr_tight,
            "monthly_meanrev_h1": monthly,
            "overall_meanrev_h1": {
                "tag": overall.tag,
                "shares": overall.shares,
                "regime_shares": overall.regime_shares,
                "bars": overall.bar_count,
            },
            "fit_30d_h1_meanrev": {"tag": fit30.tag, "shares": fit30.shares},
            "profile_regime": [r.model_dump() for r in prof.regime_distribution],
            "volatility": prof.volatility.model_dump(),
            "probes": probes,
            "probe_summary": summary,
            "recommended_probe": best_name,
            "recommended": best,
            "hard_rule": "never emit TP < SL (RR_design >= 1.0)",
            "framework_note": (
                "E_N=WR*(R+1)-1; BWR=1/(1+R); BM=WR-BWR; Leak=c_R/(R+1); EF=BM-Leak. "
                "M5 ATR-scaled. RESEARCH / UNTESTED design prior."
            ),
        }

        dest = Path(__file__).resolve().parents[2] / "research" / "assets" / "GBPJPY"
        dest.mkdir(parents=True, exist_ok=True)
        path = dest / "bmrg_m5_6m_audit.json"
        path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")

        design = [r for r in ranked if r[1]]
        stage1 = [r for r in ranked if r[0]]
        print(
            json.dumps(
                {
                    "wrote": str(path),
                    "window": out["window"],
                    "atr_m5_pts": {k: round(v, 1) for k, v in atr_stats.items()},
                    "recommended": best_name,
                    "recommended_metrics": summary[best_name],
                    "stage1_ef_ok_count": len(stage1),
                    "design_positive_count": len(design),
                    "top_design": [
                        {
                            "name": r[7],
                            "stage1": r[0],
                            "EF": round(r[8]["EF"], 4),
                            "E_N": round(r[8]["E_N"], 4),
                            "WR": round(r[8]["WR"], 4),
                            "n": r[8]["n_resolved"],
                            "sl": r[8]["sl_pts"],
                            "tp": r[8]["tp_pts"],
                        }
                        for r in design[:8]
                    ],
                    "monthly": [
                        {
                            "m": m["month"],
                            "tag": m["tag"],
                            "MATCH": round(100 * m["shares"].get("MATCH", 0), 1),
                            "FRAGILE": round(100 * m["shares"].get("FRAGILE", 0), 1),
                        }
                        for m in monthly
                        if m["bars"] > 0
                    ],
                },
                indent=2,
            )
        )
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
