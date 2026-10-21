# BMRG M15 DE40 ~6M — Chart Preset (Balanced Geometry + ATR Regime)

**Status:** RESEARCH CHART PRESET / UNTESTED  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Preset:** `Presets/BMRG-M15-DE40-6M-P0_balanced_chart.set`  
**Tester dir:** `MQL5/Profiles/Tester/BMRG/DE40/` (terminal Profiles path · `.set` + this card)  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md` · BMRG `system_profile.md`  
**Ouroboros audit:** `Ouroboros/research/assets/DE40/bmrg_m15_6m_audit.json`  
**Canvas cover:** [`bmrg-de40-m15-preset.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-de40-m15-preset.canvas.tsx)

| Field | Value |
| --- | --- |
| EA | BMRG (Bollinger Mean-Reversion Grid) v1.21 |
| Class | Mean reversion fade (FIXED_RR) · **regime-filtered** |
| Symbol | DE40 → MT5 **DE30** (Germany 40 / DAX · Point = 0.01 · Digits=2) |
| Chart TF | **M15** |
| Window | **2026.05.01 → 2026.10.07** (~6 months of available tip) |
| Aggregation | G0 basket events (`MaxLevels=1`, `MaxEntries=1`) |
| Magic | **26101902** |

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

**Read:** Jun–Aug on-home for meanrev (Aug strongest). **May MISMATCH** (trend-contested) and **Sep–Oct FRAGILE** (high-vol) are off-home — ATR max gate reduces trading in that cell. Live 30d fit is also **FRAGILE** (~55% high-vol mass). Incomplete Oct tip is not admission evidence.

**M15 ATR (points, Point=0.01):** p50 ≈ 3230 · p75 ≈ 4071 · p90 ≈ 4818 · mean ≈ 3328.  
**Broker friction (live):** Digits=2 · **spread ≈ 1020 pts** · volume_min = 0.1 → cost prior RT ≈ **1100 pts**.  
> DE30 spread is ~7× UK100 — geometry must use a fat SL or Leak destroys EF.

---

## 2. Unified Edge Framework geometry (design)

Hard rules from framework + factory:

```text
never TP < SL          →  InpTP_Points ≥ InpSL_Points
RR_design = TP / SL    →  6250 / 5000 = 1.25
BWR = 1 / (1 + R)      →  44.44% if R ≈ RR
E_N = WR × (R + 1) − 1
BM  = WR − BWR
Leak = c_R / (R + 1)
EF  = BM − Leak
```

| Piece | Choice | Intent |
| --- | --- | --- |
| SL | **5000** pts | Structural 1R on DE40 M15 (~1.55× ATR p50) — clears ~1020 spread Leak |
| TP | **6250** pts | **TP > SL** · designed RR **1.25** |
| BB | 20 / **2.2σ** | Signal threshold |
| Session | **08:00–17:00** server | Frankfurt / London cash sleeve |
| Skip Tue | **true** | Weekday cut (champ pattern) |
| ATR regime | **ON · max 4070** | ≈ ATR p75 — cut high-vol FRAGILE (Sep/Oct) |
| BB-width | OFF | Avoid fire starvation |
| Grid | depth **1** | Clean G0 events |
| Lot | **0.1** | Broker min volume |
| MaxSpread | **1500** | Must exceed live spread ≈1020 |
| AOS | **OFF** | Chart sleeve = engine only |

**Why not ATR-p50 SL (~3230)?** `c_R` ≈ 1100/3230 → Leak ≈15pp — EF collapses under the DE30 spread tax.  
**Why not SL 4400 (cost×4 floor)?** Probe EF turns **negative** under ATR≤p75 (Leak ≈11pp).  
**Why not Harvest RR=1.0?** Lower payoff; user target = mix WR + returns.  
**Why ATR max p75 (not auto-ranked p90)?** Sep–Oct FRAGILE + live 30d FRAGILE — Gate G3 prefers the tighter high-vol cut. EF nearly identical (+4.0pp vs +4.3pp) with cleaner regime alignment.

---

## 3. M15* probe scorecard (design evidence — not Tester blotter)

