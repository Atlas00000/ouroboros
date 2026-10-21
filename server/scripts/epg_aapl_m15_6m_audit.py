"""AAPL ~6m EPG (EMA Pullback Grid) M15* probe for chart preset design.

Phase-1 EPG contract (Experts/EPG Inputs.mqh):
  - trend = M15 EMA20/50 aligned + H1 close vs EMA50
  - pullback entries at EMA50 ± k*ATR (L1..L3)
  - exit: basket money TP OR EMA50 invalidation
  - HARD RULE for declared geometry: BasketTP / typical_adverse >= 1.0
Framework: docs/framework/unified_edge_framework.md
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from app.analytics.bars import load_ohlcv
from app.analytics.fit.boards import board_from_regimes
from app.analytics.regimes import MODEL_VERSION as REGIME_MODEL, regime_feature_frame
from app.config import get_settings
from app.db.session import get_session_factory

SYMBOL = "AAPL"
POINT = 0.01
COST_RT = 0.25  # $ per share round-trip prior


def _resample(m1: pd.DataFrame, rule: str) -> pd.DataFrame:
    df = m1.copy()
    df["ts"] = pd.to_datetime(df["ts"], utc=True)
    df = df.set_index("ts").sort_index()
    return (
        df.resample(rule)
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


def _atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    h, l, c = df["high"], df["low"], df["close"]
    prev = c.shift(1)
    tr = pd.concat([(h - l), (h - prev).abs(), (l - prev).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1.0 / n, adjust=False).mean()


def _probe(
    m15: pd.DataFrame,
    h1: pd.DataFrame,
    *,
    max_levels: int = 2,
    levels: tuple[float, ...] = (0.5, 1.0, 1.3),
    basket_tp: float = 4.0,
    lot: float = 1.0,
    session: tuple[int, int] | None = (14, 20),
    skip_tue: bool = True,
    require_h1: bool = True,
) -> dict:
    m = m15.copy()
    m["ema20"] = _ema(m["close"], 20)
    m["ema50"] = _ema(m["close"], 50)
    m["atr"] = _atr(m, 14)
    h = h1.copy()
    h["ema50"] = _ema(h["close"], 50)
    h = h.set_index("ts")

    close = m["close"].to_numpy(float)
    high = m["high"].to_numpy(float)
    low = m["low"].to_numpy(float)
    ema20 = m["ema20"].to_numpy(float)
    ema50 = m["ema50"].to_numpy(float)
    atr = m["atr"].to_numpy(float)
    ts = pd.to_datetime(m["ts"], utc=True)

    wins = losses = 0
    rs: list[float] = []
    blocked_flat = 0
    i = 60
    while i < len(m) - 3:
        if np.isnan(ema20[i]) or np.isnan(ema50[i]) or np.isnan(atr[i]) or atr[i] <= 0:
            i += 1
            continue
        t = ts.iloc[i]
        if skip_tue and int(t.dayofweek) == 1:
            i += 1
            continue
        if session is not None:
            h0, h1s = session
            if not (h0 <= int(t.hour) < h1s):
                i += 1
                continue

        # H1 bias at last closed H1 <= t
        h1_rows = h.loc[:t]
        if len(h1_rows) < 2:
            i += 1
            continue
        h1_close = float(h1_rows["close"].iloc[-1])
        h1_ema = float(h1_rows["ema50"].iloc[-1])
        m15_bull = ema20[i] > ema50[i]
        m15_bear = ema20[i] < ema50[i]
        h1_bull = h1_close > h1_ema
        h1_bear = h1_close < h1_ema
        if require_h1:
            if m15_bull and h1_bull:
                side = 1
            elif m15_bear and h1_bear:
                side = -1
            else:
                blocked_flat += 1
                i += 1
                continue
        else:
            if m15_bull:
                side = 1
            elif m15_bear:
                side = -1
            else:
                blocked_flat += 1
                i += 1
                continue

        # Need touch of next unfilled level (start L1)
        a0 = float(atr[i])
        e50 = float(ema50[i])
        lvl_px = e50 - side * levels[0] * a0
        touched = (low[i] <= lvl_px) if side > 0 else (high[i] >= lvl_px)
        if not touched:
            i += 1
            continue

        # Fill at level (approx)
        fills = [lvl_px]
        filled = 1
        avg = lvl_px
        cash_pnl = 0.0  # mark at exit
        one_r = max(levels[min(1, len(levels) - 1)] * a0 * lot, a0 * lot * 0.5)
        j = i + 1
        outcome = None
        while j < len(m) - 1:
            # invalidation on closed bar
            if side > 0 and close[j] < ema50[j]:
                # close basket at close[j]
                cash_pnl = sum((close[j] - f) * lot for f in fills) - COST_RT * len(fills)
                outcome = "inv"
                break
            if side < 0 and close[j] > ema50[j]:
                cash_pnl = sum((f - close[j]) * lot for f in fills) - COST_RT * len(fills)
                outcome = "inv"
                break

            # floating
            if side > 0:
                float_pnl = sum((close[j] - f) * lot for f in fills)
            else:
                float_pnl = sum((f - close[j]) * lot for f in fills)
            if float_pnl >= basket_tp:
                cash_pnl = float_pnl - COST_RT * len(fills)
                outcome = "tp"
                break

            # add next level if touched
            if filled < max_levels and filled < len(levels):
                nxt = e50 - side * levels[filled] * a0
                # freeze e50/a0 at cycle start (Phase1 uses live EMA each bar in EA —
                # use live ema50[j]/atr[j] for add prices to match EA better)
                e_live = float(ema50[j])
                a_live = float(atr[j]) if not np.isnan(atr[j]) and atr[j] > 0 else a0
                nxt = e_live - side * levels[filled] * a_live
                hit = (low[j] <= nxt) if side > 0 else (high[j] >= nxt)
                if hit:
                    fills.append(nxt)
                    filled += 1
                    avg = float(np.mean(fills))

            j += 1
            if j - i > 120:
                if side > 0:
                    cash_pnl = sum((close[j] - f) * lot for f in fills) - COST_RT * len(fills)
                else:
                    cash_pnl = sum((f - close[j]) * lot for f in fills) - COST_RT * len(fills)
                outcome = "time"
                break

        if outcome is None:
            i += 1
            continue

        pnl_r = cash_pnl / one_r if one_r > 0 else 0.0
        rs.append(pnl_r)
        if pnl_r > 0:
            wins += 1
        elif pnl_r < 0:
            losses += 1
        i = max(j + 1, i + 2)

    n = wins + losses
    wr = wins / n if n else 0.0
    aw = float(np.mean([x for x in rs if x > 0])) if wins else 0.0
    al = float(np.mean([-x for x in rs if x < 0])) if losses else 1.0
    r = aw / al if al > 0 and wins else 0.0
    # Declared 1R ≈ L2 ATR depth × lot; DesignedRR = BasketTP / 1R
    atr_med = float(np.nanmedian(atr))
    lvl_ref = levels[min(1, len(levels) - 1)]
    one_r_decl = max(lvl_ref * atr_med * lot, 0.5 * atr_med * lot)
    rr_design = basket_tp / one_r_decl if one_r_decl > 0 else 0.0
    r_use = r if r > 0 else max(rr_design, 1.0)
    bwr = 1.0 / (1.0 + r_use) if r_use > 0 else 1.0
    e_n = wr * (r_use + 1.0) - 1.0 if n else 0.0
    return {
        "n": n,
        "wins": wins,
        "losses": losses,
        "WR": wr,
        "R": r,
        "RR_design": rr_design,
        "BWR": bwr,
        "BM": wr - bwr,
        "E_N": e_n,
        "avg_R": float(np.mean(rs)) if rs else 0.0,
        "sum_R": float(np.sum(rs)) if rs else 0.0,
        "blocked_flat": blocked_flat,
        "max_levels": max_levels,
        "basket_tp": basket_tp,
        "one_r_decl": one_r_decl,
        "tp_lt_sl": 0 if rr_design >= 1.0 - 1e-9 else 1,
    }


def main() -> int:
    get_settings.cache_clear()
    session = get_session_factory()()
    try:
        df_m1 = load_ohlcv(session, SYMBOL, "M1", lookback_days=220)
        df_h1 = load_ohlcv(session, SYMBOL, "H1", lookback_days=220)
        m15 = _resample(df_m1, "15min")
        h1 = df_h1.copy()
        h1["ts"] = pd.to_datetime(h1["ts"], utc=True)

        end = pd.to_datetime(m15["ts"].iloc[-1], utc=True)
        start = pd.Timestamp(year=end.year, month=end.month, day=1, tz="UTC") - pd.DateOffset(
            months=5
        )
        start = pd.Timestamp(year=start.year, month=start.month, day=1, tz="UTC")
        m15w = m15[(m15["ts"] >= start) & (m15["ts"] <= end)].reset_index(drop=True)
        h1w = h1[(h1["ts"] >= start - pd.Timedelta(days=10)) & (h1["ts"] <= end)].reset_index(
            drop=True
        )

        atr = _atr(m15w, 14).dropna()
        atr_med = float(atr.median())

        feat = regime_feature_frame(df_h1, "H1")
        ts = pd.to_datetime(feat["ts"], utc=True)
        mask = (ts >= start) & (ts <= end)
        regimes = [str(r) for r in feat.loc[mask, "confirmed_regime"].dropna().tolist()]
        overall_tf = board_from_regimes(regimes, "trendfollow", window="30d")
        overall_mr = board_from_regimes(regimes, "meanrev", window="30d")

        # Basket TP grid so declared RR >= 1 using one_r ≈ 1.0*ATR
        candidates = []

        def add(name, **kw):
            candidates.append((name, _probe(m15w, h1w, **kw)))

        for tp in (2.0, 3.0, 4.0, 5.0, 6.0, 8.0):
            for legs in (2, 3):
                for lv in ((0.5, 1.0, 1.3), (0.5, 1.0, 1.5), (0.75, 1.25, 1.75)):
                    add(
                        f"legs{legs}_tp{tp}_lv{'-'.join(str(x) for x in lv[:legs])}",
                        max_levels=legs,
                        levels=lv,
                        basket_tp=tp,
                    )

        scored = []
        for name, p in candidates:
            ok = (
                p["n"] >= 12
                and p["WR"] > p["BWR"]
                and p["E_N"] > 0
                and p["RR_design"] >= 1.0
                and p["tp_lt_sl"] == 0
            )
            scored.append((ok, p["E_N"], p["BM"], p["n"], name, p))
        scored.sort(key=lambda x: (x[0], x[1], x[2], x[3]), reverse=True)

        out = {
            "symbol": SYMBOL,
            "tf": "M15*",
            "window": {"start": str(start), "end": str(end)},
            "atr_med_usd": atr_med,
            "overall_trendfollow": {"tag": overall_tf.tag, "shares": overall_tf.shares},
            "overall_meanrev": {"tag": overall_mr.tag, "shares": overall_mr.shares},
            "regime_model": REGIME_MODEL,
            "ranking": [
                {
                    "name": n,
                    "pass": ok,
                    "n": p["n"],
                    "WR": p["WR"],
                    "BWR": p["BWR"],
                    "BM": p["BM"],
                    "E_N": p["E_N"],
                    "R": p["R"],
                    "RR_design": p["RR_design"],
                    "basket_tp": p["basket_tp"],
                }
                for ok, _, _, _, n, p in scored[:20]
            ],
            "recommended": scored[0][4] if scored and scored[0][0] else None,
            "hard_rule": "BasketTP / adverse_1R >= 1.0 (never TP < SL by design)",
        }
        dest = Path(__file__).resolve().parents[2] / "research" / "assets" / "AAPL"
        dest.mkdir(parents=True, exist_ok=True)
        path = dest / "epg_m15_6m_audit.json"
        path.write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(json.dumps({"wrote": str(path), "recommended": out["recommended"]}, indent=2))
        print("\n=== TOP ===")
        for ok, en, bm, n, name, p in scored[:15]:
            print(
                f"{'PASS' if ok else 'fail'} {name:40} n={p['n']:3} "
                f"WR={100*p['WR']:5.1f}% BWR={100*p['BWR']:5.1f}% "
                f"E_N={p['E_N']:+.3f} RR_d={p['RR_design']:.2f} tp$={p['basket_tp']}"
            )
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
