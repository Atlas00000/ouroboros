"""Score latest BRENT/XBRUSD BMRG runs by magic."""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

log = sorted(
    Path(
        r"C:\Users\emili\AppData\Roaming\MetaQuotes\Terminal"
        r"\D0E8209F77C8CF37AD8BF550E51FF075\Tester\logs"
    ).glob("*.log"),
    key=lambda p: p.stat().st_mtime,
    reverse=True,
)[0]
lines = log.read_text(encoding="utf-16", errors="replace").splitlines()
print("log", log.name, "lines", len(lines))

deal_re = re.compile(
    r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2})\s+deal #(\d+) "
    r"(buy|sell) ([\d.]+) (\w+) at ([\d.]+) done"
)
open_re = re.compile(
    r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}).*\[BMRG\]\[TRADE\] OPEN "
    r"(BUY|SELL) lot=([\d.]+) price=([\d.]+) sl=([\d.]+) tp=([\d.]+)"
)
bar_re = re.compile(
    r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}).*ATR=([\d.]+)pt BBw=([\d.]+)%"
)

inits = [(i, L) for i, L in enumerate(lines) if "BMRG init OK" in L]
print(f"inits: {len(inits)}")
for i, L in inits[-8:]:
    stamp = re.search(r"\t(\d{2}:\d{2}:\d{2})\.", L)
    print(f"  L{i+1} @{stamp.group(1) if stamp else '?'} {L[L.find('[BMRG]'):L.find('[BMRG]')+200]}")


