"""USDCAD ~6m regime + BMRG M5* geometry probe for chart preset design.

Hard rules:
  - never emit TP < SL (RR_design >= 1.0)
  - target mix of functional WR and returns (not Harvest-only, not lottery RR)
  - regime filters when they protect EF without starving fire-count
Framework: docs/framework/unified_edge_framework.md Stage 0–1 identities.

USDCAD note: Digits=5 → Point=0.00001. Do NOT import EURUSD 250pt M5 floors
    blindly — scale from M5 ATR in points (loonie major ≈ quieter than EURUSD).
Lean grid: ATR-scaled SLs + selective BB 2.4 (full combinatorial grid is too slow on M5).
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

SYMBOL = "USDCAD"
POINT = 0.00001
# M5 MaxSpread≈20 sleeve; Leak bites harder on smaller SL — replace with blotter
COST_RT_POINTS = 18.0
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


def _probe_fixed_rr(
    g: pd.DataFrame,
    *,
    bb_dev: float,
    sl_pts: float,
    tp_pts: float,
    point: float = POINT,
    session: tuple[int, int] | None = SESSION,
    skip_tue: bool = True,
    atr_max_pts: float | None = None,
    atr_min_pts: float | None = None,
    bb_width_max_pct: float | None = None,
    cost_rt_pts: float = COST_RT_POINTS,
) -> dict:
    """Closed-bar fade probe: long <= lower, short >= upper; fixed TP/SL points."""
    upper, mid, lower = _bb(g["close"], 20, bb_dev)
    atr = _atr_wilder(g, 14)
    g = g.copy()
    g["upper"], g["mid"], g["lower"] = upper, mid, lower
    g["atr"] = atr
    g["atr_pts"] = atr / point
    g["bb_width_pct"] = 100.0 * (upper - lower) / mid.abs()

    wins = losses = 0
    blocked_regime = 0
    rrs: list[float] = []
    i = 25
    while i < len(g) - 40:
        row = g.iloc[i]
        if pd.isna(row["upper"]) or pd.isna(row["lower"]) or pd.isna(row["atr"]):
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
        bbw = float(row["bb_width_pct"])
        if atr_min_pts is not None and atr_pts < atr_min_pts:
            blocked_regime += 1
            i += 1
            continue
        if atr_max_pts is not None and atr_pts > atr_max_pts:
            blocked_regime += 1
            i += 1
            continue
        if bb_width_max_pct is not None and bbw > bb_width_max_pct:
            blocked_regime += 1
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
        sl_dist = sl_pts * point
        tp_dist = tp_pts * point
        design_rr = tp_dist / sl_dist if sl_dist > 0 else 0.0
        rrs.append(design_rr)
        if design_rr < 1.0 - 1e-12:
            i += 2
            continue

        if side == "long":
            sl = entry - sl_dist
            tp = entry + tp_dist
        else:
            sl = entry + sl_dist
            tp = entry - tp_dist

        outcome = None
        # ~24h horizon on M5 (288 bars)
        for j in range(i + 1, min(i + 1 + 288, len(g))):
            hi = float(g.iloc[j]["high"])
            lo = float(g.iloc[j]["low"])
            if side == "long":
                hit_sl = lo <= sl
                hit_tp = hi >= tp
            else:
                hit_sl = hi >= sl
                hit_tp = lo <= tp
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
        i += 3
        continue

    n = wins + losses
    wr = wins / n if n else 0.0
    rr = float(np.median(rrs)) if rrs else 0.0
    r = rr
    bwr = 1.0 / (1.0 + r) if r > 0 else 1.0
    bm = wr - bwr
    c_r = cost_rt_pts / sl_pts if sl_pts else 0.15
    leak = c_r / (r + 1.0) if r > 0 else 0.0
    ef = bm - leak
    e_n = wr * (r + 1.0) - 1.0
    return {
        "setups_armed": len(rrs),
        "n_resolved": n,
        "wins": wins,
        "losses": losses,
        "WR": wr,
        "RR_design": rr,
        "R_assumed": r,
        "BWR": bwr,
        "BM": bm,
        "c_R_prior": c_r,
        "Leak": leak,
        "EF": ef,
        "E_N": e_n,
        "tp_lt_sl_blocked": int(sum(1 for x in rrs if x < 1.0)),
        "pct_rr_ge_1": float(np.mean(np.array(rrs) >= 1.0)) if rrs else 0.0,
        "blocked_regime": blocked_regime,
        "sl_pts": sl_pts,
        "tp_pts": tp_pts,
        "bb_dev": bb_dev,
        "atr_max_pts": atr_max_pts,
        "session": list(session) if session else None,
    }


def _round_pts(x: float, step: int = 5) -> int:
    return int(round(x / step) * step)


def main() -> int:
    get_settings.cache_clear()
    session = get_session_factory()()
    try:
        df_h1 = load_ohlcv(session, SYMBOL, "H1", lookback_days=220)
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
        atr_stats = {
            "p25": float(atr_pts.quantile(0.25)),
            "p50": float(atr_pts.quantile(0.50)),
            "p75": float(atr_pts.quantile(0.75)),
            "p90": float(atr_pts.quantile(0.90)),
            "mean": float(atr_pts.mean()),
        }
        sl_floor = max(_round_pts(atr_stats["p50"] * 1.2), 20)
        atr_cap = float(atr_stats["p75"])
        atr_cap_p90 = float(atr_stats["p90"])
        atr_cap_tight = float(atr_stats["p50"]) + 0.15 * (
            atr_stats["p75"] - atr_stats["p50"]
        )
        atr_cap_tight_r = float(_round_pts(atr_cap_tight))

        # Structural SL ladder from ATR (never token stops) — lean set for M5 runtime
        sl_candidates = sorted(
            {
                _round_pts(atr_stats["p50"] * 1.6),
                _round_pts(atr_stats["p50"] * 2.0),
                _round_pts(atr_stats["p50"] * 2.5),
                _round_pts(atr_stats["p50"] * 3.0),
            }
        )
        sl_candidates = [s for s in sl_candidates if s >= sl_floor]

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

        candidates: list[tuple[str, dict]] = []

        def add(name: str, **kw) -> None:
            print(f"  probe {name}...", flush=True)
            candidates.append((name, _probe_fixed_rr(m5w, **kw)))

        print(
            f"window {start.date()} -> {end.date()} bars={len(m5w)} "
            f"ATR p50={atr_stats['p50']:.1f} p75={atr_stats['p75']:.1f}",
            flush=True,
        )

        # Lean grid: RR ∈ {1.25, 1.30} · BB ∈ {2.2, 2.4} · ATR gates (tight/p75)
        # ~32 core probes — full combinatorial too slow on M5*
        for bb in (2.2, 2.4):
            for sl in sl_candidates:
                for rr_mult, rr_tag in ((1.25, "1.25"), (1.30, "1.30")):
                    tp = max(_round_pts(sl * rr_mult), sl)
                    if tp < sl:
                        continue
                    add(
                        f"bb{bb}_RR{rr_tag}_sl{sl}_tp{tp}",
                        bb_dev=bb,
                        sl_pts=sl,
                        tp_pts=tp,
                    )
                    for cap, tag in (
                        (atr_cap_tight_r, "tight"),
                        (atr_cap, "p75"),
                    ):
                        add(
                            f"bb{bb}_RR{rr_tag}_sl{sl}_tp{tp}_atrMax{int(cap)}_{tag}",
                            bb_dev=bb,
                            sl_pts=sl,
                            tp_pts=tp,
                            atr_max_pts=cap,
                        )

        # Session ablation on best-scale mid SL
        mid_sl = _round_pts(atr_stats["p50"] * 2.5)
        mid_tp = max(_round_pts(mid_sl * 1.25), mid_sl)
        add(
            f"bb2.4_RR1.25_sl{mid_sl}_tp{mid_tp}_sess08_20_atrMax{int(atr_cap)}",
            bb_dev=2.4,
            sl_pts=mid_sl,
            tp_pts=mid_tp,
            atr_max_pts=atr_cap,
            session=(8, 20),
        )
        add(
            f"bb2.4_RR1.25_sl{mid_sl}_tp{mid_tp}_noSession",
            bb_dev=2.4,
            sl_pts=mid_sl,
            tp_pts=mid_tp,
            session=None,
            skip_tue=False,
        )

        probes = {name: p for name, p in candidates}

        ranked = []
        for name, p in probes.items():
            design_ok = (
                p["n_resolved"] >= 40
                and p["RR_design"] + 1e-12 >= 1.0
                and p["E_N"] > 0
                and p["WR"] > p["BWR"]
                and p["tp_lt_sl_blocked"] == 0
            )
            # Also score under cost 15 (MaxSpread 20 sleeve)
            c15 = 15.0 / p["sl_pts"] if p["sl_pts"] else 0.15
            leak15 = c15 / (p["RR_design"] + 1.0) if p["RR_design"] > 0 else 0.0
            ef15 = p["BM"] - leak15
            p["EF_cost15"] = ef15
            p["Leak_cost15"] = leak15
            stage1_ok = design_ok and (p["EF"] > 0 or ef15 > 0)
            rr_pref = 1.0 if 1.2 <= p["RR_design"] <= 1.35 else 0.0
            regime_pref = (
                1.0 if p.get("blocked_regime", 0) > 0 and "atrMax" in name else 0.0
            )
            bb_pref = 1.0 if p.get("bb_dev") == 2.4 else 0.0
            ranked.append(
                (
                    stage1_ok,
                    design_ok,
                    max(p["EF"], ef15),
                    rr_pref,
                    regime_pref,
                    bb_pref,
                    p["E_N"],
                    p["n_resolved"],
                    name,
                    p,
                )
            )
        ranked.sort(
            key=lambda t: (t[0], t[1], t[2], t[3], t[4], t[5], t[6], t[7]),
            reverse=True,
        )
        best_name = ranked[0][8] if ranked else None
        best = probes[best_name] if best_name else None

        summary = {}
        for name, p in probes.items():
            summary[name] = {
                "n": p["n_resolved"],
                "WR": round(p["WR"], 4),
                "RR": round(p["RR_design"], 3),
                "E_N": round(p["E_N"], 4),
                "EF": round(p["EF"], 4),
                "EF_c15": round(p.get("EF_cost15", p["EF"]), 4),
                "BM": round(p["BM"], 4),
                "Leak": round(p["Leak"], 4),
                "blocked_regime": p["blocked_regime"],
                "sl": p["sl_pts"],
                "tp": p["tp_pts"],
                "bb": p.get("bb_dev"),
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
            "sl_floor": sl_floor,
            "atr_cap_p75": atr_cap,
            "atr_cap_p90": atr_cap_p90,
            "atr_cap_tight": atr_cap_tight,
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
                "Probe R assumed ≈ RR on FIXED_RR. RESEARCH / UNTESTED design prior. "
                "USDCAD Point=0.00001 — M5 SL/TP/ATR gates in points, not EURUSD floors."
            ),
        }

        repo = Path(__file__).resolve().parents[2]
        dest = repo / "research" / "assets" / "USDCAD"
        dest.mkdir(parents=True, exist_ok=True)
        path = dest / "bmrg_m5_6m_audit.json"
        path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")

        stage1 = [r for r in ranked if r[0]]
        design = [r for r in ranked if r[1]]
        print(
            json.dumps(
                {
                    "wrote": str(path),
                    "window": out["window"],
                    "atr_m5_pts": {k: round(v, 1) for k, v in atr_stats.items()},
                    "recommended": best_name,
                    "recommended_metrics": summary.get(best_name),
                    "stage1_ef_ok_count": len(stage1),
                    "design_positive_count": len(design),
                    "top_design": [
                        {
                            "name": r[8],
                            "stage1": r[0],
                            "EF": round(r[9]["EF"], 4),
                            "EF_c15": round(r[9].get("EF_cost15", r[9]["EF"]), 4),
                            "E_N": round(r[9]["E_N"], 4),
                            "WR": round(r[9]["WR"], 4),
                            "n": r[9]["n_resolved"],
                            "sl": r[9]["sl_pts"],
                            "tp": r[9]["tp_pts"],
                            "bb": r[9].get("bb_dev"),
                            "blocked": r[9]["blocked_regime"],
                        }
                        for r in design[:12]
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
