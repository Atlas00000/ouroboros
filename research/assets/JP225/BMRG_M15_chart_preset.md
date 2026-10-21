# BMRG M15 JP225 ~6M — Chart Preset (Growth Geometry + ATR Regime)

**Status:** RESEARCH CHART PRESET / UNTESTED  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Preset:** `Presets/BMRG-M15-JP225-6M-P0_growth_chart.set`  
**Tester dir:** `Profiles/Tester/BMRG/JP225/` (own symbol folder · `.set` + this card)  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md` · BMRG `system_profile.md`  
**Ouroboros audit:** `Ouroboros/research/assets/JP225/bmrg_m15_6m_audit.json`  
**Canvas cover:** [`bmrg-jp225-m15-preset.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-jp225-m15-preset.canvas.tsx)

| Field | Value |
| --- | --- |
| EA | BMRG (Bollinger Mean-Reversion Grid) v1.23 |
| Class | Mean reversion fade (FIXED_RR) · **regime-filtered** |
| Symbol | JP225 → MT5 **JPN225** (Nikkei · Point = 0.01 · Digits=2) |
| Chart TF | **M15** |
| Window | **2026.05.01 → 2026.10.07** (~6 months) |
| Aggregation | G0 basket events (`MaxLevels=1`, `MaxEntries=1`) |
| Magic | **26101903** |

---

## 1. Last-6m asset context (Ouroboros)

`regimes.rule_v1` → `fit.map_v0` **meanrev** on H1 (home cell for BMRG):

| Month | Tag | MATCH% | FRAGILE% |
| --- | --- | ---: | ---: |
| 2026-05 | FRAGILE | 33.1 | 37.9 |
| 2026-06 | FRAGILE | 31.8 | 42.9 |
| 2026-07 | MISMATCH | 29.0 | 30.9 |
| 2026-08 | MATCH | 61.2 | 12.4 |
| 2026-09 | MATCH | 47.0 | 13.2 |
| 2026-10 | MISMATCH | 37.4 | 5.6 |

**Read:** Aug–Sep on-home for meanrev. **May–Jun FRAGILE** (high-vol) and **Jul/Oct MISMATCH** (trend-contested) are off-home — ATR max gate reduces trading in the high-vol cell. Live 30d fit is **MATCH** (ranging-contested ~45% MATCH / ~42% MISMATCH). Incomplete Oct tip is not admission evidence.

**M15 ATR (points, Point=0.01):** p50 ≈ 15509 · p75 ≈ 19673 · p90 ≈ 25065 · mean ≈ 16660.  
**Broker friction (live):** Digits=2 · **spread ≈ 2300 pts** · volume_min = 0.1 → cost prior RT ≈ **2500 pts**.  
> JPN225 spread is ~2× DE40 and ~16× UK100 — geometry must use a fat SL + higher RR or Leak destroys EF.

---

## 2. Unified Edge Framework geometry (design)

Hard rules from framework + factory:

```text
never TP < SL          →  InpTP_Points ≥ InpSL_Points
RR_design = TP / SL    →  34890 / 23260 = 1.50
BWR = 1 / (1 + R)      →  40.00% if R ≈ RR
E_N = WR × (R + 1) − 1
BM  = WR − BWR
Leak = c_R / (R + 1)
EF  = BM − Leak
```

| Piece | Choice | Intent |
| --- | --- | --- |
| SL | **23260** pts | Structural 1R on JP225 M15 (~1.5× ATR p50) — clears ~2300 spread Leak |
| TP | **34890** pts | **TP > SL** · designed RR **1.50** |
| BB | 20 / **2.2σ** | Signal threshold |
| Session | **08:00–17:00** server | London sleeve (Tokyo 02–09 probed worse) |
| Skip Tue | **true** | Weekday cut (champ pattern) |
| ATR regime | **ON · max 19670** | ≈ ATR p75 — cut May/Jun FRAGILE high-vol |
| BB-width | OFF | Avoid fire starvation |
| Grid | depth **1** | Clean G0 events |
| Lot | **0.1** | Broker min volume |
| MaxSpread | **3000** | Must exceed live spread ≈2300 |
| AOS | **OFF** | Chart sleeve = engine only |

**Why Growth RR=1.5 (not Balanced 1.25)?** Under cost prior 2500, Balanced 23260/29080 + ATR≤p75 has EF **−0.3pp** (WR 48.9% clears BWR but Leak ≈4.8pp eats BM). Growth lifts R → lowers BWR to 40% and Leak to ~4.3pp → EF **+3.2pp**.  
**Why not ATR-p50 SL (~15510)?** `c_R` ≈ 2500/15510 → Leak ≈7.2pp — E_N and EF go negative even with ATR gate.  
**Why not Harvest RR=1.0?** Higher WR (~54%) but EF **−1.3pp** after Leak — fails Stage 1 prior.  
**Why ATR max p75?** May–Jun FRAGILE + Gate G3: lifts EF vs unfiltered (+3.2pp vs +2.8pp) while keeping n≈139.

