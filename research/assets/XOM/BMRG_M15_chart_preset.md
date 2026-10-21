# BMRG M15 XOM ~6M — Chart Preset (Balanced Geometry + ATR Regime)

**Status:** RESEARCH CHART PRESET / UNTESTED  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Primary preset:** `Presets/BMRG-M15-XOM-6M-P0_balanced_TPgtSL.set`  
**Harvest sibling:** `Presets/BMRG-M15-XOM-6M-P0_harvest_WRfocus.set`  
**Tester dir:** `Profiles/Tester/BMRG/XOM/`  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md` · Stage 0–1 identities  
**Ouroboros audit:** [`bmrg_m15_6m_audit.json`](./bmrg_m15_6m_audit.json)  
**Canvas cover:** [bmrg-xom-m15-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-xom-m15-preset.canvas.tsx)

| Field | Value |
| --- | --- |
| EA | BMRG (Bollinger Mean-Reversion Grid) v1.21 |
| Class | Mean reversion fade (FIXED_RR) · **regime-filtered** |
| Symbol | XOM (MT5 `Exxon` · Point = 0.01) |
| Chart TF | **M15** |
| Window | **2026.05.01 → 2026.10.07** (~6 months) |
| Aggregation | G0 basket events (`MaxLevels=1`, `MaxEntries=1`) |
| Magic (primary) | **26101921** |
| Magic (harvest) | **26101922** |

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

**Read:** Overall ~6m H1 meanrev is **MISMATCH** (MATCH≈45% / MISMATCH≈50%). May + Oct on-home; **Jul–Sep off-home** (trend mass). Live 30d H1 meanrev = **MATCH** (59%). ATR regime gate keeps the sleeve from firing into the louder trend/HV bars of the MISMATCH months.

**M15 ATR (points, Point=0.01):** p50 ≈ 63 · p75 ≈ 73 · p90 ≈ 83 · mean ≈ 66.  
Much quieter than MSFT (ATR p50 ≈ 180) and META. Do **not** import MSFT 400pt SL floors (wrong ATR scale — that would be ~6× XOM ATR).

---

## 2. Unified Edge Framework geometry (design)

Hard rules from framework + factory:

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
| SL | **150** pts | ~2.4× ATR p50 — structural 1R on XOM M15 (not token, not MSFT-fat) |
| TP | **220** pts | **TP > SL** · designed RR **≈1.47** (mix WR + returns) |
| BB | 20 / **2.5σ** | Equity tip clears Stage-1 better than 2.2σ here |
| Session | **14:00–20:00** server | US cash RTH approx (skip open noise) |
| Skip Tue | **true** | Weekday cut (champ pattern) |
| ATR regime | **ON · 33–83** | ≈ p25×0.6 → p90 — cut Jul–Sep MISMATCH loud bars |
| BB-width | ON · 0.30–2.50% | Light sleeve (non-starving under ATR) |
| MaxSpread | **55** | Equity CFD cost prior **60 pts** RT |
| Grid | depth **1** | Clean G0 events |
| AOS | **OFF** | Chart sleeve = engine only |

**Why not MSFT SL 400?** XOM M15 ATR p50 ≈ 63 — importing 400 would be ~6× ATR and crush geometry / fire-count.  
**Why not Harvest-only RR=1.0 as primary?** Lower payoff; user target = mix WR + returns. RR≈1.47 clears Stage-1 under the 60pt cost prior; Harvest is the WR sibling.  
**Why ATR gate ON?** Declared **regime-filtered** (framework Gate G3): Jul–Sep H1 meanrev MISMATCH; ATR≤83 keeps fires inside the quieter meanrev-compatible sleeve without starving May/Oct.

---

## 3. M15* probe scorecard (design evidence — not Tester blotter)

Closed-bar fade → next open · fixed TP/SL · session 14–20 · skip Tue · ~6m M1→M15* resample · cost prior **60 pts** RT.

| Sleeve | n | WR | RR | BWR | BM | Leak† | EF | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **P0 growth 150/220 bb2.5 (chosen)** | 22 | 63.6% | 1.47 | 40.5% | +23.1pp | ~16.2pp | **+6.9pp** | **+0.570R** | Stage-1 design-positive |
| P0 + ATR≤83 p90 | 17 | 58.8% | 1.47 | 40.5% | +18.3pp | ~16.2pp | **+2.1pp** | **+0.451R** | regime-filtered sibling |
| Balanced 130/160 bb2.5 | 22 | 72.7% | 1.23 | 44.8% | +27.9pp | ~20.7pp | **+7.2pp** | +0.622R | WR-lean alt |
| Harvest 150/150 bb2.5 | 22 | 72.7% | 1.00 | 50.0% | +22.7pp | ~20.0pp | **+2.7pp** | +0.455R | WR sibling |
| Growth 350/520 bb2.2 + ATR p90 | 37 | 48.6% | 1.49 | 40.2% | +8.5pp | ~6.9pp | **+1.5pp** | +0.209R | fat-SL high-n alt |
| Balanced 350/440 bb2.2 (n≥40) | 49 | 53.1% | 1.26 | 44.3% | +8.8pp | ~7.6pp | **+1.2pp** | +0.198R | only n≥40 EF>0 |

† `c_R` prior ≈ 60 pts round-trip / SL pts (framework Stage 1 — replace with blotter).

**Sample note:** Equity M15 under US RTH + skip Tue + bb2.5 yields n≈17–22 on the Stage-1-positive structural sleeves. The fat-SL n≥40 sleeve (350/440) clears EF but is ~5.6× ATR — rejected as primary (geometry restricted). Design prior is honest: **RESEARCH / UNTESTED**, not production n.

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP &lt; SL | **TP 220 > SL 150** |
| 2 | Designed RR ≥ 1.0 | **≈1.47** |
| 3 | WR can clear BWR | Probe WR 63.6% > BWR 40.5%; E_N ≫ 0 |
| 4 | Not WR-theatre (token SL) | SL 150 ≈ 2.4× XOM ATR p50 |
| 5 | Not lottery RR | RR 1.47 in growth band; not ≥2.0 |
| 6 | Expectancy / EF positive | E_N ≈ +0.57R · EF ≈ +6.9pp (ungated) |
| 7 | Regime filter when needed | ATR 33–83 for Jul–Sep MISMATCH |
| 8 | Mix WR + returns | Primary RR≈1.47; Harvest RR1.0 sibling |

---

## 5. Chart load steps

1. Open **Exxon** M15 chart (YWO).
2. Attach **BMRG** Expert → Load `BMRG-M15-XOM-6M-P0_balanced_TPgtSL.set`.
3. Confirm: Magic **26101921** · SL 150 · TP 220 · ATR regime ON · AOS OFF.
4. Optional WR sibling: load Harvest `.set` (Magic **26101922**).
5. Strategy Tester: folder `Profiles/Tester/BMRG/XOM/` · same window · every-tick / real ticks when available.

---

## 6. Provenance

- Probe script: `server/scripts/bmrg_xom_m15_6m_audit.py`
- Models: `regimes.rule_v1` · `fit.map_v0`
- Generated from local Ouroboros pipe · research / advisory only
- Ex-post M15* FIXED_RR probe is **not** a Tester blotter and **not** a profit claim

Research / advisory only. fit.map_v0 + Stage-1 design priors gate research books — not execution.
