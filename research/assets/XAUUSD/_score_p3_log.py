"""Score BMRG P3 magic 26100918 runs from Tester log."""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

log = Path(
    r"C:\Users\emili\AppData\Roaming\MetaQuotes\Terminal"
    r"\D0E8209F77C8CF37AD8BF550E51FF075\Tester\logs\20261011.log"
)
# MT5 Tester logs are UTF-16 LE
lines = log.read_text(encoding="utf-16", errors="replace").splitlines()

inits = [
    i
    for i, L in enumerate(lines)
    if "magic=26100918" in L and "BMRG init OK" in L
]
finals = [i for i, L in enumerate(lines) if "final balance" in L]
print(f"inits at lines: {[i + 1 for i in inits]}")

open_re = re.compile(
    r"\[BMRG\]\[TRADE\] OPEN (BUY|SELL) lot=([\d.]+) price=([\d.]+) "
    r"sl=([\d.]+) tp=([\d.]+)"
)
deal_re = re.compile(
    r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2})\s+deal #(\d+) "
    r"(buy|sell) ([\d.]+) XAUUSD at ([\d.]+) done"
)
fade_re = re.compile(
    r"Fade setup|fade setup|Fade confirm|Fade expired|fade expired", re.I
)


def score_segment(start: int, end: int, label: str) -> None:
    opens = []
    deals = []
    fade_n: dict[str, int] = defaultdict(int)
    final = None
    deposit = None
    halt_on = 0
    init_line = None
    for i in range(start, end):
        L = lines[i]
        if "BMRG init OK" in L and "26100918" in L:
            init_line = L
        m = open_re.search(L)
        if m:
            side, _lot, px_s, sl_s, tp_s = m.groups()
            px, sl, tp = float(px_s), float(sl_s), float(tp_s)
            if side == "BUY":
                sl_pts = round((px - sl) / 0.01)
                tp_pts = round((tp - px) / 0.01)
            else:
                sl_pts = round((sl - px) / 0.01)
                tp_pts = round((px - tp) / 0.01)
            opens.append(
                dict(side=side, sl_pts=sl_pts, tp_pts=tp_pts, line=i + 1)
            )
        m = deal_re.search(L)
        if m:
            deals.append(
                dict(
                    t=m.group(1),
                    n=int(m.group(2)),
                    side=m.group(3),
                    lot=float(m.group(4)),
                    px=float(m.group(5)),
                    line=i + 1,
                )
            )
        if "final balance" in L:
            m2 = re.search(r"final balance ([\d.]+)", L)
            if m2:
                final = float(m2.group(1))
        if "initial deposit" in L:
            m2 = re.search(r"initial deposit ([\d.]+)", L)
            if m2:
                deposit = float(m2.group(1))
        if "Equity halt" in L or "equity halt" in L:
            halt_on += 1
        if fade_re.search(L):
            if "expired" in L.lower():
                fade_n["expired"] += 1
            elif "confirm" in L.lower():
                fade_n["confirm"] += 1
            elif "setup" in L.lower():
                fade_n["arm"] += 1
            else:
                fade_n["other"] += 1

    events = []
    j = 0
    # Skip deal #1 if balance
    dlist = [d for d in deals if d["n"] > 1]
    while j + 1 < len(dlist):
        entry, exit_ = dlist[j], dlist[j + 1]
        if entry["side"] == "buy":
            move = exit_["px"] - entry["px"]
        else:
            move = entry["px"] - exit_["px"]
        r = move / 12.0  # SL = 1200 pts = 12.00 price
        events.append(
            dict(entry=entry, exit=exit_, move=move, r=r, win=move > 0)
        )
        j += 2

    wins = [e for e in events if e["win"]]
    losses = [e for e in events if not e["win"]]
    n = len(events)
    wr = (len(wins) / n * 100) if n else 0.0
    aw = (sum(e["r"] for e in wins) / len(wins)) if wins else 0.0
    al = (abs(sum(e["r"] for e in losses) / len(losses))) if losses else 0.0
    R = (aw / al) if al else float("nan")
    bwr = (1 / (1 + R) * 100) if R == R and R > 0 else float("nan")
    en = (wr / 100) * (R + 1) - 1 if R == R else float("nan")
    bm = wr - bwr if bwr == bwr else float("nan")
    tp_hit = sum(1 for e in events if e["r"] >= 1.2)
    sl_hit = sum(1 for e in events if e["r"] <= -0.85)
    other = n - tp_hit - sl_hit

    print(f"\n===== {label} lines {start + 1}-{end} =====")
    if init_line:
        idx = init_line.find("[BMRG]")
        print("INIT", init_line[idx : idx + 200])
    print(
        f"deposit={deposit} final={final}  opens={len(opens)} "
        f"deals={len(deals)} events={n}"
    )
    if opens:
        o = opens[0]
        rr = o["tp_pts"] / o["sl_pts"] if o["sl_pts"] else None
        print(f"geom sample: {o['side']} SL={o['sl_pts']} TP={o['tp_pts']} RR={rr}")
        rrs = sorted({round(x["tp_pts"] / x["sl_pts"], 3) for x in opens if x["sl_pts"]})
        print(f"RR set: {rrs}")
    print(
        f"WR={wr:.1f}% W/L={len(wins)}/{len(losses)} "
        f"AW={aw:.3f}R AL={al:.3f}R R={R:.3f} "
        f"BWR={bwr:.1f}% BM={bm:+.1f}pp E_N={en:+.3f}R"
    )
    print(f"exits: TP>={1.2}R:{tp_hit} SL<=-0.85R:{sl_hit} other:{other}")
    print(f"fade: {dict(fade_n)} equity_halt_lines={halt_on}")
    if events:
        def fmt(e):
            return (e["entry"]["t"], e["entry"]["side"], round(e["r"], 2))

        print("first3:", [fmt(e) for e in events[:3]])
        print("last3:", [fmt(e) for e in events[-3:]])


for stamp in ["23:51:59", "23:52:34", "23:53:11"]:
    idxs = [
        i
        for i, L in enumerate(lines)
        if f"\t{stamp}." in L and "\tCore 01\t" in L
    ]
    if not idxs:
        print("no", stamp)
        continue
    score_segment(min(idxs), max(idxs) + 1, f"WALL {stamp}")

# Later truncated / re-runs
print("\n--- finals after first P3 init ---")
for i in finals:
    if i < inits[0]:
        continue
    print(f"L{i + 1}: {lines[i].strip()[-100:]}")

# Check InpUseFadeConfirm in dumped inputs near P3
print("\n--- Fade input dumps near P3 ---")
for i, L in enumerate(lines):
    if i < inits[0]:
        continue
    if "InpUseFadeConfirm" in L or "InpFadeConfirm" in L:
        print(f"L{i + 1}: {L.strip()[-120:]}")
