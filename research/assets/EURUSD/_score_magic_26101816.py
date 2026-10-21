"""Score BMRG EURUSD magic 26101816 runs from latest Tester log."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

MAGIC = "26101816"
POINT = 0.00001  # 5-digit EURUSD
COST_RT_PRIOR = 20.0  # pts; replace with measured blotter costs when available

log = sorted(
    Path(
        r"C:\Users\emili\AppData\Roaming\MetaQuotes\Terminal"
        r"\D0E8209F77C8CF37AD8BF550E51FF075\Tester\logs"
    ).glob("*.log"),
    key=lambda p: p.stat().st_mtime,
    reverse=True,
)[0]

# Shared read — Tester may still hold the file
with open(log, "r", encoding="utf-16", errors="replace") as f:
    lines = f.read().splitlines()
print("log", log.name, "lines", len(lines), "mtime", log.stat().st_mtime)

deal_re = re.compile(
    r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2})\s+deal #(\d+) "
    r"(buy|sell) ([\d.]+) EURUSD at ([\d.]+) done"
)
open_re = re.compile(
    r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}).*\[BMRG\]\[TRADE\] OPEN "
    r"(BUY|SELL) lot=([\d.]+) price=([\d.]+) sl=([\d.]+) tp=([\d.]+)"
)
block_re = re.compile(
    r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}).*Entry blocked: (.+)"
)
init_re = re.compile(
    rf"BMRG init OK \| EURUSD PERIOD_M15 .* magic={MAGIC}"
)

inits = [i for i, L in enumerate(lines) if init_re.search(L) or (
    f"magic={MAGIC}" in L and "BMRG init OK" in L and "EURUSD" in L
)]
# Also catch InpMagic= lines as run anchors if init format differs
magic_inputs = [
    i
    for i, L in enumerate(lines)
    if f"InpMagic={MAGIC}" in L
]
print("init OK lines:", len(inits), "InpMagic lines:", len(magic_inputs))


def _run_bounds_from_magic_input(idx: int) -> tuple[int, int]:
    """Walk back to testing-of / started-with-inputs; forward to next Tester start or EOF."""
    start = idx
    for j in range(idx, max(-1, idx - 200), -1):
        if "testing of Experts\\BMRG\\BMRG.ex5" in lines[j] and "EURUSD" in lines[j]:
            start = j
            break
    end = len(lines)
    for j in range(idx + 1, len(lines)):
        if "Tester" in lines[j] and "testing of Experts" in lines[j]:
            end = j
            break
        if j > idx + 5 and "started with inputs:" in lines[j] and "EURUSD" in lines[j]:
            # overlapping core start for same run — keep going
            continue
    return start, end


def score(start: int, end: int, label: str) -> dict:
    deals = []
    opens = []
    blocks: dict[str, int] = defaultdict(int)
    final = dep = atr_max = atr_on = tp = sl = window = bb_dev = None
    halt = 0
    net_profit = profit_factor = total_trades = None

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
        m = open_re.search(L)
        if m:
            side = m.group(2)
            px, slp, tpp = float(m.group(4)), float(m.group(5)), float(m.group(6))
            if side == "BUY":
                sl_pts = round((px - slp) / POINT)
                tp_pts = round((tpp - px) / POINT)
            else:
                sl_pts = round((slp - px) / POINT)
                tp_pts = round((px - tpp) / POINT)
            opens.append((side, sl_pts, tp_pts, px))
        if "final balance" in L:
            m2 = re.search(r"final balance ([\d.]+)", L)
            if m2:
                final = float(m2.group(1))
        if "initial deposit" in L:
            m2 = re.search(r"initial deposit ([\d.]+)", L)
            if m2:
                dep = float(m2.group(1))
        if "total net profit" in L.lower() or "Total Net Profit" in L:
            m2 = re.search(r"([\-\d.]+)\s*$", L.strip()) or re.search(
                r"total net profit\s+([\-\d.]+)", L, re.I
            )
            if m2:
                try:
                    net_profit = float(m2.group(1))
                except ValueError:
                    pass
        if "InpATRMaxPoints=" in L:
            atr_max = L.split("=")[-1].strip()
        if "InpUseATRRegime=" in L:
            atr_on = L.split("=")[-1].strip()
        if "InpTP_Points=" in L:
            tp = L.split("=")[-1].strip()
        if "InpSL_Points=" in L:
            sl = L.split("=")[-1].strip()
        if "InpBBDev=" in L:
            bb_dev = L.split("=")[-1].strip()
        m = re.search(
            r"from (\d{4}\.\d{2}\.\d{2}) 00:00 to (\d{4}\.\d{2}\.\d{2}) 00:00", L
        )
        if m:
            window = f"{m.group(1)} -> {m.group(2)}"
        if "Equity halt" in L:
            halt += 1
        m = block_re.search(L)
        if m:
            reason = m.group(2).strip().split("|")[0].strip()
            if reason.startswith("ATR "):
                reason = "ATR > max"
            elif reason.startswith("BB width"):
                reason = "BBw gate"
            blocks[reason] += 1

    # Pair entry/exit deals into trade events (G0 single-leg)
    dlist = [d for d in deals if d["n"] > 1]
    sl_pts_design = float(sl) if sl and sl.replace(".", "", 1).isdigit() else 300.0
    tp_pts_design = float(tp) if tp and tp.replace(".", "", 1).isdigit() else 375.0
    sl_dist = sl_pts_design * POINT
    rr_design = tp_pts_design / sl_pts_design if sl_pts_design else 0.0

    events = []
    j = 0
    while j + 1 < len(dlist):
        a, b = dlist[j], dlist[j + 1]
        # expect opposite sides for round-trip
        if a["side"] == b["side"]:
            j += 1
            continue
        move = (b["px"] - a["px"]) if a["side"] == "buy" else (a["px"] - b["px"])
        r = move / sl_dist if sl_dist else 0.0
        # classify near designed exits
        if r >= 0.85 * rr_design:
            kind = "TP"
        elif r <= -0.85:
            kind = "SL"
        else:
            kind = "other"
        events.append(dict(t=a["t"], side=a["side"], r=r, kind=kind, entry=a["px"], exit=b["px"]))
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
    c_r = COST_RT_PRIOR / sl_pts_design if sl_pts_design else 0.0
    leak = c_r / (r_real + 1.0) if r_real > 0 else 0.0
    ef = bm - leak
    e_n = wr * (r_real + 1.0) - 1.0 if n else 0.0
    # also design-assumed E_N (R≈RR)
    e_n_design = wr * (rr_design + 1.0) - 1.0 if n else 0.0
    bwr_d = 1.0 / (1.0 + rr_design) if rr_design > 0 else 1.0

    tp_lt_sl = sum(1 for _, s, t, _ in opens if t < s)
    sum_r = sum(e["r"] for e in events)

    out = {
        "label": label,
        "window": window,
        "sl": sl,
        "tp": tp,
        "rr_design": round(rr_design, 3),
        "atr_on": atr_on,
        "atr_max": atr_max,
        "bb_dev": bb_dev,
        "deposit": dep,
        "final": final,
        "pnl_currency": (final - dep) if final is not None and dep is not None else None,
        "n_opens": len(opens),
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
        "sum_R": round(sum_r, 3),
        "kinds": {
            "TP": sum(1 for e in events if e["kind"] == "TP"),
            "SL": sum(1 for e in events if e["kind"] == "SL"),
            "other": sum(1 for e in events if e["kind"] == "other"),
        },
        "tp_lt_sl_opens": tp_lt_sl,
        "halt": halt,
        "blocks_top": dict(sorted(blocks.items(), key=lambda kv: -kv[1])[:8]),
        "events_preview": [
            f"{e['t']} {e['side']} R={e['r']:+.2f} {e['kind']}" for e in events[:8]
        ],
    }
    return out


results = []
for k, mi in enumerate(magic_inputs):
    start, end = _run_bounds_from_magic_input(mi)
    label = f"run{k+1}_L{mi+1}"
    r = score(start, end, label)
    results.append(r)
    print("\n====", label, "====")
    for key in (
        "window",
        "sl",
        "tp",
        "rr_design",
        "atr_on",
        "atr_max",
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
        "blocks_top",
    ):
        print(f"  {key}: {r[key]}")
    if r["events_preview"]:
        print("  preview:")
        for p in r["events_preview"]:
            print("   ", p)

# Tip-window slice matching design prior (2026-05-01 → 2026-10-07)
print("\n==== tip window 2026.05.01–2026.10.07 (design prior compare) ====")
tip_results = []
for k, mi in enumerate(magic_inputs):
    start, end = _run_bounds_from_magic_input(mi)
    deals = []
    dep = final = None
    for i in range(start, end):
        L = lines[i]
        m = deal_re.search(L)
        if m:
            deals.append(
                dict(
                    t=m.group(1),
                    n=int(m.group(2)),
                    side=m.group(3),
                    px=float(m.group(5)),
                )
            )
        if "initial deposit" in L:
            m2 = re.search(r"initial deposit ([\d.]+)", L)
            if m2:
                dep = float(m2.group(1))
        if "final balance" in L:
            m2 = re.search(r"final balance ([\d.]+)", L)
            if m2:
                final = float(m2.group(1))
    dlist = [d for d in deals if d["n"] > 1]
    sl_dist = 300 * POINT
    ev = []
    j = 0
    while j + 1 < len(dlist):
        a, b = dlist[j], dlist[j + 1]
        if a["side"] == b["side"]:
            j += 1
            continue
        move = (b["px"] - a["px"]) if a["side"] == "buy" else (a["px"] - b["px"])
        r = move / sl_dist
        ev.append(dict(t=a["t"], r=r, month=a["t"][:7]))
        j += 2
    tip = [e for e in ev if "2026.05.01" <= e["t"] < "2026.10.08"]
    wins = [e for e in tip if e["r"] > 0]
    losses = [e for e in tip if e["r"] < 0]
    n = len(wins) + len(losses)
    wr = len(wins) / n if n else 0.0
    aw = sum(e["r"] for e in wins) / len(wins) if wins else 0.0
    al = abs(sum(e["r"] for e in losses) / len(losses)) if losses else 0.0
    r_real = aw / al if al else 0.0
    bwr = 1.0 / (1.0 + r_real) if r_real else 1.0
    c_r = COST_RT_PRIOR / 300.0
    leak = c_r / (r_real + 1.0) if r_real else 0.0
    ef = wr - bwr - leak
    e_n = wr * (r_real + 1.0) - 1.0 if n else 0.0
    by_m: dict[str, list] = defaultdict(lambda: [0, 0, 0.0])
    for e in tip:
        by_m[e["month"]][0] += 1
        by_m[e["month"]][1] += int(e["r"] > 0)
        by_m[e["month"]][2] += e["r"]
    tip_row = {
        "run": k + 1,
        "dep": dep,
        "final": final,
        "n": n,
        "WR": round(wr, 4),
        "R": round(r_real, 4),
        "BWR": round(bwr, 4),
        "BM_pp": round((wr - bwr) * 100, 2),
        "EF_pp": round(ef * 100, 2),
        "E_N": round(e_n, 4),
        "sum_R": round(sum(e["r"] for e in tip), 3),
        "monthly": {
            m: {
                "n": v[0],
                "WR": round(v[1] / v[0], 3) if v[0] else 0,
                "sum_R": round(v[2], 2),
            }
            for m, v in sorted(by_m.items())
        },
    }
    tip_results.append(tip_row)
    print(
        f"run{k+1}: dep={dep} final={final} n={n} WR={wr:.1%} R={r_real:.3f} "
        f"BWR={bwr:.1%} BM={(wr-bwr)*100:+.1f}pp EF={ef*100:+.1f}pp "
        f"E_N={e_n:+.3f}R sumR={tip_row['sum_R']:+.2f}"
    )
    print("  monthly:", tip_row["monthly"])

out_path = Path(__file__).resolve().parent / "tester_magic_26101816_score.json"
payload = {
    "magic": MAGIC,
    "scored_at": datetime.now(UTC).isoformat(),
    "log": str(log),
    "framework": "unified_edge_framework Stage 0-1 (R from deal pairs; Leak prior 20pt RT)",
    "runs": results,
    "tip_window_202605_20261007": tip_results,
}
out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print("\nwrote", out_path)
