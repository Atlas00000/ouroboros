# BMRG M5 US30 ~6M — Chart Preset (Balanced Geometry + ATR Regime)

**Status:** RESEARCH CHART PRESET / UNTESTED  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Preset:** `Presets/BMRG-M5-US30-6M-P0_balanced_chart.set`  
**Tester dir:** `Profiles/Tester/BMRG/US30/` (own symbol folder · `.set` + this card)  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md` · BMRG `system_profile.md`  
**Ouroboros audit:** `Ouroboros/research/assets/US30/bmrg_m5_6m_audit.json`  
**Canvas cover:** [`bmrg-us30-m5-preset.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-us30-m5-preset.canvas.tsx)

| Field | Value |
| --- | --- |
| EA | BMRG (Bollinger Mean-Reversion Grid) v1.21 |
| Class | Mean reversion fade (FIXED_RR) · **regime-filtered** |
| Symbol | US30 (Dow Jones · Point = 0.01 · Digits=2) |
| Chart TF | **M5** |
| Window | **2026.05.01 → 2026.10.07** (~6 months) |
| Aggregation | G0 basket events (`MaxLevels=1`, `MaxEntries=1`) |
| Magic | **26101904** |

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

**Read:** Jun–Aug on-home for meanrev (Aug strongest). **May / Sep MISMATCH** and **Oct FRAGILE** are off-home — ATR max gate reduces high-vol cells. Live 30d fit is **FRAGILE**. Incomplete Oct tip is not admission evidence.

**M5 ATR (points, Point=0.01):** p50 ≈ 2411 · p75 ≈ 3554 · p90 ≈ 5137 · mean ≈ 2849.  
**Broker friction (live):** Digits=2 · **spread ≈ 321 pts** · volume_min = 0.01 → cost prior RT ≈ **380 pts**.

---

## 2. Unified Edge Framework geometry (design)

Hard rules from framework + factory:

```text
never TP < SL          →  InpTP_Points ≥ InpSL_Points
RR_design = TP / SL    →  4520 / 3620 = 1.25
BWR = 1 / (1 + R)      →  44.44% if R ≈ RR
E_N = WR × (R + 1) − 1
BM  = WR − BWR
Leak = c_R / (R + 1)
EF  = BM − Leak
```

| Piece | Choice | Intent |
| --- | --- | --- |
| SL | **3620** pts | Structural 1R on US30 M5 (~1.5× ATR p50) — clears ~321 spread Leak |
| TP | **4520** pts | **TP > SL** · designed RR **1.25** |
| BB | 20 / **2.2σ** | Signal threshold |
| Session | **14:00–20:00** server | US RTH tip (same sleeve as M15 / equities) |
| Skip Tue | **true** | Weekday cut (champ pattern) |
| ATR regime | **ON · max 3550** | ≈ ATR p75 — cut high-vol FRAGILE; n stays ≥40 |
| BB-width | OFF | Avoid fire starvation |
| Grid | depth **1** | Clean G0 events |
| Lot | **0.01** | Broker min volume |
| MaxSpread | **500** | Must exceed live spread ≈321 |
| AOS | **OFF** | Chart sleeve = engine only |

**Why not ungated?** EF collapses to +1.6pp (WR ~50.8%) — ATR gate lifts EF to +7.4pp.  
**Why not Harvest RR=1.0?** EF ≈ 0 after Leak — fails Stage 1 viability.  
**Why not Growth RR=1.5 as primary?** Higher E_N (+0.34R) / EF (+9.4pp) but WR falls to ~53.6% — kept as returns-leaning alt; primary = mix WR + returns.  
**Why session 14–20?** No-session ablation makes E_N / EF **negative**.  
**vs M15 sleeve:** M5 uses ATR **p75** (n=69 viable); M15 needed p90 because p75 starved fires. Separate magics — do not mix on one chart.

---

## 3. M5* probe scorecard (design evidence — not Tester blotter)

