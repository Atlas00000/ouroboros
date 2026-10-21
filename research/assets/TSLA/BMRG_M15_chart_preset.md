# BMRG M15 TSLA ~6M — Chart Preset (Balanced Geometry + ATR Regime)

**Status:** RESEARCH CHART PRESET / UNTESTED  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Preset:** `Presets/BMRG-M15-TSLA-6M-P0_balanced_chart.set`  
**Tester dir:** `Profiles/Tester/BMRG/TSLA/` (own symbol folder · `.set` + this card)  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md` · BMRG system profile  
**Ouroboros audit:** [`bmrg_m15_6m_audit.json`](./bmrg_m15_6m_audit.json)  
**Canvas cover:** [`bmrg-tsla-m15-preset.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-tsla-m15-preset.canvas.tsx)

| Field | Value |
| --- | --- |
| EA | BMRG (Bollinger Mean-Reversion Grid) v1.21 |
| Class | Mean reversion fade (FIXED_RR) · **regime-filtered** |
| Symbol | TSLA / MT5 `Tesla` (equity CFD · Point = 0.01) |
| Chart TF | **M15** |
| Window | **2026.05.01 → 2026.10.07** (~6 months tip) |
| Aggregation | G0 basket events (`MaxLevels=1`, `MaxEntries=1`) |
| Magic | **26101920** (Balanced) · 26101921 Growth · 26101922 Harvest |

| Sleeve | SL/TP | RR | Session | Magic | Probe |
| --- | ---: | ---: | --- | ---: | --- |
| **Balanced (chart)** | 600/750 | 1.25 | 14:00–20 | **26101920** | WR≈54% · E_N≈+0.22R · EF≈+4.0pp |
| Growth (returns alt) | 1000/1500 | 1.50 | 14:00–20 | **26101921** | WR≈48% · E_N≈+0.19R · EF≈+4.4pp |
| Harvest (WR alt) | 810/810 | 1.00 | 14:00–20 | **26101922** | WR≈58% · E_N≈+0.16R · EF≈+3.2pp |

Shared: skip Tue · ATR **114–327** · BBW off · BBDev **2.5** · never TP &lt; SL · AOS OFF.

---

## 1. Last-6m asset context (Ouroboros)

`regimes.rule_v1` → `fit.map_v0` **meanrev** on H1 (home cell for BMRG):

| Month | Tag | MATCH% | FRAGILE% |
| --- | --- | ---: | ---: |
| 2026-05 | MISMATCH | 22.1 | 27.9 |
| 2026-06 | FRAGILE | 23.1 | 40.8 |
| 2026-07 | MATCH | 41.6 | 22.7 |
| 2026-08 | MATCH | 56.5 | 13.6 |
| 2026-09 | MATCH | 66.7 | 2.7 |
| 2026-10 | MISMATCH | 26.7 | 0.0 |

**Read:** Tip is **split** — May MISMATCH + Jun FRAGILE, then Jul–Sep MATCH, Oct thin MISMATCH. Overall H1 meanrev ≈42% MATCH / 21% FRAGILE. Live 30d fit is **MATCH** (ranging-led, fragile sleeve only ~3%). ATR max is mandatory: without it, high-vol May/Jun mass dilutes Stage-1 EF.

**M15 ATR (points, Point=0.01):** p50 ≈ 232 · p75 ≈ 279 · p90 ≈ 327 · mean ≈ 239.  
High-vol equity — **do not** import MSFT 290pt / META 540pt floors blindly. SL 600 ≈ 2.6× ATR p50 (structural 1R). Token ATR-base 370/460 **fails** Stage 0 (WR &lt; BWR).

---

## 2. Unified Edge Framework geometry (design)

Hard rules from framework + factory:

```text
never TP < SL          →  InpTP_Points ≥ InpSL_Points
RR_design = TP / SL    →  750 / 600 = 1.25
BWR = 1 / (1 + R)      →  44.4% if R ≈ RR
E_N = WR × (R + 1) − 1
BM  = WR − BWR
Leak = c_R / (R + 1)
EF  = BM − Leak
```

| Piece | Choice | Intent |
| --- | --- | --- |
| SL | **600** pts | ~2.6× ATR p50 — structural 1R on TSLA M15 |
| TP | **750** pts | **TP > SL** · designed RR **=1.25** (mix WR + returns) |
| BB | 20 / **2.5σ** | Wider bands than FX majors — equity noise |
| Session | **14:00–20:00** server | US RTH tip (skip open auction) |
| Skip Tue | **true** | Weekday cut (champ pattern) |
| ATR regime | **ON · 114–327** | Floor ≈0.6×p25 · max ≈ p90 — Gate G3 |
| BB-width | OFF | atrBBW sleeves starved n / weaker EF |
| MaxSpread | **90** | Cost prior **80 pts** RT |
| Grid | depth **1** | Clean G0 events |
| AOS | **OFF** | Chart sleeve = engine only |

**Why not Harvest RR=1.0 as chart default?** Higher WR theatre, lower payoff; user target = mix WR + returns → Balanced.  
**Why not Growth RR=1.5 as default?** Probe EF slightly higher (~+4.4pp) but RR leaves preferred [1.20, 1.35] band — kept as alt.  
**Why ATR 114–327 ON?** Declared **regime-filtered**: May MISMATCH + Jun FRAGILE need a high-vol cut. ATR≤327 lifts EF to **≈+4.0pp** (n=46) vs no-gate EF≈+2.4pp (n=55) on the same 600/750 geometry.  
**Why not P0 ATR-scaled 370/460?** Stage-0 fail — WR≈37–40% &lt; BWR≈44% → E_N negative. Geometry restricted by undersized SL.

