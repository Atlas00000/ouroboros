"""Attribute poor WR / DD in bad windows vs Jul16-Aug31 good pocket."""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

lines = Path(
    r"C:\Users\emili\AppData\Roaming\MetaQuotes\Terminal"
    r"\D0E8209F77C8CF37AD8BF550E51FF075\Tester\logs\20261011.log"
).read_text(encoding="utf-16", errors="replace").splitlines()

# Canonical full-window P3 contamin $1000 run
STAMP = "23:52:34"
idxs = [
    i
    for i, L in enumerate(lines)
    if f"\t{STAMP}." in L and "\tCore 01\t" in L
]
start, end = min(idxs), max(idxs) + 1

deal_re = re.compile(
    r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2})\s+deal #(\d+) "
    r"(buy|sell) ([\d.]+) XAUUSD at ([\d.]+) done"
)
open_re = re.compile(
    r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}).*\[BMRG\]\[TRADE\] OPEN "
    r"(BUY|SELL) lot=([\d.]+) price=([\d.]+) sl=([\d.]+) tp=([\d.]+)"
)
bar_re = re.compile(
    r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}).*\[BMRG\]\[INFO\] bar="
    r"[\d. :]+ U=([\d.]+) M=([\d.]+) L=([\d.]+) C=([\d.]+) "
    r"ATR=([\d.]+)pt BBw=([\d.]+)% side=(\w+) n=(\d+)"
)
block_re = re.compile(
    r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}).*Entry blocked: (.+)"
)

deals = []
opens = []
bars_by_t = {}
blocks = defaultdict(int)

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
    m = open_re.search(L)
    if m:
        opens.append(
            dict(
                t=m.group(1),
                side=m.group(2),
                px=float(m.group(4)),
                sl=float(m.group(5)),
                tp=float(m.group(6)),
            )
        )
    m = bar_re.search(L)
    if m:
        bars_by_t[m.group(1)] = dict(
            atr=float(m.group(6)),
            bbw=float(m.group(7)),
            side=m.group(8),
            n=int(m.group(9)),
            mid=float(m.group(3)),
            close=float(m.group(5)),
        )
    m = block_re.search(L)
    if m:
        reason = m.group(2).strip()
        # normalize
        reason = reason.split("|")[0].strip()
        blocks[reason] += 1

# Pair events
dlist = [d for d in deals if d["n"] > 1]
ev = []
j = 0
oi = 0
while j + 1 < len(dlist):
    a, b = dlist[j], dlist[j + 1]
    move = (b["px"] - a["px"]) if a["side"] == "buy" else (a["px"] - b["px"])
    r = move / 12.0
    # match open
    op = opens[oi] if oi < len(opens) else None
    oi += 1
    # bar context: look for bar line at same timestamp or nearby
    ctx = bars_by_t.get(a["t"])
    if ctx is None:
        # try find closest bar at/after entry within same minute stamp family
        for dt, bar in bars_by_t.items():
            if dt[:16] == a["t"][:16]:
                ctx = bar
                break
    hour = int(a["t"][11:13])
    weekday = __import__("datetime").datetime.strptime(
        a["t"][:10], "%Y.%m.%d"
    ).strftime("%a")

    def bucket(t: str) -> str:
        if t < "2026.07.16":
            return "bad_pre"
        if t < "2026.09.01":
            return "good_mid"
        return "bad_post"

    # extension beyond band: |C-mid| vs ATR
    ext = None
    if ctx:
        if a["side"] == "buy":
            ext = (ctx["mid"] - a["px"]) / (ctx["atr"] * 0.01) if ctx["atr"] else None
        else:
            ext = (a["px"] - ctx["mid"]) / (ctx["atr"] * 0.01) if ctx["atr"] else None

    # hold time
    t0 = __import__("datetime").datetime.strptime(a["t"], "%Y.%m.%d %H:%M:%S")
    t1 = __import__("datetime").datetime.strptime(b["t"], "%Y.%m.%d %H:%M:%S")
    hold_h = (t1 - t0).total_seconds() / 3600

    kind = "TP" if r >= 1.2 else ("SL" if r <= -0.85 else "other")
    ev.append(
        dict(
            t=a["t"],
            side=a["side"].upper(),
            r=r,
            win=r > 0,
            kind=kind,
            bucket=bucket(a["t"]),
            hour=hour,
            weekday=weekday,
            atr=ctx["atr"] if ctx else None,
            bbw=ctx["bbw"] if ctx else None,
            ext=ext,
            hold_h=hold_h,
            exit_t=b["t"],
        )
    )
    j += 2


