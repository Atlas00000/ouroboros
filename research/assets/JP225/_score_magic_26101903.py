"""Score BMRG JP225/JPN225 magic 26101903 runs from Tester log snapshot."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

MAGIC = "26101903"
SYMBOL = "JPN225"
POINT = 0.01  # Digits=2 Nikkei CFD
COST_RT_PRIOR = 2500.0  # pts; matches P0 spread~2300 + slip prior
# Design prior tip (preset card window)
TIP_START = "2026.05.01"
TIP_END = "2026.10.08"  # exclusive upper for string compare on deal timestamps

snap = Path(__file__).resolve().parent / "_tester_20261019_snap.log"
if snap.exists():
    log = snap
else:
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
    rf"(\d{{4}}\.\d{{2}}\.\d{{2}} \d{{2}}:\d{{2}}:\d{{2}})\s+deal #(\d+) "
    rf"(buy|sell) ([\d.]+) {SYMBOL} at ([\d.]+) done"
)
open_re = re.compile(
    r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}).*\[BMRG\]\[TRADE\] OPEN "
    r"(BUY|SELL) lot=([\d.]+) price=([\d.]+) sl=([\d.]+) tp=([\d.]+)"
)
block_re = re.compile(
    r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}).*Entry blocked: (.+)"
)

magic_inputs = [i for i, L in enumerate(lines) if f"InpMagic={MAGIC}" in L]
print("InpMagic lines:", len(magic_inputs))


def _run_bounds_from_magic_input(idx: int) -> tuple[int, int]:
    start = idx
    for j in range(idx, max(-1, idx - 250), -1):
        if "testing of Experts\\BMRG\\BMRG.ex5" in lines[j] and SYMBOL in lines[j]:
            start = j
            break
    end = len(lines)
    for j in range(idx + 1, len(lines)):
        if "Tester" in lines[j] and "testing of Experts" in lines[j]:
            end = j
            break
    return start, end


def _pair_events(dlist: list[dict], sl_dist: float, rr_design: float) -> list[dict]:
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
            dict(
                t=a["t"],
                side=a["side"],
                r=r,
                kind=kind,
                entry=a["px"],
                exit=b["px"],
                month=a["t"][:7],
            )
        )
        j += 2
    return events


def _metrics(events: list[dict], sl_pts: float, rr_design: float) -> dict:
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
    by_m: dict[str, list] = defaultdict(lambda: [0, 0, 0.0])
    for e in events:
        by_m[e["month"]][0] += 1
        by_m[e["month"]][1] += int(e["r"] > 0)
        by_m[e["month"]][2] += e["r"]
    return {
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
        "monthly": {
            m: {
                "n": v[0],
                "WR": round(v[1] / v[0], 3) if v[0] else 0,
                "sum_R": round(v[2], 2),
            }
            for m, v in sorted(by_m.items())
        },
    }


def score(start: int, end: int, label: str) -> dict:
    deals = []
    opens = []
    blocks: dict[str, int] = defaultdict(int)
    final = dep = atr_max = atr_on = tp = sl = window = bb_dev = None
    halt = 0

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

    dlist = [d for d in deals if d["n"] > 1]
    sl_pts_design = float(sl) if sl and sl.replace(".", "", 1).isdigit() else 23260.0
    tp_pts_design = float(tp) if tp and tp.replace(".", "", 1).isdigit() else 34890.0
    sl_dist = sl_pts_design * POINT
    rr_design = tp_pts_design / sl_pts_design if sl_pts_design else 0.0
    events = _pair_events(dlist, sl_dist, rr_design)
    metrics = _metrics(events, sl_pts_design, rr_design)
    tip = [e for e in events if TIP_START <= e["t"] < TIP_END]
    tip_m = _metrics(tip, sl_pts_design, rr_design)

    tp_lt_sl = sum(1 for _, s, t, _ in opens if t < s)
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
        "tp_lt_sl_opens": tp_lt_sl,
        "halt": halt,
        "blocks_top": dict(sorted(blocks.items(), key=lambda kv: -kv[1])[:8]),
        "full": metrics,
        "tip_202605_20261007": tip_m,
        "events_preview": [
            f"{e['t']} {e['side']} R={e['r']:+.2f} {e['kind']}" for e in events[:8]
        ],
        "events_tail": [
            f"{e['t']} {e['side']} R={e['r']:+.2f} {e['kind']}" for e in events[-6:]
        ],
    }
    return out


results = []
for k, mi in enumerate(magic_inputs):
    start, end = _run_bounds_from_magic_input(mi)
    label = f"run{k + 1}_L{mi + 1}"
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
        "bb_dev",
        "deposit",
        "final",
        "pnl_currency",
        "n_opens",
        "n_deal_pairs",
        "tp_lt_sl_opens",
        "halt",
        "blocks_top",
    ):
        print(f"  {key}: {r[key]}")
    f = r["full"]
    print(
        f"  FULL: n={f['n_scored']} WR={f['WR']:.1%} R={f['R']:.3f} "
        f"BWR={f['BWR']:.1%} BM={f['BM']*100:+.1f}pp EF={f['EF_prior']*100:+.1f}pp "
        f"E_N={f['E_N']:+.3f} sumR={f['sum_R']:+.2f} kinds={f['kinds']}"
    )
    print(f"  FULL monthly: {f['monthly']}")
    t = r["tip_202605_20261007"]
    print(
        f"  TIP:  n={t['n_scored']} WR={t['WR']:.1%} R={t['R']:.3f} "
        f"BWR={t['BWR']:.1%} BM={t['BM']*100:+.1f}pp EF={t['EF_prior']*100:+.1f}pp "
        f"E_N={t['E_N']:+.3f} sumR={t['sum_R']:+.2f} kinds={t['kinds']}"
    )
    print(f"  TIP monthly: {t['monthly']}")
    if r["events_preview"]:
        print("  preview:")
        for p in r["events_preview"]:
            print("   ", p)

out_path = Path(__file__).resolve().parent / "tester_magic_26101903_score.json"
payload = {
    "magic": MAGIC,
    "symbol": SYMBOL,
    "scored_at": datetime.now(UTC).isoformat(),
    "log": str(log),
    "framework": (
        "unified_edge_framework Stage 0-1 (R from deal pairs; "
        f"Leak prior {COST_RT_PRIOR:g}pt RT · Point={POINT})"
    ),
    "design_prior": {
        "sl": 23260,
        "tp": 34890,
        "rr": 1.5,
        "atr_max": 19670,
        "probe_n": 139,
        "probe_WR": 0.4748,
        "probe_EF_pp": 3.2,
        "probe_E_N": 0.187,
        "tip_window": f"{TIP_START} -> 2026.10.07",
    },
    "hard_rule": "never TP < SL",
    "runs": results,
}
out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print("\nwrote", out_path)
