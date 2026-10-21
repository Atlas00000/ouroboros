"""Short NVDA M5 re-probe: tighter regime + cost sensitivity on top candidates."""
from __future__ import annotations
import importlib.util, json
from pathlib import Path
import pandas as pd
from app.analytics.bars import load_ohlcv
from app.config import get_settings
from app.db.session import get_session_factory

spec = importlib.util.spec_from_file_location("m", Path("scripts/bmrg_nvda_m5_6m_audit.py"))
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

get_settings.cache_clear()
session = get_session_factory()()
try:
    m1 = load_ohlcv(session, "NVDA", "M1", lookback_days=220)
    m5 = mod._resample_m5(m1)
    start = pd.Timestamp("2026-05-01", tz="UTC")
    end = pd.to_datetime(m5["ts"].iloc[-1], utc=True)
    g = m5[(m5["ts"] >= start) & (m5["ts"] <= end)].reset_index(drop=True)
    atr = mod._atr_wilder(g, 14)
    ap = (atr / 0.01).dropna()
    floor = float(max(15.0, ap.quantile(0.25) * 0.6))
    cap75, cap90 = float(ap.quantile(0.75)), float(ap.quantile(0.90))
    print(f"atr p50={ap.quantile(0.5):.1f} floor={floor:.1f} cap75={cap75:.1f} cap90={cap90:.1f}", flush=True)

    specs = []
    for sl in (280, 300, 320, 350, 380, 400, 450, 500, 550):
        for rr, tag in ((1.0, "harvest"), (1.25, "balanced"), (1.5, "growth")):
            tp = max(sl, int(round(sl * rr / 10) * 10))
            for bb in (2.2, 2.5):
                for fname, kw in [
                    ("raw", {}),
                    ("atr90", {"atr_min_pts": floor, "atr_max_pts": cap90}),
                    ("atr75", {"atr_min_pts": floor, "atr_max_pts": cap75}),
                    ("atrBBW", {"atr_min_pts": floor, "atr_max_pts": cap90, "bb_width_min_pct": 0.20, "bb_width_max_pct": 1.60}),
                    ("atrBBW_t", {"atr_min_pts": floor, "atr_max_pts": cap75, "bb_width_min_pct": 0.25, "bb_width_max_pct": 1.20}),
                    ("atrBBW_m", {"atr_min_pts": floor, "atr_max_pts": cap90, "bb_width_min_pct": 0.30, "bb_width_max_pct": 1.40}),
                ]:
                    specs.append((f"{tag}_sl{sl}_tp{tp}_bb{bb}_{fname}", sl, tp, bb, kw))

    print(f"specs={len(specs)}", flush=True)
    rows = []
    for i, (name, sl, tp, bb, kw) in enumerate(specs, 1):
        if i == 1 or i % 15 == 0:
            print(f"  {i}/{len(specs)} {name}", flush=True)
        p = mod._probe_fixed_rr(g, bb_dev=bb, sl_pts=float(sl), tp_pts=float(tp), cost_rt_pts=50.0, **kw)
        if p["n_resolved"] < 40 or p["RR_design"] < 1.0 - 1e-12:
            continue
        for c in (35.0, 40.0, 45.0, 50.0, 60.0, 70.0):
            c_r = c / sl
            leak = c_r / (p["RR_design"] + 1.0)
            ef = p["BM"] - leak
            ok = ef > 0 and p["E_N"] > 0 and p["WR"] > p["BWR"] and p["tp_lt_sl_blocked"] == 0
            rows.append({
                "ok": ok, "cost": c, "EF": round(ef, 4), "E_N": round(p["E_N"], 4),
                "WR": round(p["WR"], 4), "n": p["n_resolved"], "sl": sl, "tp": tp,
                "bb": bb, "BM": round(p["BM"], 4), "Leak": round(leak, 4),
                "BWR": round(p["BWR"], 4), "rr": round(p["RR_design"], 3),
                "blocked": p["blocked_regime"], "name": name,
            })

    out = {"floor": floor, "cap75": cap75, "cap90": cap90, "by_cost": {}}
    for c in (35, 40, 45, 50, 60, 70):
        ranked = sorted([r for r in rows if r["cost"] == c], key=lambda x: (x["ok"], x["EF"], x["E_N"], x["n"]), reverse=True)
        viable = [r for r in ranked if r["ok"]]
        # prefer RR in 1.2-1.35 among viable
        out["by_cost"][str(c)] = {"viable_count": len(viable), "viable": viable[:10], "top": ranked[:8]}
        print(f"\ncost={c} viable={len(viable)}", flush=True)
        show = viable[:5] if viable else ranked[:5]
        for x in show:
            print(f"  ok={x['ok']} EF={x['EF']:+.4f} EN={x['E_N']:+.4f} WR={x['WR']:.3f} n={x['n']} {x['sl']}/{x['tp']} {x['name']}", flush=True)

    path = Path("../research/assets/NVDA/bmrg_m5_6m_reprobe.json")
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", path, flush=True)
finally:
    session.close()