def summarize(name: str, rows: list) -> None:
    if not rows:
        print(f"\n{name}: empty")
        return
    n = len(rows)
    wr = sum(1 for e in rows if e["win"]) / n * 100
    sum_r = sum(e["r"] for e in rows)
    atrs = [e["atr"] for e in rows if e["atr"] is not None]
    bbws = [e["bbw"] for e in rows if e["bbw"] is not None]
    exts = [e["ext"] for e in rows if e["ext"] is not None]
    holds = [e["hold_h"] for e in rows]
    by_side = defaultdict(lambda: [0, 0])
    by_wd = defaultdict(lambda: [0, 0])
    by_hr = defaultdict(lambda: [0, 0])
    by_kind = defaultdict(int)
    for e in rows:
        by_side[e["side"]][0] += 1
        by_side[e["side"]][1] += int(e["win"])
        by_wd[e["weekday"]][0] += 1
        by_wd[e["weekday"]][1] += int(e["win"])
        by_hr[e["hour"]][0] += 1
        by_hr[e["hour"]][1] += int(e["win"])
        by_kind[e["kind"]] += 1

    def avg(xs):
        return sum(xs) / len(xs) if xs else float("nan")

    print(f"\n=== {name} n={n} WR={wr:.0f}% sumR={sum_r:+.1f} ===")
    print(
        f"  ATR pt: mean={avg(atrs):.0f} med={sorted(atrs)[len(atrs)//2] if atrs else 'na'}"
    )
    print(
        f"  BBw %:  mean={avg(bbws):.2f} med={sorted(bbws)[len(bbws)//2] if bbws else 'na'}"
    )
    print(
        f"  |ext|/ATR: mean={avg(exts):.2f}  hold_h: mean={avg(holds):.1f} "
        f"med={sorted(holds)[len(holds)//2]:.1f}"
    )
    print(f"  exits: {dict(by_kind)}")
    print(
        "  side:",
        {
            s: f"n={v[0]} WR={v[1]/v[0]*100:.0f}%"
            for s, v in sorted(by_side.items())
        },
    )
    print(
        "  weekday:",
        {
            d: f"n={v[0]} WR={v[1]/v[0]*100:.0f}%"
            for d, v in sorted(by_wd.items(), key=lambda x: ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"].index(x[0]) if x[0] in ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"] else 99)
        },
    )
    # hour bands
    bands = {"12-14": [0, 0], "15-17": [0, 0], "18-20": [0, 0]}
    for e in rows:
        if 12 <= e["hour"] <= 14:
            b = "12-14"
        elif 15 <= e["hour"] <= 17:
            b = "15-17"
        else:
            b = "18-20"
        bands[b][0] += 1
        bands[b][1] += int(e["win"])
    print(
        "  session:",
        {k: f"n={v[0]} WR={v[1]/v[0]*100:.0f}%" for k, v in bands.items() if v[0]},
    )
    # ATR terciles within this bucket
    if atrs:
        xs = sorted(atrs)
        t1, t2 = xs[len(xs) // 3], xs[2 * len(xs) // 3]
        terc = {"lowATR": [0, 0], "midATR": [0, 0], "hiATR": [0, 0]}
        for e in rows:
            if e["atr"] is None:
                continue
            if e["atr"] <= t1:
                k = "lowATR"
            elif e["atr"] <= t2:
                k = "midATR"
            else:
                k = "hiATR"
            terc[k][0] += 1
            terc[k][1] += int(e["win"])
        print(
            f"  ATR terciles (cuts {t1:.0f}/{t2:.0f}):",
            {
                k: f"n={v[0]} WR={v[1]/v[0]*100:.0f}%"
                for k, v in terc.items()
                if v[0]
            },
        )
    # list losing trades
    losses = sorted([e for e in rows if not e["win"]], key=lambda e: e["r"])
    print("  losses:")
    for e in losses:
        atr_s = f"{e['atr']:.0f}" if e["atr"] is not None else "na"
        bbw_s = f"{e['bbw']:.2f}" if e["bbw"] is not None else "na"
        print(
            f"    {e['t']} {e['side']:4} {e['kind']:5} r={e['r']:+.2f} "
            f"ATR={atr_s} BBw={bbw_s} hold={e['hold_h']:.1f}h"
        )


for b, name in [
    ("bad_pre", "BAD pre-Jul16 (May–mid Jul)"),
    ("good_mid", "GOOD Jul16–Aug31"),
    ("bad_post", "BAD post-Aug (Sep–Oct)"),
]:
    summarize(name, [e for e in ev if e["bucket"] == b])

print("\n=== Entry blocks (full run, top reasons) ===")
for reason, c in sorted(blocks.items(), key=lambda x: -x[1])[:15]:
    print(f"  {c:5d}  {reason}")

# Direction of losses: buys in up-drift?
print("\n=== Loss clustering ===")
for b in ("bad_pre", "good_mid", "bad_post"):
    rows = [e for e in ev if e["bucket"] == b and not e["win"]]
    buys = sum(1 for e in rows if e["side"] == "BUY")
    sells = sum(1 for e in rows if e["side"] == "SELL")
    print(f"  {b}: loss buys={buys} sells={sells}")