Closed-bar fade → next open · fixed TP/SL · session 14–20 · skip Tue · BBDev 2.2 · ~6m M1→M5* resample · cost prior **380 pts** RT · horizon ≈12h (144 bars).

| Sleeve | n | WR | RR | BWR | BM | Leak† | EF | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **Balanced 3620/4520 + ATR≤3550 (chosen)** | 69 | 56.5% | 1.25 | 44.4% | +12.1pp | ~4.7pp | **+7.4pp** | **+0.271R** | design-viable |
| Growth 3620/5430 + ATR≤3550 | 69 | 53.6% | 1.50 | 40.0% | +13.6pp | ~4.2pp | +9.4pp | +0.341R | returns-leaning alt |
| Balanced 3620/4520 + ATR≤5137 (p90) | 129 | 55.8% | 1.25 | 44.4% | +11.3pp | ~4.7pp | +6.7pp | +0.255R | looser alt |
| Balanced 3620/4520 (no ATR gate) | 195 | 50.8% | 1.25 | 44.4% | +6.3pp | ~4.7pp | +1.6pp | +0.142R | diluted EF |
| Harvest 3620/3620 (no ATR) | 195 | 55.4% | 1.00 | 50.0% | +5.4pp | ~5.3pp | **+0.1pp** | +0.108R | reject (Leak theatre) |
| Balanced 3620/4520 no session | 1129 | 44.1% | 1.25 | 44.4% | −0.4pp | ~4.7pp | **−5.0pp** | −0.008R | reject |

† `c_R` prior ≈ 380 pts round-trip / SL pts (framework Stage 1 — replace with blotter).  
Live US30 spread measured **≈321 pts** at design time — re-check before Tester.

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP < SL | **TP 4520 > SL 3620** |
| 2 | Designed RR ≥ 1.0 | **1.25** |
| 3 | WR can clear BWR after Leak prior | Probe WR 56.5% > BWR 44.4%; EF ≫ 0 |
| 4 | Not WR-theatre (token SL) | SL 3620 structural vs US30 M5 ATR |
| 5 | Not lottery RR | RR 1.25, not ≥3 |
| 6 | G0 single-leg events | MaxLevels=1 / MaxEntries=1 |
| 7 | Filters protect edge, not starve fires | Session + ATR max p75; BB-width OFF; n≈69 |
| 8 | Regime filter declared | ATR≤p75 · meanrev home · Oct FRAGILE cut |
| 9 | AOS not required for geometry claim | AOS OFF |
| 10 | Incomplete tip not used for admission | Oct FRAGILE noted only |

---

## 5. Load path (chart)

1. Open **US30** **M5** chart.  
2. Attach `Experts\BMRG\BMRG.ex5`.  
3. Inputs → **Load** →  
   `Experts\BMRG\Presets\BMRG-M5-US30-6M-P0_balanced_chart.set`  
4. Confirm: `SL=3620` · `TP=4520` · `BBDev=2.2` · time **14–20** · **Tue off** · **ATR max=3550** · lot **0.01** · MaxSpread **500** · magic **26101904** · AOS off.  
5. Optional visual: Bollinger(20, 2.2) on chart (EA uses its own handles).

### Tester

Load from **`Profiles/Tester/BMRG/US30/BMRG-M5-US30-6M-P0_balanced_chart.set`**.  
Symbol: **US30**. TF: **M5**. Dates **2026.05.01 – 2026.10.07** (or through Aug end to skip Sep–Oct off-home tip). Model: every tick / real ticks if available. Deposit ≥ 1000.

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
- The **M15** US30 balanced sleeve (magic 26101903) is a separate TF — do not run both on one chart without distinct magics and blotters.  
- Do not raise `f` / MaxLevels until a scored blotter clears Stage 1.  
- `regime_filtered=true` for Gate G3 scoring — do not claim cross-regime robustness without re-open ATR gate tests.  
- Spread prior is live snapshot (~321); re-measure before promoting.
