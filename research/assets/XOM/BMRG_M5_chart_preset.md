# BMRG M5 XOM ~6M — Chart Preset (Growth Geometry + ATR Regime)

**Status:** RESEARCH CHART PRESET / UNTESTED  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Primary preset:** `Presets/BMRG-M5-XOM-6M-P0_balanced_TPgtSL.set`  
**Harvest sibling:** `Presets/BMRG-M5-XOM-6M-P0_harvest_WRfocus.set`  
**Tester dir:** `Profiles/Tester/BMRG/XOM/`  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md` · Stage 0–1 identities  
**Ouroboros audit:** [`bmrg_m5_6m_audit.json`](./bmrg_m5_6m_audit.json)  
**Canvas cover:** [bmrg-xom-m5-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-xom-m5-preset.canvas.tsx)

| Field | Value |
| --- | --- |
| EA | BMRG (Bollinger Mean-Reversion Grid) v1.21 |
| Class | Mean reversion fade (FIXED_RR) · **regime-filtered** |
| Symbol | XOM (MT5 `Exxon` · Point = 0.01) |
| Chart TF | **M5** |
| Window | **2026.05.01 → 2026.10.07** (~6 months) |
| Aggregation | G0 basket events (`MaxLevels=1`, `MaxEntries=1`) |
| Magic (primary) | **26101931** |
| Magic (harvest) | **26101932** |

---

## 1. Last-6m asset context (Ouroboros)

`regimes.rule_v1` → `fit.map_v0` **meanrev** on H1 (home cell for BMRG):

| Month | Tag | MATCH% | FRAGILE% |
| --- | --- | ---: | ---: |
| 2026-05 | MATCH | 46.9 | 10.2 |
| 2026-06 | — | — | — (M1/D1 pipe gap) |
| 2026-07 | **MISMATCH** | 45.7 | 0.0 |
| 2026-08 | **MISMATCH** | 38.8 | 8.8 |
| 2026-09 | **MISMATCH** | 42.2 | 2.7 |
| 2026-10 | MATCH | 90.0 | 0.0 |

**Read:** Same sleeve as the M15 card — overall ~6m H1 meanrev **MISMATCH**; Jul–Sep off-home. Live 30d H1 meanrev = **MATCH**. ATR gate keeps M5 fires out of the louder trend/HV bars.

**M5 ATR (points, Point=0.01):** p50 ≈ 34 · p75 ≈ 45 · p90 ≈ 54 · mean ≈ 37.  
~half of XOM M15 ATR p50 (≈63). Do **not** import FX M5 token stops; do **not** import MSFT M15 400pt floors.

---

## 2. Unified Edge Framework geometry (design)

```text
never TP < SL          →  InpTP_Points ≥ InpSL_Points
RR_design = TP / SL    →  220 / 150 ≈ 1.47
BWR = 1 / (1 + R)      →  ≈40.5% if R ≈ RR
E_N = WR × (R + 1) − 1
BM  = WR − BWR
Leak = c_R / (R + 1)
EF  = BM − Leak
```

| Piece | Choice | Intent |
| --- | --- | --- |
| SL | **150** pts | Clears 60pt RT Leak on M5 (smaller ATR-scale SLs go EF-negative) |
| TP | **220** pts | **TP > SL** · designed RR **≈1.47** (mix WR + returns) |
| BB | 20 / **2.5σ** | Only bb2.5 sleeves cleared Stage-1 EF on this window |
| Session | **14:00–20:00** server | US cash RTH approx |
| Skip Tue | **true** | Champ weekday cut |
| ATR regime | **ON · 16–45** | ≈ p25×0.6 → p75 — Jul–Sep MISMATCH |
| BB-width | ON · 0.30–2.50% | Light sleeve |
| MaxSpread | **55** | Equity CFD cost prior **60 pts** RT |
| Grid | depth **1** | Clean G0 events |
| AOS | **OFF** | Chart sleeve = engine only |

**Why SL 150 on ATR p50≈34 (~4.4×)?** Under a 60pt RT cost prior, SL≤120 leaves Leak large enough that EF turns negative even when E_N>0. Fat-enough SL is the Leak floor — not lottery RR (RR stays 1.47).  
**Why not Harvest as primary?** Harvest 150/150 has WR≈66% and E_N≈+0.32R but **EF≈−3.8pp** (Leak). Primary must clear Stage-1 EF.  
**Why ATR gate ON?** Jul–Sep H1 meanrev MISMATCH; ATR≤45 cuts the loudest bars without starving n (62 vs 70 ungated).

---

## 3. M5* probe scorecard (design evidence — not Tester blotter)

Closed-bar fade → next open · fixed TP/SL · session 14–20 · skip Tue · ~6m M1→M5* resample · cost prior **60 pts** RT · 5708 M5 bars · bb2.5 signals n≈71.

| Sleeve | n | WR | RR | BWR | BM | Leak† | EF | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **P0 growth 150/220 + ATR≤45 (chosen)** | 62 | 58.1% | 1.47 | 40.5% | +17.5pp | ~16.2pp | **+1.3pp** | **+0.432R** | Stage-1 design-positive |
| P0 ungated 150/220 bb2.5 | 70 | 58.6% | 1.47 | 40.5% | +18.1pp | ~16.2pp | **+1.8pp** | **+0.445R** | ungated sibling |
| P0 + ATR≤54 p90 | 69 | 58.0% | 1.47 | 40.5% | +17.5pp | ~16.2pp | **+1.2pp** | **+0.430R** | looser HV cut |
| Harvest 150/150 bb2.5 | 71 | 66.2% | 1.00 | 50.0% | +16.2pp | ~20.0pp | **−3.8pp** | +0.324R | WR sibling (EF Leak-bitten) |
| Balanced 150/190 bb2.5 + ATR | 62 | 58.1% | 1.27 | 44.1% | +14.0pp | ~17.7pp | −3.7pp | +0.316R | E_N>0 but EF fails |

† `c_R` prior ≈ 60 pts round-trip / SL pts.

**Sample note:** Only **growth RR≈1.47 · SL150 · bb2.5** clears Stage-1 (n≥40 · EF>0 · E_N>0 · WR>BWR) on this M5 window. Design prior is honest: **RESEARCH / UNTESTED**.

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP &lt; SL | **TP 220 > SL 150** |
| 2 | Designed RR ≥ 1.0 | **≈1.47** |
| 3 | WR can clear BWR | Probe WR 58% > BWR 40.5%; E_N ≫ 0 |
| 4 | Not WR-theatre (token SL) | SL 150 sized to clear M5 Leak, not a 20pt toy stop |
| 5 | Not lottery RR | RR 1.47 in growth band; not ≥2.0 |
| 6 | Expectancy / EF positive | E_N ≈ +0.43R · EF ≈ +1.3pp (ATR-gated) |
| 7 | Regime filter when needed | ATR 16–45 for Jul–Sep MISMATCH |
| 8 | Mix WR + returns | Primary RR≈1.47; Harvest WR sibling (EF caveat) |

---

## 5. Chart load steps

1. Open **Exxon** M5 chart (YWO).
2. Attach **BMRG** Expert → Load `BMRG-M5-XOM-6M-P0_balanced_TPgtSL.set`.
3. Confirm: Magic **26101931** · SL 150 · TP 220 · ATR 16–45 · AOS OFF.
4. Optional WR sibling: Harvest `.set` (Magic **26101932**) — EF Leak-bitten under 60pt prior.
5. Strategy Tester: folder `Profiles/Tester/BMRG/XOM/` · same window · every-tick / real ticks when available.

---

## 6. Provenance

- Probe script: `server/scripts/bmrg_xom_m5_6m_audit.py`
- Models: `regimes.rule_v1` · `fit.map_v0`
- Sibling M15 card: [`BMRG_M15_chart_preset.md`](./BMRG_M15_chart_preset.md)
- Ex-post M5* FIXED_RR probe is **not** a Tester blotter and **not** a profit claim

Research / advisory only. fit.map_v0 + Stage-1 design priors gate research books — not execution.
