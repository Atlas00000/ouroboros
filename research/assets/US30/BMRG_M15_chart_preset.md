# BMRG M15 US30 ~6M — Chart Preset (Balanced Geometry + ATR Regime)

**Status:** RESEARCH CHART PRESET / UNTESTED  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Preset:** `Presets/BMRG-M15-US30-6M-P0_balanced_chart.set`  
**Tester dir:** `Profiles/Tester/BMRG/US30/` (own symbol folder · `.set` + this card)  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md` · BMRG `system_profile.md`  
**Ouroboros audit:** `Ouroboros/research/assets/US30/bmrg_m15_6m_audit.json`  
**Canvas cover:** [`bmrg-us30-m15-preset.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-us30-m15-preset.canvas.tsx)

| Field | Value |
| --- | --- |
| EA | BMRG (Bollinger Mean-Reversion Grid) v1.21 |
| Class | Mean reversion fade (FIXED_RR) · **regime-filtered** |
| Symbol | US30 (Dow Jones · Point = 0.01 · Digits=2) |
| Chart TF | **M15** |
| Window | **2026.05.01 → 2026.10.07** (~6 months) |
| Aggregation | G0 basket events (`MaxLevels=1`, `MaxEntries=1`) |
| Magic | **26101903** |

---

## 1. Last-6m asset context (Ouroboros)

`regimes.rule_v1` → `fit.map_v0` **meanrev** on H1 (home cell for BMRG):

| Month | Tag | MATCH% | FRAGILE% |
| --- | --- | ---: | ---: |
| 2026-05 | MISMATCH | 41.3 | 10.2 |
| 2026-06 | MATCH | 42.2 | 37.6 |
| 2026-07 | MATCH | 57.9 | 18.2 |
| 2026-08 | MATCH | 62.9 | 8.2 |
| 2026-09 | MISMATCH | 18.5 | 36.7 |
| 2026-10 | FRAGILE | 18.7 | 68.2 |

**Read:** Jun–Aug on-home for meanrev (Aug strongest). **May / Sep MISMATCH** and **Oct FRAGILE** are off-home — ATR max gate reduces extreme high-vol cells. Live 30d fit is **FRAGILE** (~53% high-vol mass). Incomplete Oct tip is not admission evidence.

**M15 ATR (points, Point=0.01):** p50 ≈ 4614 · p75 ≈ 6391 · p90 ≈ 8104 · mean ≈ 5092.  
**Broker friction (live):** Digits=2 · **spread ≈ 321 pts** · volume_min = 0.01 → cost prior RT ≈ **380 pts**.

---

## 2. Unified Edge Framework geometry (design)

Hard rules from framework + factory:

```text
never TP < SL          →  InpTP_Points ≥ InpSL_Points
RR_design = TP / SL    →  5190 / 4150 = 1.25
BWR = 1 / (1 + R)      →  44.44% if R ≈ RR
E_N = WR × (R + 1) − 1
BM  = WR − BWR
Leak = c_R / (R + 1)
EF  = BM − Leak
```

| Piece | Choice | Intent |
| --- | --- | --- |
| SL | **4150** pts | Structural 1R on US30 M15 (~0.9× ATR p50) — clears ~321 spread Leak |
| TP | **5190** pts | **TP > SL** · designed RR **1.25** |
| BB | 20 / **2.2σ** | Signal threshold |
| Session | **14:00–20:00** server | US RTH tip (same sleeve as MSFT/TSLA) |
| Skip Tue | **true** | Weekday cut (champ pattern) |
| ATR regime | **ON · max 8100** | ≈ ATR p90 — cut extreme high-vol; p75 starves n&lt;40 |
| BB-width | OFF | Avoid fire starvation |
| Grid | depth **1** | Clean G0 events |
| Lot | **0.01** | Broker min volume |
| MaxSpread | **500** | Must exceed live spread ≈321 |
| AOS | **OFF** | Chart sleeve = engine only |

**Why not ATR-p75 gate (~6391)?** Probe n drops to 24 (&lt;40 fire floor) and thicker-SL sleeves flip EF negative.  
**Why not Harvest RR=1.0?** EF ≈ 0 after Leak — fails Stage 1 viability.  
**Why not Growth RR=1.5 as primary?** Higher E_N (+0.27R) but WR falls to ~51% — kept as returns-leaning alt; primary = mix WR + returns.  
**Why session 14–20?** No-session ablation kills EF (WR≪BWR). Extended 13–21 dilutes EF toward zero.

