# BMRG M5 GBPJPY ~6M — Chart Preset (Balanced Geometry · Session Regime)

**Status:** RESEARCH CHART PRESET / UNTESTED  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Preset:** `Presets/BMRG-M5-GBPJPY-6M-P0_balanced_chart.set`  
**Tester dir:** `Profiles/Tester/BMRG/GBPJPY/` (own symbol folder · `.set` + this card)  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md` · BMRG `system_profile.md`  
**Ouroboros audit:** `Ouroboros/research/assets/GBPJPY/bmrg_m5_6m_audit.json`

| Field | Value |
| --- | --- |
| EA | BMRG (Bollinger Mean-Reversion Grid) v1.21 |
| Class | Mean reversion fade (FIXED_RR) · **session-regime filtered** |
| Symbol | GBPJPY (fx yen cross · Point ≈ 0.001) |
| Chart TF | **M5** |
| Window | **2026.04.01 → 2026.09.11** (~6 months of available tip) |
| Aggregation | G0 basket events (`MaxLevels=1`, `MaxEntries=1`) |
| Magic | **26101835** |

---

## 1. Last-6m asset context (Ouroboros)

`regimes.rule_v1` → `fit.map_v0` **meanrev** on H1 (home cell for BMRG):

| Month | Tag | MATCH% | FRAGILE% |
| --- | --- | ---: | ---: |
| 2026-04 | MATCH | 49.6 | 13.2 |
| 2026-05 | MATCH | 45.3 | 32.2 |
| 2026-06 | MATCH | 47.7 | 24.2 |
| 2026-07 | MATCH | 53.0 | 19.3 |
| 2026-08 | MATCH | 51.7 | 20.1 |
| 2026-09 | **FRAGILE** | 37.1 | **62.9** |

**Read:** Apr–Aug on-home for meanrev. **Sep FRAGILE** (high-vol tip) is the off-home month. On **M5**, ATR max gates **hurt** Stage-0 design (WR/E_N) — opposite of the M15 sleeve. Regime protection here is **session 12–20 + skip Tue**, not ATR cap.

**M5 ATR (points, Point=0.001):** p50 ≈ 57 · p75 ≈ 73 · p90 ≈ 96 · mean ≈ 65.  
Yen cross — **do not import M15 160/200 or EURGBP 50pt floors** (wrong ATR scale).

---

## 2. Unified Edge Framework geometry (design)

Hard rules from framework + factory:

```text
never TP < SL          →  InpTP_Points ≥ InpSL_Points
RR_design = TP / SL    →  180 / 140 ≈ 1.29
BWR = 1 / (1 + R)      →  ≈43.7% if R ≈ RR
E_N = WR × (R + 1) − 1
BM  = WR − BWR
Leak = c_R / (R + 1)
EF  = BM − Leak
```

| Piece | Choice | Intent |
| --- | --- | --- |
| SL | **140** pts | ~2.5× ATR p50 — structural 1R on yen M5 |
| TP | **180** pts | **TP > SL** · designed RR **≈1.29** |
| BB | 20 / **2.2σ** | Signal threshold |
| Cooldown | **3** bars | Match probe |
| Session | **12:00–20:00** server | London/NY overlap (regime sleeve) |
| Skip Tue | **true** | Weekday cut |
| ATR regime | **OFF** | Ablation: ATR≤p75 / p90 / tight → WR & E_N worse |
| BB-width | OFF | Avoid starvation |
| MaxSpread | **40** | Align with ~58pt RT cost prior |
| Grid | depth **1** | Clean G0 events |
| AOS | **OFF** | Chart sleeve = engine only |

**Why SL 140 not 90/110?** Mid SL (110) is ~breakeven E_N; 140 clears WR>BWR with best E_N among lean grid.  
**Why not ATR max 73?** Probe ATR≤p75 drops WR below BWR and E_N negative — filter would starve the edge, not protect it.  
**Why MaxSpread 40?** M15 blotter mean spr ~29; M5 cost prior 58 RT → slightly wider gate than M15's 35.

---

## 3. M5* probe scorecard (design evidence — not Tester blotter)

Closed-bar fade → next open · fixed TP/SL · session 12–20 · skip Tue · ~6m M1→M5* resample · cost prior **58 pts** RT.

| Sleeve | n | WR | RR | BWR | BM | Leak† | EF | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **P0 balanced 140/180 (chosen)** | 378 | 45.8% | 1.29 | 43.7% | +2.0pp | ~18.1pp | **−16.1pp** | **+0.046R** | Stage-0 design-positive |
| Balanced 140/180 RR1.30 (same TP) | 378 | 45.8% | 1.29 | 43.7% | +2.0pp | ~18.1pp | −16.1pp | +0.046R | duplicate geometry |
| Balanced 90/110 | 378 | 45.2% | 1.22 | 45.0% | +0.2pp | ~29.0pp | −28.8pp | +0.005R | thin; high Leak |
| Balanced 90/120 | 378 | 43.1% | 1.33 | 42.9% | +0.3pp | ~27.6pp | −27.4pp | +0.006R | thin |
| Growth 140/210 + ATR≤73 | 228 | 40.8% | 1.50 | 40.0% | +0.8pp | ~16.6pp | −15.8pp | +0.020R | ATR ok but weaker WR |
| Balanced 140/180 + ATR≤73 | 228 | 42.5% | 1.29 | 43.7% | −1.2pp | ~18.1pp | −19.3pp | −0.028R | **reject** — ATR hurts |
| Session 08–20 + ATR≤73 (mid SL) | 355 | 39.4% | 1.27 | 44.0% | −4.6pp | ~23.2pp | −27.8pp | −0.104R | wider session dilutes |

† `c_R` prior ≈ 58 pts round-trip / SL pts (framework Stage 1 — replace with blotter).

**Stage-1 note:** `stage1_ef_ok_count = 0` under the 58pt prior. Geometry / WR / E_N are **not** restricted by design; EF needs measured Leak from Tester before Stage-1 claim.

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP &lt; SL | **TP 180 > SL 140** (ConfigValidate enforces) |
| 2 | Designed RR ≥ 1.0 | **≈1.29** |
| 3 | WR can clear BWR | Probe WR 45.8% > BWR 43.7%; E_N > 0 |
| 4 | Not WR-theatre (token SL) | SL 140 ≈ 2.5× yen M5 ATR p50 |
| 5 | Not lottery RR | RR ≈1.29, not ≥3 |
| 6 | G0 single-leg events | MaxLevels=1 / MaxEntries=1 |
| 7 | Filters protect edge, not starve | Session 12–20; ATR OFF (ablation failed) |
| 8 | Regime filter declared | **Time regime** (12–20 · skip Tue); ATR optional later |
| 9 | AOS not required for geometry claim | AOS OFF |
| 10 | Incomplete tip noted | Bars end 2026-09-11 |

---

## 5. Load path (chart)

1. Open **GBPJPY M5** chart.  
2. Attach `Experts\BMRG\BMRG.ex5`.  
3. Inputs → **Load** →  
   `Experts\BMRG\Presets\BMRG-M5-GBPJPY-6M-P0_balanced_chart.set`  
4. Confirm: `SL=140` · `TP=180` · `BBDev=2.2` · CD **3** · time **12–20** · **Tue off** · **ATR regime OFF** · magic **26101835** · AOS off · MaxSpread **40**.  
5. Optional visual: Bollinger(20, 2.2) on chart (EA uses its own handles).

### Tester

Load from **`Profiles/Tester/BMRG/GBPJPY/BMRG-M5-GBPJPY-6M-P0_balanced_chart.set`**.  
Dates **2026.04.01 – 2026.09.11**. Model: every tick / real ticks if available. Deposit ≥ 500. Period **M5**.

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
| BM by month (esp. Sep FRAGILE) | |

**Accept to iterate:** `E_N>0`, `WR>BWR`, `EF>0` preferred, `RR−R` not crushed, fires not starved.  
**Reject geometry:** TP&lt;SL theatre, or WR≪BWR with OK R and no cost excuse.

### Sleeve ladder (Tester)

| Sleeve | Magic | Delta | Status |
| --- | ---: | --- | --- |
| **P0** | **26101835** | BB 2.2 · CD 3 · MaxSpr 40 · Fade OFF · ATR OFF | **NEXT** |
| P1 WR-lift | 26101836 | (reserved) BB+CD only; do not widen TP / shrink SL | pending blotter |

---

## 7. Explicit non-claims

- Probe is a **design prior**, not a Strategy Tester blotter / G0–G5 gate.  
- M15 GBPJPY sleeve (160/200 + ATR≤126) is a **separate** TF sleeve — do not mix magics or claim cross-TF equivalence.  
- Do not raise `f` / MaxLevels until a scored blotter clears Stage 1 (`EF>0` after measured Leak).  
- `regime_filtered=true` via **session**, not ATR — do not claim HV-robust without re-opening ATR gate tests on blotter.  
- If blotter WR &lt; BWR with n≥40, raise WR first (BB/CD/spread) before touching SL/TP.
