"""TSLA ~6m regime + BMRG M15* geometry probe for chart preset design.

Hard rules:
  - never emit TP < SL (RR_design >= 1.0)
  - target mix of functional WR and returns (not Harvest-only, not lottery RR)
  - regime filters when they protect EF without starving fire-count
Framework: docs/framework/unified_edge_framework.md Stage 0–1 identities.

YWO MT5 ticker: Tesla (equity CFD Digits=2 → Point=0.01).
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

SYMBOL = "TSLA"
# Equity CFD Digits=2 → Point=0.01 (YWO Tesla)
POINT = 0.01
# Round-trip cost prior in points (Tesla CFD: wider than MSFT; replace with blotter)
COST_RT_POINTS = 80.0
# US cash RTH approx during EDT (broker server often GMT+2/+3 — verify)
SESSION_US_RTH = (14, 20)


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


def _probe_fixed_rr(
    g: pd.DataFrame,
    *,
    bb_dev: float,
    sl_pts: float,
    tp_pts: float,
    point: float = POINT,
    session: tuple[int, int] | None = SESSION_US_RTH,
    skip_tue: bool = True,
    atr_max_pts: float | None = None,
    atr_min_pts: float | None = None,
    bb_width_max_pct: float | None = None,
    bb_width_min_pct: float | None = None,
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
        if bb_width_min_pct is not None and bbw < bb_width_min_pct:
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
        for j in range(i + 1, min(i + 1 + 96, len(g))):
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
    }


def main() -> int:
    get_settings.cache_clear()
    session = get_session_factory()()
    try:
        df_h1 = load_ohlcv(session, SYMBOL, "H1", lookback_days=220)
        df_m1 = load_ohlcv(session, SYMBOL, "M1", lookback_days=220)
        if df_m1.empty or df_h1.empty:
            raise SystemExit(f"{SYMBOL}: empty M1/H1 — backfill before audit")
        m15 = _resample_m15(df_m1)
        end = pd.to_datetime(m15["ts"].iloc[-1], utc=True)
        # Requested 6m; clamp start to first available bar month
        start_req = pd.Timestamp(year=end.year, month=end.month, day=1, tz="UTC") - pd.DateOffset(
            months=5
        )
        start_req = pd.Timestamp(year=start_req.year, month=start_req.month, day=1, tz="UTC")
        data_start = pd.to_datetime(m15["ts"].iloc[0], utc=True)
        start = max(start_req, data_start.replace(day=1, hour=0, minute=0, second=0, microsecond=0))

        m15w = m15[(m15["ts"] >= start) & (m15["ts"] <= end)].reset_index(drop=True)
        atr = _atr_wilder(m15w, 14)
        atr_pts = (atr / POINT).dropna()
        atr_stats = {
            "p25": float(atr_pts.quantile(0.25)),
            "p50": float(atr_pts.quantile(0.50)),
            "p75": float(atr_pts.quantile(0.75)),
            "p90": float(atr_pts.quantile(0.90)),
            "mean": float(atr_pts.mean()),
        }
        # Structural SL ≈ 1.5–2.0× median ATR (equity M15 — not token)
        sl_base = int(round(atr_stats["p50"] * 1.6 / 10.0) * 10)
        sl_base = max(sl_base, 80)
        atr_cap = float(atr_stats["p75"])
        atr_cap_p90 = float(atr_stats["p90"])
        atr_floor = float(max(20.0, atr_stats["p25"] * 0.6))

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
            bb = float(kw.pop("bb_dev", 2.2))
            candidates.append((name, _probe_fixed_rr(m15w, bb_dev=bb, **kw)))

        # Equity SL grid around ATR-scaled base (TSLA high-vol: include 500–1200)
        eq_sls = sorted(
            {
                sl_base,
                int(round(sl_base * 1.25 / 10) * 10),
                int(round(sl_base * 0.85 / 10) * 10),
                int(round(atr_stats["p50"] * 1.2 / 10) * 10),
                int(round(atr_stats["p50"] * 2.0 / 10) * 10),
                int(round(atr_stats["p50"] * 2.5 / 10) * 10),
                int(round(atr_stats["p50"] * 3.0 / 10) * 10),
                int(round(atr_stats["p50"] * 3.5 / 10) * 10),
                200,
                300,
                400,
                500,
                600,
                700,
                800,
                900,
                1000,
                1200,
            }
        )
        for sl in eq_sls:
            sl = int(round(sl / 10) * 10)
            if sl < 80:
                continue
            tp125 = max(sl, int(round(sl * 1.25 / 10) * 10))
            tp150 = max(sl, int(round(sl * 1.5 / 10) * 10))
            tp100 = sl
            for bb in (2.2, 2.5):
                tag = f"bb{bb}"
                add(
                    f"balanced_RR1.25_sl{sl}_tp{tp125}_{tag}",
                    sl_pts=sl,
                    tp_pts=tp125,
                    bb_dev=bb,
                )
                add(
                    f"growth_RR1.5_sl{sl}_tp{tp150}_{tag}",
                    sl_pts=sl,
                    tp_pts=tp150,
                    bb_dev=bb,
                )
                add(
                    f"harvest_RR1.0_sl{sl}_tp{tp100}_{tag}",
                    sl_pts=sl,
                    tp_pts=tp100,
                    bb_dev=bb,
                )
                for cap, ctag in ((atr_cap, "p75"), (atr_cap_p90, "p90")):
                    add(
                        f"balanced_RR1.25_sl{sl}_tp{tp125}_{tag}_atrMax{int(cap)}_{ctag}",
                        sl_pts=sl,
                        tp_pts=tp125,
                        atr_max_pts=cap,
                        atr_min_pts=atr_floor,
                        bb_dev=bb,
                    )
                    add(
                        f"growth_RR1.5_sl{sl}_tp{tp150}_{tag}_atrMax{int(cap)}_{ctag}",
                        sl_pts=sl,
                        tp_pts=tp150,
                        atr_max_pts=cap,
                        atr_min_pts=atr_floor,
                        bb_dev=bb,
                    )
                # ATR + BB-width sleeve (META-style light + tighter alt)
                add(
                    f"balanced_RR1.25_sl{sl}_tp{tp125}_{tag}_atrBBW",
                    sl_pts=sl,
                    tp_pts=tp125,
                    atr_max_pts=atr_cap_p90,
                    atr_min_pts=atr_floor,
                    bb_width_min_pct=0.30,
                    bb_width_max_pct=2.50,
                    bb_dev=bb,
                )
                add(
                    f"growth_RR1.5_sl{sl}_tp{tp150}_{tag}_atrBBW",
                    sl_pts=sl,
                    tp_pts=tp150,
                    atr_max_pts=atr_cap_p90,
                    atr_min_pts=atr_floor,
                    bb_width_min_pct=0.30,
                    bb_width_max_pct=2.50,
                    bb_dev=bb,
                )
                add(
                    f"harvest_RR1.0_sl{sl}_tp{tp100}_{tag}_atrBBW",
                    sl_pts=sl,
                    tp_pts=tp100,
                    atr_max_pts=atr_cap_p90,
                    atr_min_pts=atr_floor,
                    bb_width_min_pct=0.30,
                    bb_width_max_pct=2.50,
                    bb_dev=bb,
                )
                add(
                    f"balanced_RR1.25_sl{sl}_tp{tp125}_{tag}_atrBBW_tight",
                    sl_pts=sl,
                    tp_pts=tp125,
                    atr_max_pts=atr_cap,
                    atr_min_pts=atr_floor,
                    bb_width_min_pct=0.40,
                    bb_width_max_pct=1.80,
                    bb_dev=bb,
                )

        # Session ablations on base balanced
        sl = sl_base
        tp = max(sl, int(round(sl * 1.25 / 10) * 10))
        add(
            f"balanced_RR1.25_sl{sl}_tp{tp}_bb2.2_noSession",
            sl_pts=sl,
            tp_pts=tp,
            session=None,
            skip_tue=False,
        )
        add(
            f"balanced_RR1.25_sl{sl}_tp{tp}_bb2.2_atrMax_noSession",
            sl_pts=sl,
            tp_pts=tp,
            atr_max_pts=atr_cap,
            atr_min_pts=atr_floor,
            session=None,
            skip_tue=False,
        )
        # London/NY overlap alt (12–20) vs US RTH (14–20)
        add(
            f"balanced_RR1.25_sl{sl}_tp{tp}_bb2.2_sess12_20",
            sl_pts=sl,
            tp_pts=tp,
            session=(12, 20),
        )
        add(
            f"balanced_RR1.25_sl{sl}_tp{tp}_bb2.2_atrMax_sess12_20",
            sl_pts=sl,
            tp_pts=tp,
            atr_max_pts=atr_cap,
            atr_min_pts=atr_floor,
            session=(12, 20),
        )

        probes = {name: p for name, p in candidates}

        # Full ~6m equity tip: n>=40 design prior (majors band)
        min_n = 40
        ranked = []
        for name, p in probes.items():
            ok = (
                p["n_resolved"] >= min_n
                and p["RR_design"] + 1e-12 >= 1.0
                and p["E_N"] > 0
                and p["EF"] > 0
                and p["WR"] > p["BWR"]
                and p["tp_lt_sl_blocked"] == 0
            )
            rr_pref = 1.0 if 1.2 <= p["RR_design"] <= 1.35 else (
                0.5 if 1.35 < p["RR_design"] <= 1.55 else 0.0
            )
            regime_pref = (
                1.0
                if p.get("blocked_regime", 0) > 0
                and ("atrMax" in name or "atrBBW" in name)
                else 0.0
            )
            ranked.append(
                (ok, rr_pref, regime_pref, p["EF"], p["E_N"], p["n_resolved"], name, p)
            )
        ranked.sort(
            key=lambda t: (t[0], t[1], t[2], t[3], t[4], t[5]), reverse=True
        )
        best_name = ranked[0][6] if ranked else None
        best = probes[best_name] if best_name else None

        summary = {}
        for name, p in probes.items():
            summary[name] = {
                "n": p["n_resolved"],
                "WR": round(p["WR"], 4),
                "RR": round(p["RR_design"], 3),
                "E_N": round(p["E_N"], 4),
                "EF": round(p["EF"], 4),
                "BM": round(p["BM"], 4),
                "Leak": round(p["Leak"], 4),
                "blocked_regime": p["blocked_regime"],
                "sl": p["sl_pts"],
                "tp": p["tp_pts"],
                "bb_dev": p["bb_dev"],
            }

        out = {
            "symbol": SYMBOL,
            "mt5_ticker": "Tesla",
            "tf_probe": "M15*",
            "point": POINT,
            "cost_rt_points_prior": COST_RT_POINTS,
            "generated_at": datetime.now(UTC).isoformat(),
            "window": {
                "start": str(start),
                "end": str(end),
                "requested_start": str(start_req),
                "depth_note": "YWO Tesla M1 covers requested ~6m window",
            },
            "models": {"regime": REGIME_MODEL, "fit": FIT_MODEL},
            "atr_m15_points": atr_stats,
            "sl_base_from_atr_p50": sl_base,
            "atr_cap_p75": atr_cap,
            "atr_cap_p90": atr_cap_p90,
            "atr_floor": atr_floor,
            "session_default_utc": list(SESSION_US_RTH),
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
            "min_n_design": min_n,
            "hard_rule": "never emit TP < SL (RR_design >= 1.0)",
            "framework_note": (
                "E_N=WR*(R+1)-1; BWR=1/(1+R); BM=WR-BWR; Leak=c_R/(R+1); EF=BM-Leak. "
                "Probe R assumed ≈ RR on FIXED_RR. RESEARCH / UNTESTED design prior."
            ),
        }

        repo = Path(__file__).resolve().parents[2]
        dest = repo / "research" / "assets" / "TSLA"
        dest.mkdir(parents=True, exist_ok=True)
        path = dest / "bmrg_m15_6m_audit.json"
        path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")

        viable = [r for r in ranked if r[0]]
        print(
            json.dumps(
                {
                    "wrote": str(path),
                    "window": out["window"],
                    "atr_m15_pts": {k: round(v, 1) for k, v in atr_stats.items()},
                    "sl_base": sl_base,
                    "recommended": best_name,
                    "recommended_metrics": summary.get(best_name),
                    "viable_count": len(viable),
                    "top_viable": [
                        {
                            "name": r[6],
                            "EF": round(r[7]["EF"], 4),
                            "E_N": round(r[7]["E_N"], 4),
                            "WR": round(r[7]["WR"], 4),
                            "n": r[7]["n_resolved"],
                            "sl": r[7]["sl_pts"],
                            "tp": r[7]["tp_pts"],
                            "bb": r[7]["bb_dev"],
                            "blocked": r[7]["blocked_regime"],
                        }
                        for r in viable[:12]
                    ],
                    "top_overall": [
                        {
                            "name": r[6],
                            "ok": r[0],
                            "EF": round(r[7]["EF"], 4),
                            "E_N": round(r[7]["E_N"], 4),
                            "WR": round(r[7]["WR"], 4),
                            "n": r[7]["n_resolved"],
                            "sl": r[7]["sl_pts"],
                            "tp": r[7]["tp_pts"],
                        }
                        for r in ranked[:15]
                    ],
                    "monthly": [
                        {
                            "m": m["month"],
                            "tag": m["tag"],
                            "MATCH": round(100 * m["shares"].get("MATCH", 0), 1),
                            "MISMATCH": round(100 * m["shares"].get("MISMATCH", 0), 1),
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
