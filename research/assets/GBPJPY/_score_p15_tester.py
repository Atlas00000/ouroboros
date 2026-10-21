"""Score GBPJPY P1.5 Tester runs from UTF-16 log copy."""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path

text = Path(
    r"c:\Users\emili\OneDrive\Desktop\Ouroboros\research\assets\GBPJPY\_20261018_tester.log"
).read_text(encoding="utf-16", errors="ignore").splitlines()

starts = [i for i, l in enumerate(text) if "GBPJPY" in l and "started with inputs" in l]
print("starts", len(starts))


def in_design(line: str) -> bool:
    m = re.search(r"2026\.(\d{2})\.(\d{2})", line)
    if not m:
        return False
    mo, d = int(m.group(1)), int(m.group(2))
    if mo < 5 or mo > 9:
        return False
    if mo == 9 and d > 11:
        return False
    return True


def score(start: int, end: int) -> dict:
    block = text[start:end]

    def inp(key: str) -> str:
        hit = next((l for l in block[:140] if key in l), "")
        return hit.split("=")[-1].strip() if hit else "?"

    bal = next((l for l in block if "final balance" in l), "")
    win = "?"
    for j in range(max(0, start - 5), start + 2):
        m = re.search(r"from ([\d.]+) 00:00 to ([\d.]+)", text[j])
        if m and "GBPJPY" in text[j]:
            win = f"{m.group(1)} -> {m.group(2)}"
            break

    tp = [l for l in block if "take profit triggered" in l and "GBPJPY" in l]
    sl = [l for l in block if "stop loss triggered" in l and "GBPJPY" in l]
    n = len(tp) + len(sl)
    wr = len(tp) / n if n else 0.0
    rr = 1.25
    bwr = 1.0 / (1.0 + rr)
    en = wr * (rr + 1.0) - 1.0
    bm = wr - bwr

    month: dict[str, Counter] = defaultdict(Counter)
    for kind, rows in (("TP", tp), ("SL", sl)):
        for l in rows:
            m = re.search(r"(2026\.\d{2})", l)
            if m:
                month[m.group(1)][kind] += 1

    side: dict[str, Counter] = defaultdict(Counter)
    for kind, rows in (("TP", tp), ("SL", sl)):
        for l in rows:
            m = re.search(r"triggered #\d+ (buy|sell)", l)
            if m:
                side[m.group(1)][kind] += 1

    pat = re.compile(
        r"market (buy|sell) .* GBPJPY sl: ([\d.]+) tp: ([\d.]+) \(([\d.]+) / ([\d.]+) /"
    )
    sprs = [
        (float(m.group(5)) - float(m.group(4))) / 0.001
        for l in block
        for m in [pat.search(l)]
        if m
    ]
    mean_spr = sum(sprs) / len(sprs) if sprs else 0.0
    c_r = (mean_spr * 2) / 160.0 if sprs else 0.0
    leak = c_r / (rr + 1.0)
    ef = bm - leak

    td = sum(1 for l in tp if in_design(l))
    sd = sum(1 for l in sl if in_design(l))
    nd = td + sd
    wrd = td / nd if nd else 0.0

    blocks: Counter = Counter()
    for l in block:
        if "Entry blocked:" not in l:
            continue
        reason = l.split("Entry blocked:")[-1].strip()
        if reason.startswith("spread"):
            reason = "spread > max"
        elif reason.startswith("ATR"):
            reason = "ATR > max"
        elif "fail pause" in reason:
            reason = "fail pause"
        elif "cooldown" in reason:
            reason = "cooldown"
        blocks[reason] += 1

    return {
        "magic": inp("InpMagic="),
        "fade": inp("InpUseFadeConfirm="),
        "bb": inp("InpBBDev="),
        "ms": inp("InpMaxSpread="),
        "cd": inp("InpCooldownBars="),
        "bal": bal.split()[-2] if bal else "?",
        "win": win,
        "TP": len(tp),
        "SL": len(sl),
        "n": n,
        "WR": wr,
        "BWR": bwr,
        "EN": en,
        "spr": mean_spr,
        "Leak": leak,
        "EF": ef,
        "dn": nd,
        "dWR": wrd,
        "dEN": wrd * (rr + 1.0) - 1.0 if nd else 0.0,
        "months": month,
        "sides": side,
        "blocks": blocks,
    }


for i, s in enumerate(starts):
    e = starts[i + 1] if i + 1 < len(starts) else len(text)
    r = score(s, e)
    if r["magic"] != "26101827":
        continue
    print("===", r["magic"], r["win"], "===")
    print(
        f"BB={r['bb']} fade={r['fade']} CD={r['cd']} MaxSpr={r['ms']} bal={r['bal']}"
    )
    print(
        f"FULL n={r['n']} TP={r['TP']} SL={r['SL']} WR={r['WR']:.1%} "
        f"BWR={r['BWR']:.1%} E_N={r['EN']:+.3f}R"
    )
    print(
        f"COST spr~{r['spr']:.1f} Leak~{r['Leak']*100:.1f}pp EF~{r['EF']*100:+.1f}pp"
    )
    print(
        f"DESIGN May1-Sep11 n={r['dn']} WR={r['dWR']:.1%} E_N={r['dEN']:+.3f}R"
    )
    print(
        "months",
        {
            m: f"{c['TP']/(c['TP']+c['SL']):.0%}({c['TP']}/{c['TP']+c['SL']})"
            for m, c in sorted(r["months"].items())
        },
    )
    print(
        "sides",
        {
            s2: f"{c['TP']/(c['TP']+c['SL']):.0%}({c['TP']}/{c['TP']+c['SL']})"
            for s2, c in r["sides"].items()
        },
    )
    print("blocks", r["blocks"].most_common(6))
    print()
