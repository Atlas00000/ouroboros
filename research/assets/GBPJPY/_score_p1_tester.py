"""Score latest GBPJPY P1 Tester runs from UTF-16 log copy."""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path

log = Path(
    r"c:\Users\emili\OneDrive\Desktop\Ouroboros\research\assets\GBPJPY\_20261018_tester.log"
)
text = log.read_text(encoding="utf-16", errors="ignore").splitlines()

# Find all GBPJPY started-with-inputs blocks
starts = [i for i, l in enumerate(text) if "GBPJPY" in l and "started with inputs" in l]
print(f"GBPJPY test starts: {len(starts)} @ lines {[s+1 for s in starts]}")


def score_block(start: int, end: int) -> dict:
    block = text[start:end]
    magic = next((l for l in block[:120] if "InpMagic=" in l), "")
    fade = next((l for l in block[:120] if "InpUseFadeConfirm=" in l), "")
    bb = next((l for l in block[:120] if "InpBBDev=" in l), "")
    ms = next((l for l in block[:120] if "InpMaxSpread=" in l), "")
    cd = next((l for l in block[:120] if "InpCooldownBars=" in l), "")
    bal = next((l for l in block if "final balance" in l), "")
    # window from nearby Tester line
    win = ""
    for j in range(max(0, start - 5), start + 3):
        if "testing of" in text[j] and "GBPJPY" in text[j]:
            win = text[j]
            break

    tp = [l for l in block if "take profit triggered" in l and "GBPJPY" in l]
    sl = [l for l in block if "stop loss triggered" in l and "GBPJPY" in l]
    n = len(tp) + len(sl)
    wr = len(tp) / n if n else 0.0
    rr = 200 / 160
    bwr = 1 / (1 + rr)
    en = wr * (rr + 1) - 1
    bm = wr - bwr

    month = defaultdict(Counter)
    for kind, rows in (("TP", tp), ("SL", sl)):
        for l in rows:
            m = re.search(r"(2026\.\d{2})", l)
            if m:
                month[m.group(1)][kind] += 1

    side = defaultdict(Counter)
    for kind, rows in (("TP", tp), ("SL", sl)):
        for l in rows:
            m = re.search(r"triggered #\d+ (buy|sell)", l)
            if m:
                side[m.group(1)][kind] += 1

    # spreads on market entries
    pat = re.compile(
        r"market (buy|sell) .* GBPJPY sl: ([\d.]+) tp: ([\d.]+) \(([\d.]+) / ([\d.]+) /"
    )
    sprs = []
    for l in block:
        m = pat.search(l)
        if m:
            sprs.append((float(m.group(5)) - float(m.group(4))) / 0.001)

    blocks = Counter()
    for l in block:
        if "Entry blocked:" in l:
            blocks[l.split("Entry blocked:")[-1].strip()] += 1

    # design window May1-Sep11 only
    def in_design(l: str) -> bool:
        m = re.search(r"2026\.(\d{2})\.(\d{2})", l)
        if not m:
            return False
        mo, d = int(m.group(1)), int(m.group(2))
        if mo < 5 or mo > 9:
            return False
        if mo == 9 and d > 11:
            return False
        return True

    t_d = sum(1 for l in tp if in_design(l))
    s_d = sum(1 for l in sl if in_design(l))
    n_d = t_d + s_d
    wr_d = t_d / n_d if n_d else 0.0

    mean_spr = sum(sprs) / len(sprs) if sprs else 0.0
    c_r = (mean_spr * 2) / 160 if sprs else 0.0
    leak = c_r / (rr + 1) if rr else 0.0
    ef = bm - leak

    return {
        "win": win[-90:] if win else "",
        "magic": magic.strip().split()[-1] if magic else "?",
        "fade": fade.strip().split("=")[-1] if fade else "?",
        "bb": bb.strip().split("=")[-1] if bb else "?",
        "maxspread": ms.strip().split("=")[-1] if ms else "?",
        "cd": cd.strip().split("=")[-1] if cd else "?",
        "balance": bal.strip().split()[-2] if bal else "?",
        "TP": len(tp),
        "SL": len(sl),
        "n": n,
        "WR": wr,
        "BWR": bwr,
        "E_N": en,
        "BM": bm,
        "mean_spr": mean_spr,
        "Leak": leak,
        "EF": ef,
        "design_n": n_d,
        "design_WR": wr_d,
        "design_E_N": wr_d * (rr + 1) - 1 if n_d else 0,
        "months": {
            m: {
                "TP": c["TP"],
                "SL": c["SL"],
                "WR": c["TP"] / (c["TP"] + c["SL"]) if (c["TP"] + c["SL"]) else 0,
            }
            for m, c in sorted(month.items())
        },
        "sides": {
            s: {
                "TP": c["TP"],
                "SL": c["SL"],
                "WR": c["TP"] / (c["TP"] + c["SL"]) if (c["TP"] + c["SL"]) else 0,
            }
            for s, c in side.items()
        },
        "blocks": blocks.most_common(8),
    }


for idx, start in enumerate(starts):
    end = starts[idx + 1] if idx + 1 < len(starts) else len(text)
    # also cut at next final balance + a bit
    r = score_block(start, end)
    if "26101825" not in r["magic"] and "26101826" not in r["magic"]:
        continue
    print("\n=== RUN ===")
    print(r["win"])
    print(
        f"magic={r['magic']} fade={r['fade']} BB={r['bb']} CD={r['cd']} "
        f"MaxSpr={r['maxspread']} bal={r['balance']}"
    )
    print(
        f"FULL: TP={r['TP']} SL={r['SL']} n={r['n']} WR={r['WR']:.1%} "
        f"BWR={r['BWR']:.1%} E_N={r['E_N']:+.3f}R BM={r['BM']*100:+.1f}pp"
    )
    print(
        f"COST: spr≈{r['mean_spr']:.1f}pt Leak≈{r['Leak']*100:.1f}pp EF≈{r['EF']*100:+.1f}pp"
    )
    print(
        f"DESIGN May1-Sep11: n={r['design_n']} WR={r['design_WR']:.1%} "
        f"E_N={r['design_E_N']:+.3f}R"
    )
    print("months:", {m: f"{v['WR']:.0%}({v['TP']}/{v['TP']+v['SL']})" for m, v in r["months"].items()})
    print("sides:", {s: f"{v['WR']:.0%}({v['TP']}/{v['TP']+v['SL']})" for s, v in r["sides"].items()})
    print("blocks:", r["blocks"][:5])
