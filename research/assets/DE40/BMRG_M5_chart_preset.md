# BMRG M5 DE40 ~6M — Chart Preset (Balanced Geometry + ATR Regime)

**Status:** RESEARCH CHART PRESET / UNTESTED  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Preset:** `Presets/BMRG-M5-DE40-6M-P0_balanced_chart.set`  
**Tester dir:** `MQL5/Profiles/Tester/BMRG/DE40/`  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md`  
**Ouroboros audit:** `research/assets/DE40/bmrg_m5_6m_audit.json`  
**Canvas cover:** [`bmrg-de40-m5-preset.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-de40-m5-preset.canvas.tsx)

| Field | Value |
| --- | --- |
| EA | BMRG (Bollinger Mean-Reversion Grid) v1.21 |
| Class | Mean reversion fade (FIXED_RR) · **regime-filtered** |
| Symbol | DE40 → MT5 **DE30** (Germany 40 / DAX · Point = 0.01 · Digits=2) |
| Chart TF | **M5** |
| Window | **2026.05.01 → 2026.10.07** (~6 months) |
| Aggregation | G0 basket events (`MaxLevels=1`, `MaxEntries=1`) |
| Magic | **26101903** |

---

## 1. Last-6m asset context (Ouroboros)

`regimes.rule_v1` → `fit.map_v0` **meanrev** on H1 (home cell for BMRG):

| Month | Tag | MATCH% | FRAGILE% |
| --- | --- | ---: | ---: |
| 2026-05 | MISMATCH | 40.4 | 14.1 |
| 2026-06 | MATCH | 49.9 | 21.0 |
| 2026-07 | MATCH | 49.1 | 21.6 |
| 2026-08 | MATCH | 67.2 | 0.0 |
| 2026-09 | FRAGILE | 31.0 | 45.9 |
| 2026-10 | FRAGILE | 15.0 | 66.4 |

**Read:** Jun–Aug on-home. **Sep–Oct FRAGILE** + live 30d FRAGILE → ATR max gate required. Incomplete Oct tip is not admission evidence.

**M5 ATR (points, Point=0.01):** p50 ≈ 1782 · p75 ≈ 2384 · p90 ≈ 2912 · mean ≈ 1860.  
**Broker friction (live):** Digits=2 · **spread ≈ 1020 pts** · volume_min = 0.1 → cost prior RT ≈ **1100 pts**.  
> Same fat-spread constraint as the M15 sleeve — SL must clear Leak or EF dies.

---

## 2. Unified Edge Framework geometry (design)

```text
never TP < SL          →  InpTP_Points ≥ InpSL_Points
RR_design = TP / SL    →  8750 / 7000 = 1.25
BWR = 1 / (1 + R)      →  44.44% if R ≈ RR
E_N = WR × (R + 1) − 1
BM  = WR − BWR
Leak = c_R / (R + 1)
EF  = BM − Leak
```

| Piece | Choice | Intent |
| --- | --- | --- |
| SL | **7000** pts | Structural 1R on DE40 M5 (~3.9× ATR p50) — clears ~1020 spread Leak |
| TP | **8750** pts | **TP > SL** · designed RR **1.25** |
| BB | 20 / **2.2σ** | Signal threshold |
| Session | **08:00–17:00** server | Frankfurt / London cash sleeve |
| Skip Tue | **true** | Weekday cut |
| ATR regime | **ON · max 2380** | ≈ M5 ATR p75 — cut high-vol FRAGILE |
| BB-width | OFF | Avoid fire starvation |
| Grid | depth **1** | Clean G0 events |
| Lot | **0.1** | Broker min volume |
| MaxSpread | **1500** | Must exceed live spread ≈1020 |
| AOS | **OFF** | Chart sleeve = engine only |

**Why not SL ≈ ATR×1.5 (~2700)?** Leak ≈ 1100/2700 / 2.25 ≈ 18pp — EF crushed.  
**Why not Harvest RR=1.0 (7000/7000)?** Higher WR theatre; user target = mix WR + returns. Kept as alt (EF≈+4.0pp).  
**Why ATR max p75?** Sep–Oct FRAGILE — Gate G3. Lifts EF vs unfiltered while keeping n≈141.