---

## 3. M15* probe scorecard (design evidence — not Tester blotter)

Closed-bar fade → next open · fixed TP/SL · session 14–20 · skip Tue · BBDev 2.2 · ~6m M1→M15* resample · cost prior **380 pts** RT.

| Sleeve | n | WR | RR | BWR | BM | Leak† | EF | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **Balanced 4150/5190 + ATR≤8100 (chosen)** | 51 | 54.9% | 1.25 | 44.4% | +10.5pp | ~4.1pp | **+6.4pp** | **+0.236R** | design-viable |
| Growth 4150/6220 + ATR≤8100 | 51 | 51.0% | 1.50 | 40.0% | +11.0pp | ~3.7pp | +7.3pp | +0.274R | returns-leaning alt |
| Balanced 4150/5190 (no ATR gate) | 84 | 52.4% | 1.25 | 44.4% | +8.0pp | ~4.1pp | +3.9pp | +0.179R | diluted EF |
| Balanced 4150/5190 + ATR≤6391 (p75) | 24 | 54.2% | 1.25 | 44.4% | +9.7pp | ~4.1pp | +5.7pp | +0.219R | reject (n&lt;40) |
| Balanced 5000/6250 + ATR≤8100 | 51 | 51.0% | 1.25 | 44.4% | +6.5pp | ~3.4pp | +3.2pp | +0.147R | thicker SL alt |
| Harvest 4150/4150 (no ATR) | 84 | 54.8% | 1.00 | 50.0% | +4.8pp | ~4.6pp | **+0.2pp** | +0.095R | reject (Leak theatre) |

† `c_R` prior ≈ 380 pts round-trip / SL pts (framework Stage 1 — replace with blotter).  
Live US30 spread measured **≈321 pts** at design time — re-check before Tester.

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP < SL | **TP 5190 > SL 4150** |
| 2 | Designed RR ≥ 1.0 | **1.25** |
| 3 | WR can clear BWR after Leak prior | Probe WR 54.9% > BWR 44.4%; EF ≫ 0 |
| 4 | Not WR-theatre (token SL) | SL 4150 structural vs US30 M15 ATR |
| 5 | Not lottery RR | RR 1.25, not ≥3 |
| 6 | G0 single-leg events | MaxLevels=1 / MaxEntries=1 |
| 7 | Filters protect edge, not starve fires | Session + ATR max p90; BB-width OFF; n≈51 |
| 8 | Regime filter declared | ATR≤p90 · meanrev home · Oct FRAGILE cut |
| 9 | AOS not required for geometry claim | AOS OFF |
| 10 | Incomplete tip not used for admission | Oct FRAGILE noted only |

---

## 5. Load path (chart)

1. Open **US30** M15 chart.  
2. Attach `Experts\BMRG\BMRG.ex5`.  
3. Inputs → **Load** →  
   `Experts\BMRG\Presets\BMRG-M15-US30-6M-P0_balanced_chart.set`  
4. Confirm: `SL=4150` · `TP=5190` · `BBDev=2.2` · time **14–20** · **Tue off** · **ATR max=8100** · lot **0.01** · MaxSpread **500** · magic **26101903** · AOS off.  
5. Optional visual: Bollinger(20, 2.2) on chart (EA uses its own handles).

### Tester

Load from **`Profiles/Tester/BMRG/US30/BMRG-M15-US30-6M-P0_balanced_chart.set`**.  
Symbol: **US30**. Dates **2026.05.01 – 2026.10.07** (or through Aug end to skip Sep–Oct off-home tip). Model: every tick / real ticks if available. Deposit ≥ 1000.

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
- UK100 / DE40 / equity M15 balanced remain separate sleeves; this file is the **US30 M15 chart** balanced + ATR-regime sleeve for the last ~6m tip.  
- Do not raise `f` / MaxLevels until a scored blotter clears Stage 1.  
- `regime_filtered=true` for Gate G3 scoring — do not claim cross-regime robustness without re-open ATR gate tests.  
- Spread prior is live snapshot (~321); re-measure before promoting.