---

## 3. M15* probe scorecard (design evidence — not Tester blotter)

Closed-bar fade → next open · fixed TP/SL · session 14–20 · skip Tue · ~6m M1→M15* resample · cost prior **80 pts** RT.

| Sleeve | n | WR | RR | BWR | BM | Leak† | EF | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **P0 balanced 600/750 + ATR≤327 (chosen)** | 46 | 54.4% | 1.25 | 44.4% | +9.9pp | ~5.9pp | **+4.0pp** | **+0.223R** | Stage-1 ok |
| Balanced 600/750 no ATR gate | 55 | 52.7% | 1.25 | 44.4% | +8.3pp | ~5.9pp | +2.4pp | +0.186R | diluted |
| Growth 1000/1500 + ATR≤327 | 42 | 47.6% | 1.50 | 40.0% | +7.6pp | ~3.2pp | +4.4pp | +0.191R | returns alt |
| Growth 1000/1500 no ATR | 51 | 51.0% | 1.50 | 40.0% | +11.0pp | ~3.2pp | +7.8pp | +0.275R | unfiltered research |
| Harvest 810/810 | 55 | 58.2% | 1.00 | 50.0% | +8.2pp | ~4.9pp | +3.2pp | +0.164R | WR alt |
| Balanced 370/460 (ATR-base) | 91 | 37.4% | 1.24 | 44.6% | −7.2pp | ~9.6pp | **−16.9pp** | **−0.162R** | reject |
| Balanced 370/460 + ATR≤327 | 77 | 40.3% | 1.24 | 44.6% | −4.3pp | ~9.6pp | **−14.0pp** | **−0.097R** | reject |

† `c_R` prior ≈ 80 pts round-trip / SL pts (framework Stage 1 — replace with blotter).

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP &lt; SL | **TP 750 > SL 600** (ConfigValidate enforces) |
| 2 | Designed RR ≥ 1.0 | **=1.25** |
| 3 | WR can clear BWR | Probe WR 54.4% > BWR 44.4%; E_N ≫ 0 |
| 4 | Not WR-theatre (token SL) | SL 600 ≈ 2.6× TSLA ATR p50; 370pt token rejected |
| 5 | Not lottery RR | RR 1.25, not ≥3 |
| 6 | G0 single-leg events | MaxLevels=1 / MaxEntries=1 |
| 7 | Filters protect edge, not starve | Session + ATR 114–327; n≈46 (≥40) |
| 8 | Regime filter declared | ATR gate · meanrev home · high-vol / thin-trend cut |
| 9 | AOS not required for geometry claim | AOS OFF |
| 10 | Incomplete tip noted | Oct 2026 partial · bars end 2026-10-07 |

Stage-1 **EF ≈ +4.0pp** under an 80pt cost prior. Geometry / WR / E_N are **not** restricted by design. Re-score blotter Leak before promoting.

---

## 5. Load path (chart)

1. Open **Tesla (TSLA) M15** chart.  
2. Attach `Experts\BMRG\BMRG.ex5`.  
3. Inputs → **Load** →  
   `Experts\BMRG\Presets\BMRG-M15-TSLA-6M-P0_balanced_chart.set`  
4. Confirm: `SL=600` · `TP=750` · `BBDev=2.5` · time **14–20** · **Tue off** · **ATR 114–327** · magic **26101920** · AOS off · MaxSpread **90**.  
5. Optional visual: Bollinger(20, 2.5) on chart (EA uses its own handles).

### Tester

Load from **`Profiles/Tester/BMRG/TSLA/BMRG-M15-TSLA-6M-P0_balanced_chart.set`**.  
Dates **2026.05.01 – 2026.10.07**. Model: every tick / real ticks if available. Deposit ≥ 2000 (1.0 share equity CFD).

Alts in same folder: `_growth_TPgtSL.set` (magic 26101921) · `_harvest_WRfocus.set` (magic 26101922).

---

## 6. Post-run fill (framework Stage 0–1)

_Pending Strategy Tester blotter · magic **26101920**._

| Check | Result |
| --- | --- |
| Never TP &lt; SL | Design pass — TP 750 > SL 600 |
| Geometry / payoff | Design pass — RR=1.25 held in probe |
| Hit-rate / Stage 0 | Design prior WR 54.4% > BWR 44.4% — **confirm on blotter** |
| Regime filter active | ATR 114–327 ON · session 14–20 · skip Tue |

**Accept to iterate:** tip n≥40 · WR > BWR · E_N > 0 · EF>0 after measured Leak.  
**Reject geometry:** only if blotter shows TP&lt;SL theatre or R collapses — not indicated by probe.

---

## 7. Explicit non-claims

- Probe is a **design prior**, not a Strategy Tester blotter / G0–G5 gate.  
- META / MSFT / AUDUSD M15 balanced remain separate sleeves.  
- Do not raise `f` / MaxLevels until a scored blotter clears Stage 1 (`EF>0` after measured Leak).  
- `regime_filtered=true` for Gate G3 scoring — do not claim cross-regime robustness without re-open ATR gate tests.  
- May 2026 MISMATCH + Jun FRAGILE months are intentionally partially blocked by ATR max.
