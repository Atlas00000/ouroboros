# BMRG M5 NVDA ~6M — Chart Preset (Balanced Geometry + ATR Regime)

**Status:** RESEARCH CHART PRESET / UNTESTED  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Preset:** `Presets/BMRG-M5-NVDA-6M-P0_balanced_chart.set`  
**Tester dir:** `Profiles/Tester/BMRG/NVDA/`  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md` · BMRG system profile  
**Ouroboros audit:** [`bmrg_m5_6m_audit.json`](./bmrg_m5_6m_audit.json) · [`bmrg_m5_6m_reprobe.json`](./bmrg_m5_6m_reprobe.json)  
**Canvas cover:** [`bmrg-nvda-m5-preset.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-nvda-m5-preset.canvas.tsx)  
**Companion M15:** [`BMRG_M15_chart_preset.md`](./BMRG_M15_chart_preset.md) (550/690)

| Field | Value |
| --- | --- |
| EA | BMRG (Bollinger Mean-Reversion Grid) v1.21 |
| Class | Mean reversion fade (FIXED_RR) · **regime-filtered** |
| Symbol | NVDA / MT5 `NVDA` (equity CFD · Point = 0.01) |
| Chart TF | **M5** |
| Window | **2026.05.01 → 2026.10.16** (~6 months tip) |
| Aggregation | G0 basket events (`MaxLevels=1`, `MaxEntries=1`) |
| Magic | **26101940** (Balanced) · 26101941 Growth · 26101942 Harvest |

| Sleeve | SL/TP | RR | Session | Magic | Probe (@40pt cost) |
| --- | ---: | ---: | --- | ---: | --- |
| **Balanced (chart)** | 300/380 | ≈1.27 | 14:00–20 | **26101940** | WR≈51% · E_N≈+0.15R · EF≈+0.9pp |
| Growth (returns alt) | 300/450 | 1.50 | 14:00–20 | **26101941** | WR≈45% · E_N≈+0.13R · EF thin |
| Harvest (WR alt) | 300/300 | 1.00 | 14:00–20 | **26101942** | WR≈57% · E_N≈+0.15R · EF≈+0.7pp |

Shared: skip Tue · ATR **27–95** · BBW off · BBDev **2.5** · never TP &lt; SL · AOS OFF.

---

## 1. Last-6m asset context (Ouroboros)

`regimes.rule_v1` → `fit.map_v0` **meanrev** on H1 (home cell for BMRG):

| Month | Tag | MATCH% | FRAGILE% |
| --- | --- | ---: | ---: |
| 2026-05 | FRAGILE | 11.4 | 46.4 |
| 2026-06 | FRAGILE | 32.7 | 38.1 |
| 2026-07 | MATCH | 50.6 | 37.0 |
| 2026-08 | MISMATCH | 25.9 | 13.6 |
| 2026-09 | MISMATCH | 33.3 | 17.0 |
| 2026-10 | MISMATCH | 33.3 | 0.0 |

**Read:** Same hostile tip as M15 — mostly FRAGILE/MISMATCH; only Jul MATCH. ATR max is mandatory: ungated 300/380 fails Stage-1 EF even at a 40pt cost prior.

**M5 ATR (points, Point=0.01):** p50 ≈ 59 · p75 ≈ 78 · p90 ≈ 95 · mean ≈ 64.  
≈ half of M15 ATR (p50≈109) — do **not** import M15 550/690 floors onto M5.

---

## 2. Unified Edge Framework geometry (design)

```text
never TP < SL          →  InpTP_Points ≥ InpSL_Points
RR_design = TP / SL    →  380 / 300 ≈ 1.27
BWR = 1 / (1 + R)      →  ≈44.1% if R ≈ RR
E_N = WR × (R + 1) − 1
BM  = WR − BWR
Leak = c_R / (R + 1)
EF  = BM − Leak
```

| Piece | Choice | Intent |
| --- | --- | --- |
| SL | **300** pts | ~5.1× ATR p50 — structural 1R on NVDA M5 |
| TP | **380** pts | **TP > SL** · designed RR **≈1.27** (mix WR + returns) |
| BB | 20 / **2.5σ** | Equity fade bands |
| Session | **14:00–20:00** server | US RTH tip |
| Skip Tue | **true** | Weekday cut |
| ATR regime | **ON · 27–95** | Floor ≈0.6×p25 · max ≈ p90 — Gate G3 |
| BB-width | OFF | atrBBW did not beat ATR-only on this tip |
| MaxSpread | **50** | Cost prior **40 pts** RT |
| Grid | depth **1** | Clean G0 events |
| AOS | **OFF** | Chart sleeve = engine only |