---

## 3. M5* probe scorecard (design evidence — not Tester blotter)

Closed-bar fade → next open · fixed TP/SL · session 08–17 · skip Tue · BBDev 2.2 · ~6m M1→M5* · cost prior **1100 pts** RT · horizon ≈12h.

| Sleeve | n | WR | RR | BWR | BM | Leak† | EF | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **Balanced 7000/8750 + ATR≤2380 (chosen)** | 141 | 54.6% | 1.25 | 44.4% | +10.2pp | ~7.0pp | **+3.2pp** | **+0.229R** | design-viable |
| Balanced 7000/8750 + ATR≤2912 (p90) | 215 | 53.0% | 1.25 | 44.4% | +8.6pp | ~7.0pp | +1.6pp | +0.193R | looser alt |
| Balanced 6000/7500 + ATR≤2380 | 154 | 53.9% | 1.25 | 44.4% | +9.5pp | ~8.1pp | +1.3pp | +0.213R | thinner SL |
| Growth 7000/10500 + ATR≤2380 | 133 | 48.1% | 1.50 | 40.0% | +8.1pp | ~6.3pp | +1.8pp | +0.203R | returns-leaning |
| Harvest 7000/7000 + ATR≤2380 | 152 | 61.8% | 1.00 | 50.0% | +11.8pp | ~7.9pp | +4.0pp | +0.237R | WR-lean alt |
| Balanced 7000/8750 (no ATR gate) | — | — | 1.25 | — | — | ~7.0pp | thinner | — | diluted |

† `c_R` prior ≈ 1100 pts RT / SL pts. Live DE30 spread ≈1020 — re-check before Tester.

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP &lt; SL | **TP 8750 > SL 7000** |
| 2 | Designed RR ≥ 1.0 | **1.25** |
| 3 | WR can clear BWR after Leak | Probe WR 54.6% > BWR 44.4%; EF ≫ 0 |
| 4 | Not WR-theatre (token SL) | SL 7000 structural vs DE40 M5 ATR + fat spread |
| 5 | Not lottery RR | RR 1.25, not ≥3 |
| 6 | G0 single-leg events | MaxLevels=1 / MaxEntries=1 |
| 7 | Filters protect edge, not starve | Session + ATR≤p75; n≈141 |
| 8 | Regime filter declared | ATR≤2380 · meanrev home · Sep/Oct FRAGILE cut |
| 9 | AOS not required for geometry claim | AOS OFF |
| 10 | Incomplete tip noted | Oct FRAGILE tip only |

---

## 5. Load path (chart)

1. Open **DE30** **M5** chart.  
2. Attach `Experts\BMRG\BMRG.ex5`.  
3. Inputs → **Load** →  
   `Experts\BMRG\Presets\BMRG-M5-DE40-6M-P0_balanced_chart.set`  
4. Confirm: `SL=7000` · `TP=8750` · `BBDev=2.2` · time **08–17** · **Tue off** · **ATR max=2380** · lot **0.1** · MaxSpread **1500** · magic **26101903** · AOS off.

### Tester

Load from **`MQL5\Profiles\Tester\BMRG\DE40\BMRG-M5-DE40-6M-P0_balanced_chart.set`**.  
Symbol: **DE30**. Dates **2026.05.01 – 2026.10.07**. Model: every tick / real ticks. Deposit ≥ 2000.

---

## 6. Post-run fill (framework Stage 0–1)

| Metric | Fill |
| --- | --- |
| n | |
| WR | |
| R = AW/AL | |
| BWR / BM / Leak / EF / E_N | |
| MaxDD | |

**Accept:** `E_N>0`, `WR>BWR`, `EF>0` preferred.  
**Reject:** TP&lt;SL theatre, or EF≤0 after measured Leak.

---

## 7. Explicit non-claims

- Probe is a **design prior**, not a Strategy Tester blotter / G0–G5 gate.  
- Separate from the DE40 **M15** balanced sleeve (magic 26101902 · SL 5000/TP 6250).  
- Do not raise `f` / MaxLevels until a scored blotter clears Stage 1.  
- `regime_filtered=true` for Gate G3 — re-open ATR gate before claiming cross-regime robustness.
