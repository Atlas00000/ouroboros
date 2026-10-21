"""Compare what drove collapses vs the clean short-window P3 run."""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

lines = Path(
    r"C:\Users\emili\AppData\Roaming\MetaQuotes\Terminal"
    r"\D0E8209F77C8CF37AD8BF550E51FF075\Tester\logs\20261011.log"
).read_text(encoding="utf-16", errors="replace").splitlines()

deal_re = re.compile(
    r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2})\s+deal #(\d+) "
    r"(buy|sell) ([\d.]+) XAUUSD at ([\d.]+) done"
)


def parse_run(stamp: str, label: str) -> None:
    idxs = [
        i
        for i, L in enumerate(lines)
        if f"\t{stamp}." in L and "\tCore 01\t" in L
    ]
    if not idxs:
        print(label, "NO DATA")
        return
    start, end = min(idxs), max(idxs) + 1
    deals = []
    final = dep = fade = magic = tp_in = fade_inp = window = None
    halt_lines = 0
    first_halt = None
    equity_blocks = 0

    for i in range(start, end):
        L = lines[i]
        if "BMRG init OK" in L:
            m = re.search(r"magic=(\d+).*fade=(\d)", L)
            if m:
                magic, fade = m.group(1), m.group(2)
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
        if "final balance" in L:
            m2 = re.search(r"final balance ([\d.]+)", L)
            if m2:
                final = float(m2.group(1))
        if "initial deposit" in L:
            m2 = re.search(r"initial deposit ([\d.]+)", L)
            if m2:
                dep = float(m2.group(1))
        if "InpTP_Points=" in L:
            tp_in = L.split("=")[-1].strip()
        if "InpUseFadeConfirm=" in L:
            fade_inp = L.split("=")[-1].strip()
        m = re.search(r"from ([\d.]+) 00:00 to ([\d.]+) 00:00", L)
        if m:
            window = f"{m.group(1)} -> {m.group(2)}"
        if "Equity halt ON" in L or ("dd=" in L and "halt" in L.lower()):
            halt_lines += 1
            if first_halt is None:
                tm = re.search(r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2})", L)
                dd = re.search(r"dd=([\d.]+)", L)
                first_halt = (
                    tm.group(1) if tm else "?",
                    dd.group(1) if dd else "?",
                )
        if "Entry blocked: equity" in L or "equity halt" in L.lower():
            equity_blocks += 1

    dlist = [d for d in deals if d["n"] > 1]
    ev = []
    j = 0
    while j + 1 < len(dlist):
        a, b = dlist[j], dlist[j + 1]
        move = (b["px"] - a["px"]) if a["side"] == "buy" else (a["px"] - b["px"])
        r = move / 12.0
        ev.append(
            dict(t=a["t"], side=a["side"], r=r, win=r > 0, month=a["t"][:7])
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

    cum = 0.0
    min_cum = 0.0
    by_m: dict[str, list] = defaultdict(lambda: [0, 0, 0.0])
    for e in ev:
        cum += e["r"]
        min_cum = min(min_cum, cum)
        by_m[e["month"]][0] += 1
        by_m[e["month"]][1] += int(e["win"])
        by_m[e["month"]][2] += e["r"]

    max_streak = streak = 0
    for e in ev:
        if not e["win"]:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0

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

    d_pnl = None if not (dep and final) else round(final - dep, 2)
    print(f"\n=== {label} wall={stamp} ===")
    print(f"  magic={magic} fade={fade} fade_inp={fade_inp} TP={tp_in}")
    print(f"  window={window} dep={dep} final={final} dPnL={d_pnl}")
    print(
        f"  n={n} WR={wr:.1f}% R={R:.3f} BWR={bwr:.1f}% "
        f"BM={wr - bwr:+.1f}pp E_N={en:+.3f}R"
    )
    print(
        f"  cumR={cum:+.2f} minCumR={min_cum:+.2f} maxLossStreak={max_streak}"
    )
    print(
        f"  first_halt={first_halt} halt_lines={halt_lines} "
        f"equity_related={equity_blocks}"
    )
    print(
        "  monthly:",
        {
            m: f"n={v[0]} WR={v[1] / v[0] * 100:.0f}% sumR={v[2]:+.1f}"
            for m, v in sorted(by_m.items())
        },
    )
    print(
        "  buckets:",
        {
            b: f"n={v[0]} WR={v[1] / v[0] * 100:.0f}% sumR={v[2]:+.1f}"
            for b, v in sorted(bk.items())
            if v[0]
        },
    )


runs = [
    ("23:51:59", "P3 contamin fade1 dep400 COLLAPSE"),
    ("23:52:34", "P3 contamin fade1 dep1000 OK-ish"),
    ("23:53:11", "P3 contamin fade1 dep500 weak"),
    ("23:57:13", "late contamin dep500"),
    ("23:58:26", "P3 CLEAN fade0 SHORT Jul16-Aug31"),
]

# P2 fadeConfirm init stamp
for i, L in enumerate(lines):
    if "magic=26100917" in L and "BMRG init OK" in L:
        m = re.search(r"\t(\d{2}:\d{2}:\d{2})\.", L)
        if m:
            runs.insert(0, (m.group(1), "P2 fadeConfirm 26100917"))
        break

for stamp, label in runs:
    parse_run(stamp, label)

# Cross-cut: on the $1000 full run, how does Jul16-Aug31 alone look?
print("\n=== KEY: same trades as clean window, inside $1000 full run ===")
parse_run("23:52:34", "(reprise) — see Jul16_Aug31 bucket above")
