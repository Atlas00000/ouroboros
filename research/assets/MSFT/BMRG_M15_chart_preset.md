# BMRG M15 MSFT ~6M — Chart Preset (Balanced Geometry + ATR Regime)

**Status:** RESEARCH CHART PRESET / UNTESTED  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Primary preset:** `Presets/BMRG-M15-MSFT-6M-P0_balanced_TPgtSL.set`  
**Harvest sibling:** `Presets/BMRG-M15-MSFT-6M-P0_harvest_WRfocus.set`  
**Tester dir:** `MQL5/Profiles/Tester/BMRG/MSFT/` (terminal Profiles — not under Experts)  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md` · Stage 0–1 identities  
**Ouroboros audit:** [`bmrg_m15_6m_audit.json`](./bmrg_m15_6m_audit.json)  
**Canvas cover:** [bmrg-msft-m15-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-msft-m15-preset.canvas.tsx)

| Field | Value |
| --- | --- |
| EA | BMRG (Bollinger Mean-Reversion Grid) v1.21 |
| Class | Mean reversion fade (FIXED_RR) · **regime-filtered** |
| Symbol | MSFT (MT5 `Microsoft` · Point = 0.01) |
| Chart TF | **M15** |
| Window | **2026.05.01 → 2026.10.07** (~6 months) |
| Aggregation | G0 basket events (`MaxLevels=1`, `MaxEntries=1`) |
| Magic (primary) | **26101901** |
| Magic (harvest) | **26101902** |

---

## 1. Last-6m asset context (Ouroboros)

`regimes.rule_v1` → `fit.map_v0` **meanrev** on H1 (home cell for BMRG):

| Month | Tag | MATCH% | FRAGILE% |
| --- | --- | ---: | ---: |
| 2026-05 | MATCH | 61.2 | 38.8 |
| 2026-06 | — | — | — (M1/D1 pipe gap) |
| 2026-07 | **FRAGILE** | 20.0 | **57.9** |
| 2026-08 | MATCH | 44.2 | 15.6 |
| 2026-09 | MATCH | 68.7 | 4.8 |
| 2026-10 | MATCH | 46.7 | 30.0 |

**Read:** May + Aug–Oct on-home for meanrev. **Jul FRAGILE** (high-vol) is the off-home month — ATR max gate keeps the sleeve trading inside regime. Live 30d H1 meanrev = **MATCH** (64.4%). Overall ~6m meanrev MATCH share ≈ 46%.

**M15 ATR (points, Point=0.01):** p50 ≈ 180 · p75 ≈ 212 · p90 ≈ 251 · mean ≈ 192.  
Quieter than META (ATR p50 ≈ 335). Do **not** import META 1000pt SL floors (wrong ATR scale).

---

## 2. Unified Edge Framework geometry (design)

Hard rules from framework + factory:

```text
never TP < SL          →  InpTP_Points ≥ InpSL_Points
RR_design = TP / SL    →  600 / 400 = 1.50
BWR = 1 / (1 + R)      →  40.0% if R ≈ RR
E_N = WR × (R + 1) − 1
BM  = WR − BWR
Leak = c_R / (R + 1)
EF  = BM − Leak
```

| Piece | Choice | Intent |
| --- | --- | --- |
| SL | **400** pts | ~2.2× ATR p50 — structural 1R on MSFT M15 (not token) |
| TP | **600** pts | **TP > SL** · designed RR **1.50** (mix WR + returns) |
| BB | 20 / **2.5σ** | Equity tip clears Stage-1 better than 2.2σ here |
| Session | **14:00–20:00** server | US cash RTH approx (skip open noise) |
| Skip Tue | **true** | Weekday cut (champ pattern) |
| ATR regime | **ON · 90–251** | ≈ p25×0.6 → p90 — cut Jul FRAGILE high-vol |
| BB-width | ON · 0.30–2.50% | Light sleeve (non-starving under ATR) |
| MaxSpread | **55** | Equity CFD cost prior **60 pts** RT |
| Grid | depth **1** | Clean G0 events |
| AOS | **OFF** | Chart sleeve = engine only |

**Why not META SL 1000?** MSFT M15 ATR p50 ≈ 180 — importing 1000 would be ~5.5× ATR and crush geometry.  
**Why not Harvest-only RR=1.0 as primary?** Lower payoff; user target = mix WR + returns. RR=1.50 clears Stage-1 under the 60pt cost prior; Harvest is the WR sibling.  
**Why ATR gate ON?** Declared **regime-filtered** (framework Gate G3): Jul FRAGILE is the HV month; ATR≤251 keeps fires inside the ranging/meanrev sleeve without starving May/Aug–Oct.

---

## 3. M15* probe scorecard (design evidence — not Tester blotter)

Closed-bar fade → next open · fixed TP/SL · session 14–20 · skip Tue · ~6m M1→M15* resample · cost prior **60 pts** RT.

| Sleeve | n | WR | RR | BWR | BM | Leak† | EF | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **P0 balanced 400/600 bb2.5 (chosen)** | 26 | 50.0% | 1.50 | 40.0% | +10.0pp | ~6.0pp | **+4.0pp** | **+0.250R** | Stage-1 design-positive |
| P0 + ATR≤251 p90 | 25 | 48.0% | 1.50 | 40.0% | +8.0pp | ~6.0pp | **+2.0pp** | **+0.200R** | regime-filtered sibling |
| P0 + ATR≤211 p75 | 20 | 50.0% | 1.50 | 40.0% | +10.0pp | ~6.0pp | **+4.0pp** | **+0.250R** | tighter HV cut |
| Balanced 450/560 bb2.5 | 26 | 53.8% | 1.24 | 44.6% | +9.2pp | ~5.9pp | **+3.4pp** | +0.209R | WR-lean alt |
| Harvest 300/300 bb2.5 | 26 | 61.5% | 1.00 | 50.0% | +11.5pp | ~10.0pp | **+1.5pp** | +0.231R | WR sibling |
| Balanced 300/380 bb2.2 (n≈55) | 55 | 49.1% | 1.27 | 44.1% | +5.0pp | ~8.8pp | −3.9pp | +0.113R | Leak bites at n |
| Balanced 290/360 bb2.2 (n≈55) | 55 | 49.1% | 1.24 | 44.6% | +4.5pp | ~9.2pp | −4.8pp | +0.100R | leak |

† `c_R` prior ≈ 60 pts round-trip / SL pts (framework Stage 1 — replace with blotter).

**Sample note:** Equity M15 under US RTH + skip Tue yields n≈25–26 on the Stage-1-positive sleeves. High-n (n≥40) bb2.2 sleeves stay E_N>0 but EF turns negative under the same cost prior — Leak, not geometry failure. Design prior is honest: **RESEARCH / UNTESTED**, not production n.

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP &lt; SL | **TP 600 > SL 400** |
| 2 | Designed RR ≥ 1.0 | **1.50** |
| 3 | WR can clear BWR | Probe WR 50% > BWR 40%; E_N ≫ 0 |
| 4 | Not WR-theatre (token SL) | SL 400 ≈ 2.2× MSFT ATR p50 |
| 5 | Not lottery RR | RR 1.50 in growth band; not ≥2.0 |
| 6 | Expectancy / EF positive | E_N ≈ +0.25R · EF ≈ +4.0pp (ungated) |
| 7 | Regime filter when needed | ATR 90–251 for Jul FRAGILE |
| 8 | Mix WR + returns | Primary RR1.5; Harvest RR1.0 sibling |

---

## 5. Chart load steps

1. Open **Microsoft** M15 chart (YWO).
2. Attach **BMRG** Expert → Load `BMRG-M15-MSFT-6M-P0_balanced_TPgtSL.set`.
3. Confirm: Magic **26101901** · SL 400 · TP 600 · ATR regime ON · AOS OFF.
4. Optional WR sibling: load Harvest `.set` (Magic **26101902**).
5. Strategy Tester: folder `Profiles/Tester/BMRG/MSFT/` · same window · every-tick / real ticks when available.

---

## 6. Provenance

- Probe script: `server/scripts/bmrg_msft_m15_6m_audit.py`
- Models: `regimes.rule_v1` · `fit.map_v0`
- Generated from local Ouroboros pipe · research / advisory only
- Ex-post M15* FIXED_RR probe is **not** a Tester blotter and **not** a profit claim

Research / advisory only. fit.map_v0 + Stage-1 design priors gate research books — not execution.
