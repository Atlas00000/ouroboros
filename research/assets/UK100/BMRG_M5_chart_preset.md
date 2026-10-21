# BMRG M5 UK100 ~6M — Chart Preset (Balanced Geometry + ATR Regime)

**Status:** RESEARCH CHART PRESET / UNTESTED  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Preset:** `Presets/BMRG-M5-UK100-6M-P0_balanced_chart.set`  
**Tester dir:** `Profiles/Tester/BMRG/UK100/`  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md`  
**Ouroboros audit:** `Ouroboros/research/assets/UK100/bmrg_m5_6m_audit.json`

| Field | Value |
| --- | --- |
| EA | BMRG (Bollinger Mean-Reversion Grid) v1.21 |
| Class | Mean reversion fade (FIXED_RR) · **regime-filtered** |
| Symbol | UK100 (FTSE · Point = 0.01 · Digits=2) |
| Chart TF | **M5** |
| Window | **2026.05.01 → 2026.10.11** (~6 months) |
| Aggregation | G0 basket events (`MaxLevels=1`, `MaxEntries=1`) |
| Magic | **26101905** |

---

## 1. Last-6m asset context (Ouroboros)

`regimes.rule_v1` → `fit.map_v0` **meanrev** on H1 (home cell for BMRG):

| Month | Tag | MATCH% | FRAGILE% |
| --- | --- | ---: | ---: |
| 2026-05 | MATCH | 51.4 | 16.2 |
| 2026-06 | MATCH | 51.2 | 25.9 |
| 2026-07 | MATCH | 43.6 | 35.9 |
| 2026-08 | MATCH | 79.3 | 3.1 |
| 2026-09 | MATCH | 44.7 | 28.2 |
| 2026-10 | FRAGILE | 18.0 | 63.4 |

**Read:** May–Sep on-home for meanrev. **Oct FRAGILE** is off-home — ATR max gate cuts that sleeve. Incomplete Oct tip is not admission evidence.

**M5 ATR (points, Point=0.01):** p50 ≈ 643 · p75 ≈ 869 · p90 ≈ 1047 · mean ≈ 671.  
**Broker friction:** spread ≈ 140 pts · volume_min = 0.1 → cost prior RT ≈ 160 pts.

---

## 2. Unified Edge Framework geometry (design)

```text
never TP < SL          →  InpTP_Points ≥ InpSL_Points
RR_design = TP / SL    →  2250 / 1800 = 1.25
BWR = 1 / (1 + R)      →  44.44% if R ≈ RR
E_N = WR × (R + 1) − 1
BM  = WR − BWR
Leak = c_R / (R + 1)
EF  = BM − Leak
```

| Piece | Choice | Intent |
| --- | --- | --- |
| SL | **1800** pts | Structural 1R on UK100 M5 (~2.8× ATR p50) — clears spread Leak |
| TP | **2250** pts | **TP > SL** · designed RR **1.25** |
| BB | 20 / **2.2σ** | Signal threshold |
| Session | **08:00–17:00** server | London cash sleeve |
| Skip Tue | **true** | Weekday cut |
| ATR regime | **ON · max 869** | ≈ ATR p75 — **required** on M5 |
| BB-width | OFF | Avoid fire starvation |
| Grid | depth **1** | Clean G0 events |
| Lot | **0.1** | Broker min volume |
| MaxSpread | **200** | Must exceed live spread ≈140 |
| Cooldown | **3** bars | denser M5 spacing |
| AOS | **OFF** | Chart sleeve = engine only |

**Why ATR max ON?** Unfiltered same SL/TP: WR≈46.8% · EF≈**−1.6pp** — fails Stage 1. With ATR≤p75: EF≈**+2.3pp**.  
**Why not SL≈1000?** Leak ≈7pp → EF negative even with ATR gate.  
**Why not Harvest RR=1.0?** Unfiltered harvest EF negative; thinner E_N vs balanced.

---

## 3. M5* probe scorecard (design evidence — not Tester blotter)

Closed-bar fade → next open · fixed TP/SL · session 08–17 · skip Tue · BBDev 2.2 · ~6m M1→M5* resample · cost prior 160 pts RT.

| Sleeve | n | WR | RR | BWR | BM | Leak† | EF | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **Balanced 1800/2250 + ATR≤869 (chosen)** | 154 | 50.7% | 1.25 | 44.4% | +6.2pp | ~4.0pp | **+2.3pp** | **+0.140R** | design-viable |
| Balanced 2000/2500 + ATR≤869 | 154 | 49.4% | 1.25 | 44.4% | +4.9pp | ~3.6pp | +1.4pp | +0.110R | alt |
| Balanced 1200/1500 + ATR≤869 | 156 | 51.3% | 1.25 | 44.4% | +6.8pp | ~5.9pp | +0.9pp | +0.154R | higher Leak |
| Growth 1800/2700 + ATR≤869 | 154 | 46.1% | 1.50 | 40.0% | +6.1pp | ~3.6pp | +2.6pp | +0.153R | returns-leaning alt |
| Balanced 1800/2250 (**no ATR**) | 325 | 46.8% | 1.25 | 44.4% | +2.3pp | ~4.0pp | **−1.6pp** | +0.052R | **reject** |
| Balanced **1000/1250** + ATR≤869 | 156 | 49.4% | 1.25 | 44.4% | +4.9pp | ~7.1pp | **−2.2pp** | +0.111R | **restricted** |

† `c_R` prior ≈ 160 / SL pts.

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP < SL | **TP 2250 > SL 1800** |
| 2 | Designed RR ≥ 1.0 | **1.25** |
| 3 | WR can clear BWR after Leak | WR 50.7% > BWR 44.4%; EF > 0 |
| 4 | Not WR-theatre (token SL) | SL 1800 structural vs M5 ATR + spread |
| 5 | Not lottery RR | RR 1.25 |
| 6 | G0 single-leg events | MaxLevels=1 / MaxEntries=1 |
| 7 | Filters protect edge | ATR max required; n≈154 |
| 8 | Regime filter declared | ATR≤p75 · meanrev home |
| 9 | AOS not required for geometry | AOS OFF |
| 10 | Incomplete tip not admission | Oct FRAGILE noted only |

---

## 5. Load path

1. Open **UK100 M5** chart.  
2. Attach `Experts\BMRG\BMRG.ex5`.  
3. Inputs → **Load** → `Experts\BMRG\Presets\BMRG-M5-UK100-6M-P0_balanced_chart.set`  
4. Confirm: `SL=1800` · `TP=2250` · ATR max **869** · time **08–17** · Tue off · lot **0.1** · magic **26101905** · AOS off.

### Tester

Load from **`Profiles/Tester/BMRG/UK100/BMRG-M5-UK100-6M-P0_balanced_chart.set`**. Dates **2026.05.01 – 2026.10.11** (or through Sep end to skip Oct FRAGILE). Deposit ≥ 1000.

---

## 6. Explicit non-claims

- Probe is a **design prior**, not a Strategy Tester blotter / G0–G5 gate.  
- M15 UK100 P0 remains a separate sleeve; this file is the **M5** balanced + ATR-regime sleeve.  
- Do not raise `f` / MaxLevels until a scored blotter clears Stage 1.  
- `regime_filtered=true` — do not claim cross-regime robustness without re-open ATR tests.
