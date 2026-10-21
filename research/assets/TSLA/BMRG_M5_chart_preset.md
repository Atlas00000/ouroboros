# BMRG M5 TSLA ~6M — Chart Preset (Balanced Geometry + Tight Session Regime)

**Status:** RESEARCH CHART PRESET / UNTESTED  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Preset:** `Presets/BMRG-M5-TSLA-6M-P0_balanced_chart.set`  
**Tester dir:** `Profiles/Tester/BMRG/TSLA/`  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md`  
**Ouroboros audit:** [`bmrg_m5_6m_audit.json`](./bmrg_m5_6m_audit.json)  
**Canvas cover:** [`bmrg-tsla-m5-preset.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-tsla-m5-preset.canvas.tsx)  
**Sibling:** M15 Balanced 600/750 — [`BMRG_M15_chart_preset.md`](./BMRG_M15_chart_preset.md)

| Field | Value |
| --- | --- |
| EA | BMRG (Bollinger Mean-Reversion Grid) v1.21 |
| Class | Mean reversion fade (FIXED_RR) · **regime-filtered** |
| Symbol | TSLA / MT5 `Tesla` (equity CFD · Point = 0.01) |
| Chart TF | **M5** |
| Window | **2026.05.01 → 2026.10.07** (~6 months tip) |
| Aggregation | G0 (`MaxLevels=1`, `MaxEntries=1`) |
| Magic | **26101930** (Balanced) · 26101931 Harvest |

| Sleeve | SL/TP | RR | Session | Magic | Probe |
| --- | ---: | ---: | --- | ---: | --- |
| **Balanced (chart)** | 500/620 | 1.24 | **15:00–19** | **26101930** | WR≈53% · E_N≈+0.20R · EF≈+1.6pp |
| Harvest (WR alt) | 600/600 | 1.00 | 15:00–19 | **26101931** | WR≈58% · E_N≈+0.16R · EF≈+1.3pp |

Shared: skip Tue · ATR **58–164** (floor → p75) · BBDev **2.2** · never TP &lt; SL · AOS OFF.

---

## 1. Last-6m asset context (Ouroboros)

Same H1 meanrev tip as M15:

| Month | Tag | MATCH% | FRAGILE% |
| --- | --- | ---: | ---: |
| 2026-05 | MISMATCH | 22.1 | 27.9 |
| 2026-06 | FRAGILE | 23.1 | 40.8 |
| 2026-07 | MATCH | 41.6 | 22.7 |
| 2026-08 | MATCH | 56.5 | 13.6 |
| 2026-09 | MATCH | 66.7 | 2.7 |
| 2026-10 | MISMATCH | 26.7 | 0.0 |

**M5 ATR (points):** p50 ≈ 125 · p75 ≈ 164 · p90 ≈ 202 · mean ≈ 133.  
~0.54× M15 ATR scale — do **not** paste M15 600/750 / session 14–20 onto M5.

---

## 2. Unified Edge Framework geometry (design)

```text
never TP < SL          →  TP 620 > SL 500
RR_design = TP / SL    →  620 / 500 = 1.24
BWR = 1 / (1 + R)      →  44.6%
E_N = WR × (R + 1) − 1
EF  = BM − Leak
```

| Piece | Choice | Intent |
| --- | --- | --- |
| SL | **500** pts | ~4× ATR p50 — structural 1R; amortizes 80pt cost prior |
| TP | **620** pts | **TP > SL** · RR **≈1.24** (mix WR + returns) |
| BB | 20 / **2.2σ** | Signal threshold |
| Session | **15:00–19:00** | Skip RTH open hour — unlocks Stage-1 EF |
| Skip Tue | **true** | Weekday cut |
| ATR regime | **ON · 58–164** | Floor ≈0.6×p25 · max ≈ **p75** (tighter than M15 p90) |
| MaxSpread | **90** | Cost prior **80 pts** RT |
| AOS | **OFF** | Chart = engine only |

**Why not session 14–20?** Wide RTH window fails Stage-1 on M5 under 80pt Leak (best EF ≈ −5pp). Tight **15–19** lifts WR to ~53% and clears EF≈+1.6pp.  
**Why ATR p75 not p90?** p90 sleeves stay Leak-dominated; p75 + afternoon session is the combination that passes.

---

## 3. M5* probe scorecard (design prior — not Tester blotter)

| Sleeve | n | WR | RR | EF | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| **P0 500/620 + ATR≤164 + 15–19 (chosen)** | 88 | 53.4% | 1.24 | **+1.6pp** | **+0.196R** | Stage-1 ok |
| Harvest 600/600 + same filters | 88 | 58.0% | 1.00 | +1.3pp | +0.159R | WR alt |
| Harvest 700/700 + same | 86 | 55.8% | 1.00 | +0.1pp | +0.116R | thin EF |
| Balanced 440/550 + ATR≤202 + 14–20 | 162 | 47.5% | 1.25 | **−5.0pp** | +0.069R | reject (Leak) |
| Balanced 500/620 + ATR≤164 + 14–20 | 145 | 46.9% | 1.24 | **−4.9pp** | +0.051R | reject (session) |

† Cost prior 80 pts RT / SL. EF clears at cost≤80 on the chosen sleeve (sensitivity: cost 40 → EF≈+5.2pp).

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP &lt; SL | **TP 620 > SL 500** |
| 2 | Designed RR ≥ 1.0 | **≈1.24** |
| 3 | WR can clear BWR | 53.4% > 44.6%; E_N ≫ 0 |
| 4 | Not token SL | SL 500 ≈ 4× M5 ATR p50 |
| 5 | Not lottery RR | RR 1.24 |
| 6 | G0 single-leg | MaxLevels=1 |
| 7 | Filters protect, not starve | n≈88 (≥40) |
| 8 | Regime filter declared | ATR 58–164 + session 15–19 |
| 9 | AOS OFF | yes |
| 10 | M5 ≠ M15 paste | separate sleeve |

---

## 5. Load path (chart)

1. Open **Tesla (TSLA) M5** chart.  
2. Attach `Experts\BMRG\BMRG.ex5`.  
3. Load `Experts\BMRG\Presets\BMRG-M5-TSLA-6M-P0_balanced_chart.set`  
4. Confirm: `SL=500` · `TP=620` · `BBDev=2.2` · time **15–19** · Tue off · ATR **58–164** · magic **26101930** · AOS off.

### Tester

`Profiles/Tester/BMRG/TSLA/BMRG-M5-TSLA-6M-P0_balanced_chart.set`  
Dates **2026.05.01 – 2026.10.07**. Deposit ≥ 2000.

---

## 6. Explicit non-claims

- Design prior only — confirm Leak on Strategy Tester blotter.  
- M15 Balanced remains the stronger Stage-1 tip sleeve (EF≈+4.0pp vs M5 ≈+1.6pp).  
- Do not reopen session to 14–20 without re-proving EF.  
- `regime_filtered=true` for Gate G3.
