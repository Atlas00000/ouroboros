# BMRG M5 USDJPY ~6M — Chart Preset (Balanced Geometry + ATR Regime)

**Status:** RESEARCH CHART PRESET / UNTESTED  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Preset:** `Presets/BMRG-M5-USDJPY-6M-P0_balanced_chart.set`  
**Tester dir:** `Profiles/Tester/BMRG/USDJPY/`  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md` · BMRG `system_profile.md`  
**Ouroboros audit:** `Ouroboros/research/assets/USDJPY/bmrg_m5_6m_audit.json`

| Field | Value |
| --- | --- |
| EA | BMRG (Bollinger Mean-Reversion Grid) v1.21 |
| Class | Mean reversion fade (FIXED_RR) · **regime-filtered** |
| Symbol | USDJPY (fx yen major · Point ≈ 0.001) |
| Chart TF | **M5** |
| Window | **2026.04.01 → 2026.09.21** (~6 months of available tip) |
| Aggregation | G0 basket events (`MaxLevels=1`, `MaxEntries=1`) |
| Magic | **26101831** |

---

## 1. Last-6m asset context (Ouroboros)

`regimes.rule_v1` → `fit.map_v0` **meanrev** on H1 (home cell for BMRG):

| Month | Tag | MATCH% | FRAGILE% |
| --- | --- | ---: | ---: |
| 2026-04 | MATCH | 59.7 | 20.5 |
| 2026-05 | MATCH | 52.4 | 17.3 |
| 2026-06 | MATCH | 55.7 | 19.9 |
| 2026-07 | MATCH | 41.3 | 35.7 |
| 2026-08 | MATCH | 49.9 | 21.7 |
| 2026-09 | **FRAGILE** | 20.6 | **57.4** |

**Read:** Apr–Aug on-home for meanrev. **Sep FRAGILE** (high-vol tip) → ATR max gate required. Same H1 regime clock as the M15 sleeve.

**M5 ATR (points, Point=0.001):** p50 ≈ 35 · p75 ≈ 51 · p90 ≈ 75 · mean ≈ 44.  
Quieter than M15 (p50 ≈ 65). Do **not** import EURUSD M5 250pt floors or leave M15 ATR max=70 unchanged (wrong scale).

---

## 2. Unified Edge Framework geometry (design)

```text
never TP < SL          →  InpTP_Points ≥ InpSL_Points
RR_design = TP / SL    →  120 / 100 = 1.20
BWR = 1 / (1 + R)      →  45.45% if R ≈ RR
E_N = WR × (R + 1) − 1
BM  = WR − BWR
Leak = c_R / (R + 1)
EF  = BM − Leak
```

| Piece | Choice | Intent |
| --- | --- | --- |
| SL | **100** pts | ~2.9× M5 ATR p50 — structural 1R (same points as M15 P0; relative ATR larger) |
| TP | **120** pts | **TP > SL** · designed RR **1.20** (mix WR + returns) |
| BB | 20 / **2.2σ** | Signal threshold |
| Session | **12:00–20:00** server | London/NY overlap (Tokyo / wider session diluted) |
| Skip Tue | **true** | Weekday cut |
| ATR regime | **ON · max 37** | ≈ tight (~p50 + 0.15×IQR) — cut Sep FRAGILE |
| MaxSpread | **25** | Major USDJPY · 25pt RT cost prior |
| Grid | depth **1** | Clean G0 events |
| AOS | **OFF** | Chart sleeve = engine only |

**Why SL 100 on quieter M5?** Smaller ATR-scaled stops (55–70) raise `c_R` so Leak dominates BM. SL 100 cuts Leak while keeping RR=1.20 and the best observed EF among design-positive M5 sleeves.  
**Why not Harvest RR=1.0?** Mix WR + returns target.  
**Why ATR max 37 ON?** Gate G3 — Sep FRAGILE HV tip; without it EF worsens.

---

## 3. M5* probe scorecard (design evidence — not Tester blotter)

Closed-bar fade → next open · fixed TP/SL · session 12–20 · skip Tue · ~6m M1→M5* · cost prior **25 pts** RT.

| Sleeve | n | WR | RR | BWR | BM | Leak† | EF | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **P0 100/120 + ATR≤37 (chosen)** | 176 | 51.1% | 1.20 | 45.5% | +5.7pp | ~11.4pp | **−5.7pp** | **+0.125R** | Design-positive · Stage-1 miss |
| 70/88 + ATR≤51 | 268 | 49.3% | 1.26 | 44.3% | +5.0pp | ~14.1pp | −9.1pp | +0.112R | more fire · worse Leak |
| 100/120 + ATR≤51 | 257 | 47.9% | 1.20 | 45.5% | +2.4pp | ~11.4pp | −9.0pp | +0.053R | looser ATR dilutes |
| 100/120 bb2.4 + ATR≤51 | 182 | 50.5% | 1.20 | 45.5% | +5.1pp | ~11.4pp | −6.3pp | +0.112R | alt selectivity |
| Session 08–20 100/120 + ATR≤51 | 402 | 48.3% | 1.20 | 45.5% | +2.8pp | ~11.4pp | −8.6pp | +0.062R | wider session |

† `c_R` prior ≈ 25 / SL pts.

**Stage-1 note:** No M5 FIXED_RR sleeve cleared `EF>0` under cost priors 12–25pt in this window. M5 noise caps WR ~51% while Leak needs ~57%+ at RR=1.20. Prefer **M15 P0 (magic 26101828)** when Stage-1 EF is the gate.

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP &lt; SL | **TP 120 > SL 100** |
| 2 | Designed RR ≥ 1.0 | **1.20** |
| 3 | WR can clear BWR | Probe WR 51.1% > BWR 45.5%; **E_N +0.125R** |
| 4 | Not WR-theatre (token SL) | SL 100 ≈ 2.9× M5 ATR p50 |
| 5 | Not lottery RR | RR 1.20, not ≥3 |
| 6 | G0 single-leg events | MaxLevels=1 / MaxEntries=1 |
| 7 | Filters protect, not starve | Session + ATR≤37; n≈176 (≥40) |
| 8 | Regime filter declared | ATR≤37 · meanrev home · Sep FRAGILE cut |
| 9 | AOS not required for geometry claim | AOS OFF |
| 10 | Stage-1 EF honesty | **EF −5.7pp** under 25pt prior — not claimed positive |

Geometry / expectancy (E_N) / WR-vs-BWR are **not** restricted by design. Stage-1 **EF after costs** is the open gap — re-score blotter Leak before promoting.

---

## 5. Load path (chart)

1. Open **USDJPY M5** chart.  
2. Attach `Experts\BMRG\BMRG.ex5`.  
3. Inputs → **Load** →  
   `Experts\BMRG\Presets\BMRG-M5-USDJPY-6M-P0_balanced_chart.set`  
4. Confirm: `SL=100` · `TP=120` · `BBDev=2.2` · time **12–20** · **Tue off** · **ATR max=37** · magic **26101831** · AOS off · MaxSpread **25**.  

### Tester

Load from **`Profiles/Tester/BMRG/USDJPY/BMRG-M5-USDJPY-6M-P0_balanced_chart.set`**.  
Dates **2026.04.01 – 2026.09.21**. Every tick / real ticks if available. Deposit ≥ 500.

---

## 6. Post-run fill (framework Stage 0–1)

| Metric | Fill |
| --- | --- |
| n | |
| WR | |
| R = AW/AL | |
| BWR / BM / Leak / EF | |
| E_N | |
| MaxDD | |
| BM by month (esp. Jul / Sep) | |

**Accept to iterate:** `E_N>0`, `WR>BWR`, prefer `EF>0` after measured Leak.  
**Sibling:** M15 P0 magic **26101828** remains the Stage-1 EF-positive sleeve for this symbol.

### Sleeve ladder

| Sleeve | Magic | Delta | Status |
| --- | ---: | --- | --- |
| **P0 M5** | **26101831** | RR 1.20 (100/120) · ATR≤37 · BB 2.2 | **NEXT — chart / Tester** |
| M5 fire-count | 26101832 | BB 2.0 · same geometry · ATR≤51 | more n |
| **M15 P0** | **26101828** | ATR≤70 · Stage-1 EF≈+0.8pp | preferred EF sleeve |

---

## 7. Explicit non-claims

- Probe is a **design prior**, not a Strategy Tester blotter / G0–G5 gate.  
- Stage-1 **EF is negative** under the declared cost prior — do not claim production edge.  
- Do not raise `f` / MaxLevels until blotter clears `EF>0` after measured Leak.  
- `regime_filtered=true` for Gate G3 — Sep FRAGILE cut is intentional.
