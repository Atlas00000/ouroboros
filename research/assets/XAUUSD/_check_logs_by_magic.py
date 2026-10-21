"""Inspect Tester logs by magic — diagnose zero-trade runs."""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

logdir = Path(
    r"C:\Users\emili\AppData\Roaming\MetaQuotes\Terminal"
    r"\D0E8209F77C8CF37AD8BF550E51FF075\Tester\logs"
)
logs = sorted(logdir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
print("logs:", [(p.name, p.stat().st_size) for p in logs[:4]])

deal_re = re.compile(
    r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2})\s+deal #(\d+) "
    r"(buy|sell) ([\d.]+) XAUUSD at ([\d.]+) done"
)
open_re = re.compile(r"\[BMRG\]\[TRADE\] OPEN ")
block_re = re.compile(r"Entry blocked: (.+)")


def analyze_run(lines: list[str], start: int, end: int, label: str) -> None:
    deals = []
    opens = 0
    blocks: dict[str, int] = defaultdict(int)
    final = dep = fade = magic = atr_max = bbw_max = bbw_min = None
    tp = sl = bbdev = cd = window = None
    halt = 0
    signals = 0
    bar_n1 = 0

    for i in range(start, end):
        L = lines[i]
        if "BMRG init OK" in L:
            m = re.search(r"magic=(\d+).*fade=(\d)", L)
            if m:
                magic, fade = m.group(1), m.group(2)
        if open_re.search(L):
            opens += 1
        m = deal_re.search(L)
        if m:
            deals.append(m.group(1))
        if "final balance" in L:
            m2 = re.search(r"final balance ([\d.]+)", L)
            if m2:
                final = float(m2.group(1))
        if "initial deposit" in L:
            m2 = re.search(r"initial deposit ([\d.]+)", L)
            if m2:
                dep = float(m2.group(1))
        for key, attr in [
            ("InpATRMaxPoints=", "atr_max"),
            ("InpBBWidthMaxPct=", "bbw_max"),
            ("InpBBWidthMinPct=", "bbw_min"),
            ("InpTP_Points=", "tp"),
            ("InpSL_Points=", "sl"),
            ("InpBBDev=", "bbdev"),
            ("InpCooldownBars=", "cd"),
            ("InpUseFadeConfirm=", "fade_inp"),
            ("InpUseATRRegime=", "atr_on"),
            ("InpUseBBWidthRegime=", "bbw_on"),
            ("InpUseTimeFilter=", "time_on"),
            ("InpStartHour=", "sh"),
            ("InpEndHour=", "eh"),
            ("InpTradeTue=", "tue"),
            ("InpAllowBuy=", "buy"),
            ("InpAllowSell=", "sell"),
        ]:
            if key in L:
                globals()  # noqa — use locals dict below
        if "InpATRMaxPoints=" in L:
            atr_max = L.split("=")[-1].strip()
        if "InpBBWidthMaxPct=" in L:
            bbw_max = L.split("=")[-1].strip()
        if "InpBBWidthMinPct=" in L:
            bbw_min = L.split("=")[-1].strip()
        if "InpTP_Points=" in L:
            tp = L.split("=")[-1].strip()
        if "InpSL_Points=" in L:
            sl = L.split("=")[-1].strip()
        if "InpBBDev=" in L:
            bbdev = L.split("=")[-1].strip()
        if "InpCooldownBars=" in L:
            cd = L.split("=")[-1].strip()
        m = re.search(r"from ([\d.]+) 00:00 to ([\d.]+) 00:00", L)
        if m:
            window = f"{m.group(1)} -> {m.group(2)}"
        if "Equity halt" in L:
            halt += 1
        m = block_re.search(L)
        if m:
            reason = m.group(1).strip().split("|")[0].strip()
            if reason.startswith("ATR "):
                reason = "ATR > max"
            elif "BB width" in reason.lower() or "BBw" in reason:
                if ">" in reason or "above" in reason.lower() or "max" in reason.lower():
                    reason = "BBw > max"
                elif "<" in reason or "min" in reason.lower():
                    reason = "BBw < min"
                else:
                    reason = "BBw gate"
            blocks[reason] += 1
        if "sig=1" in L or " signal " in L.lower():
            signals += 1
        if re.search(r"side=(BUY|SELL) n=0", L):
            pass
        if "side=BUY" in L or "side=SELL" in L:
            if " n=0 " in L or "n=0 " in L:
                bar_n1 += 0

    # count bar lines with side set but no position
    side_sig = sum(
        1
        for i in range(start, end)
        if re.search(r"side=(BUY|SELL)", lines[i])
        and "n=0" in lines[i]
    )

    dlist_n = len([d for d in deals])
    print(f"\n===== {label} =====")
    print(f"  magic={magic} fade={fade} window={window}")
    print(f"  dep={dep} final={final} opens={opens} xau_deals={dlist_n}")
    print(f"  SL={sl} TP={tp} BBDev={bbdev} CD={cd} ATRmax={atr_max} BBwMin={bbw_min} BBwMax={bbw_max}")
    print(f"  side_flat_bars(BUY|SELL n=0)={side_sig} equity_halt_lines={halt}")
    top = sorted(blocks.items(), key=lambda x: -x[1])[:12]
    print(f"  blocks({sum(blocks.values())}):", dict(top) if top else "{}")
    if not opens:
        print("  >>> ZERO TRADES")


for logpath in logs[:2]:
    lines = logpath.read_text(encoding="utf-16", errors="replace").splitlines()
    print(f"\n######## {logpath.name} lines={len(lines)} ########")

    # Find all distinct run stamps via init OK
    inits = [
        (i, L)
        for i, L in enumerate(lines)
        if "BMRG init OK" in L
    ]
    print(f"BMRG inits: {len(inits)}")

    # Also catch InpMagic dumps for runs without matching segment
    magic_dumps = [
        (i, re.search(r"InpMagic=(\d+)", L).group(1), L)
        for i, L in enumerate(lines)
        if "InpMagic=" in L
    ]
    print("InpMagic dumps:", [(i + 1, m) for i, m, _ in magic_dumps[-15:]])

    for k, (init_i, init_L) in enumerate(inits):
        m = re.search(r"\t(\d{2}:\d{2}:\d{2})\.", init_L)
        stamp = m.group(1) if m else f"init{k}"
        mag_m = re.search(r"magic=(\d+)", init_L)
        mag = mag_m.group(1) if mag_m else "?"
        idxs = [
            i
            for i, L in enumerate(lines)
            if f"\t{stamp}." in L and "\tCore 01\t" in L
        ]
        if not idxs:
            start, end = init_i, (
                inits[k + 1][0] if k + 1 < len(inits) else len(lines)
            )
        else:
            start, end = min(idxs), max(idxs) + 1
        analyze_run(lines, start, end, f"{logpath.name} magic={mag} wall={stamp}")
