"""Score BMRG P4 magic 26100919 from latest Tester log."""
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
    r"(buy|sell) ([\d.]+) XAUUSD at ([\d.]+) done"
)
open_re = re.compile(
    r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}).*\[BMRG\]\[TRADE\] OPEN "
    r"(BUY|SELL) lot=([\d.]+) price=([\d.]+) sl=([\d.]+) tp=([\d.]+)"
)
block_re = re.compile(
    r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}).*Entry blocked: (.+)"
)

inits = [
    i
    for i, L in enumerate(lines)
    if "magic=26100919" in L and "BMRG init OK" in L
]


def score(start: int, end: int, label: str) -> None:
    deals = []
    opens = []
    blocks: dict[str, int] = defaultdict(int)
    final = dep = fade = atr_max = bbw_max = tp = sl = window = None
    halt = 0

    for i in range(start, end):
        L = lines[i]
        if "BMRG init OK" in L and "26100919" in L:
            m = re.search(r"fade=(\d)", L)
            if m:
                fade = m.group(1)
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
        m = open_re.search(L)
        if m:
            side = m.group(2)
            px, slp, tpp = float(m.group(4)), float(m.group(5)), float(m.group(6))
            if side == "BUY":
                sl_pts = round((px - slp) / 0.01)
                tp_pts = round((tpp - px) / 0.01)
            else:
                sl_pts = round((slp - px) / 0.01)
                tp_pts = round((px - tpp) / 0.01)
            opens.append((side, sl_pts, tp_pts))
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
        if "InpBBWidthMaxPct=" in L:
            bbw_max = L.split("=")[-1].strip()
        if "InpTP_Points=" in L:
            tp = L.split("=")[-1].strip()
        if "InpSL_Points=" in L:
            sl = L.split("=")[-1].strip()
        if "InpUseFadeConfirm=" in L:
            pass
        m = re.search(r"from ([\d.]+) 00:00 to ([\d.]+) 00:00", L)
        if m:
            window = f"{m.group(1)} -> {m.group(2)}"
        if "Equity halt" in L:
            halt += 1
        m = block_re.search(L)
        if m:
            reason = m.group(2).strip().split("|")[0].strip()
            # collapse ATR numeric variants
            if reason.startswith("ATR "):
                reason = "ATR > max"
            elif reason.startswith("BB width"):
                if ">" in reason:
                    reason = "BBw > max"
                elif "<" in reason:
                    reason = "BBw < min"
            blocks[reason] += 1

    dlist = [d for d in deals if d["n"] > 1]
    # RR=1 → SL distance 12.0 price
    sl_dist = 12.0
    ev = []
    j = 0
    while j + 1 < len(dlist):
        a, b = dlist[j], dlist[j + 1]
        move = (b["px"] - a["px"]) if a["side"] == "buy" else (a["px"] - b["px"])
        r = move / sl_dist
        kind = "TP" if r >= 0.85 else ("SL" if r <= -0.85 else "other")
        ev.append(
            dict(
                t=a["t"],
                side=a["side"],
                r=r,
                win=r > 0,
                kind=kind,
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
    # design BWR for RR=1 is 50%
    en = (wr / 100) * (R + 1) - 1 if R == R else float("nan")
    bm = wr - bwr if bwr == bwr else float("nan")
    design_bwr = 50.0
    bm_design = wr - design_bwr

    by_m: dict[str, list] = defaultdict(lambda: [0, 0, 0.0])
    for e in ev:
        by_m[e["month"]][0] += 1
        by_m[e["month"]][1] += int(e["win"])
        by_m[e["month"]][2] += e["r"]

    def bucket(t: str) -> str:
        if t < "2026.07.16":
            return "pre_Jul16"
        if t < "2026.09.01":
            return "Jul16_Aug31"
        return "post_Aug"

    bk: dict[str, list] = defaultdict(lambda: [0, 0, 0.0])
    for e in ev:
        b = bucket(e["t"])
        bk[b][0] += 1
        bk[b][1] += int(e["win"])
        bk[b][2] += e["r"]

    tp_n = sum(1 for e in ev if e["kind"] == "TP")
    sl_n = sum(1 for e in ev if e["kind"] == "SL")
    oth = n - tp_n - sl_n
    d_pnl = round(final - dep, 2) if final is not None and dep is not None else None

    print(f"\n===== {label} L{start+1}-{end} =====")
    print(f"window={window} dep={dep} final={final} dPnL={d_pnl}")
    print(f"fade={fade} SL={sl} TP={tp} ATRmax={atr_max} BBwMax={bbw_max}")
    if opens:
        print(
            f"geom sample SL/TP pts={opens[0][1]}/{opens[0][2]} "
            f"RR={opens[0][2]/opens[0][1]:.2f} n_opens={len(opens)}"
        )
    print(
        f"n={n} WR={wr:.1f}% W/L={len(wins)}/{len(losses)} "
        f"AW={aw:.3f}R AL={al:.3f}R R={R:.3f}"
    )
    print(
        f"design BWR=50% BM_design={bm_design:+.1f}pp | "
        f"blotter BWR={bwr:.1f}% BM={bm:+.1f}pp E_N={en:+.3f}R"
    )
    print(f"exits TP/SL/other={tp_n}/{sl_n}/{oth} equity_halt_lines={halt}")
    print(
        "monthly:",
        {
            m: f"n={v[0]} WR={v[1]/v[0]*100:.0f}% sumR={v[2]:+.1f}"
            for m, v in sorted(by_m.items())
        },
    )
    print(
        "buckets:",
        {
            b: f"n={v[0]} WR={v[1]/v[0]*100:.0f}% sumR={v[2]:+.1f}"
            for b, v in sorted(bk.items())
            if v[0]
        },
    )
    print("top blocks:", dict(sorted(blocks.items(), key=lambda x: -x[1])[:8]))
    if ev:
        print("first3:", [(e["t"], e["side"], e["kind"], round(e["r"], 2)) for e in ev[:3]])
        print("last3:", [(e["t"], e["side"], e["kind"], round(e["r"], 2)) for e in ev[-3:]])


# Segment by wall-clock stamp on each init
for k, init_i in enumerate(inits):
    m = re.search(r"\t(\d{2}:\d{2}:\d{2})\.", lines[init_i])
    stamp = m.group(1) if m else None
    if stamp:
        idxs = [
            i
            for i, L in enumerate(lines)
            if f"\t{stamp}." in L and "\tCore 01\t" in L
        ]
        start, end = min(idxs), max(idxs) + 1
    else:
        start = init_i
        end = inits[k + 1] if k + 1 < len(inits) else len(lines)
    score(start, end, f"RUN{k+1} wall={stamp}")
