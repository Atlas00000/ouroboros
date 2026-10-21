"""Score GBPJPY BMRG blotter from Tester log 20261018."""
from __future__ import annotations

import re
import statistics as st
from collections import Counter, defaultdict
from pathlib import Path

log = Path(
    r"c:\Users\emili\OneDrive\Desktop\Ouroboros\research\assets\GBPJPY\_20261018_tester.log"
)
# MT5 Tester logs are UTF-16 LE
text = log.read_text(encoding="utf-16", errors="ignore").splitlines()

starts = [i for i, l in enumerate(text) if "GBPJPY" in l and "started with inputs" in l]
inits = [i for i, l in enumerate(text) if "BMRG init OK | GBPJPY" in l]
tests = [i for i, l in enumerate(text) if "testing of Experts\\BMRG\\BMRG.ex5" in l and "GBPJPY" in l]
print("matches", {"starts": starts[-3:], "inits": inits[-3:], "tests": tests[-3:]})
# Prefer the last Tester GBPJPY announcement a bit before init
cands = tests + starts + inits
if not cands:
    raise SystemExit("no GBPJPY test block found")
start = max(cands)
# rewind to nearest "started with inputs" or Tester line within 200 lines
for i in range(start, max(-1, start - 200), -1):
    if "GBPJPY" in text[i] and ("started with inputs" in text[i] or "testing of" in text[i]):
        start = i
        break
block = text[start:]
for i, l in enumerate(block):
    if "final balance" in l:
        print(l)
        end = i
        break
else:
    end = len(block)
block = block[: end + 40]

print("start_line", start)
for l in block[:140]:
    if "Inp" in l and any(
        k in l
        for k in (
            "SL",
            "TP",
            "ATRMax",
            "BBDev",
            "MaxSpread",
            "Magic",
            "StartHour",
            "TradeTue",
            "Cooldown",
            "UseATR",
            "EndHour",
        )
    ):
        print(l.split("\t")[-1] if "\t" in l else l[-140:])

tp = [l for l in block if "take profit triggered" in l and "GBPJPY" in l]
sl = [l for l in block if "stop loss triggered" in l and "GBPJPY" in l]
print(f"\nTP={len(tp)} SL={len(sl)}")
n = len(tp) + len(sl)
wr = len(tp) / n if n else 0.0
rr = 200 / 160
bwr = 1 / (1 + rr)
en = wr * (rr + 1) - 1
bm = wr - bwr
# cost prior from fills later
print(f"WR={wr:.3%} BWR={bwr:.3%} BM={bm*100:+.1f}pp E_N={en:+.3f}R (design RR={rr:.2f})")

pat = re.compile(
    r"market (buy|sell) .* GBPJPY sl: ([\d.]+) tp: ([\d.]+) \(([\d.]+) / ([\d.]+) /"
)
deal_pat = re.compile(r"deal #\d+ (buy|sell) .* GBPJPY at ([\d.]+) done")
fills = []
for i, l in enumerate(block):
    m = pat.search(l)
    if not m:
        continue
    side, slp, tpp, bid, ask = (
        m.group(1),
        float(m.group(2)),
        float(m.group(3)),
        float(m.group(4)),
        float(m.group(5)),
    )
    fill = None
    for j in range(i, min(i + 6, len(block))):
        dm = deal_pat.search(block[j])
        if dm and dm.group(1) == side:
            fill = float(dm.group(2))
            break
    if fill is None:
        continue
    spr_pts = (ask - bid) / 0.001
    if side == "buy":
        slip = (fill - ask) / 0.001
        d_sl = (fill - slp) / 0.001
        d_tp = (tpp - fill) / 0.001
    else:
        slip = (bid - fill) / 0.001
        d_sl = (slp - fill) / 0.001
        d_tp = (fill - tpp) / 0.001
    fills.append(
        dict(
            side=side,
            spr=spr_pts,
            slip=slip,
            d_sl=d_sl,
            d_tp=d_tp,
            rr=d_tp / d_sl if d_sl else None,
        )
    )

print(f"parsed fills={len(fills)}")
if fills:
    print(
        f"spread pts mean={st.mean(f['spr'] for f in fills):.1f} "
        f"med={st.median(f['spr'] for f in fills):.1f}"
    )
    print(f"entry slip pts mean={st.mean(f['slip'] for f in fills):.2f}")
    print(
        f"realized SL dist mean={st.mean(f['d_sl'] for f in fills):.1f} "
        f"TP dist mean={st.mean(f['d_tp'] for f in fills):.1f}"
    )
    rrs = [f["rr"] for f in fills if f["rr"] is not None]
    print(f"realized RR mean={st.mean(rrs):.3f} med={st.median(rrs):.3f}")
    print("sides", dict(Counter(f["side"] for f in fills)))
    # Approx Leak: round-trip = entry spr + exit spr (~same) / SL
    c_r = (st.mean(f["spr"] for f in fills) * 2) / 160.0
    leak = c_r / (rr + 1)
    ef = bm - leak
    print(
        "c_R=%.3f Leak=%.1fpp EF=%+.1fpp"
        % (c_r, leak * 100, ef * 100)
    )

month_out: dict[str, Counter] = defaultdict(Counter)
for l in tp:
    m = re.search(r"(2026\.\d{2})", l)
    if m:
        month_out[m.group(1)]["TP"] += 1
for l in sl:
    m = re.search(r"(2026\.\d{2})", l)
    if m:
        month_out[m.group(1)]["SL"] += 1
print("\nby month:")
for m in sorted(month_out):
    c = month_out[m]
    nn = c["TP"] + c["SL"]
    w = c["TP"] / nn if nn else 0
    print(f"  {m}: TP={c['TP']} SL={c['SL']} WR={w:.1%} n={nn}")

blocks = Counter()
for l in block:
    if "Entry blocked:" in l:
        blocks[l.split("Entry blocked:")[-1].strip()] += 1
print("\nentry blocks:", blocks.most_common(10))

# buy vs sell win rates from TP/SL lines
def side_from_close(l: str) -> str | None:
    # take profit triggered #76 sell ... means the open was sell
    m = re.search(r"triggered #\d+ (buy|sell)", l)
    return m.group(1) if m else None


side_c: dict[str, Counter] = defaultdict(Counter)
for l in tp:
    s = side_from_close(l)
    if s:
        side_c[s]["TP"] += 1
for l in sl:
    s = side_from_close(l)
    if s:
        side_c[s]["SL"] += 1
print("\nby side (open side):")
for s, c in side_c.items():
    nn = c["TP"] + c["SL"]
    print(f"  {s}: TP={c['TP']} SL={c['SL']} WR={c['TP']/nn:.1%} n={nn}")
