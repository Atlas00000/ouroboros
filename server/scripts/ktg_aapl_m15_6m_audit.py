"""AAPL ~6m regime + KTG M15* geometry probe for chart preset design.

KTG = Keltner Trend Grid (trendfollow / expansion pyramid).
Hard rules:
  - never emit DesignedRR < 1.0 (TP >= SL by design)
  - target mix of functional WR and returns (Balanced sleeve)
  - regime filters when they protect EF without starving fire-count
Framework: docs/framework/unified_edge_framework.md Stage 0–1.
"""

from __future__ import annotations

import calendar
import json
from pathlib import Path

import numpy as np
import pandas as pd

from app.analytics.bars import load_ohlcv
from app.analytics.fit.boards import board_from_regimes
from app.analytics.fit.mapper import MODEL_VERSION as FIT_MODEL
from app.analytics.regimes import MODEL_VERSION as REGIME_MODEL, regime_feature_frame
from app.config import get_settings
from app.db.session import get_session_factory

SYMBOL = "AAPL"
# YWO Apple: Digits=2 → Point=0.01
POINT = 0.01
# Round-trip prior in points (from BMRG Apple blotter ~20–30 median)
COST_RT_POINTS = 25.0


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


def _er(closes: np.ndarray, period: int) -> float:
    if len(closes) < period + 1:
        return 0.0
    change = abs(closes[-1] - closes[-(period + 1)])
    path = float(np.abs(np.diff(closes[-(period + 1) :])).sum())
    return float(change / path) if path > 0 else 0.0


def _atr_pctile(atrs: np.ndarray, cur: float) -> float:
    if len(atrs) == 0:
        return 50.0
    return 100.0 * float(np.sum(atrs <= cur)) / float(len(atrs))