def score(stamp: str, mag_hint: str | None = None) -> None:
    idxs = [
        i
        for i, L in enumerate(lines)
        if f"\t{stamp}." in L and "\tCore 01\t" in L
    ]
    if not idxs:
        print(stamp, "no lines")
        return
    start, end = min(idxs), max(idxs) + 1
    deals = []
    opens = []
    bars = {}
    final = dep = fade = magic = sym = atr_max = tp = sl = window = None
    blocks: dict[str, int] = defaultdict(int)
    halt = 0

    for i in range(start, end):
        L = lines[i]
        if "BMRG init OK" in L:
            m = re.search(
                r"BMRG init OK \| (\w+) .* magic=(\d+).*fade=(\d)", L
            )
            if m:
                sym, magic, fade = m.group(1), m.group(2), m.group(3)
        m = deal_re.search(L)
        if m:
            deals.append(
                dict(
                    t=m.group(1),
                    n=int(m.group(2)),
                    side=m.group(3),
                    sym=m.group(5),
                    px=float(m.group(6)),
                )
            )
        m = open_re.search(L)
        if m:
            side = m.group(2)
            px, slp, tpp = float(m.group(4)), float(m.group(5)), float(m.group(6))
            # point guess from SL distance
            opens.append(dict(t=m.group(1), side=side, px=px, sl=slp, tp=tpp))
        m = bar_re.search(L)
        if m:
            bars[m.group(1)] = (float(m.group(2)), float(m.group(3)))
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
        if "InpTP_Points=" in L:
            tp = L.split("=")[-1].strip()
        if "InpSL_Points=" in L:
            sl = L.split("=")[-1].strip()
        m = re.search(r"from ([\d.]+) 00:00 to ([\d.]+) 00:00", L)
        if m:
            window = f"{m.group(1)}->{m.group(2)}"
        if "Equity halt" in L:
            halt += 1
        if "Entry blocked:" in L:
            reason = L.split("Entry blocked:")[-1].strip().split("|")[0].strip()
            if reason.startswith("ATR "):
                reason = "ATR > max"
            blocks[reason] += 1

    if mag_hint and magic and magic != mag_hint:
        pass

    # Infer point size from first open SL distance vs InpSL
    sl_pts = float(sl) if sl and sl.replace(".", "", 1).isdigit() else 250.0
    point = None
    if opens:
        o = opens[0]
        raw = abs(o["px"] - o["sl"])
        point = raw / sl_pts if sl_pts else None
    sl_dist = sl_pts * point if point else None

    # Pair deals (skip #1 balance if present)
    dlist = [d for d in deals if d["n"] > 1]
    # Prefer symbol matching init
    if sym:
        dlist = [d for d in dlist if d["sym"] == sym] or dlist

    ev = []
    j = 0
    while j + 1 < len(dlist):
        a, b = dlist[j], dlist[j + 1]
        move = (b["px"] - a["px"]) if a["side"] == "buy" else (a["px"] - b["px"])
        r = move / sl_dist if sl_dist else float("nan")
        # hold
        from datetime import datetime

        t0 = datetime.strptime(a["t"], "%Y.%m.%d %H:%M:%S")
        t1 = datetime.strptime(b["t"], "%Y.%m.%d %H:%M:%S")
        hold_h = (t1 - t0).total_seconds() / 3600
        atr = bars.get(a["t"], (None, None))[0]
        kind = "TP" if r == r and r >= 0.85 else ("SL" if r == r and r <= -0.85 else "other")
        ev.append(
            dict(
                t=a["t"],
                side=a["side"],
                r=r,
                win=r > 0 if r == r else False,
                kind=kind,
                hold_h=hold_h,
                atr=atr,
                month=a["t"][:7],
            )
        )
        j += 2

    wins = [e for e in ev if e["win"]]
    losses = [e for e in ev if not e["win"]]
    n = len(ev)
    wr = len(wins) / n * 100 if n else 0.0
    aw = sum(e["r"] for e in wins) / len(wins) if wins else 0.0
    al = abs(sum(e["r"] for e in losses) / len(losses)) if losses else 0.0
    R = aw / al if al else float("nan")
    bwr = 1 / (1 + R) * 100 if R == R else float("nan")
    en = (wr / 100) * (R + 1) - 1 if R == R else float("nan")
    bm = wr - bwr if bwr == bwr else float("nan")
    tp_n = sum(1 for e in ev if e["kind"] == "TP")
    sl_n = sum(1 for e in ev if e["kind"] == "SL")
    oth = n - tp_n - sl_n

    by_m = defaultdict(lambda: [0, 0, 0.0])
    for e in ev:
        by_m[e["month"]][0] += 1
        by_m[e["month"]][1] += int(e["win"])
        by_m[e["month"]][2] += e["r"] if e["r"] == e["r"] else 0

    holds_w = [e["hold_h"] for e in wins] or [0]
    holds_l = [e["hold_h"] for e in losses] or [0]
    fast_sl = sum(1 for e in losses if e["hold_h"] < 1.0)

    print(f"\n===== magic={magic} wall={stamp} sym={sym} =====")
    print(f"window={window} dep={dep} final={final} dPnL={None if dep is None or final is None else round(final-dep,2)}")
    print(
        f"fade={fade} SL/TP inp={sl}/{tp} ATRmax={atr_max} "
        f"point~={point} sl_dist~={sl_dist}"
    )
    print(f"opens={len(opens)} events={n} WR={wr:.1f}% W/L={len(wins)}/{len(losses)}")
    print(f"AW={aw:.3f}R AL={al:.3f}R R={R:.3f} BWR={bwr:.1f}% BM={bm:+.1f}pp E_N={en:+.3f}R")
    print(f"exits TP/SL/other={tp_n}/{sl_n}/{oth} halt_lines={halt}")
    print(f"loss hold: med={sorted(holds_l)[len(holds_l)//2]:.2f}h fast<1h={fast_sl}/{len(losses)}")
    print(f"win hold: med={sorted(holds_w)[len(holds_w)//2]:.2f}h")
    print(
        "monthly:",
        {
            m: f"n={v[0]} WR={v[1]/v[0]*100:.0f}% sumR={v[2]:+.1f}"
            for m, v in sorted(by_m.items())
        },
    )
    print("top blocks:", dict(sorted(blocks.items(), key=lambda x: -x[1])[:6]))
    if losses:
        print("worst losses:")
        for e in sorted(losses, key=lambda x: x["r"])[:6]:
            print(
                f"  {e['t']} {e['side']} {e['kind']} r={e['r']:+.2f} "
                f"hold={e['hold_h']:.2f}h ATR={e['atr']}"
            )


# Score last few inits (prefer 26101221)
stamps = []
for i, L in inits:
    m = re.search(r"\t(\d{2}:\d{2}:\d{2})\.", L)
    mag = re.search(r"magic=(\d+)", L)
    if m and mag:
        stamps.append((m.group(1), mag.group(1)))

# unique last occurrence per magic, keep order
seen = {}
for stamp, mag in stamps:
    seen[mag] = stamp
# score all recent magics from tonight after 01:36 or all last 6
for stamp, mag in stamps[-6:]:
    score(stamp, mag)
