# BMRG M5 MSFT ~6M — Chart Preset (Balanced Geometry + ATR Regime)

**Status:** RESEARCH CHART PRESET / UNTESTED  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Primary preset:** `BMRG-M5-MSFT-6M-P0_balanced_TPgtSL.set`  
**Tester dir:** `MQL5/Profiles/Tester/BMRG/MSFT/`  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md` · Stage 0–1 identities  
**Ouroboros audit:** [`bmrg_m5_6m_audit.json`](./bmrg_m5_6m_audit.json)  
**Canvas cover:** [bmrg-msft-m5-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-msft-m5-preset.canvas.tsx)

| Field | Value |
| --- | --- |
| EA | BMRG (Bollinger Mean-Reversion Grid) v1.21 |
| Class | Mean reversion fade (FIXED_RR) · **regime-filtered** |
| Symbol | MSFT (MT5 `Microsoft` · Point = 0.01) |
| Chart TF | **M5** |
| Window | **2026.05.01 → 2026.10.07** (~6 months) |
| Aggregation | G0 basket events (`MaxLevels=1`, `MaxEntries=1`) |
| Magic | **26101903** |

---

## 1. Last-6m asset context (Ouroboros)

`regimes.rule_v1` → `fit.map_v0` **meanrev** on H1 (home cell for BMRG):

| Month | Tag | MATCH% | FRAGILE% |
| --- | --- | ---: | ---: |
| 2026-05 | MATCH | 61.2 | 38.8 |
| 2026-06 | — | — | — (M1 pipe gap) |
| 2026-07 | **FRAGILE** | 22.1 | **55.7** |
| 2026-08 | MATCH | 44.2 | 15.6 |
| 2026-09 | MATCH | 68.7 | 4.8 |
| 2026-10 | MATCH | 46.7 | 30.0 |

**Read:** May + Aug–Oct on-home. **Jul FRAGILE** is the off-home month — ATR max gate keeps the sleeve inside regime.

**M5 ATR (points, Point=0.01):** p50 ≈ 99 · p75 ≈ 129 · p90 ≈ 162 · mean ≈ 107.  
Do **not** import M15 SL 400 (≈4× M5 ATR) or META equity floors.

---

## 2. Unified Edge Framework geometry (design)

```text
never TP < SL          →  InpTP_Points ≥ InpSL_Points
RR_design = TP / SL    →  380 / 250 = 1.52
BWR = 1 / (1 + R)      →  ≈39.7% if R ≈ RR
E_N = WR × (R + 1) − 1
BM  = WR − BWR
Leak = c_R / (R + 1)
EF  = BM − Leak
```

| Piece | Choice | Intent |
| --- | --- | --- |
| SL | **250** pts | ~2.5× M5 ATR p50 — structural 1R (not token) |
| TP | **380** pts | **TP > SL** · designed RR **1.52** (mix WR + returns) |
| BB | 20 / **2.5σ** | Clears Stage-1; bb2.2 growth EF turns soft-negative |
| Session | **14:00–20:00** server | US cash RTH approx |
| Skip Tue | **true** | Weekday cut |
| ATR regime | **ON · 45–162** | ≈ p25×0.6 → p90 — cut Jul FRAGILE HV |
| BB-width | ON · 0.30–2.50% | Light sleeve |
| Cooldown | **6** bars | ≈30m on M5 |
| MaxSpread | **55** | Cost prior **60 pts** RT |
| Grid | depth **1** | Clean G0 events |
| AOS | **OFF** | Chart sleeve = engine only |

**Why not Harvest RR=1.0 as primary?** Harvest 250/250 is E_N>0 (WR≈59%) but **EF soft-negative** under the 60pt cost prior — fails Stage-1 EF>0 gate. Primary keeps mix WR + returns with EF+.  
**Why ATR gate ON?** Jul FRAGILE; gated sleeve remains Stage-1 viable (n=60).

---

## 3. M5* probe scorecard (design evidence — not Tester blotter)

Closed-bar fade → next open · fixed TP/SL · session 14–20 · skip Tue · ~6m M1→M5* resample · cost prior **60 pts** RT.

| Sleeve | n | WR | RR | BWR | EF | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **P0 250/380 bb2.5 + ATR≤162 (chosen)** | 60 | 50.0% | 1.52 | 39.7% | **+0.8pp** | **+0.260R** | Stage-1 viable · regime-filtered |
| P0 250/380 bb2.5 ungated | 61 | 50.8% | 1.52 | 39.7% | **+1.6pp** | **+0.281R** | Stage-1 viable · no HV cut |
| Balanced 250/310 bb2.5 | 61 | 54.1% | 1.24 | 44.6% | −1.3pp | +0.212R | E_N+ · Leak bites EF |
| Harvest 250/250 bb2.5 | 61 | 59.0% | 1.00 | 50.0% | −3.0pp | +0.180R | WR high · EF− under cost |
| Growth 250/380 bb2.2 | 117 | 44.4% | 1.52 | 39.7% | −4.8pp | +0.120R | WR below useful margin |

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP &lt; SL | **TP 380 > SL 250** |
| 2 | Designed RR ≥ 1.0 | **1.52** |
| 3 | WR can clear BWR | Probe WR 50% > BWR ≈39.7%; E_N ≫ 0 |
| 4 | Not WR-theatre (token SL) | SL 250 ≈ 2.5× M5 ATR p50 |
| 5 | Not lottery RR | RR 1.52 growth band; not ≥2.0 |
| 6 | Expectancy / EF positive | E_N ≈ +0.26R · EF ≈ +0.8pp (gated) |
| 7 | Regime filter when needed | ATR 45–162 for Jul FRAGILE |
| 8 | Mix WR + returns | Primary RR 1.52 (Harvest EF− under prior) |

---

## 5. Chart load steps

1. Open **Microsoft** **M5** chart (YWO).
2. Attach **BMRG** → Load `BMRG-M5-MSFT-6M-P0_balanced_TPgtSL.set`.
3. Confirm: Magic **26101903** · SL 250 · TP 380 · ATR regime ON · AOS OFF.
4. Strategy Tester: `Profiles/Tester/BMRG/MSFT/` · window 2026.05.01 → 2026.10.07.

---

## 6. Provenance

- Probe script: `server/scripts/bmrg_msft_m5_6m_audit.py`
- Models: `regimes.rule_v1` · `fit.map_v0`
- Sibling M15 card: [`BMRG_M15_chart_preset.md`](./BMRG_M15_chart_preset.md)
- Research / advisory only — M5* FIXED_RR probe is **not** a Tester blotter

Research / advisory only. fit.map_v0 + Stage-1 design priors gate research books — not execution.
