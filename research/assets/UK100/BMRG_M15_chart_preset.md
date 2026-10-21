# BMRG M15 UK100 ~6M — Chart Preset (Balanced Geometry + ATR Regime)

**Status:** RESEARCH CHART PRESET / UNTESTED  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Preset:** `Presets/BMRG-M15-UK100-6M-P0_balanced_chart.set`  
**Tester dir:** `Profiles/Tester/BMRG/UK100/` (own symbol folder · `.set` + this card + README)  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md` · BMRG `system_profile.md`  
**Ouroboros audit:** `Ouroboros/research/assets/UK100/bmrg_m15_6m_audit.json`

| Field | Value |
| --- | --- |
| EA | BMRG (Bollinger Mean-Reversion Grid) v1.21 |
| Class | Mean reversion fade (FIXED_RR) · **regime-filtered** |
| Symbol | UK100 (FTSE · Point = 0.01 · Digits=2) |
| Chart TF | **M15** |
| Window | **2026.05.01 → 2026.10.11** (~6 months of available tip) |
| Aggregation | G0 basket events (`MaxLevels=1`, `MaxEntries=1`) |
| Magic | **26101201** |

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

**Read:** May–Sep on-home for meanrev (Aug strongest). **Oct FRAGILE** (high-vol) is off-home — ATR max gate reduces trading in that cell. Incomplete Oct tip is not admission evidence.

**M15 ATR (points, Point=0.01):** p50 ≈ 1189 · p75 ≈ 1471 · p90 ≈ 1716 · mean ≈ 1209.  
**Broker friction:** spread ≈ 140 pts · volume_min = 0.1 → cost prior RT ≈ 160 pts.

---

## 2. Unified Edge Framework geometry (design)

Hard rules from framework + factory:

```text
never TP < SL          →  InpTP_Points ≥ InpSL_Points
RR_design = TP / SL    →  3125 / 2500 = 1.25
BWR = 1 / (1 + R)      →  44.44% if R ≈ RR
E_N = WR × (R + 1) − 1
BM  = WR − BWR
Leak = c_R / (R + 1)
EF  = BM − Leak
```

| Piece | Choice | Intent |
| --- | --- | --- |
| SL | **2500** pts | Structural 1R on UK100 M15 (~2.1× ATR p50) — clears spread Leak |
| TP | **3125** pts | **TP > SL** · designed RR **1.25** |
| BB | 20 / **2.2σ** | Signal threshold |
| Session | **08:00–17:00** server | London cash sleeve |
| Skip Tue | **true** | Weekday cut (champ pattern) |
| ATR regime | **ON · max 1470** | ≈ ATR p75 — cut high-vol FRAGILE |
| BB-width | OFF | Avoid fire starvation |
| Grid | depth **1** | Clean G0 events |
| Lot | **0.1** | Broker min volume |
| MaxSpread | **200** | Must exceed live spread ≈140 |
| AOS | **OFF** | Chart sleeve = engine only |

**Why not ATR-p50 SL (~1190)?** Higher `c_R` (160/1190) → Leak ≈6pp · EF thinner.  
**Why not Harvest RR=1.0?** Lower E_N / thinner EF — user target = mix WR + returns.  
**Why ATR max ON?** Declared **regime-filtered** (framework Gate G3): improves EF (+6.7pp vs +1.3pp unfiltered) while keeping n≥40.

---

## 3. M15* probe scorecard (design evidence — not Tester blotter)

Closed-bar fade → next open · fixed TP/SL · session 08–17 · skip Tue · BBDev 2.2 · ~6m M1→M15* resample · cost prior 160 pts RT.

| Sleeve | n | WR | RR | BWR | BM | Leak† | EF | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **Balanced 2500/3120 + ATR≤1470 (chosen)** | 74 | 54.1% | 1.25 | 44.4% | +9.6pp | ~2.9pp | **+6.7pp** | **+0.215R** | design-viable |
| Balanced 2000/2500 + ATR≤1470 | 74 | 54.1% | 1.25 | 44.4% | +9.6pp | ~3.6pp | +6.1pp | +0.216R | alt / slightly higher Leak |
| Growth 2500/3750 + ATR≤1470 | 73 | 49.3% | 1.50 | 40.0% | +9.3pp | ~2.6pp | +6.8pp | +0.233R | returns-leaning alt |
| Balanced 2500/3120 (no ATR gate) | 144 | 48.6% | 1.25 | 44.4% | +4.1pp | ~2.9pp | +1.3pp | +0.093R | more fires / thinner EF |
| Balanced **1200/1500** + ATR≤1470 | 74 | 51.4% | 1.25 | 44.4% | +6.9pp | ~5.9pp | +1.0pp | +0.155R | spread-taxed |

† `c_R` prior ≈ 160 pts round-trip / SL pts (framework Stage 1 cost spirit — replace with blotter).  
Preset emits **TP=3125** (exact RR 1.25); probe table used rounded TP=3120.

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP < SL | **TP 3125 > SL 2500** |
| 2 | Designed RR ≥ 1.0 | **1.25** |
| 3 | WR can clear BWR after Leak prior | Probe WR 54.1% > BWR 44.4%; EF ≫ 0 |
| 4 | Not WR-theatre (token SL) | SL 2500 structural vs UK100 M15 ATR + spread |
| 5 | Not lottery RR | RR 1.25, not ≥3 |
| 6 | G0 single-leg events | MaxLevels=1 / MaxEntries=1 |
| 7 | Filters protect edge, not starve fires | Session + ATR max; BB-width OFF; n≈74 |
| 8 | Regime filter declared | ATR≤p75 · meanrev home |
| 9 | AOS not required for geometry claim | AOS OFF |
| 10 | Incomplete tip not used for admission | Oct FRAGILE noted only |

---

## 5. Load path (chart)

1. Open **UK100 M15** chart.  
2. Attach `Experts\BMRG\BMRG.ex5`.  
3. Inputs → **Load** →  
   `Experts\BMRG\Presets\BMRG-M15-UK100-6M-P0_balanced_chart.set`  
4. Confirm: `SL=2500` · `TP=3125` · `BBDev=2.2` · time **08–17** · **Tue off** · **ATR max=1470** · lot **0.1** · magic **26101201** · AOS off.  
5. Optional visual: Bollinger(20, 2.2) on chart (EA uses its own handles).

### Tester

Load from **`Profiles/Tester/BMRG/UK100/BMRG-M15-UK100-6M-P0_balanced_chart.set`**. Dates **2026.05.01 – 2026.10.11** (or through Sep end to skip Oct FRAGILE tip). Model: every tick / real ticks if available. Deposit ≥ 1000.

---

## 6. Post-run fill (framework Stage 0–1)

After a logged run, score **basket events** (not ticket spam):

| Metric | Fill |
| --- | --- |
| n | |
| WR | |
| R = AW/AL | |
| BWR = 1/(1+R) | |
| BM = WR−BWR | |
| mean c_R / Leak | |
| EF = BM−Leak | |
| E_N = WR×(R+1)−1 | |
| MaxDD | |
| BM by ATR tercile / ER cell | |

**Accept to iterate:** `E_N>0`, `WR>BWR`, `EF>0` preferred, `RR−R` not crushed, fires not starved.  
**Reject geometry:** TP&lt;SL theatre, or WR≪BWR with OK R and no cost excuse, or EF≤0 after measured Leak.

---

## 7. Explicit non-claims

- Probe is a **design prior**, not a Strategy Tester blotter / G0–G5 gate.  
- XAUUSD / EURUSD M15 balanced remain separate sleeves; this file is the **UK100 M15 chart** balanced + ATR-regime sleeve for the last ~6m tip.  
- Do not raise `f` / MaxLevels until a scored blotter clears Stage 1.  
- `regime_filtered=true` for Gate G3 scoring — do not claim cross-regime robustness without re-open ATR gate tests.