---

## 3. M15* probe scorecard (design evidence — not Tester blotter)

Closed-bar fade → next open · fixed TP/SL · session 08–17 · skip Tue · BBDev 2.2 · ~6m M1→M15* resample · cost prior **2500 pts** RT.

| Sleeve | n | WR | RR | BWR | BM | Leak† | EF | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **Growth 23260/34890 + ATR≤19670 (chosen)** | 139 | 47.5% | 1.50 | 40.0% | +7.5pp | ~4.3pp | **+3.2pp** | **+0.187R** | design-viable |
| Growth 23260/34890 + ATR≤25065 (p90) | 163 | 46.6% | 1.50 | 40.0% | +6.6pp | ~4.3pp | +2.3pp | +0.166R | looser alt |
| Growth 23260/34890 (no ATR gate) | 170 | 47.1% | 1.50 | 40.0% | +7.1pp | ~4.3pp | +2.8pp | +0.176R | diluted EF |
| Balanced 23260/29080 + ATR≤19670 | 139 | 48.9% | 1.25 | 44.4% | +4.5pp | ~4.8pp | **−0.3pp** | +0.101R | reject (Leak) |
| Balanced 15510/19390 + ATR≤19670 | 139 | 43.2% | 1.25 | 44.4% | −1.3pp | ~7.2pp | **−8.4pp** | −0.029R | reject |
| Harvest 23260/23260 (no ATR) | 170 | 54.1% | 1.00 | 50.0% | +4.1pp | ~5.4pp | **−1.3pp** | +0.082R | reject (Leak) |
| Tokyo 02–09 15510/19390 | 72 | 43.1% | 1.25 | 44.4% | −1.4pp | ~7.2pp | **−8.6pp** | −0.031R | off-home session |

† `c_R` prior ≈ 2500 pts round-trip / SL pts (framework Stage 1 — replace with blotter).  
Live JPN225 spread measured **≈2300 pts** at design time — re-check before Tester.

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP < SL | **TP 34890 > SL 23260** |
| 2 | Designed RR ≥ 1.0 | **1.50** |
| 3 | WR can clear BWR after Leak prior | Probe WR 47.5% > BWR 40.0%; EF ≫ 0 |
| 4 | Not WR-theatre (token SL) | SL 23260 structural vs JP225 M15 ATR + fat spread |
| 5 | Not lottery RR | RR 1.50, not ≥3 |
| 6 | G0 single-leg events | MaxLevels=1 / MaxEntries=1 |
| 7 | Filters protect edge, not starve fires | Session + ATR max; BB-width OFF; n≈139 |
| 8 | Regime filter declared | ATR≤p75 · meanrev home · May/Jun FRAGILE cut |
| 9 | AOS not required for geometry claim | AOS OFF |
| 10 | Incomplete tip not used for admission | Oct MISMATCH noted only |
| 11 | Mix WR + returns (not Harvest-only) | RR 1.5 Growth — Balanced fails Leak on this name |

---

## 5. Load path (chart)

1. Open **JPN225** M15 chart (YWO ticker for JP225).  
2. Attach `Experts\BMRG\BMRG.ex5`.  
3. Inputs → **Load** →  
   `Experts\BMRG\Presets\BMRG-M15-JP225-6M-P0_growth_chart.set`  
4. Confirm: `SL=23260` · `TP=34890` · `BBDev=2.2` · time **08–17** · **Tue off** · **ATR max=19670** · lot **0.1** · MaxSpread **3000** · magic **26101903** · AOS off.  
5. Optional visual: Bollinger(20, 2.2) on chart (EA uses its own handles).

### Tester

Load from **`Profiles/Tester/BMRG/JP225/BMRG-M15-JP225-6M-P0_growth_chart.set`**.  
Symbol: **JPN225**. Dates **2026.05.01 – 2026.10.07** (or through Sep end to skip Oct MISMATCH tip). Model: every tick / real ticks if available. Deposit ≥ **5000** (index min lot + fat SL).

---

## 6. Post-run fill (framework Stage 0–1)

Scored from Tester log `20261019.log` · magic **26101903** · deal-pair G0 events · Leak prior **2500 pts** RT.  
Script: `_score_magic_26101903.py` → [`tester_magic_26101903_score.json`](./tester_magic_26101903_score.json).

