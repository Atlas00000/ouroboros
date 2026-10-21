# BMRG M15 AUDUSD ~6M — Chart Preset (Balanced Geometry + ATR Regime)

**Status:** RESEARCH CHART PRESET / UNTESTED  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Preset:** `Presets/BMRG-M15-AUDUSD-6M-P0_balanced_chart.set`  
**Tester dir:** `Profiles/Tester/BMRG/AUDUSD/` (own symbol folder · `.set` + this card)  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md` · BMRG `system_profile.md`  
**Ouroboros audit:** `Ouroboros/research/assets/AUDUSD/bmrg_m15_6m_audit.json`  
**Canvas cover:** [`bmrg-audusd-m15-preset.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-audusd-m15-preset.canvas.tsx)

| Field | Value |
| --- | --- |
| EA | BMRG (Bollinger Mean-Reversion Grid) v1.21 |
| Class | Mean reversion fade (FIXED_RR) · **regime-filtered** |
| Symbol | AUDUSD (fx major · Point ≈ 0.00001) |
| Chart TF | **M15** |
| Window | **2026.04.01 → 2026.09.21** (~6 months of available tip) |
| Aggregation | G0 basket events (`MaxLevels=1`, `MaxEntries=1`) |
| Magic | **26101901** |

---

## 1. Last-6m asset context (Ouroboros)

`regimes.rule_v1` → `fit.map_v0` **meanrev** on H1 (home cell for BMRG):

| Month | Tag | MATCH% | FRAGILE% |
| --- | --- | ---: | ---: |
| 2026-04 | MATCH | 52.7 | 13.6 |
| 2026-05 | MATCH | 39.9 | 24.8 |
| 2026-06 | MATCH | 57.4 | 19.7 |
| 2026-07 | MATCH | 56.6 | 23.7 |
| 2026-08 | MATCH | 48.3 | 15.8 |
| 2026-09 | MATCH | 58.9 | 23.4 |

**Read:** Apr–Sep **all MATCH** for meanrev — no FRAGILE tip month (unlike EURUSD/USDJPY). Overall H1 meanrev ≈52% MATCH / 20% FRAGILE. Live 30d fit is also **MATCH** (ranging-led). ATR max still pays: cutting intra-month high-vol mass lifts Stage-1 EF without starving fire-count.

**M15 ATR (points, Point=0.00001):** p50 ≈ 44 · p75 ≈ 55 · p90 ≈ 69 · mean ≈ 47.  
Aussie major — **do not** import EURUSD 300pt SL floors (wrong ATR scale). SL 130 ≈ 3× ATR p50.

---

## 2. Unified Edge Framework geometry (design)

Hard rules from framework + factory:

```text
never TP < SL          →  InpTP_Points ≥ InpSL_Points
RR_design = TP / SL    →  170 / 130 ≈ 1.31
BWR = 1 / (1 + R)      →  43.3% if R ≈ RR
E_N = WR × (R + 1) − 1
BM  = WR − BWR
Leak = c_R / (R + 1)
EF  = BM − Leak
```

| Piece | Choice | Intent |
| --- | --- | --- |
| SL | **130** pts | ~3× ATR p50 — structural 1R on AUDUSD M15 |
| TP | **170** pts | **TP > SL** · designed RR **≈1.31** (mix WR + returns) |
| BB | 20 / **2.2σ** | Signal threshold |
| Session | **12:00–20:00** server | London/NY overlap |
| Skip Tue | **true** | Weekday cut (champ pattern) |
| ATR regime | **ON · max 55** | ≈ M15 p75 — cut high-vol sleeve (Gate G3) |
| BB-width | OFF | Avoid fire starvation |
| MaxSpread | **30** | Cost prior **20 pts** RT |
| Grid | depth **1** | Clean G0 events |
| AOS | **OFF** | Chart sleeve = engine only |

**Why not Harvest RR=1.0?** Higher WR theatre, lower payoff; user target = mix WR + returns.  
**Why not Growth RR=1.5 (130/195)?** Probe EF even higher (~+7.1pp) but RR leaves the preferred [1.20, 1.35] band — kept as alt.  
**Why ATR max 55 ON?** Declared **regime-filtered** (framework Gate G3): even with all months MATCH, high-vol bars dilute EF. ATR≤55 lifts EF to **≈+4.6pp** with n=77 vs no-gate EF≈+2.7pp n=146. Tight ATR≤45 starves n≈38.  
**Why not P0 ATR-scaled 85/110?** Under ATR≤45, Stage-1 EF turns negative (Leak bites small SL) — reject for chart.

---

## 3. M15* probe scorecard (design evidence — not Tester blotter)

Closed-bar fade → next open · fixed TP/SL · session 12–20 · skip Tue · ~6m M1→M15* resample · cost prior **20 pts** RT.