**Why cost prior 40 (not M15’s 50)?** Absolute RT friction is TF-independent; M5 SL is smaller so Leak as a fraction of 1R is higher. At 40pt prior EF≈+0.9pp; at 50pt EF≈−0.5pp — **re-score blotter before promote**.  
**Why ATR ON?** Tip is meanrev-hostile; raw sleeve EF≤0.  
**Why not M15 550/690 on M5?** Wrong ATR scale — undersized relative fire / oversize vs M5 noise.

---

## 3. M5* probe scorecard (design evidence — not Tester blotter)

Closed-bar fade → next open · fixed TP/SL · session 14–20 · skip Tue · ~6m M1→M5* · cost prior **40 pts** RT.

| Sleeve | n | WR | RR | BWR | BM | Leak† | EF | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **P0 balanced 300/380 + ATR≤95 (chosen)** | 106 | 50.9% | 1.27 | 44.1% | +6.8pp | ~5.9pp | **+0.9pp** | **+0.155R** | Stage-1 ok @40 |
| Same @50pt cost | 106 | 50.9% | 1.27 | 44.1% | +6.8pp | ~7.4pp | **−0.5pp** | +0.155R | cost-sensitive |
| Balanced 300/380 ungated | 118 | 49.2% | 1.27 | 44.1% | +5.0pp | ~5.9pp | **≤0** | +0.11R | reject |
| Harvest 300/300 + ATR≤95 | 108 | 57.4% | 1.00 | 50.0% | +7.4pp | ~6.7pp | +0.7pp | +0.15R | WR alt |
| Growth 300/450 + ATR≤95 | 102 | 45.1% | 1.50 | 40.0% | +5.1pp | ~5.3pp | thin | +0.13R | returns alt |

† `c_R` prior ≈ cost_pts / SL pts (framework Stage 1 — replace with blotter).

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP &lt; SL | **TP 380 > SL 300** |
| 2 | Designed RR ≥ 1.0 | **≈1.27** |
| 3 | WR can clear BWR | Probe WR 50.9% > BWR 44.1%; E_N ≫ 0 |
| 4 | Not WR-theatre (token SL) | SL 300 ≈ 5× M5 ATR p50 |
| 5 | Not lottery RR | RR ≈1.27, not ≥3 |
| 6 | G0 single-leg events | MaxLevels=1 / MaxEntries=1 |
| 7 | Filters protect edge, not starve | Session + ATR 27–95; n≈106 (≥40) |
| 8 | Regime filter declared | ATR gate · meanrev home · FRAGILE/MISMATCH tip cut |
| 9 | AOS not required for geometry claim | AOS OFF |
| 10 | Cost sensitivity noted | EF flips ~45–50pt prior — blotter Leak required |

---

## 5. Load path (chart)

1. Open **NVDA M5** chart.  
2. Attach `Experts\BMRG\BMRG.ex5`.  
3. Inputs → **Load** →  
   `Experts\BMRG\Presets\BMRG-M5-NVDA-6M-P0_balanced_chart.set`  
4. Confirm: `SL=300` · `TP=380` · `BBDev=2.5` · time **14–20** · **Tue off** · **ATR 27–95** · magic **26101940** · AOS off · MaxSpread **50**.

### Tester

Load from **`Profiles/Tester/BMRG/NVDA/BMRG-M5-NVDA-6M-P0_balanced_chart.set`**.  
Dates **2026.05.01 – 2026.10.16**. Model: every tick / real ticks if available.

Alts: `_growth_TPgtSL.set` (26101941) · `_harvest_WRfocus.set` (26101942).

---

## 6. Explicit non-claims

- Probe is a **design prior**, not a Strategy Tester blotter / G0–G5 gate.  
- Tip is meanrev-MISMATCH overall — do not claim cross-regime robustness with ATR closed.  
- M15 balanced (550/690) remains a separate sleeve — do not mix magics on one chart.  
- Do not raise `f` / MaxLevels until blotter clears Stage 1 after **measured** Leak.
