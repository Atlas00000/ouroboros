# BMRG M15 USDJPY ~6M — Chart Preset (Balanced Geometry + ATR Regime)

**Status:** RESEARCH CHART PRESET / UNTESTED  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Preset:** `Presets/BMRG-M15-USDJPY-6M-P0_balanced_chart.set`  
**Tester dir:** `Profiles/Tester/BMRG/USDJPY/` (own symbol folder · `.set` + this card + README)  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md` · BMRG `system_profile.md`  
**Ouroboros audit:** `Ouroboros/research/assets/USDJPY/bmrg_m15_6m_audit.json`

| Field | Value |
| --- | --- |
| EA | BMRG (Bollinger Mean-Reversion Grid) v1.21 |
| Class | Mean reversion fade (FIXED_RR) · **regime-filtered** |
| Symbol | USDJPY (fx yen major · Point ≈ 0.001) |
| Chart TF | **M15** |
| Window | **2026.04.01 → 2026.09.21** (~6 months of available tip) |
| Aggregation | G0 basket events (`MaxLevels=1`, `MaxEntries=1`) |
| Magic | **26101828** |

---

## 1. Last-6m asset context (Ouroboros)

`regimes.rule_v1` → `fit.map_v0` **meanrev** on H1 (home cell for BMRG):

| Month | Tag | MATCH% | FRAGILE% |
| --- | --- | ---: | ---: |
| 2026-04 | MATCH | 59.7 | 20.5 |
| 2026-05 | MATCH | 52.4 | 17.3 |
| 2026-06 | MATCH | 55.7 | 19.9 |
| 2026-07 | MATCH | 41.3 | 35.7 |
| 2026-08 | MATCH | 49.9 | 21.7 |
| 2026-09 | **FRAGILE** | 20.6 | **57.4** |

**Read:** Apr–Aug on-home for meanrev. **Sep FRAGILE** (high-vol tip) is the off-home month — ATR max gate is required so the sleeve trades inside regime. Live 30d fit tip is both-families FRAGILE; confirmed H1 state is stale trending_up.

**M15 ATR (points, Point=0.001):** p50 ≈ 65 · p75 ≈ 92 · p90 ≈ 133 · mean ≈ 80.  
Yen major — **quieter than GBPJPY** (ATR p50 ≈ 100). Do **not** import EURUSD 300pt or GBPJPY 160pt SL floors (wrong ATR scale).

---

## 2. Unified Edge Framework geometry (design)

Hard rules from framework + factory:

```text
never TP < SL          →  InpTP_Points ≥ InpSL_Points
RR_design = TP / SL    →  120 / 100 = 1.20
BWR = 1 / (1 + R)      →  45.45% if R ≈ RR
E_N = WR × (R + 1) − 1
BM  = WR − BWR
Leak = c_R / (R + 1)
EF  = BM − Leak
```

| Piece | Choice | Intent |
| --- | --- | --- |
| SL | **100** pts | ~1.5× ATR p50 — structural 1R on USDJPY M15 |
| TP | **120** pts | **TP > SL** · designed RR **1.20** (mix WR + returns) |
| BB | 20 / **2.2σ** | Signal threshold |
| Session | **12:00–20:00** server | London/NY overlap (Tokyo 02–12 failed probe) |
| Skip Tue | **true** | Weekday cut (champ pattern) |
| ATR regime | **ON · max 70** | ≈ tight (~p50 + 0.15×IQR) — cut Sep FRAGILE high-vol |
| BB-width | OFF | Avoid fire starvation (non-binding under ATR max) |
| MaxSpread | **25** | Major USDJPY — cost prior **25 pts** RT |
| Grid | depth **1** | Clean G0 events |
| AOS | **OFF** | Chart sleeve = engine only |

**Why not GBPJPY SL 160?** USDJPY M15 ATR p50 ≈ 65 — importing 160 would be ~2.5× ATR and crush fire-count under ATR≤70.  
**Why not Harvest RR=1.0?** Lower payoff; user target = mix WR + returns. RR=1.20 sits in the preferred [1.20, 1.35] band. Exact RR=1.25 (100/125) is thinner on Stage-1 under a 25pt cost prior — kept as alt with MaxSpread 20.  
**Why ATR max 70 ON?** Declared **regime-filtered** (framework Gate G3): Sep FRAGILE is the HV tip; ATR≤70 lifts WR to **57.6%** and Stage-1 **EF ≈ +0.8pp** with n=66. Wider ATR≤92 dilutes EF. No-gate still design-positive on E_N but EF turns negative under the same cost prior.

---

## 3. M15* probe scorecard (design evidence — not Tester blotter)

Closed-bar fade → next open · fixed TP/SL · session 12–20 · skip Tue · ~6m M1→M15* resample · cost prior **25 pts** RT (USDJPY MaxSpread sleeve).

| Sleeve | n | WR | RR | BWR | BM | Leak† | EF | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **P0 balanced 100/120 + ATR≤70 (chosen)** | 66 | 57.6% | 1.20 | 45.5% | +12.1pp | ~11.4pp | **+0.8pp** | **+0.267R** | Stage-1 design-positive |
| P0 RR1.25 100/125 + ATR≤70 | 66 | 53.0% | 1.25 | 44.4% | +8.6pp | ~11.1pp | −2.5pp | +0.193R | design-ok; Leak bites |
| Balanced 100/125 (no ATR gate) | 156 | 50.0% | 1.25 | 44.4% | +5.6pp | ~11.1pp | −5.6pp | +0.125R | Sep leak |
| ATR≤92 p75 100/125 | 108 | 49.1% | 1.25 | 44.4% | +4.6pp | ~11.1pp | −6.5pp | +0.104R | diluted |
| Session 02–12 Tokyo 100/125 + ATR≤70 | 113 | 45.1% | 1.25 | 44.4% | +0.7pp | ~11.1pp | −10.4pp | +0.015R | off-home session |
| Session 08–20 + ATR≤70 100/125 | 103 | 50.5% | 1.25 | 44.4% | +6.0pp | ~11.1pp | −5.1pp | +0.136R | wider session dilutes |
| BB 2.0 · 100/120 + ATR≤70 | 93 | 58.1% | 1.20 | 45.5% | +12.6pp | ~11.4pp | **+1.3pp** | +0.277R | fire-count alt |

† `c_R` prior ≈ 25 pts round-trip / SL pts (framework Stage 1 — replace with blotter).

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP &lt; SL | **TP 120 > SL 100** (ConfigValidate enforces) |
| 2 | Designed RR ≥ 1.0 | **1.20** |
| 3 | WR can clear BWR | Probe WR 57.6% > BWR 45.5%; E_N ≫ 0 |
| 4 | Not WR-theatre (token SL) | SL 100 ≈ 1.5× USDJPY ATR p50 |
| 5 | Not lottery RR | RR 1.20, not ≥3 |
| 6 | G0 single-leg events | MaxLevels=1 / MaxEntries=1 |
| 7 | Filters protect edge, not starve | Session + ATR≤70; n≈66 (≥30) |
| 8 | Regime filter declared | ATR≤70 · meanrev home · Sep FRAGILE cut |
| 9 | AOS not required for geometry claim | AOS OFF |
| 10 | Incomplete tip noted | Bars end 2026-09-21 |

Stage-1 **EF ≈ +0.8pp** on the full tip under a 25pt cost prior. Geometry / WR / E_N are **not** restricted by design. Re-score blotter Leak before promoting (EF is thin — measured costs matter).

---

## 5. Load path (chart)

1. Open **USDJPY M15** chart.  
2. Attach `Experts\BMRG\BMRG.ex5`.  
3. Inputs → **Load** →  
   `Experts\BMRG\Presets\BMRG-M15-USDJPY-6M-P0_balanced_chart.set`  
4. Confirm: `SL=100` · `TP=120` · `BBDev=2.2` · time **12–20** · **Tue off** · **ATR max=70** · magic **26101828** · AOS off · MaxSpread **25**.  
5. Optional visual: Bollinger(20, 2.2) on chart (EA uses its own handles).

### Tester

Load from **`Profiles/Tester/BMRG/USDJPY/BMRG-M15-USDJPY-6M-P0_balanced_chart.set`**.  
Dates **2026.04.01 – 2026.09.21**. Model: every tick / real ticks if available. Deposit ≥ 500.

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
| BM by ATR tercile / month (esp. Sep) | |

**Accept to iterate:** `E_N>0`, `WR>BWR`, `EF>0` preferred, `RR−R` not crushed, fires not starved.  
**Reject geometry:** TP&lt;SL theatre, or WR≪BWR with OK R and no cost excuse, or EF≤0 after measured Leak with no regime excuse.

### Sleeve ladder (Tester)

| Sleeve | Magic | Delta | Status |
| --- | ---: | --- | --- |
| **P0** | **26101828** | BB 2.2 · RR 1.20 (100/120) · ATR≤70 · CD 2 | **NEXT — chart / Tester** |
| P0 exact RR1.25 | 26101829 | RR 1.25 (100/125) · ATR≤70 · MaxSpread 20 | alt if tighter cost holds |
| P0 fire-count | 26101830 | BB 2.0 · RR 1.20 (100/120) · ATR≤70 | more n · EF≈+1.3pp |

---

## 7. Explicit non-claims

- Probe is a **design prior**, not a Strategy Tester blotter / G0–G5 gate.  
- EURUSD / GBPJPY / XAUUSD M15 balanced remain separate sleeves; this file is the **USDJPY M15** yen-major sleeve for the last ~6m tip.  
- Do not raise `f` / MaxLevels until a scored blotter clears Stage 1 (`EF>0` after measured Leak).  
- `regime_filtered=true` for Gate G3 scoring — do not claim cross-regime robustness without re-open ATR gate tests (esp. Sep FRAGILE).  
- Stage-1 EF is **thin (+0.8pp)** under the 25pt prior — treat as a research chart sleeve, not a capital-scale claim.
