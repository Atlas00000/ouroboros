# BMRG M5 JP225 ~6M — Chart Preset (Growth RR2 + ATR Band)

**Status:** RESEARCH CHART PRESET / UNTESTED  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Preset:** `Presets/BMRG-M5-JP225-6M-P0_growth_chart.set`  
**Tester dir:** `Profiles/Tester/BMRG/JP225/`  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md` · BMRG `system_profile.md`  
**Ouroboros audit:** `bmrg_m5_6m_audit.json` · WR-lift `bmrg_m5_wr_lift.json`  
**Canvas cover:** [`bmrg-jp225-m5-preset.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-jp225-m5-preset.canvas.tsx)

| Field | Value |
| --- | --- |
| EA | BMRG (Bollinger Mean-Reversion Grid) v1.23 |
| Class | Mean reversion fade (FIXED_RR) · **regime-filtered (ATR band)** |
| Symbol | JP225 → MT5 **JPN225** (Nikkei · Point = 0.01 · Digits=2) |
| Chart TF | **M5** |
| Window | **2026.05.01 → 2026.10.07** (~6 months) |
| Aggregation | G0 basket events (`MaxLevels=1`, `MaxEntries=1`) |
| Magic | **26101906** |

---

## 1. Last-6m asset context (Ouroboros)

`regimes.rule_v1` → `fit.map_v0` **meanrev** on H1 (home cell for BMRG):

| Month | Tag | MATCH% | FRAGILE% |
| --- | --- | ---: | ---: |
| 2026-05 | FRAGILE | 33.1 | 37.9 |
| 2026-06 | FRAGILE | 31.8 | 42.9 |
| 2026-07 | MISMATCH | 29.0 | 30.9 |
| 2026-08 | MATCH | 61.2 | 12.4 |
| 2026-09 | MATCH | 47.0 | 13.2 |
| 2026-10 | MISMATCH | 37.4 | 5.6 |

**Read:** Aug–Sep on-home for meanrev. **May–Jun FRAGILE** (high-vol) and **Jul/Oct MISMATCH** are off-home. ATR **band** (min≈p40 · max≈p75) cuts both choppy low-vol and FRAGILE high-vol. Incomplete Oct tip is not admission evidence.

**M5 ATR (points, Point=0.01):** p40 ≈ 7614 · p50 ≈ 8472 · p75 ≈ 11285 · p90 ≈ 14830 · mean ≈ 9290.  
**Broker friction (live):** Digits=2 · **spread ≈ 2300 pts** · volume_min = 0.1 → cost prior RT ≈ **2500 pts**.  
> JPN225 spread is ~2× DE40 and ~16× UK100 — M5 Balanced RR=1.25 / Growth RR=1.5 all failed Stage 1 under this Leak. Only Growth **RR=2.0** + ATR band cleared EF>0.

---

## 2. Unified Edge Framework geometry (design)

Hard rules from framework + factory:

```text
never TP < SL          →  InpTP_Points ≥ InpSL_Points
RR_design = TP / SL    →  50000 / 25000 = 2.00
BWR = 1 / (1 + R)      →  33.33% if R ≈ RR
E_N = WR × (R + 1) − 1
BM  = WR − BWR
Leak = c_R / (R + 1)
EF  = BM − Leak
```

| Piece | Choice | Intent |
| --- | --- | --- |
| SL | **25000** pts | Structural 1R on JP225 M5 (~3.0× ATR p50) — clears ~2300 spread Leak |
| TP | **50000** pts | **TP > SL** · designed RR **2.00** |
| BB | 20 / **2.5σ** | Selectivity (2.2/2.4 failed Stage 1 on this geometry) |
| Session | **08:00–17:00** server | London sleeve (Tokyo failed on M15 probes) |
| Skip Tue | **true** | Weekday cut |
| ATR regime | **ON · min 7610 · max 11285** | ≈ p40–p75 band — mid-vol only |
| BB-width | OFF | Avoid fire starvation |
| Grid | depth **1** | Clean G0 events |
| Lot | **0.1** | Broker min volume |
| Cooldown | **3** bars | denser M5 spacing |
| MaxSpread | **3000** | Must exceed live spread ≈2300 |
| AOS | **OFF** | Chart sleeve = engine only |

**Why RR=2.0 (not Balanced 1.25 / Growth 1.5)?** Lean M5 grid (`bmrg_m5_6m_audit.json`) had **viable_count=0** — every RR≤1.5 sleeve had EF&lt;0 under cost prior 2500. WR-lift (`bmrg_m5_wr_lift.json`) found a single Stage-1 pass: RR=2.0 lowers BWR to 33.3% and Leak to ~3.3pp so WR≈38% clears.  
**Why ATR band (not max-only)?** ATR≤p75 alone on RR2 BB2.5: EF **−0.7pp**. Band (cut low-vol chop) lifts WR to 38.3% → EF **+1.7pp**.  
**Why BB 2.5?** Same geometry BB 2.4 atrBand: EF **−0.5pp**. Tighter band entry required.  
**Why not Harvest RR=1.0?** Higher WR theatre; Leak eats BM on this name — lean harvest sleeves all EF&lt;0.  
**Why not M15 geometry on M5 (23260/34890)?** Probe EF **−3.7pp** — M5 noise + fat Leak; keep M15 as separate sleeve (magic 26101903+).