| Sleeve | n | WR | RR | BWR | BM | Leak† | EF | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **P0 balanced 130/170 + ATR≤55 (chosen)** | 77 | 54.5% | 1.31 | 43.3% | +11.2pp | ~6.7pp | **+4.6pp** | **+0.259R** | Stage-1 ok |
| Balanced 110/145 RR1.32 + ATR≤55 | 78 | 55.1% | 1.32 | 43.1% | +12.0pp | ~7.8pp | +4.2pp | +0.278R | WR-lean alt |
| Balanced 130/160 RR1.23 + ATR≤55 | 77 | 54.5% | 1.23 | 44.8% | +9.7pp | ~6.9pp | +2.8pp | +0.217R | RR1.25 band |
| Growth 130/195 RR1.5 + ATR≤55 | 77 | 53.2% | 1.50 | 40.0% | +13.2pp | ~6.2pp | +7.1pp | +0.331R | alt (RR outside band) |
| 130/170 ATR≤69 (p90) | 114 | 53.5% | 1.31 | 43.3% | +10.2pp | ~6.7pp | +3.5pp | +0.235R | more fires |
| 130/170 ATR≤45 (tight) | 38 | 52.6% | 1.31 | 43.3% | +9.3pp | ~6.7pp | +2.6pp | +0.215R | thin n |
| 130/170 no ATR gate | 146 | 52.7% | 1.31 | 43.3% | +9.4pp | ~6.7pp | +2.7pp | +0.217R | diluted |
| P0 85/110 + ATR≤45 | 38 | 50.0% | 1.29 | 43.6% | +6.4pp | ~10.3pp | **−3.9pp** | +0.147R | reject |

† `c_R` prior ≈ 20 pts round-trip / SL pts (framework Stage 1 — replace with blotter).

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP &lt; SL | **TP 170 > SL 130** (ConfigValidate enforces) |
| 2 | Designed RR ≥ 1.0 | **≈1.31** |
| 3 | WR can clear BWR | Probe WR 54.5% > BWR 43.3%; E_N ≫ 0 |
| 4 | Not WR-theatre (token SL) | SL 130 ≈ 3× AUDUSD ATR p50 |
| 5 | Not lottery RR | RR 1.31, not ≥3 |
| 6 | G0 single-leg events | MaxLevels=1 / MaxEntries=1 |
| 7 | Filters protect edge, not starve | Session + ATR≤55; n≈77 (≥30) |
| 8 | Regime filter declared | ATR≤55 · meanrev home · high-vol cut |
| 9 | AOS not required for geometry claim | AOS OFF |
| 10 | Incomplete tip noted | Bars end 2026-09-21 |

Stage-1 **EF ≈ +4.6pp** under a 20pt cost prior. Geometry / WR / E_N are **not** restricted by design. Re-score blotter Leak before promoting.

---

## 5. Load path (chart)

1. Open **AUDUSD M15** chart.  
2. Attach `Experts\BMRG\BMRG.ex5`.  
3. Inputs → **Load** →  
   `Experts\BMRG\Presets\BMRG-M15-AUDUSD-6M-P0_balanced_chart.set`  
4. Confirm: `SL=130` · `TP=170` · `BBDev=2.2` · time **12–20** · **Tue off** · **ATR max=55** · magic **26101901** · AOS off · MaxSpread **30**.  
5. Optional visual: Bollinger(20, 2.2) on chart (EA uses its own handles).

### Tester

Load from **`Profiles/Tester/BMRG/AUDUSD/BMRG-M15-AUDUSD-6M-P0_balanced_chart.set`**.  
Dates **2026.04.01 – 2026.09.21**. Model: every tick / real ticks if available. Deposit ≥ 500.

---

## 6. Post-run fill (framework Stage 0–1)

_Pending Strategy Tester blotter · magic **26101901**._

| Check | Result |
| --- | --- |
| Never TP &lt; SL | Design pass — TP 170 > SL 130 |
| Geometry / payoff | Design pass — RR≈1.31 held in probe |
| Hit-rate / Stage 0 | Design prior WR 54.5% > BWR 43.3% — **confirm on blotter** |
| Regime filter active | ATR≤55 ON · session 12–20 · skip Tue |

**Accept to iterate:** tip n≥30 · WR > BWR · E_N > 0 · EF>0 after measured Leak.  
**Reject geometry:** only if blotter shows TP&lt;SL theatre or R collapses — not indicated by probe.

---

## 7. Explicit non-claims

- Probe is a **design prior**, not a Strategy Tester blotter / G0–G5 gate.  
- EURUSD / USDJPY / USDCAD M15 balanced remain separate sleeves.  
- Do not raise `f` / MaxLevels until a scored blotter clears Stage 1 (`EF>0` after measured Leak).  
- `regime_filtered=true` for Gate G3 scoring — do not claim cross-regime robustness without re-open ATR gate tests.
