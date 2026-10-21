"""UK100 ~6m regime + BMRG M5* geometry probe for chart preset design.

Hard rules:
  - never emit TP < SL (RR_design >= 1.0)
  - target mix of functional WR and returns (not Harvest-only, not lottery RR)
  - regime filters when they protect EF without starving fire-count
Framework: docs/framework/unified_edge_framework.md Stage 0–1 identities.

YWO MT5 UK100: Digits=2 · Point=0.01 · spread≈140 · volume_min=0.1
Broker history tip from ~2025-12-17 (~10m); probe uses last ~6 calendar months.
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

SYMBOL = "UK100"
# YWO UK100 index CFD: Digits=2 → Point=0.01
POINT = 0.01
# Round-trip cost prior ≈ spread(140) + slip; replace with blotter later
COST_RT_POINTS = 160.0
# London cash / early NY (broker server often GMT+2/+3 — verify in Tester)
SESSION_LONDON = (8, 17)
SESSION_LONDON_NY = (8, 20)


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


def _feat_frame(g: pd.DataFrame, bb_dev: float, point: float = POINT) -> pd.DataFrame:
    """Precompute BB / ATR columns once per bb_dev."""
    upper, mid, lower = _bb(g["close"], 20, bb_dev)
    atr = _atr_wilder(g, 14)
    out = g.copy()
    out["upper"], out["mid"], out["lower"] = upper, mid, lower
    out["atr"] = atr
    out["atr_pts"] = atr / point
    out["bb_width_pct"] = 100.0 * (upper - lower) / mid.abs()
    out["hour"] = pd.to_datetime(out["ts"], utc=True).dt.hour
    out["dow"] = pd.to_datetime(out["ts"], utc=True).dt.dayofweek
    return out


def _probe_fixed_rr(
    g: pd.DataFrame,
    *,
    bb_dev: float | None = None,
    sl_pts: float,
    tp_pts: float,
    point: float = POINT,
    session: tuple[int, int] | None = SESSION_LONDON,
    skip_tue: bool = True,
    atr_max_pts: float | None = None,
    atr_min_pts: float | None = None,
    bb_width_max_pct: float | None = None,
    cost_rt_pts: float = COST_RT_POINTS,
    precomputed: bool = False,
) -> dict:
    """Closed-bar fade probe: long <= lower, short >= upper; fixed TP/SL points.

    Pass ``precomputed=True`` when ``g`` already has upper/mid/lower/atr_pts/hour/dow.
    """
    if not precomputed:
        if bb_dev is None:
            raise ValueError("bb_dev required when not precomputed")
        g = _feat_frame(g, bb_dev, point)

    # numpy views — M5 density makes iloc loops too slow
    open_ = g["open"].to_numpy(dtype=float)
    high = g["high"].to_numpy(dtype=float)
    low = g["low"].to_numpy(dtype=float)
    close = g["close"].to_numpy(dtype=float)
    upper = g["upper"].to_numpy(dtype=float)
    lower = g["lower"].to_numpy(dtype=float)
    atr_pts_a = g["atr_pts"].to_numpy(dtype=float)
    bbw_a = g["bb_width_pct"].to_numpy(dtype=float)
    hour = g["hour"].to_numpy(dtype=int)
    dow = g["dow"].to_numpy(dtype=int)
    n_bars = len(g)

    wins = losses = 0
    blocked_regime = 0
    rrs: list[float] = []
    i = 25
    horizon = 144  # ~12h on M5
    cooldown = 6
    while i < n_bars - 40:
        if not np.isfinite(upper[i]) or not np.isfinite(lower[i]) or not np.isfinite(
            atr_pts_a[i]
        ):
            i += 1
            continue
        if skip_tue and int(dow[i]) == 1:
            i += 1
            continue
        if session is not None:
            h0, h1 = session
            if not (h0 <= int(hour[i]) < h1):
                i += 1
                continue

        ap = float(atr_pts_a[i])
        bbw = float(bbw_a[i])
        if atr_min_pts is not None and ap < atr_min_pts:
            blocked_regime += 1
            i += 1
            continue
        if atr_max_pts is not None and ap > atr_max_pts:
            blocked_regime += 1
            i += 1
            continue
        if bb_width_max_pct is not None and bbw > bb_width_max_pct:
            blocked_regime += 1
            i += 1
            continue

        if close[i] <= lower[i]:
            side = 1  # long
        elif close[i] >= upper[i]:
            side = -1  # short
        else:
            i += 1
            continue

        entry = float(open_[i + 1])
        sl_dist = sl_pts * point
        tp_dist = tp_pts * point
        design_rr = tp_dist / sl_dist if sl_dist > 0 else 0.0
        rrs.append(design_rr)
        if design_rr < 1.0 - 1e-12:
            i += 2
            continue

        if side == 1:
            sl_px = entry - sl_dist
            tp_px = entry + tp_dist
        else:
            sl_px = entry + sl_dist
            tp_px = entry - tp_dist

        outcome = None
        j_end = min(i + 1 + horizon, n_bars)
        for j in range(i + 1, j_end):
            hi = high[j]
            lo = low[j]
            if side == 1:
                hit_sl = lo <= sl_px
                hit_tp = hi >= tp_px
            else:
                hit_sl = hi >= sl_px
                hit_tp = lo <= tp_px
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
        i += cooldown
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
    }


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
        print(
            f"UK100 M5* window {start.date()}→{end.date()} bars={len(m5w)}",
            flush=True,
        )
        atr = _atr_wilder(m5w, 14)
        atr_pts = (atr / POINT).dropna()
        atr_stats = {
            "p25": float(atr_pts.quantile(0.25)),
            "p50": float(atr_pts.quantile(0.50)),
            "p75": float(atr_pts.quantile(0.75)),
            "p90": float(atr_pts.quantile(0.90)),
            "mean": float(atr_pts.mean()),
        }
        # Structural SL ≈ ~1.25–2.0× median M5 ATR; floor clears spread Leak
        # Cost prior ~160 pts → prefer SL ≥ ~1000 so Leak stays modest
        sl_base = int(round(atr_stats["p50"] * 1.5 / 10.0) * 10)
        sl_base = max(sl_base, 1000)  # floor: ≥6× cost prior for index spread on M5
        atr_cap = float(atr_stats["p75"])  # cut high-vol FRAGILE sleeve
        atr_cap_p90 = float(atr_stats["p90"])

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

        # Geometry grid — lean set, all enforce TP >= SL; features precomputed once
        feat22 = _feat_frame(m5w, 2.2)
        feat24 = _feat_frame(m5w, 2.4)
        candidates: list[tuple[str, dict]] = []

        def add(name: str, feat: pd.DataFrame, **kw) -> None:
            candidates.append(
                (name, _probe_fixed_rr(feat, precomputed=True, **kw))
            )

        # Focused SL ladder around ~1.5–2.5× M5 ATR p50 (spread-aware floor 1000)
        p50 = atr_stats["p50"]
        idx_sls = sorted(
            {
                sl_base,
                int(round(p50 * 1.5 / 10) * 10),
                int(round(p50 * 2.0 / 10) * 10),
                int(round(p50 * 2.5 / 10) * 10),
                1200,
                1500,
                1800,
                2000,
            }
        )
        for sl in idx_sls:
            sl = int(round(sl / 10) * 10)
            if sl < 1000:
                continue
            tp125 = max(sl, int(round(sl * 1.25 / 5) * 5))  # exact-ish RR 1.25
            tp150 = max(sl, int(round(sl * 1.5 / 5) * 5))
            tp100 = sl
            add(f"balanced_RR1.25_sl{sl}_tp{tp125}", feat22, sl_pts=sl, tp_pts=tp125)
            add(f"growth_RR1.5_sl{sl}_tp{tp150}", feat22, sl_pts=sl, tp_pts=tp150)
            add(f"harvest_RR1.0_sl{sl}_tp{tp100}", feat22, sl_pts=sl, tp_pts=tp100)
            add(
                f"balanced_RR1.25_sl{sl}_tp{tp125}_atrMax{int(atr_cap)}_p75",
                feat22,
                sl_pts=sl,
                tp_pts=tp125,
                atr_max_pts=atr_cap,
            )
            add(
                f"growth_RR1.5_sl{sl}_tp{tp150}_atrMax{int(atr_cap)}_p75",
                feat22,
                sl_pts=sl,
                tp_pts=tp150,
                atr_max_pts=atr_cap,
            )

        # Session / selectivity ablations on sl_base balanced
        sl = sl_base
        tp = max(sl, int(round(sl * 1.25 / 5) * 5))
        add(
            f"balanced_RR1.25_sl{sl}_tp{tp}_noSession",
            feat22,
            sl_pts=sl,
            tp_pts=tp,
            session=None,
            skip_tue=False,
        )
        add(
            f"balanced_RR1.25_sl{sl}_tp{tp}_atrMax_noSession",
            feat22,
            sl_pts=sl,
            tp_pts=tp,
            atr_max_pts=atr_cap,
            session=None,
            skip_tue=False,
        )
        add(
            f"balanced_RR1.25_sl{sl}_tp{tp}_atrMax_sess08_20",
            feat22,
            sl_pts=sl,
            tp_pts=tp,
            atr_max_pts=atr_cap,
            session=SESSION_LONDON_NY,
        )
        add(
            f"balanced_RR1.25_sl{sl}_tp{tp}_atrMax_bbwMax1p2",
            feat22,
            sl_pts=sl,
            tp_pts=tp,
            atr_max_pts=atr_cap,
            bb_width_max_pct=1.2,
        )
        add(
            f"balanced_RR1.25_sl{sl}_tp{tp}_bb2.4_atrMax{int(atr_cap)}",
            feat24,
            sl_pts=sl,
            tp_pts=tp,
            atr_max_pts=atr_cap,
        )
        # p90 ATR cap alt on best-scale balanced
        add(
            f"balanced_RR1.25_sl{sl}_tp{tp}_atrMax{int(atr_cap_p90)}_p90",
            feat22,
            sl_pts=sl,
            tp_pts=tp,
            atr_max_pts=atr_cap_p90,
        )

        probes = {name: p for name, p in candidates}

        # Rank: design-viable first, then EF, E_N, n
        # M5 denser sample — prefer n>=50, RR>=1, E_N>0, EF>0, WR>BWR
        ranked = []
        for name, p in probes.items():
            ok = (
                p["n_resolved"] >= 50
                and p["RR_design"] + 1e-12 >= 1.0
                and p["E_N"] > 0
                and p["EF"] > 0
                and p["WR"] > p["BWR"]
                and p["tp_lt_sl_blocked"] == 0
            )
            # Prefer balanced RR ~1.25 slightly over harvest/growth for mix target
            rr_pref = 1.0 if 1.2 <= p["RR_design"] <= 1.35 else 0.0
            # Prefer regime-gated sleeves when they fire
            regime_pref = (
                1.0 if p.get("blocked_regime", 0) > 0 and "atrMax" in name else 0.0
            )
            ranked.append(
                (ok, rr_pref, regime_pref, p["EF"], p["E_N"], p["n_resolved"], name, p)
            )
        ranked.sort(
            key=lambda t: (t[0], t[1], t[2], t[3], t[4], t[5]), reverse=True
        )
        best_name = ranked[0][6] if ranked else None
        best = probes[best_name] if best_name else None

        # Compact probe summary for console
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
            }

        out = {
            "symbol": SYMBOL,
            "tf_probe": "M5*",
            "point": POINT,
            "cost_rt_points_prior": COST_RT_POINTS,
            "broker": {
                "digits": 2,
                "point": POINT,
                "spread_pts_now": 140,
                "volume_min": 0.1,
            },
            "session_default": list(SESSION_LONDON),
            "generated_at": datetime.now(UTC).isoformat(),
            "window": {"start": str(start), "end": str(end)},
            "models": {"regime": REGIME_MODEL, "fit": FIT_MODEL},
            "atr_m5_points": atr_stats,
            "sl_base_from_atr_p50": sl_base,
            "atr_cap_p75": atr_cap,
            "atr_cap_p90": atr_cap_p90,
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
                "Probe R assumed ≈ RR on FIXED_RR. RESEARCH / UNTESTED design prior."
            ),
        }

        repo = Path(__file__).resolve().parents[2]
        dest = repo / "research" / "assets" / "UK100"
        dest.mkdir(parents=True, exist_ok=True)
        path = dest / "bmrg_m5_6m_audit.json"
        path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")

        # Top viable + top 8 overall
        viable = [r for r in ranked if r[0]]
        print(
            json.dumps(
                {
                    "wrote": str(path),
                    "window": out["window"],
                    "atr_m5_pts": {k: round(v, 1) for k, v in atr_stats.items()},
                    "sl_base": sl_base,
                    "atr_cap_p75": round(atr_cap, 1),
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
                            "blocked": r[7]["blocked_regime"],
                        }
                        for r in viable[:10]
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
                        for r in ranked[:8]
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
