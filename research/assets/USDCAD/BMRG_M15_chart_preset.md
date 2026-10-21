# BMRG M15 USDCAD ~6M — Chart Preset (Selective Geometry + ATR Regime)

**Status:** RESEARCH CHART PRESET / UNTESTED  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Preset:** `Presets/BMRG-M15-USDCAD-6M-P0_selective_chart.set`  
**Tester dir:** `Profiles/Tester/BMRG/USDCAD/` (own symbol folder · `.set` + this card + README)  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md` · BMRG `system_profile.md`  
**Ouroboros audit:** `Ouroboros/research/assets/USDCAD/bmrg_m15_6m_audit.json`

| Field | Value |
| --- | --- |
| EA | BMRG (Bollinger Mean-Reversion Grid) v1.21 |
| Class | Mean reversion fade (FIXED_RR) · **regime-filtered** · **selective BB** |
| Symbol | USDCAD (fx loonie major · Point ≈ 0.00001) |
| Chart TF | **M15** |
| Window | **2026.04.01 → 2026.09.21** (~6 months of available tip) |
| Aggregation | G0 basket events (`MaxLevels=1`, `MaxEntries=1`) |
| Magic | **26101901** |

---

## 1. Last-6m asset context (Ouroboros)

`regimes.rule_v1` → `fit.map_v0` **meanrev** on H1 (home cell for BMRG):

| Month | Tag | MATCH% | FRAGILE% |
| --- | --- | ---: | ---: |
| 2026-04 | **MISMATCH** | 40.9 | 17.2 |
| 2026-05 | MATCH | 50.6 | 24.6 |
| 2026-06 | MATCH | 39.8 | 33.0 |
| 2026-07 | MATCH | 53.7 | 24.6 |
| 2026-08 | MATCH | 47.5 | 20.5 |
| 2026-09 | **MISMATCH** | 22.4 | 21.4 |

**Read:** May–Aug on-home for meanrev. **Apr + Sep MISMATCH** (trend mass edges ranging) — ATR max gate is required so the sleeve trades inside quieter meanrev ATR, not the off-home tip. Live 30d fit tip is meanrev **MISMATCH** (trending_up-led); confirmed H1 state is stale trending_up.

**M15 ATR (points, Point=0.00001):** p50 ≈ 47.5 · p75 ≈ 59.6 · p90 ≈ 71.8 · mean ≈ 50.6.  
Loonie major — **quieter than EURUSD** (ATR p50 often ~70–90). Do **not** import EURUSD 300pt SL floors (wrong ATR scale).

---

## 2. Unified Edge Framework geometry (design)

Hard rules from framework + factory:

```text
never TP < SL          →  InpTP_Points ≥ InpSL_Points
RR_design = TP / SL    →  175 / 140 = 1.25
BWR = 1 / (1 + R)      →  44.44% if R ≈ RR
E_N = WR × (R + 1) − 1
BM  = WR − BWR
Leak = c_R / (R + 1)
EF  = BM − Leak
```

| Piece | Choice | Intent |
| --- | --- | --- |
| SL | **140** pts | ~2.9× ATR p50 — structural 1R that clears BWR on this quiet major |
| TP | **175** pts | **TP > SL** · designed RR **1.25** (mix WR + returns) |
| BB | 20 / **2.4σ** | Selective threshold (2.2 base failed Stage-1 Leak under 20pt prior) |
| Session | **12:00–20:00** server | London/NY overlap |
| Skip Tue | **true** | Weekday cut (champ pattern) |
| Cooldown | **3** bars | Selectivity with BB 2.4 |
| ATR regime | **ON · max 59** | ≈ p75 — cut high-vol / off-home sleeves |
| BB-width | OFF | Avoid fire starvation |
| MaxSpread | **20** | Cost prior **15 pts** RT (Leak under control) |
| Grid | depth **1** | Clean G0 events |
| AOS | **OFF** | Chart sleeve = engine only |

**Why not EURUSD SL 300?** USDCAD M15 ATR p50 ≈ 47.5 — importing 300 would be ~6× ATR and starve fires under ATR≤59.  
**Why not Harvest RR=1.0?** Lower payoff; user target = mix WR + returns. RR=1.25 sits in the preferred [1.20, 1.35] band.  
**Why BB 2.4 + ATR max 59?** Declared **regime-filtered + selective** (framework Gate G3): BB 2.2 / SL 145 cleared Stage-0 but Stage-1 EF flipped negative under a 20pt cost prior. BB 2.4 lifts WR to **56.4%** and Stage-1 **EF ≈ +5.6pp** (cost20) / **+7.2pp** (cost15) with n=39.

---

## 3. M15* probe scorecard (design evidence — not Tester blotter)

Closed-bar fade → next open · fixed TP/SL · session 12–20 · skip Tue · ~6m M1→M15* resample · cost priors 12 / 15 / 20 pts RT.

| Sleeve | n | WR | RR | BWR | BM | Leak† | EF | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **P0 selective 140/175 BB2.4 + ATR≤59 (chosen)** | 39 | 56.4% | 1.25 | 44.4% | +12.0pp | ~5.3pp‡ | **+5.6–+8.2pp** | **+0.269R** | Stage-1 design-positive |
| BB2.4 · 145/175 + ATR≤59 | 39 | 56.4% | 1.21 | 45.3% | +11.1pp | ~5.3pp‡ | +4.9–+7.4pp | +0.245R | RR alt |
| BB2.4 · 145/180 + ATR≤59 | 39 | 53.8% | 1.24 | 44.6% | +9.2pp | ~5.3pp‡ | +3.1–+5.5pp | +0.207R | thinner WR |
| BB2.2 · 140/175 + ATR≤59 | 61 | 50.8% | 1.25 | 44.4% | +6.4pp | ~5.3pp‡ | ~0–+2.6pp | +0.143R | more n; EF thin at cost20 |
| BB2.2 · 145/180 + ATR≤59 | 61 | 49.2% | 1.24 | 44.6% | +4.6pp | ~6.2pp§ | −1.6–+0.9pp | +0.102R | Stage-0 ok; Leak bites |
| BB2.2 · 145/180 (no ATR) | 147 | 49.0% | 1.24 | 44.6% | +4.4pp | ~6.2pp§ | −1.8–+0.7pp | +0.098R | no regime cut |
| P0 ATR-scaled 95/125 + ATR≤50 | 28 | 39.3% | 1.32 | 43.1% | −3.9pp | — | negative | −0.090R | starved + WR≪BWR |

† `c_R` prior ≈ cost_rt / SL pts (framework Stage 1 — replace with blotter).  
‡ cost15 → Leak ≈ 15/140/(1+1.25) ≈ 4.8pp; cost12 ≈ 3.8pp; cost20 ≈ 6.3pp.  
§ cost20 / 145.

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP &lt; SL | **TP 175 > SL 140** (ConfigValidate enforces) |
| 2 | Designed RR ≥ 1.0 | **1.25** |
| 3 | WR can clear BWR | Probe WR 56.4% > BWR 44.4%; E_N ≫ 0 |
| 4 | Not WR-theatre (token SL) | SL 140 ≈ 2.9× USDCAD ATR p50 |
| 5 | Not lottery RR | RR 1.25, not ≥3 |
| 6 | G0 single-leg events | MaxLevels=1 / MaxEntries=1 |
| 7 | Filters protect edge, not starve | Session + ATR≤59 + BB 2.4; n≈39 (≥30) |
| 8 | Regime filter declared | ATR≤59 · meanrev home · Apr/Sep MISMATCH cut |
| 9 | AOS not required for geometry claim | AOS OFF |
| 10 | Incomplete tip noted | Bars end 2026-09-21 |

Stage-1 **EF ≈ +5.6pp** (cost20) / **+7.2pp** (cost15) on the selective tip. Geometry / WR / E_N are **not** restricted by design. Re-score blotter Leak before promoting.

---

## 5. Load path (chart)

1. Open **USDCAD M15** chart.  
2. Attach `Experts\BMRG\BMRG.ex5`.  
3. Inputs → **Load** →  
   `Experts\BMRG\Presets\BMRG-M15-USDCAD-6M-P0_selective_chart.set`  
4. Confirm: `SL=140` · `TP=175` · `BBDev=2.4` · time **12–20** · **Tue off** · **ATR max=59** · magic **26101901** · AOS off · MaxSpread **20**.  
5. Optional visual: Bollinger(20, 2.4) on chart (EA uses its own handles).

### Tester

Load from **`Profiles/Tester/BMRG/USDCAD/BMRG-M15-USDCAD-6M-P0_selective_chart.set`**.  
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
| BM by ATR tercile / month (esp. Apr / Sep MISMATCH) | |

**Accept to iterate:** `E_N>0`, `WR>BWR`, `EF>0` preferred, `RR−R` not crushed, fires not starved.  
**Reject geometry:** TP&lt;SL theatre, or WR≪BWR with OK R and no cost excuse, or EF≤0 after measured Leak with no regime excuse.

### Sleeve ladder (Tester)

| Sleeve | Magic | Delta | Status |
| --- | ---: | --- | --- |
| **P0** | **26101901** | BB 2.4 · RR 1.25 (140/175) · ATR≤59 · CD 3 · MaxSpread 20 | **NEXT — chart / Tester** |
| P0 RR1.21 alt | 26101902 | RR 1.21 (145/175) · ATR≤59 · BB 2.4 | alt if tip prefers wider SL |
| P0 fire-count | 26101903 | BB 2.2 · RR 1.25 (140/175) · ATR≤59 | more n · EF thin at cost20 |

---

## 7. Explicit non-claims

- Probe is a **design prior**, not a Strategy Tester blotter / G0–G5 gate.  
- EURUSD / USDJPY / GBPJPY / XAUUSD M15 balanced remain separate sleeves; this file is the **USDCAD M15** loonie-major sleeve for the last ~6m tip.  
- Do not raise `f` / MaxLevels until a scored blotter clears Stage 1 (`EF>0` after measured Leak).  
- `regime_filtered=true` for Gate G3 scoring — do not claim cross-regime robustness without re-open ATR gate tests (esp. Apr / Sep MISMATCH).  
- Live tip meanrev is **MISMATCH** — treat as a research chart sleeve for on-home windows, not a capital-scale claim into a trending tip.
