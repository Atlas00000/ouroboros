"""Greedy diversified shortlist from D1 return correlations.

Usage (repo root):
  PYTHONPATH=server python server/scripts/diversified_shortlist.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import select

# Ensure server package imports when run as a script.
ROOT = Path(__file__).resolve().parents[2]
SERVER = ROOT / "server"
if str(SERVER) not in sys.path:
    sys.path.insert(0, str(SERVER))


def load_env() -> None:
    for env in (SERVER / ".env", ROOT / ".env"):
        if not env.exists():
            continue
        for line in env.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            k, v = s.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def bucket(sym: str, meta: dict) -> str:
    m = meta.get(sym, {})
    klass = str(m.get("asset_class", "")).lower()
    name = str(m.get("display_name", "")).lower()
    if sym in ("XTIUSD", "XBRUSD") or "oil" in name or "crude" in name:
        return "energy"
    if klass == "metal" or sym in ("XAUUSD", "XAGUSD"):
        return "metal"
    if klass == "index":
        if sym in ("DE40", "UK100", "JP225"):
            return "ex_us_index"
        return "us_index"
    if klass == "equity":
        if sym == "XOM":
            return "equity_energy"
        if sym == "JPM":
            return "equity_financial"
        if sym in ("AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "AVGO", "TSLA"):
            return "equity_growth"
        return "equity_other"
    if klass == "fx":
        if sym in ("USDJPY", "EURJPY", "GBPJPY"):
            return "fx_jpy"
        if sym in ("AUDUSD", "NZDUSD", "USDCAD"):
            return "fx_commodity"
        if sym in ("EURUSD", "GBPUSD", "EURGBP", "USDCHF"):
            return "fx_g10"
        return "fx_other"
    return klass or "other"


def main() -> None:
    load_env()

    from app.analytics.bars import load_ohlcv
    from app.db.session import get_session_factory
    from app.models.asset import Asset

    with get_session_factory()() as session:
        assets = session.scalars(select(Asset).where(Asset.is_active.is_(True)).order_by(Asset.symbol)).all()
        meta = {
            a.symbol: {
                "display_name": a.display_name,
                "asset_class": a.asset_class,
                "quote_currency": a.quote_currency,
            }
            for a in assets
        }
        frames: dict[str, pd.Series] = {}
        tf = "D1"
        lookback = 120
        for a in assets:
            df = load_ohlcv(session, a.symbol, "D1", lookback_days=lookback)
            if df.empty or len(df) < 20:
                df = load_ohlcv(session, a.symbol, "H1", lookback_days=45)
                if not df.empty and len(df) >= 40:
                    tf = "mixed_d1_h1"
                else:
                    continue
            s = df.set_index("ts")["close"].astype(float)
            s = s[~s.index.duplicated(keep="last")].sort_index()
            frames[a.symbol] = s

    if not frames:
        print(json.dumps({"error": "no bar series"}, indent=2))
        return

    wide = pd.DataFrame(frames).sort_index()
    # Align on calendar / session gaps with limited ffill
    wide = wide.ffill(limit=2)
    rets = wide.pct_change()
    min_obs = 15 if tf == "D1" else 40
    corr = rets.corr(min_periods=min_obs)
    symbols = [s for s in corr.columns if corr[s].notna().sum() >= 5]

    avg_abs = corr.loc[symbols, symbols].abs().mean().sort_values()
    selected: list[str] = []
    used_buckets: dict[str, int] = {}
    energy = {"XTIUSD", "XBRUSD"}
    # Hard class caps for a 10-name diversified desk sleeve.
    # FX capped at 2 in pass-1 spirit; soft fill may use 3.
    caps = {"equity": 3, "fx": 2, "index": 2, "precious": 1, "energy": 1}
    max_pair_abs = 0.40

    def role(sym: str) -> str:
        b = bucket(sym, meta)
        if b == "energy" or sym in energy:
            return "energy"
        if b == "metal":
            return "precious"
        return str(meta.get(sym, {}).get("asset_class", "other"))

    def counts() -> dict[str, int]:
        out: dict[str, int] = {}
        for s in selected:
            r = role(s)
            out[r] = out.get(r, 0) + 1
        return out

    def admissible(cand: str) -> bool:
        c = counts()
        r = role(cand)
        if c.get(r, 0) >= caps.get(r, 10):
            return False
        # Avoid a second FX in the same factor bucket (e.g. EURGBP + GBPUSD).
        if role(cand) == "fx":
            b = bucket(cand, meta)
            if any(bucket(s, meta) == b for s in selected if role(s) == "fx"):
                return False
        # Reject if any pairwise |corr| would breach the uncorrelated budget.
        if selected:
            vals = [abs(float(corr.loc[cand, s])) for s in selected if pd.notna(corr.loc[cand, s])]
            if vals and max(vals) > max_pair_abs:
                return False
        # Prefer one US + one ex-US index if both slots used.
        if role(cand) == "index":
            selected_idx = [s for s in selected if role(s) == "index"]
            if len(selected_idx) == 1:
                have_us = bucket(selected_idx[0], meta) == "us_index"
                cand_us = bucket(cand, meta) == "us_index"
                if have_us == cand_us:
                    # Only block if an opposite-region index also clears corr/class caps.
                    # (Avoid deadlock when the preferred region is pair-incompatible.)
                    def _pair_ok(sym: str) -> bool:
                        vals = [
                            abs(float(corr.loc[sym, s]))
                            for s in selected
                            if pd.notna(corr.loc[sym, s])
                        ]
                        return (not vals) or max(vals) <= max_pair_abs

                    opp = [
                        s
                        for s in symbols
                        if s not in selected
                        and role(s) == "index"
                        and (bucket(s, meta) == "us_index") != have_us
                        and _pair_ok(s)
                    ]
                    if opp:
                        return False
        return True

    def score(cand: str) -> float:
        if not selected:
            return float(avg_abs.get(cand, 1.0))
        block = corr.loc[cand, selected].abs()
        max_c = float(block.max()) if len(block) else 1.0
        mean_c = float(block.mean()) if len(block) else 1.0
        b = bucket(cand, meta)
        bucket_pen = 0.08 * used_buckets.get(b, 0)
        # Prefer gold over silver when both still free (classic diversifier).
        gold_bias = -0.02 if cand == "XAUUSD" else 0.0
        # Prefer financial / energy equity after first growth pick.
        sector_bias = -0.03 if b in ("equity_financial", "equity_energy") else 0.0
        return max_c + 0.35 * mean_c + bucket_pen + gold_bias + sector_bias

    seed_candidates = [s for s in avg_abs.index.astype(str).tolist() if admissible(s)]
    seed = seed_candidates[0]
    selected.append(seed)
    used_buckets[bucket(seed, meta)] = 1

    def fill(limit: int, pair_cap: float) -> None:
        nonlocal max_pair_abs
        max_pair_abs = pair_cap
        while len(selected) < limit and len(selected) < len(symbols):
            remaining = [s for s in symbols if s not in selected and admissible(s)]
            if not remaining:
                break
            remaining.sort(key=score)
            nxt = remaining[0]
            selected.append(nxt)
            used_buckets[bucket(nxt, meta)] = used_buckets.get(bucket(nxt, meta), 0) + 1

    # Pass 1: strict uncorrelated core. Later passes soften pair / class caps.
    fill(10, 0.40)
    if len(selected) < 10:
        fill(10, 0.48)
    if len(selected) < 10:
        # Prefer a low-corr extra equity (AAPL) before stretching FX vs gold.
        caps["equity"] = 4
        fill(10, 0.45)
    if len(selected) < 10:
        caps["fx"] = 3
        fill(10, 0.55)

    sub = corr.loc[selected, selected]
    pairs = []
    for i, a in enumerate(selected):
        for b in selected[i + 1 :]:
            val = sub.loc[a, b]
            pairs.append(
                {
                    "a": a,
                    "b": b,
                    "corr": None if pd.isna(val) else round(float(val), 3),
                }
            )
    mask = ~np.eye(len(selected), dtype=bool)
    mean_abs = float(sub.abs().to_numpy()[mask].mean()) if len(selected) > 1 else 0.0

    out = {
        "timeframe": tf,
        "lookback_days": lookback,
        "n_assets_universe": len(assets),
        "n_with_corr": len(symbols),
        "shortlist": [
            {
                "rank": i + 1,
                "symbol": s,
                "display_name": meta.get(s, {}).get("display_name"),
                "asset_class": meta.get(s, {}).get("asset_class"),
                "bucket": bucket(s, meta),
                "avg_abs_corr_to_shortlist": round(
                    float(sub.loc[s, [x for x in selected if x != s]].abs().mean()),
                    3,
                )
                if len(selected) > 1
                else None,
            }
            for i, s in enumerate(selected)
        ],
        "mean_abs_pairwise_corr": round(mean_abs, 3),
        "pairs_high_to_low": sorted(pairs, key=lambda r: abs(r["corr"] or 0), reverse=True),
        "matrix": {
            a: {
                b: (None if pd.isna(sub.loc[a, b]) else round(float(sub.loc[a, b]), 3))
                for b in selected
            }
            for a in selected
        },
        "excluded_thin": [a.symbol for a in assets if a.symbol not in symbols],
        "universe_by_class": {},
    }
    by_class: dict[str, list[str]] = {}
    for a in assets:
        by_class.setdefault(a.asset_class, []).append(a.symbol)
    out["universe_by_class"] = by_class
    out_path = Path(__file__).resolve().parent / "_shortlist_out.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({"wrote": str(out_path), "n": len(selected), "mean_abs": out["mean_abs_pairwise_corr"], "symbols": selected}, indent=2))


if __name__ == "__main__":
    main()