def _probe_ktg(
    g: pd.DataFrame,
    *,
    max_legs: int = 3,
    mults: tuple[float, ...] = (1.0, 1.5, 2.0, 2.5, 3.0),
    trail_atr: float = 1.5,
    one_r_atr: float = 1.5,
    designed_rr: float = 1.5,
    mae_abort_r: float = 0.75,
    min_break_atr: float = 1.5,
    er_period: int = 50,
    er_trend: float = 0.40,
    atr_pctile_n: int = 20,
    require_trend: bool = True,
    deny_vol_high: bool = True,
    session_hours: tuple[int, int] | None = (14, 20),  # US RTH approx UTC
    deny_asia: bool = True,
    cooldown_bars: int = 3,
    cost_rt_pts: float = COST_RT_POINTS,
) -> dict:
    """Closed-bar KTG-01 probe: L1 breakout → pyramid adds → ATR trail / MAE abort."""
    assert designed_rr >= 1.0 - 1e-12, "HARD RULE: DesignedRR >= 1.0"

    ema = _ema(g["close"], 20)
    atr = _atr_wilder(g, 14)
    close = g["close"].to_numpy(dtype=float)
    high = g["high"].to_numpy(dtype=float)
    low = g["low"].to_numpy(dtype=float)
    ts = pd.to_datetime(g["ts"], utc=True)
    ema_a = ema.to_numpy(dtype=float)
    atr_a = atr.to_numpy(dtype=float)

    wins = losses = 0
    sum_r = 0.0
    rs: list[float] = []
    blocked_regime = blocked_session = blocked_break = 0
    n_cycles = 0

    i = max(er_period + 5, 60)
    cooldown_until = -1

    while i < len(g) - 5:
        if i < cooldown_until:
            i += 1
            continue
        if np.isnan(ema_a[i]) or np.isnan(atr_a[i]) or atr_a[i] <= 0:
            i += 1
            continue

        t = ts.iloc[i]
        hour = int(t.hour)
        if deny_asia and hour < 7:
            blocked_session += 1
            i += 1
            continue
        if session_hours is not None:
            h0, h1 = session_hours
            if not (h0 <= hour < h1):
                blocked_session += 1
                i += 1
                continue

        er = _er(close[: i + 1], er_period)
        is_trend = er >= er_trend
        if require_trend and not is_trend:
            blocked_regime += 1
            i += 1
            continue

        atr_win = atr_a[max(0, i - atr_pctile_n + 1) : i + 1]
        atr_win = atr_win[~np.isnan(atr_win)]
        pct = _atr_pctile(atr_win, float(atr_a[i]))
        if deny_vol_high and pct > 66.0:
            blocked_regime += 1
            i += 1
            continue

        e0 = float(ema_a[i])
        a0 = float(atr_a[i])
        c0 = float(close[i])
        break_atr = abs(c0 - e0) / a0
        if min_break_atr > 0 and break_atr < min_break_atr:
            blocked_break += 1
            i += 1
            continue

        direction = 0
        if c0 >= e0 + mults[0] * a0:
            direction = 1
        elif c0 <= e0 - mults[0] * a0:
            direction = -1
        else:
            i += 1
            continue

        # Cycle start at next bar open (approx fill)
        entry_i = i + 1
        if entry_i >= len(g):
            break
        fill = float(g.iloc[entry_i]["open"])
        one_r = one_r_atr * a0
        if one_r <= 0:
            i += 1
            continue

        legs = 1
        next_level = 2
        extreme = fill  # highest for long / lowest for short
        mae = 0.0
        mfe = 0.0
        outcome_r: float | None = None
        j = entry_i

        while j < len(g) - 1:
            hi = float(high[j])
            lo = float(low[j])
            cl = float(close[j])

            if direction > 0:
                extreme = max(extreme, hi)
                adverse = fill - lo
                fav = hi - fill
            else:
                extreme = min(extreme, lo)
                adverse = hi - fill
                fav = fill - lo
            mae = max(mae, adverse)
            mfe = max(mfe, fav)

            # MAE abort
            if mae_abort_r > 0 and mae >= mae_abort_r * one_r:
                outcome_r = -mae_abort_r
                break

            # Trail stop
            if direction > 0:
                stop = extreme - trail_atr * a0
                if lo <= stop:
                    # exit at stop (approx)
                    pnl = stop - fill
                    outcome_r = pnl / one_r
                    break
            else:
                stop = extreme + trail_atr * a0
                if hi >= stop:
                    pnl = fill - stop
                    outcome_r = pnl / one_r
                    break

            # Pyramid add on closed bar beyond next level
            if next_level <= max_legs and next_level <= len(mults):
                lvl = e0 + direction * mults[next_level - 1] * a0
                crossed = cl >= lvl if direction > 0 else cl <= lvl
                if crossed:
                    # equal-lot basket: approximate avg entry shift
                    add_px = lvl
                    fill = (fill * legs + add_px) / (legs + 1)
                    legs += 1
                    next_level += 1

            j += 1
            if j - entry_i > 200:
                # time flatten at close
                pnl = (cl - fill) if direction > 0 else (fill - cl)
                outcome_r = pnl / one_r
                break

        if outcome_r is None:
            i += 1
            continue

        # Cost in R
        c_r = (cost_rt_pts * POINT) / one_r if one_r > 0 else 0.1
        pnl_r = outcome_r - c_r
        n_cycles += 1
        rs.append(pnl_r)
        sum_r += pnl_r
        if pnl_r > 0:
            wins += 1
        elif pnl_r < 0:
            losses += 1

        cooldown_until = j + cooldown_bars
        i = max(j + 1, i + 1)

    n = wins + losses
    wr = wins / n if n else 0.0
    aw = float(np.mean([x for x in rs if x > 0])) if wins else 0.0
    al = float(np.mean([-x for x in rs if x < 0])) if losses else 1.0
    r_real = aw / al if al > 0 and wins else 0.0
    # Designed R for BWR reference (framework Stage 0 uses realised R when available)
    r_use = r_real if r_real > 0 else designed_rr
    bwr = 1.0 / (1.0 + r_use) if r_use > 0 else 1.0
    bm = wr - bwr
    e_n = wr * (r_use + 1.0) - 1.0 if n else 0.0
    # Leak prior from cost vs designed 1R at median ATR proxy
    leak = 0.0
    if n and r_use > 0:
        # already netted cost into pnl_r; report gross-ish prior
        leak = (COST_RT_POINTS * POINT) / (one_r_atr * float(np.nanmedian(atr_a))) / (
            r_use + 1.0
        )

    return {
        "n": n,
        "wins": wins,
        "losses": losses,
        "WR": wr,
        "R_realised": r_real,
        "RR_design": designed_rr,
        "BWR": bwr,
        "BM": bm,
        "E_N": e_n,
        "sum_R": sum_r,
        "avg_R": float(np.mean(rs)) if rs else 0.0,
        "median_R": float(np.median(rs)) if rs else 0.0,
        "Leak_prior": leak,
        "EF_approx": bm - leak,
        "blocked_regime": blocked_regime,
        "blocked_session": blocked_session,
        "blocked_break": blocked_break,
        "tp_lt_sl": 0 if designed_rr >= 1.0 else 1,
        "max_legs": max_legs,
        "trail": trail_atr,
        "er_trend": er_trend,
        "min_break": min_break_atr,
        "mae_r": mae_abort_r,
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
            b_tf = board_from_regimes(regimes, "trendfollow", window="calendar_month")
            monthly.append(
                {
                    "month": mk,
                    "trendfollow": b_tf.tag,
                    "regime_shares": b_tf.regime_shares,
                    "bars": b_tf.bar_count,
                }
            )

        overall_mask = (ts >= start) & (ts <= end)
        regimes_all = [
            str(r)
            for r in feat_h1.loc[overall_mask, "confirmed_regime"].dropna().tolist()
        ]
        overall_tf = board_from_regimes(regimes_all, "trendfollow", window="30d")
        overall_mr = board_from_regimes(regimes_all, "meanrev", window="30d")

        candidates: list[tuple[str, dict]] = []

        def add(name: str, **kw) -> None:
            candidates.append((name, _probe_ktg(m15w, **kw)))

        # Baseline Phase1-like vs selectivity ladder (all RR_design >= 1)
        add("5leg_trail2_raw", max_legs=5, trail_atr=2.0, designed_rr=1.0,
            mae_abort_r=0.0, min_break_atr=0.0, require_trend=False, deny_vol_high=False,
            er_trend=0.30)
        add("3leg_trail1.5_raw", max_legs=3, trail_atr=1.5, designed_rr=1.5,
            mae_abort_r=0.0, min_break_atr=0.0, require_trend=False, deny_vol_high=False)
        add("3leg_trail1.5_TREND", max_legs=3, trail_atr=1.5, designed_rr=1.5,
            mae_abort_r=1.0, min_break_atr=0.0, require_trend=True, deny_vol_high=True,
            er_trend=0.30)
        add("3leg_trail1.5_TREND40", max_legs=3, trail_atr=1.5, designed_rr=1.5,
            mae_abort_r=0.75, min_break_atr=1.0, require_trend=True, deny_vol_high=True,
            er_trend=0.40)
        add("3leg_trail1.5_strict", max_legs=3, trail_atr=1.5, designed_rr=1.5,
            mae_abort_r=0.75, min_break_atr=1.5, require_trend=True, deny_vol_high=True,
            er_trend=0.40)
        add("3leg_trail1.5_bal_rr125", max_legs=3, trail_atr=1.5, designed_rr=1.25,
            one_r_atr=1.5, mae_abort_r=0.75, min_break_atr=1.25, require_trend=True,
            deny_vol_high=True, er_trend=0.35)
        add("2leg_trail1.5_strict", max_legs=2, trail_atr=1.5, designed_rr=1.5,
            mae_abort_r=0.75, min_break_atr=1.5, require_trend=True, deny_vol_high=True,
            er_trend=0.40)
        add("3leg_trail1.25_strict", max_legs=3, trail_atr=1.25, designed_rr=1.5,
            mae_abort_r=0.75, min_break_atr=1.5, require_trend=True, deny_vol_high=True,
            er_trend=0.40)
        # AAPL tip winners: deep break + wide trail (let R run) + TREND/deny HV
        add("3leg_trail3_mb2_er25", max_legs=3, trail_atr=3.0, designed_rr=1.5,
            one_r_atr=3.0, mae_abort_r=1.0, min_break_atr=2.0, require_trend=True,
            deny_vol_high=True, er_trend=0.25)
        add("3leg_trail3_mb2_er30", max_legs=3, trail_atr=3.0, designed_rr=1.5,
            one_r_atr=3.0, mae_abort_r=1.0, min_break_atr=2.0, require_trend=True,
            deny_vol_high=True, er_trend=0.30)
        add("BALANCED_chart", max_legs=3, trail_atr=3.0, designed_rr=1.5,
            one_r_atr=3.0, mae_abort_r=1.0, min_break_atr=2.0, require_trend=True,
            deny_vol_high=True, er_trend=0.30, session_hours=(14, 20))

        # Rank: require WR > BWR, E_N > 0, n >= 8; prefer Balanced mix (BM>0, E_N, n)
        scored = []
        for name, p in candidates:
            ok = (
                p["n"] >= 8
                and p["WR"] > p["BWR"]
                and p["E_N"] > 0
                and p["RR_design"] >= 1.0
            )
            scored.append((ok, p["E_N"], p["BM"], p["n"], name, p))
        scored.sort(key=lambda x: (x[0], x[1], x[2], x[3]), reverse=True)

        out = {
            "symbol": SYMBOL,
            "tf": "M15*",
            "window": {"start": str(start), "end": str(end)},
            "models": {"regime": REGIME_MODEL, "fit": FIT_MODEL},
            "atr_pts": atr_stats,
            "overall_trendfollow": {
                "tag": overall_tf.tag,
                "shares": overall_tf.shares,
                "regime_shares": overall_tf.regime_shares,
            },
            "overall_meanrev": {
                "tag": overall_mr.tag,
                "shares": overall_mr.shares,
            },
            "monthly_trendfollow": monthly,
            "candidates": {n: p for n, p in candidates},
            "ranking": [
                {
                    "name": n,
                    "pass": ok,
                    "n": p["n"],
                    "WR": p["WR"],
                    "BWR": p["BWR"],
                    "BM": p["BM"],
                    "E_N": p["E_N"],
                    "R": p["R_realised"],
                    "RR_design": p["RR_design"],
                    "avg_R": p["avg_R"],
                }
                for ok, _, _, _, n, p in scored
            ],
            "recommended": scored[0][4] if scored and scored[0][0] else None,
            "hard_rule": "never DesignedRR < 1.0 (TP >= SL)",
            "disclaimer": "Probe ≠ Strategy Tester. Research / advisory only.",
        }

        dest = Path(__file__).resolve().parents[2] / "research" / "assets" / "AAPL"
        dest.mkdir(parents=True, exist_ok=True)
        path = dest / "ktg_m15_6m_audit.json"
        path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
        print(json.dumps({"wrote": str(path), "recommended": out["recommended"],
                          "ranking_top": out["ranking"][:5]}, indent=2))
        print("\n=== ALL CANDIDATES ===")
        for ok, en, bm, n, name, p in scored:
            flag = "PASS" if ok else "fail"
            print(
                f"{flag:4} {name:28} n={p['n']:3} WR={100*p['WR']:5.1f}% "
                f"BWR={100*p['BWR']:5.1f}% BM={100*p['BM']:+5.1f}pp "
                f"E_N={p['E_N']:+.3f}R R={p['R_realised']:.2f} avgR={p['avg_R']:+.3f}"
            )
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