Closed-bar fade → next open · fixed TP/SL · session 08–17 · skip Tue · BBDev 2.2 · ~6m M1→M15* resample · cost prior **1100 pts** RT.

| Sleeve | n | WR | RR | BWR | BM | Leak† | EF | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **Balanced 5000/6250 + ATR≤4070 (chosen)** | 79 | 58.2% | 1.25 | 44.4% | +13.8pp | ~9.8pp | **+4.0pp** | **+0.310R** | design-viable |
| Balanced 5000/6250 + ATR≤4818 (p90) | 118 | 58.5% | 1.25 | 44.4% | +14.0pp | ~9.8pp | +4.3pp | +0.316R | looser alt |
| Balanced 5000/6250 (no ATR gate) | 147 | 56.5% | 1.25 | 44.4% | +12.0pp | ~9.8pp | +2.2pp | +0.270R | diluted EF |
| Growth 5000/7500 + ATR≤4070 | 79 | 51.9% | 1.50 | 40.0% | +11.9pp | ~8.8pp | +3.1pp | +0.298R | returns-leaning alt |
| Balanced 5500/6880 + ATR≤4070 | 79 | 55.7% | 1.25 | 44.4% | +11.3pp | ~8.9pp | +2.4pp | +0.254R | thicker SL / thinner EF |
| Balanced **4400/5500** + ATR≤4070 | 79 | 54.4% | 1.25 | 44.4% | +10.0pp | ~11.1pp | **−1.1pp** | +0.225R | reject (Leak) |

† `c_R` prior ≈ 1100 pts round-trip / SL pts (framework Stage 1 — replace with blotter).  
Live DE30 spread measured **≈1020 pts** at design time — re-check before Tester.

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP < SL | **TP 6250 > SL 5000** |
| 2 | Designed RR ≥ 1.0 | **1.25** |
| 3 | WR can clear BWR after Leak prior | Probe WR 58.2% > BWR 44.4%; EF ≫ 0 |
| 4 | Not WR-theatre (token SL) | SL 5000 structural vs DE40 M15 ATR + fat spread |
| 5 | Not lottery RR | RR 1.25, not ≥3 |
| 6 | G0 single-leg events | MaxLevels=1 / MaxEntries=1 |
| 7 | Filters protect edge, not starve fires | Session + ATR max; BB-width OFF; n≈79 |
| 8 | Regime filter declared | ATR≤p75 · meanrev home · Sep/Oct FRAGILE cut |
| 9 | AOS not required for geometry claim | AOS OFF |
| 10 | Incomplete tip not used for admission | Oct FRAGILE noted only |

---

## 5. Load path (chart)

1. Open **DE30** M15 chart (YWO ticker for DE40).  
2. Attach `Experts\BMRG\BMRG.ex5`.  
3. Inputs → **Load** →  
   `Experts\BMRG\Presets\BMRG-M15-DE40-6M-P0_balanced_chart.set`  
4. Confirm: `SL=5000` · `TP=6250` · `BBDev=2.2` · time **08–17** · **Tue off** · **ATR max=4070** · lot **0.1** · MaxSpread **1500** · magic **26101902** · AOS off.  
5. Optional visual: Bollinger(20, 2.2) on chart (EA uses its own handles).

### Tester

Load from **`MQL5\Profiles\Tester\BMRG\DE40\BMRG-M15-DE40-6M-P0_balanced_chart.set`**.  
Symbol: **DE30**. Dates **2026.05.01 – 2026.10.07** (or through Aug end to skip Sep–Oct FRAGILE tip). Model: every tick / real ticks if available. Deposit ≥ 2000 (index min lot + fat SL).

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
- UK100 / EURUSD M15 balanced remain separate sleeves; this file is the **DE40/DE30 M15 chart** balanced + ATR-regime sleeve for the last ~6m tip.  
- Do not raise `f` / MaxLevels until a scored blotter clears Stage 1.  
- `regime_filtered=true` for Gate G3 scoring — do not claim cross-regime robustness without re-open ATR gate tests.  
- Spread prior is live snapshot (~1020); re-measure before promoting.
