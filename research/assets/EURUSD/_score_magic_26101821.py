"""Score EPG EURUSD magic 26101821 runs from latest Tester log."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

MAGIC = "26101821"
POINT = 0.00001
COST_RT_PRIOR = 20.0
SL_DEFAULT = 250.0
TP_DEFAULT = 310.0

log = sorted(
    Path(
        r"C:\Users\emili\AppData\Roaming\MetaQuotes\Terminal"
        r"\D0E8209F77C8CF37AD8BF550E51FF075\Tester\logs"
    ).glob("*.log"),
    key=lambda p: p.stat().st_mtime,
    reverse=True,
)[0]

with open(log, "r", encoding="utf-16", errors="replace") as f:
    lines = f.read().splitlines()
print("log", log.name, "lines", len(lines), "mtime", log.stat().st_mtime)

deal_re = re.compile(
    r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2})\s+deal #(\d+) "
    r"(buy|sell) ([\d.]+) EURUSD at ([\d.]+) done"
)
open_mkt_re = re.compile(
    r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2})\s+market (buy|sell) "
    r"([\d.]+) EURUSD sl: ([\d.]+) tp: ([\d.]+)"
)
filled_re = re.compile(r"\[EPG\] Filled ")
close_re = re.compile(r"\[EPG\] Basket closed: (.+)$")
deny_re = re.compile(r"\[EPG\] Entry denied: (.+)$")
init_re = re.compile(
    rf"\[EPG\] Init OK — EPG \| magic={MAGIC} SL=(\d+) TP=(\d+) RR=([\d.]+)"
)

magic_inputs = [i for i, L in enumerate(lines) if f"InpMagic={MAGIC}" in L]
print("InpMagic lines:", len(magic_inputs))


def _run_bounds(idx: int) -> tuple[int, int]:
    start = idx
    for j in range(idx, max(-1, idx - 80), -1):
        if "testing of Experts\\EPG\\EPG.ex5" in lines[j] and "EURUSD" in lines[j]:
            start = j
            break
    end = len(lines)
    for j in range(idx + 1, len(lines)):
        if "Tester" in lines[j] and "testing of Experts" in lines[j]:
            end = j
            break
    return start, end


def score(start: int, end: int, label: str) -> dict:
    deals = []
    opens = []
    closes: dict[str, int] = defaultdict(int)
    denies: dict[str, int] = defaultdict(int)
    final = dep = window = None
    sl_pts = SL_DEFAULT
    tp_pts = TP_DEFAULT
    level1 = atr_max = max_levels = None

    for i in range(start, end):
        L = lines[i]
        m = deal_re.search(L)
        if m:
            deals.append(
                dict(
                    t=m.group(1),
                    n=int(m.group(2)),
                    side=m.group(3),
                    lot=float(m.group(4)),
                    px=float(m.group(5)),
                )
            )
        m = open_mkt_re.search(L)
        if m:
            side, px, slp, tpp = (
                m.group(2),
                float(m.group(3)),  # lot — wrong; price is not here
                float(m.group(4)),
                float(m.group(5)),
            )
            # recover entry mid from next deal if needed; use sl/tp geometry vs mid quote
            # market line: buy ... sl: X tp: Y — entry ≈ ask from subsequent deal
            # geometry from SL/TP spacing:
            if side == "buy":
                # approximate entry as midpoint of sl/tp weighted by design RR
                # better: entry ≈ sl + SL_pts*POINT after we know SL
                pass
            opens.append((side, slp, tpp))
        if filled_re.search(L):
            pass
        m = close_re.search(L)
        if m:
            closes[m.group(1).strip()] += 1
        m = deny_re.search(L)
        if m:
            denies[m.group(1).strip()] += 1
        m = init_re.search(L)
        if m:
            sl_pts = float(m.group(1))
            tp_pts = float(m.group(2))
        if "InpLevel1Atr=" in L:
            level1 = L.split("=")[-1].strip().split("||")[0]
        if "InpAtrMaxPoints=" in L:
            atr_max = L.split("=")[-1].strip().split("||")[0]
        if "InpMaxLevels=" in L:
            max_levels = L.split("=")[-1].strip().split("||")[0]
        if "final balance" in L:
            m2 = re.search(r"final balance ([\d.]+)", L)
            if m2:
                final = float(m2.group(1))
        if "initial deposit" in L:
            m2 = re.search(r"initial deposit ([\d.]+)", L)
            if m2:
                dep = float(m2.group(1))
        m = re.search(
            r"from (\d{4}\.\d{2}\.\d{2}) 00:00 to (\d{4}\.\d{2}\.\d{2}) 00:00", L
        )
        if m:
            window = f"{m.group(1)} -> {m.group(2)}"

    # Geometry from market open lines paired with next deal price
    open_geoms = []
    for i in range(start, end):
        L = lines[i]
        m = open_mkt_re.search(L)
        if not m:
            continue
        side, slp, tpp = m.group(2), float(m.group(4)), float(m.group(5))
        # find next deal price as entry
        entry = None
        for j in range(i, min(i + 8, end)):
            md = deal_re.search(lines[j])
            if md and md.group(3) == side:
                entry = float(md.group(5))
                break
        if entry is None:
            continue
        if side == "buy":
            sl_d = round((entry - slp) / POINT)
            tp_d = round((tpp - entry) / POINT)
        else:
            sl_d = round((slp - entry) / POINT)
            tp_d = round((entry - tpp) / POINT)
        open_geoms.append((side, sl_d, tp_d, entry))

    rr_design = tp_pts / sl_pts if sl_pts else 0.0
    sl_dist = sl_pts * POINT

    dlist = [d for d in deals if d["n"] > 0]
    events = []
    j = 0
    while j + 1 < len(dlist):
        a, b = dlist[j], dlist[j + 1]
        if a["side"] == b["side"]:
            j += 1
            continue
        move = (b["px"] - a["px"]) if a["side"] == "buy" else (a["px"] - b["px"])
        r = move / sl_dist if sl_dist else 0.0
        if r >= 0.85 * rr_design:
            kind = "TP"
        elif r <= -0.85:
            kind = "SL"
        else:
            kind = "other"
        events.append(
            dict(t=a["t"], side=a["side"], r=r, kind=kind, entry=a["px"], exit=b["px"])
        )
        j += 2

    wins = [e for e in events if e["r"] > 0]
    losses = [e for e in events if e["r"] < 0]
    n = len(wins) + len(losses)
    wr = len(wins) / n if n else 0.0
    aw = sum(e["r"] for e in wins) / len(wins) if wins else 0.0
    al = abs(sum(e["r"] for e in losses) / len(losses)) if losses else 0.0
    r_real = aw / al if al > 0 else 0.0
    bwr = 1.0 / (1.0 + r_real) if r_real > 0 else 1.0
    bm = wr - bwr
    c_r = COST_RT_PRIOR / sl_pts if sl_pts else 0.0
    leak = c_r / (r_real + 1.0) if r_real > 0 else 0.0
    ef = bm - leak
    e_n = wr * (r_real + 1.0) - 1.0 if n else 0.0
    e_n_design = wr * (rr_design + 1.0) - 1.0 if n else 0.0
    bwr_d = 1.0 / (1.0 + rr_design) if rr_design > 0 else 1.0
    tp_lt_sl = sum(1 for _, s, t, _ in open_geoms if t < s)

    tip = [e for e in events if "2026.05.01" <= e["t"] < "2026.10.08"]
    tip_w = [e for e in tip if e["r"] > 0]
    tip_l = [e for e in tip if e["r"] < 0]
    tip_n = len(tip_w) + len(tip_l)
    tip_wr = len(tip_w) / tip_n if tip_n else 0.0
    tip_aw = sum(e["r"] for e in tip_w) / len(tip_w) if tip_w else 0.0
    tip_al = abs(sum(e["r"] for e in tip_l) / len(tip_l)) if tip_l else 0.0
    tip_r = tip_aw / tip_al if tip_al else 0.0
    tip_bwr = 1.0 / (1.0 + tip_r) if tip_r else 1.0
    tip_en = tip_wr * (tip_r + 1.0) - 1.0 if tip_n else 0.0
    by_m: dict[str, list] = defaultdict(lambda: [0, 0, 0.0])
    for e in tip:
        by_m[e["t"][:7]][0] += 1
        by_m[e["t"][:7]][1] += int(e["r"] > 0)
        by_m[e["t"][:7]][2] += e["r"]

    return {
        "label": label,
        "window": window,
        "sl": sl_pts,
        "tp": tp_pts,
        "rr_design": round(rr_design, 3),
        "level1_atr": level1,
        "atr_max": atr_max,
        "max_levels": max_levels,
        "deposit": dep,
        "final": final,
        "pnl_currency": (final - dep) if final is not None and dep is not None else None,
        "n_opens": len(open_geoms),
        "n_deal_pairs": len(events),
        "n_scored": n,
        "wins": len(wins),
        "losses": len(losses),
        "WR": round(wr, 4),
        "AW": round(aw, 4),
        "AL": round(al, 4),
        "R": round(r_real, 4),
        "BWR": round(bwr, 4),
        "BM": round(bm, 4),
        "Leak_prior": round(leak, 4),
        "EF_prior": round(ef, 4),
        "E_N": round(e_n, 4),
        "E_N_designR": round(e_n_design, 4),
        "BWR_design": round(bwr_d, 4),
        "sum_R": round(sum(e["r"] for e in events), 3),
        "kinds": {
            "TP": sum(1 for e in events if e["kind"] == "TP"),
            "SL": sum(1 for e in events if e["kind"] == "SL"),
            "other": sum(1 for e in events if e["kind"] == "other"),
        },
        "tp_lt_sl_opens": tp_lt_sl,
        "closes": dict(closes),
        "denies_top": dict(sorted(denies.items(), key=lambda kv: -kv[1])[:8]),
        "tip_202605_20261007": {
            "n": tip_n,
            "WR": round(tip_wr, 4),
            "R": round(tip_r, 4),
            "BWR": round(tip_bwr, 4),
            "E_N": round(tip_en, 4),
            "sum_R": round(sum(e["r"] for e in tip), 3),
            "monthly": {
                m: {
                    "n": v[0],
                    "WR": round(v[1] / v[0], 3) if v[0] else 0,
                    "sum_R": round(v[2], 2),
                }
                for m, v in sorted(by_m.items())
            },
        },
        "events_preview": [
            f"{e['t']} {e['side']} R={e['r']:+.2f} {e['kind']}" for e in events[:10]
        ],
        "open_geom_sample": [
            f"{s} SL={sl} TP={tp}" for s, sl, tp, _ in open_geoms[:5]
        ],
    }


results = []
for k, mi in enumerate(magic_inputs):
    start, end = _run_bounds(mi)
    label = f"run{k+1}_L{mi+1}"
    r = score(start, end, label)
    results.append(r)
    print("\n====", label, "====")
    for key in (
        "window",
        "sl",
        "tp",
        "rr_design",
        "level1_atr",
        "atr_max",
        "max_levels",
        "deposit",
        "final",
        "pnl_currency",
        "n_opens",
        "n_scored",
        "wins",
        "losses",
        "WR",
        "R",
        "BWR",
        "BM",
        "Leak_prior",
        "EF_prior",
        "E_N",
        "E_N_designR",
        "sum_R",
        "kinds",
        "tp_lt_sl_opens",
        "closes",
        "denies_top",
        "tip_202605_20261007",
    ):
        print(f"  {key}: {r[key]}")
    if r["events_preview"]:
        print("  preview:")
        for p in r["events_preview"]:
            print("   ", p)

out_path = Path(__file__).resolve().parent / "tester_magic_26101821_score.json"
payload = {
    "magic": MAGIC,
    "ea": "EPG",
    "scored_at": datetime.now(UTC).isoformat(),
    "log": str(log),
    "framework": "unified_edge_framework Stage 0-1 (R from deal pairs; Leak prior 20pt RT)",
    "runs": results,
}
out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print("\nwrote", out_path)
