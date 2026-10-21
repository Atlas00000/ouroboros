"""EURUSD ~6m EPG (EMA pullback) M15* geometry probe for chart preset design.

EPG edge family = trendfollow. Hard rules:
  - never emit TP < SL (RR_design >= 1.0)
  - mix functional WR + returns (prefer RR 1.20–1.35)
  - regime: EMA20/50 + H1 bias (native) + optional ATR max / session
Framework: docs/framework/unified_edge_framework.md Stage 0–1.
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
from app.analytics.regimes import MODEL_VERSION as REGIME_MODEL, regime_feature_frame
from app.config import get_settings
from app.db.session import get_session_factory

SYMBOL = "EURUSD"
POINT = 0.00001
COST_RT_POINTS = 20.0


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


def _ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()


def _atr_wilder(df: pd.DataFrame, n: int = 14) -> pd.Series:
    h, l, c = df["high"], df["low"], df["close"]
    prev_c = c.shift(1)
    tr = pd.concat([(h - l), (h - prev_c).abs(), (l - prev_c).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1.0 / n, adjust=False).mean()


def _probe_epg(
    m15: pd.DataFrame,
    h1: pd.DataFrame,
    *,
    sl_pts: float,
    tp_pts: float,
    level_atr: float = 0.5,
    session: tuple[int, int] | None = (12, 20),
    skip_tue: bool = True,
    atr_max_pts: float | None = 74.0,
    atr_min_pts: float | None = None,
    allow_long: bool = True,
    allow_short: bool = True,
    require_h1_trend_regime: bool = False,
    h1_regime: pd.DataFrame | None = None,
    cooldown_bars: int = 4,
    cost_rt_pts: float = COST_RT_POINTS,
) -> dict:
    """Closed-bar EPG L1 pullback: long EMA50-k*ATR when EMA20>EMA50 & H1 bull; fixed TP/SL."""
    g = m15.copy()
    g["ts"] = pd.to_datetime(g["ts"], utc=True)
    g["ema20"] = _ema(g["close"], 20)
    g["ema50"] = _ema(g["close"], 50)
    g["atr"] = _atr_wilder(g, 14)
    g["atr_pts"] = g["atr"] / POINT

    h = h1.copy()
    h["ts"] = pd.to_datetime(h["ts"], utc=True)
    h["h1_ema50"] = _ema(h["close"], 50)
    h = h[["ts", "close", "h1_ema50"]].rename(columns={"close": "h1_close"})
    g = pd.merge_asof(
        g.sort_values("ts"),
        h.sort_values("ts"),
        on="ts",
        direction="backward",
    )
    if require_h1_trend_regime and h1_regime is not None:
        hr = h1_regime.copy()
        hr["ts"] = pd.to_datetime(hr["ts"], utc=True)
        g = pd.merge_asof(
            g.sort_values("ts"),
            hr[["ts", "confirmed_regime"]].sort_values("ts"),
            on="ts",
            direction="backward",
        )

    wins = losses = blocked_regime = 0
    rrs: list[float] = []
    i = 60
    while i < len(g) - 40:
        row = g.iloc[i]
        if pd.isna(row["ema20"]) or pd.isna(row["ema50"]) or pd.isna(row["atr"]):
            i += 1
            continue
        if pd.isna(row.get("h1_ema50")) or pd.isna(row.get("h1_close")):
            i += 1
            continue
        ts = pd.to_datetime(row["ts"], utc=True)
        if skip_tue and int(ts.dayofweek) == 1:
            i += 1
            continue
        if session is not None:
            h0, h1b = session
            if not (h0 <= int(ts.hour) < h1b):
                i += 1
                continue
        atr_pts = float(row["atr_pts"])
        if atr_max_pts is not None and atr_pts > atr_max_pts:
            blocked_regime += 1
            i += 1
            continue
        if atr_min_pts is not None and atr_pts < atr_min_pts:
            blocked_regime += 1
            i += 1
            continue
        if require_h1_trend_regime:
            reg = str(row.get("confirmed_regime") or "")
            if reg not in ("trending_up", "trending_down"):
                blocked_regime += 1
                i += 1
                continue

        m15_bull = float(row["ema20"]) > float(row["ema50"])
        m15_bear = float(row["ema20"]) < float(row["ema50"])
        h1_bull = float(row["h1_close"]) > float(row["h1_ema50"])
        h1_bear = float(row["h1_close"]) < float(row["h1_ema50"])

        side = None
        atr = float(row["atr"])
        ema50 = float(row["ema50"])
        if allow_long and m15_bull and h1_bull:
            level = ema50 - level_atr * atr
            if float(row["close"]) <= level:
                side = "long"
        if side is None and allow_short and m15_bear and h1_bear:
            level = ema50 + level_atr * atr
            if float(row["close"]) >= level:
                side = "short"
        if side is None:
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
        i += max(1, int(cooldown_bars))
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
        "tp_lt_sl_blocked": int(sum(1 for x in rrs if x < 1.0)),
        "blocked_regime": blocked_regime,
        "sl_pts": sl_pts,
        "tp_pts": tp_pts,
        "level_atr": level_atr,
        "setups_armed": len(rrs),
    }


def main() -> int:
    get_settings.cache_clear()
    session = get_session_factory()()
    try:
        df_h1 = load_ohlcv(session, SYMBOL, "H1", lookback_days=220)
        df_m1 = load_ohlcv(session, SYMBOL, "M1", lookback_days=220)
        m15 = _resample_m15(df_m1)
        end = pd.to_datetime(m15["ts"].iloc[-1], utc=True)
        start = pd.Timestamp(year=end.year, month=end.month, day=1, tz="UTC") - pd.DateOffset(
            months=5
        )
        start = pd.Timestamp(year=start.year, month=start.month, day=1, tz="UTC")
        m15w = m15[(m15["ts"] >= start) & (m15["ts"] <= end)].reset_index(drop=True)
        h1w = df_h1.copy()
        h1w["ts"] = pd.to_datetime(h1w["ts"], utc=True)

        atr = _atr_wilder(m15w, 14)
        atr_pts = (atr / POINT).dropna()
        atr_stats = {
            "p25": float(atr_pts.quantile(0.25)),
            "p50": float(atr_pts.quantile(0.50)),
            "p75": float(atr_pts.quantile(0.75)),
            "p90": float(atr_pts.quantile(0.90)),
            "mean": float(atr_pts.mean()),
        }

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
            b = board_from_regimes(regimes, "trendfollow", window="calendar_month")
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
        overall = board_from_regimes(regimes_all, "trendfollow", window="30d")
        fit30 = board_from_ohlcv(df_h1, "trendfollow", timeframe="H1", window="30d")

        candidates: list[tuple[str, dict]] = []
        feat_h1_reg = feat_h1[["ts", "confirmed_regime"]].copy()

        def add(name: str, **kw) -> None:
            candidates.append((name, _probe_epg(m15w, h1w, **kw)))

        # Baseline shallow L1=0.5 grid (prior pass)
        for sl, rr in ((280, 1.25), (300, 1.25), (300, 1.30), (300, 1.50), (320, 1.25)):
            tp = max(sl, int(round(sl * rr / 5) * 5))
            add(f"L0.5_RR{rr:.2f}_sl{sl}_tp{tp}", sl_pts=sl, tp_pts=tp, atr_max_pts=None)
            add(
                f"L0.5_RR{rr:.2f}_sl{sl}_tp{tp}_atrMax74",
                sl_pts=sl,
                tp_pts=tp,
                atr_max_pts=74.0,
            )

        # Focused deep-pullback + session / MATCH-regime search (tip MISMATCH for TF)
        geos = [(280, 1.25), (300, 1.25), (300, 1.50), (250, 1.25)]
        levels = (0.5, 1.0, 1.5, 2.0)
        sessions = {
            "s12_20": (12, 20),
            "s08_16": (8, 16),
            "s13_21": (13, 21),
            "all": None,
        }
        for level in levels:
            for sl, rr in geos:
                tp = max(sl, int(round(sl * rr / 5) * 5))
                for sess_name, sess in sessions.items():
                    for atr_max in (None, 74.0):
                        atr_tag = "atrOff" if atr_max is None else f"atrMax{int(atr_max)}"
                        base = f"L{level:g}_RR{rr:.2f}_sl{sl}_tp{tp}_{sess_name}_{atr_tag}"
                        kw = dict(
                            sl_pts=sl,
                            tp_pts=tp,
                            level_atr=level,
                            session=sess,
                            skip_tue=(sess is not None),
                            atr_max_pts=atr_max,
                        )
                        add(base, **kw)
                        add(
                            base + "_matchReg",
                            **kw,
                            require_h1_trend_regime=True,
                            h1_regime=feat_h1_reg,
                        )
                        # Side sleeves only on London/NY + ATR gate (keep grid tractable)
                        if sess_name == "s12_20" and atr_max == 74.0:
                            add(base + "_longOnly", **kw, allow_short=False)
                            add(base + "_shortOnly", **kw, allow_long=False)

        # Explicit P0 chart candidates (shallow + deep)
        add("P0_L0.5_RR1.25_sl300_tp375_atrMax74", sl_pts=300, tp_pts=375, atr_max_pts=74.0)
        add("P0_L1.5_RR1.25_sl300_tp375_atrMax74", sl_pts=300, tp_pts=375, level_atr=1.5, atr_max_pts=74.0)
        add("P0_L2.0_RR1.25_sl300_tp375_atrMax74", sl_pts=300, tp_pts=375, level_atr=2.0, atr_max_pts=74.0)
        add(
            "P0_L1.5_RR1.25_sl300_tp375_atrMax74_matchReg",
            sl_pts=300,
            tp_pts=375,
            level_atr=1.5,
            atr_max_pts=74.0,
            require_h1_trend_regime=True,
            h1_regime=feat_h1_reg,
        )
        add(
            "P0_L1.0_RR1.25_sl280_tp350_s08_16_atrMax74",
            sl_pts=280,
            tp_pts=350,
            level_atr=1.0,
            session=(8, 16),
            atr_max_pts=74.0,
        )

        probes = {n: p for n, p in candidates}
        ranked = []
        for name, p in probes.items():
            n_floor = 25 if float(p.get("level_atr") or 0.5) >= 1.0 else 30
            design_ok = (
                p["n_resolved"] >= n_floor
                and p["RR_design"] + 1e-12 >= 1.0
                and p["E_N"] > 0
                and p["WR"] > p["BWR"]
                and p["tp_lt_sl_blocked"] == 0
            )
            stage1_ok = design_ok and p["EF"] > 0
            rr_pref = 1.0 if 1.2 <= p["RR_design"] <= 1.35 else 0.0
            harvest_pen = 0.0 if abs(p["RR_design"] - 1.0) < 1e-9 else 1.0
            regime_pref = 1.0 if (
                ("atrMax" in name or "matchReg" in name) and p.get("blocked_regime", 0) > 0
            ) else 0.0
            p0_pref = 1.0 if name.startswith("P0_") else 0.0
            both_sides = 1.0 if ("longOnly" not in name and "shortOnly" not in name) else 0.0
            ranked.append(
                (
                    stage1_ok,
                    design_ok,
                    p0_pref,
                    rr_pref,
                    harvest_pen,
                    regime_pref,
                    both_sides,
                    p["EF"],
                    p["E_N"],
                    p["n_resolved"],
                    name,
                    p,
                )
            )
        ranked.sort(
            key=lambda t: (t[0], t[1], t[2], t[3], t[4], t[5], t[6], t[7], t[8], t[9]),
            reverse=True,
        )
        best_name = ranked[0][10] if ranked else None
        best = probes.get(best_name) if best_name else None

        summary = {
            n: {
                "n": p["n_resolved"],
                "WR": round(p["WR"], 4),
                "RR": round(p["RR_design"], 3),
                "E_N": round(p["E_N"], 4),
                "EF": round(p["EF"], 4),
                "BM": round(p["BM"], 4),
                "blocked": p["blocked_regime"],
                "sl": p["sl_pts"],
                "tp": p["tp_pts"],
                "L": p.get("level_atr"),
            }
            for n, p in probes.items()
        }

        out = {
            "symbol": SYMBOL,
            "ea": "EPG",
            "family": "trendfollow",
            "tf_probe": "M15*",
            "generated_at": datetime.now(UTC).isoformat(),
            "window": {"start": str(start), "end": str(end)},
            "models": {"regime": REGIME_MODEL, "fit": FIT_MODEL},
            "atr_m15_points": atr_stats,
            "monthly_trendfollow_h1": monthly,
            "overall_trendfollow_h1": {
                "tag": overall.tag,
                "shares": overall.shares,
                "regime_shares": overall.regime_shares,
                "bars": overall.bar_count,
            },
            "fit_30d_h1_trendfollow": {"tag": fit30.tag, "shares": fit30.shares},
            "probes": probes,
            "probe_summary": summary,
            "recommended_probe": best_name,
            "recommended": best,
            "hard_rule": "never emit TP < SL (RR_design >= 1.0)",
            "framework_note": (
                "E_N=WR*(R+1)-1; BWR=1/(1+R); BM=WR-BWR; Leak=c_R/(R+1); EF=BM-Leak. "
                "EPG L1 pullback probe; R≈RR on FIXED_RR. RESEARCH / UNTESTED."
            ),
        }

        dest = Path(__file__).resolve().parents[2] / "research" / "assets" / "EURUSD"
        dest.mkdir(parents=True, exist_ok=True)
        path = dest / "epg_m15_6m_audit.json"
        path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")

        design = [r for r in ranked if r[1]]
        print(
            json.dumps(
                {
                    "wrote": str(path),
                    "window": out["window"],
                    "atr_m15_pts": {k: round(v, 1) for k, v in atr_stats.items()},
                    "recommended": best_name,
                    "recommended_metrics": summary.get(best_name),
                    "design_positive_count": len(design),
                    "top_design": [
                        {
                            "name": r[10],
                            "stage1": r[0],
                            "EF": round(r[11]["EF"], 4),
                            "E_N": round(r[11]["E_N"], 4),
                            "WR": round(r[11]["WR"], 4),
                            "n": r[11]["n_resolved"],
                            "sl": r[11]["sl_pts"],
                            "tp": r[11]["tp_pts"],
                            "L": r[11].get("level_atr"),
                        }
                        for r in design[:10]
                    ],
                    "top_near": [
                        {
                            "name": r[10],
                            "EF": round(r[11]["EF"], 4),
                            "E_N": round(r[11]["E_N"], 4),
                            "WR": round(r[11]["WR"], 4),
                            "BWR": round(r[11]["BWR"], 4),
                            "n": r[11]["n_resolved"],
                            "sl": r[11]["sl_pts"],
                            "tp": r[11]["tp_pts"],
                            "L": r[11].get("level_atr"),
                        }
                        for r in ranked[:15]
                    ],
                    "monthly_tf": [
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