| Metric | Tip run (2026.05.01→08.31) | Long run (2026.01.01→08.31) |
| --- | ---: | ---: |
| n | **99** | **195** |
| WR | **42.4%** | **38.5%** |
| R = AW/AL | **1.542** | **1.550** |
| BWR = 1/(1+R) | 39.4% | 39.2% |
| BM = WR−BWR | **+3.1pp** | **−0.8pp** |
| Leak prior (2500/SL) | ~4.2pp | ~4.2pp |
| EF = BM−Leak | **−1.1pp** | **−5.0pp** |
| E_N = WR×(R+1)−1 | **+0.078R** | **−0.019R** |
| kinds | TP 42 / SL 57 | TP 75 / SL 120 |
| tp_lt_sl opens | **0** | **0** |
| deposit / final | 500 → 510.47 | 500 → 492.01 |

**Geometry check:** SL=23260 · TP=34890 · RR=1.50 · ATR max=19670 · BBDev=2.2 · ATR regime ON — matches preset. Hard rule held (never TP&lt;SL). Realised R ≈ design RR (no RR crush).

**Monthly (tip):** May WR40% / Jun **54%** (+10R) / Jul 36% / Aug 38%. Jun carries the tip; May FRAGILE + Jul MISMATCH drag WR below probe (47.5%).

**Verdict:** Stage 0 tip is weakly positive (`E_N>0`, `WR>BWR`) but **Stage 1 fails** (`EF≤0` after Leak prior). Probe overstated WR. Currency PnL on this deposit is not the diagnosis — raise WR, not capital. No Sep–Oct tip in these runs.

**Accept to iterate:** lift WR (see §7 P1) until `WR > BWR + Leak` / `EF>0`. Deposit **unchanged**.  
**Reject for live:** EF≤0 after measured/prior Leak; do not raise MaxLevels/`f` / capital.

---

## 7. P1 WR-lift ladder (NEXT)

Geometry **frozen** (SL 23260 / TP 34890 / RR 1.50). Selectivity only — edge before capital.

| Sleeve | Magic | Knobs | Probe tip (May–Aug) | Intent |
| --- | ---: | --- | --- | --- |
| P0 growth | 26101903 | BB 2.2 · CD 2 · Fade OFF · ATR≤19670 | probe WR~46% · blotter WR **42.4%** · EF **−1.1pp** | baseline (failed Stage 1) |
| **P1 WR-lift** | **26101904** | **BB 2.3 · CD 2 · Fade ON · ATR≤19670** | probe WR≈47.3% · **blotter tip WR 43.0% · EF −0.8pp** (n=79) | slight lift vs P0; **Stage 1 still fail** |
| **P1.5 light** | **26101905** | BB 2.3 · CD 4 · Fade OFF · ATR≤18620 | probe WR≈47.0% · EF +2.7pp | **NEXT** — no-fade selectivity |

Audit: [`bmrg_m15_p1_wr_lift.json`](./bmrg_m15_p1_wr_lift.json) · script `server/scripts/bmrg_jp225_m15_p1_wr_lift.py`

### P1 blotter (magic 26101904)

Score: [`tester_magic_26101904_score.json`](./tester_magic_26101904_score.json)

| Window | n | WR | EF | E_N | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| Tip May–Aug | **79** | **43.0%** | **−0.8pp** | +0.09R | vs P0 42.4% / −1.1pp — slight lift, still fail |
| Jul–Aug only | 36 | 44.4% | +0.1pp | +0.11R | short · Aug WR 52% |

Inputs OK (BB 2.3 · Fade ON · frozen SL/TP · tp&lt;sl=0 · not starved). Deposit unchanged.

### P1.5 load (NEXT)

`Presets/BMRG-M15-JP225-6M-P1p5_light_chart.set` · magic **26101905**  
Confirm: SL/TP frozen · BBDev=2.3 · **Fade OFF** · CD=**4** · ATR max=**18620** · lot 0.1.

**Pass blotter:** `WR > BWR + Leak` (~44%+) · `EF>0` · `n≥40` · `tp_lt_sl=0`.

---

## 8. Explicit non-claims

- Probe is a **design prior**, not a Strategy Tester blotter / G0–G5 gate.  
- UK100 / DE40 / EURUSD M15 sleeves remain separate; this file is the **JP225/JPN225 M15 chart** growth + ATR-regime sleeve for the last ~6m tip.  
- Do not raise `f` / MaxLevels / deposit until a scored blotter clears Stage 1.  
- `regime_filtered=true` for Gate G3 scoring — do not claim cross-regime robustness without re-open ATR gate tests.  
- Spread prior is live snapshot (~2300); re-measure before promoting. Balanced RR=1.25 is **not** design-viable on this name under current friction.