---

## 3. M5* probe scorecard (design evidence — not Tester blotter)

Closed-bar fade → next open · fixed TP/SL · session 08–17 · skip Tue · ~6m M1→M5* · cost prior **2500 pts** RT · horizon ≈12h.

| Sleeve | n | WR | RR | BWR | BM | Leak† | EF | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **Growth 25000/50000 BB2.5 + ATR∈[7610,11285] (chosen)** | 107 | 38.3% | 2.00 | 33.3% | +5.0pp | ~3.3pp | **+1.7pp** | **+0.150R** | design-viable |
| Growth 25000/50000 BB2.4 + ATR band | 130 | 36.2% | 2.00 | 33.3% | +2.8pp | ~3.3pp | **−0.5pp** | +0.085R | reject |
| Growth 25000/50000 BB2.5 + ATR≤p75 (no min) | 186 | 36.0% | 2.00 | 33.3% | +2.7pp | ~3.3pp | **−0.7pp** | +0.081R | reject |
| Growth 25000/43750 RR1.75 BB2.5 + ATR≤p75 | 190 | 39.5% | 1.75 | 36.4% | +3.1pp | ~3.6pp | **−0.5pp** | +0.086R | reject |
| Growth 25000/37500 RR1.5 BB2.2 + ATR≤p75 | 337 | 43.0% | 1.50 | 40.0% | +3.0pp | ~4.0pp | **−1.0pp** | +0.076R | reject (Leak) |
| Growth 23260/34890 RR1.5 BB2.2 + ATR≤p75 | 337 | 40.7% | 1.50 | 40.0% | +0.6pp | ~4.3pp | **−3.7pp** | +0.016R | reject |
| Lean Balanced best (21180/26480 ATR≤p75) | 312 | 44.2% | 1.25 | 44.4% | −0.2pp | ~5.3pp | **−5.5pp** | −0.005R | reject |

† `c_R` prior ≈ 2500 pts round-trip / SL pts (framework Stage 1 — replace with blotter).  
Lean grid: **0** viable. WR-lift: **1** viable (this sleeve).

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP &lt; SL | **TP 50000 > SL 25000** |
| 2 | Designed RR ≥ 1.0 | **2.00** |
| 3 | WR can clear BWR after Leak prior | Probe WR 38.3% > BWR 33.3% + Leak 3.3pp; EF &gt; 0 |
| 4 | Not WR-theatre (token SL) | SL 25000 structural vs JP225 M5 ATR + fat spread |
| 5 | Not lottery-only claim | RR 2.0 is returns-leaning **required** by Leak; RR≤1.75 all fail Stage 1 |
| 6 | G0 single-leg events | MaxLevels=1 / MaxEntries=1 |
| 7 | Filters protect edge, not starve fires | ATR band + BB 2.5; n≈107 |
| 8 | Regime filter declared | ATR∈[p40,p75] · meanrev home · May/Jun FRAGILE cut |
| 9 | AOS not required for geometry claim | AOS OFF |
| 10 | Incomplete tip not used for admission | Oct MISMATCH noted only |
| 11 | Mix WR + returns | Functional WR clears BWR; R=2 supplies E_N after fat Leak |

---

## 5. Load path (chart)

1. Open **JPN225** M5 chart (YWO ticker for JP225).  
2. Attach `Experts\BMRG\BMRG.ex5`.  
3. Inputs → **Load** →  
   `Experts\BMRG\Presets\BMRG-M5-JP225-6M-P0_growth_chart.set`  
4. Confirm: `SL=25000` · `TP=50000` · `BBDev=2.5` · time **08–17** · **Tue off** · **ATR min=7610 · max=11285** · CD **3** · lot **0.1** · MaxSpread **3000** · magic **26101906** · AOS off.  
5. Optional visual: Bollinger(20, 2.5) on chart (EA uses its own handles).

### Tester

Load from **`Profiles/Tester/BMRG/JP225/BMRG-M5-JP225-6M-P0_growth_chart.set`**.  
Symbol: **JPN225**. Dates **2026.05.01 – 2026.10.07** (or through Sep end to skip Oct MISMATCH tip). Model: every tick / real ticks if available. Deposit ≥ **5000** (index min lot + fat SL) — **do not raise deposit to “fix” edge**.

---

## 6. Post-run fill (framework Stage 0–1)

*Pending Tester blotter.* Score with a magic-26101906 scorer when the log is available.

**Pass blotter:** `WR > BWR + Leak` · `EF>0` · `E_N>0` · `n≥40` · `tp_lt_sl=0` · geometry matches preset.  
**Fail → iterate selectivity only** (BB / ATR band / CD) — freeze SL/TP. Deposit unchanged.

---

## 7. Explicit non-claims

- Probe is a **design prior**, not a Strategy Tester blotter / G0–G5 gate.  
- M15 JP225 sleeves (26101903–05) remain separate; this file is the **M5** growth + ATR-band sleeve.  
- Do not raise `f` / MaxLevels / deposit until a scored blotter clears Stage 1.  
- `regime_filtered=true` — do not claim cross-regime robustness without re-open ATR band tests.  
- Spread prior is live snapshot (~2300); re-measure before promoting. RR≤1.5 is **not** design-viable on M5 under current friction.
