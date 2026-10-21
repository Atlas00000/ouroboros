# BMRG M5 EURGBP ~6M — Chart Preset (Balanced Geometry + ATR Regime)

**Status:** RESEARCH CHART PRESET / UNTESTED  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Preset:** `Presets/BMRG-M5-EURGBP-6M-P0_balanced_chart.set`  
**Tester dir:** `Profiles/Tester/BMRG/EURGBP/` (own symbol folder · `.set` + this card + README)  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md` · BMRG `system_profile.md`  
**Ouroboros audit:** `Ouroboros/research/assets/EURGBP/bmrg_m5_6m_audit.json`

| Field | Value |
| --- | --- |
| EA | BMRG (Bollinger Mean-Reversion Grid) v1.21 |
| Class | Mean reversion fade (FIXED_RR) · **regime-filtered** |
| Symbol | EURGBP (fx cross · Point ≈ 0.00001) |
| Chart TF | **M5** |
| Window | **2026.04.01 → 2026.09.11** (~6 months of available tip) |
| Aggregation | G0 basket events (`MaxLevels=1`, `MaxEntries=1`) |
| Magic | **26101950** |

---

## 1. Last-6m asset context (Ouroboros)

`regimes.rule_v1` → `fit.map_v0` **meanrev** on H1 (home cell for BMRG):

| Month | Tag | MATCH% | FRAGILE% |
| --- | --- | ---: | ---: |
| 2026-04 | MATCH | 71.5 | 12.2 |
| 2026-05 | MATCH | 50.2 | 28.8 |
| 2026-06 | MATCH | 56.8 | 18.6 |
| 2026-07 | **FRAGILE** | 34.6 | **43.4** |
| 2026-08 | MATCH | 65.7 | 3.9 |
| 2026-09 | MATCH | 49.8 | 24.9 |

**Read:** Apr–Jun and Aug–Sep on-home for meanrev. **Jul FRAGILE** is the off-home month — ATR max gate keeps the M5 sleeve trading inside regime. Bars tip ends 2026-09-11.

**M5 ATR (points, Point=0.00001):** p50 ≈ 14 · p75 ≈ 19 · p90 ≈ 23 · mean ≈ 15.  
Quiet cross — **do not import EURUSD M5 250–320pt floors** (that would be ~20× ATR and restrict WR by design).

---

## 2. Unified Edge Framework geometry (design)

Hard rules from framework + factory:

```text
never TP < SL          →  InpTP_Points ≥ InpSL_Points
RR_design = TP / SL    →  65 / 50 = 1.30
BWR = 1 / (1 + R)      →  43.48% if R ≈ RR
E_N = WR × (R + 1) − 1
BM  = WR − BWR
Leak = c_R / (R + 1)
EF  = BM − Leak
```

| Piece | Choice | Intent |
| --- | --- | --- |
| SL | **50** pts | ~3.5× ATR p50 — structural 1R (cost-aware on M5) |
| TP | **65** pts | **TP > SL** · designed RR **1.30** |
| BB | 20 / **2.2σ** | Signal threshold |
| Session | **12:00–20:00** server | London/NY overlap |
| Skip Tue | **true** | Weekday cut (champ pattern) |
| ATR regime | **ON · max 18** | ≈ M5 ATR p75 — cut Jul FRAGILE |
| BB-width | OFF | Avoid fire starvation |
| MaxSpread | **18** | Keep realized Leak near 12pt RT prior |
| Cooldown | **3** bars | Mild re-entry spacing on M5 |
| Grid | depth **1** | Clean G0 events |
| AOS | **OFF** | Chart sleeve = engine only |

**Why not ATR×2.5 (SL 35 / TP 45)?** Probe E_N ≤ 0 under 12pt cost prior — geometry restricted by token stop vs quiet-cross friction.  
**Why not Harvest RR=1.0?** Lower payoff; user target = mix WR + returns.  
**Why ATR max 18 ON?** Declared **regime-filtered** (framework Gate G3): Jul FRAGILE high-vol; p75 gate keeps n≈170 while protecting EF vs unfiltered.

---

## 3. M5* probe scorecard (design evidence — not Tester blotter)

Closed-bar fade → next open · fixed TP/SL · session 12–20 · skip Tue · ~6m M1→M5* resample · cost prior **12 pts** RT (tight MaxSpread sleeve).

| Sleeve | n | WR | RR | BWR | BM | Leak† | EF | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **P0 balanced 50/65 + ATR≤18 (chosen)** | 170 | 50.0% | 1.30 | 43.5% | +6.5pp | ~10.4pp | **−3.9pp** | **+0.150R** | design-positive |
| Balanced 45/55 + ATR≤18 | 170 | 52.4% | 1.22 | 45.0% | +7.3pp | ~11.8pp | −4.7pp | +0.163R | WR-lean alt |
| Balanced 50/60 + ATR≤18 | 170 | 51.8% | 1.20 | 45.5% | +6.3pp | ~10.9pp | −4.6pp | +0.139R | alt |
| P0 ATR×2.5 35/45 + ATR≤15 | 86 | 43.0% | 1.29 | 43.7% | −0.7pp | ~15.0pp | −15.7pp | −0.017R | **restricted** |
| P0b EF-lean 45/55 BB2.0 + ATR≤23 | 358 | 46.9% | 1.22 | 45.0% | +1.9pp | ~12.0pp | −10.1pp | +0.043R | more fires |

† `c_R` prior ≈ 12 pts round-trip / SL pts (framework Stage 1 — replace with blotter).

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP &lt; SL | **TP 65 > SL 50** (ConfigValidate enforces) |
| 2 | Designed RR ≥ 1.0 | **1.30** |
| 3 | WR can clear BWR | Probe WR 50.0% > BWR 43.5%; E_N ≫ 0 |
| 4 | Not WR-theatre (token SL) | SL 50 ≈ 3.5× quiet-cross M5 ATR p50 |
| 5 | Not lottery RR | RR 1.30, not ≥3 |
| 6 | G0 single-leg events | MaxLevels=1 / MaxEntries=1 |
| 7 | Filters protect edge, not starve | Session + ATR≤18; n≈170 |
| 8 | Regime filter declared | ATR≤p75 · meanrev home · Jul FRAGILE cut |
| 9 | AOS not required for geometry claim | AOS OFF |
| 10 | Incomplete tip noted | Bars end 2026-09-11 |

Stage-1 **EF** is ≈ −4pp on the full tip under a 12pt cost prior (quiet-cross cost/ATR ratio on M5). Geometry / WR / E_N are **not** restricted; tighten fills (`MaxSpread=18`) and re-score blotter Leak before promoting.

---

## 5. Load path (chart)

1. Open **EURGBP M5** chart.  
2. Attach `Experts\BMRG\BMRG.ex5`.  
3. Inputs → **Load** →  
   `Experts\BMRG\Presets\BMRG-M5-EURGBP-6M-P0_balanced_chart.set`  
4. Confirm: `SL=50` · `TP=65` · `BBDev=2.2` · time **12–20** · **Tue off** · **ATR max=18** · magic **26101950** · AOS off · MaxSpread **18**.  
5. Optional visual: Bollinger(20, 2.2) on chart (EA uses its own handles).

### Tester

Load from **`Profiles/Tester/BMRG/EURGBP/BMRG-M5-EURGBP-6M-P0_balanced_chart.set`**.  
Dates **2026.04.01 – 2026.09.11**. Model: every tick / real ticks if available. Deposit ≥ 500.

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
| BM by ATR tercile / month (esp. Jul) | |

**Accept to iterate:** `E_N>0`, `WR>BWR`, `EF>0` preferred, `RR−R` not crushed, fires not starved.  
**Reject geometry:** TP&lt;SL theatre, or WR≪BWR with OK R and no cost excuse, or EF≤0 after measured Leak with no regime excuse.

### Sleeve ladder (Tester)

| Sleeve | Magic | Delta | Status |
| --- | ---: | --- | --- |
| **P0** | **26101950** | BB 2.2 · RR 1.30 (50/65) · ATR≤18 · CD 3 | **NEXT — chart / Tester** |
| P0 WR-lean | 26101951 | RR ~1.22 (45/55) · ATR≤18 | alt if WR lab needed |
| M15 P0 (sibling) | 26101215 | same 50/65 · ATR≤28 on M15 | separate TF sleeve |

---

## 7. Explicit non-claims

- Probe is a **design prior**, not a Strategy Tester blotter / G0–G5 gate.  
- EURGBP M15 P0 (magic 26101215) is a separate sleeve; this file is the **M5** quiet-cross chart preset.  
- Do not raise `f` / MaxLevels until a scored blotter clears Stage 1 (`EF>0` after measured Leak).  
- `regime_filtered=true` for Gate G3 scoring — do not claim cross-regime robustness without re-open ATR gate tests (esp. Jul FRAGILE).
