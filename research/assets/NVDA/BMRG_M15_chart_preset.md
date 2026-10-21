# BMRG M15 NVDA ~6M — Chart Preset (Balanced Geometry + ATR/BBW Regime)

**Status:** RESEARCH CHART PRESET / UNTESTED  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Preset:** `Presets/BMRG-M15-NVDA-6M-P0_balanced_chart.set`  
**Tester dir:** `Profiles/Tester/BMRG/NVDA/` (own symbol folder · `.set` + this card)  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md` · BMRG system profile  
**Ouroboros audit:** [`bmrg_m15_6m_audit.json`](./bmrg_m15_6m_audit.json) · [`bmrg_m15_6m_reprobe.json`](./bmrg_m15_6m_reprobe.json)  
**Canvas cover:** [`bmrg-nvda-m15-preset.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-nvda-m15-preset.canvas.tsx)

| Field | Value |
| --- | --- |
| EA | BMRG (Bollinger Mean-Reversion Grid) v1.21 |
| Class | Mean reversion fade (FIXED_RR) · **regime-filtered** |
| Symbol | NVDA / MT5 `NVDA` (equity CFD · Point = 0.01) |
| Chart TF | **M15** |
| Window | **2026.05.01 → 2026.10.16** (~6 months tip; broker M1 from 2026-01-14) |
| Aggregation | G0 basket events (`MaxLevels=1`, `MaxEntries=1`) |
| Magic | **26101930** (Balanced) · 26101931 Growth · 26101932 Harvest |

| Sleeve | SL/TP | RR | Session | Magic | Probe (@50pt cost) |
| --- | ---: | ---: | --- | ---: | --- |
| **Balanced (chart)** | 550/690 | ≈1.25 | 14:00–20 | **26101930** | WR≈51% · E_N≈+0.16R · EF≈+3.0pp |
| Growth (returns alt) | 550/820 | ≈1.49 | 14:00–20 | **26101931** | WR≈45% · E_N≈+0.13R · EF≈+1.7pp |
| Harvest (WR alt) | 550/550 | 1.00 | 14:00–20 | **26101932** | WR≈54% · E_N≈+0.08R · EF thin |

Shared: skip Tue · ATR **54–155** · BBW **0.25–1.80%** · BBDev **2.2** · never TP &lt; SL · AOS OFF.

---

## 1. Last-6m asset context (Ouroboros)

`regimes.rule_v1` → `fit.map_v0` **meanrev** on H1 (home cell for BMRG):

| Month | Tag | MATCH% | FRAGILE% |
| --- | --- | ---: | ---: |
| 2026-05 | FRAGILE | 11.4 | 46.4 |
| 2026-06 | FRAGILE | 32.7 | 38.1 |
| 2026-07 | MATCH | 46.8 | 40.9 |
| 2026-08 | MISMATCH | 25.9 | 13.6 |
| 2026-09 | MISMATCH | 33.3 | 17.0 |
| 2026-10 | MISMATCH | 33.3 | 0.0 |

**Read:** Tip is **meanrev-hostile overall** (MISMATCH ~41%, FRAGILE ~28%). Only Jul is MATCH. Live 30d fit is also **MISMATCH** (trend-led). ATR + BB-width gates are mandatory so the EA fires inside quieter, band-width-bounded meanrev geometry — not into May/Jun high-vol or Aug–Oct trend mass.

**M15 ATR (points, Point=0.01):** p50 ≈ 109 · p75 ≈ 133 · p90 ≈ 155 · mean ≈ 113.  
NVDA tip ATR is **~half of TSLA** — do not import TSLA 600/750 floors blindly. SL 550 ≈ 5.0× ATR p50 (structural 1R after regime cut).

---

## 2. Unified Edge Framework geometry (design)

```text
never TP < SL          →  InpTP_Points ≥ InpSL_Points
RR_design = TP / SL    →  690 / 550 ≈ 1.25
BWR = 1 / (1 + R)      →  ≈44.4% if R ≈ RR
E_N = WR × (R + 1) − 1
BM  = WR − BWR
Leak = c_R / (R + 1)
EF  = BM − Leak
```

| Piece | Choice | Intent |
| --- | --- | --- |
| SL | **550** pts | Structural 1R after ATR/BBW selection (not ATR-token 170) |
| TP | **690** pts | **TP > SL** · designed RR **≈1.25** (mix WR + returns) |
| BB | 20 / **2.2σ** | Equity fade bands |
| Session | **14:00–20:00** server | US RTH tip (skip open auction) |
| Skip Tue | **true** | Weekday cut (champ pattern) |
| ATR regime | **ON · 54–155** | Floor ≈0.6×p25 · max ≈ p90 — Gate G3 |
| BB-width | **ON · 0.25–1.80%** | Cuts skinny + blown-out bands |
| MaxSpread | **70** | Cost prior **50 pts** RT (still EF+ under 70) |
| Grid | depth **1** | Clean G0 events |
| AOS | **OFF** | Chart sleeve = engine only |

**Why not Harvest RR=1.0 as chart default?** Higher WR theatre, thinner EF under realistic cost — user target = mix WR + returns → Balanced.  
**Why not Growth RR≈1.5 as default?** Viable but leaves preferred [1.20, 1.35] band — kept as alt.  
**Why ATR+BBW ON?** Tip months are mostly FRAGILE/MISMATCH. Without both gates, Stage-1 EF stays ≤0 at n≥30 under a 50–70pt cost prior.  
**Why not ATR-scaled base 170/210?** Cost Leak dominates (`c_R` ≈ 50/170) and tip WR does not clear BWR+Leak for Balanced RR.

---

## 3. M15* probe scorecard (design evidence — not Tester blotter)

Closed-bar fade → next open · fixed TP/SL · session 14–20 · skip Tue · ~6m M1→M15* · cost prior **50 pts** RT (sensitivity also checked at 40/60/70).

| Sleeve | n | WR | RR | BWR | BM | Leak† | EF | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **P0 balanced 550/690 + ATR/BBW (chosen)** | 35 | 51.4% | 1.25 | 44.4% | +7.1pp | ~4.0pp | **+3.0pp** | **+0.160R** | Stage-1 ok |
| Balanced 600/750 + ATR/BBW | 34 | 50.0% | 1.25 | 44.4% | +5.6pp | ~3.7pp | +1.9pp | +0.125R | near-twin |
| Growth 550/820 + ATR/BBW | 33 | 45.5% | 1.49 | 40.1% | +5.3pp | ~3.7pp | +1.7pp | +0.132R | returns alt |
| Harvest 550/550 + ATR/BBW | 37 | 54.0% | 1.00 | 50.0% | +4.0pp | ~4.5pp | thin | +0.08R | WR alt |
| Ungated / no BBW (typical) | ≥50 | varies | 1.25 | 44.4% | ≤0 | high | **≤0** | mixed | reject for tip |

† `c_R` prior ≈ 50 pts round-trip / SL pts. Chosen sleeve remains EF>0 at **70pt** prior (EF≈+1.4pp).

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP &lt; SL | **TP 690 > SL 550** |
| 2 | Designed RR ≥ 1.0 | **≈1.25** |
| 3 | WR can clear BWR | Probe WR 51.4% > BWR 44.4%; E_N ≫ 0 |
| 4 | Not WR-theatre (token SL) | SL 550 after regime cut; 170pt ATR-base rejected on Leak |
| 5 | Not lottery RR | RR ≈1.25, not ≥3 |
| 6 | G0 single-leg events | MaxLevels=1 / MaxEntries=1 |
| 7 | Filters protect edge, not starve | Session + ATR 54–155 + BBW 0.25–1.80; n≈35 (≥30 tip bar) |
| 8 | Regime filter declared | ATR+BBW · meanrev home · FRAGILE/MISMATCH tip cut |
| 9 | AOS not required for geometry claim | AOS OFF |
| 10 | Incomplete tip noted | Oct 2026 partial · bars end 2026-10-16 |

Stage-1 **EF ≈ +3.0pp** under a 50pt cost prior. Geometry / WR / E_N are **not** restricted by design. Re-score blotter Leak before promoting.

---

## 5. Load path (chart)

1. Open **NVDA M15** chart.  
2. Attach `Experts\BMRG\BMRG.ex5`.  
3. Inputs → **Load** →  
   `Experts\BMRG\Presets\BMRG-M15-NVDA-6M-P0_balanced_chart.set`  
4. Confirm: `SL=550` · `TP=690` · `BBDev=2.2` · time **14–20** · **Tue off** · **ATR 54–155** · **BBW 0.25–1.80** · magic **26101930** · AOS off · MaxSpread **70**.  
5. Optional visual: Bollinger(20, 2.2) on chart (EA uses its own handles).

### Tester

Load from **`Profiles/Tester/BMRG/NVDA/BMRG-M15-NVDA-6M-P0_balanced_chart.set`**.  
Dates **2026.05.01 – 2026.10.16**. Model: every tick / real ticks if available. Deposit ≥ 2000 (1.0 share equity CFD).

Alts in same folder: `_growth_TPgtSL.set` (magic 26101931) · `_harvest_WRfocus.set` (magic 26101932).

---

## 6. Post-run fill (framework Stage 0–1)

_Pending Strategy Tester blotter · magic **26101930**._

| Check | Result |
| --- | --- |
| Never TP &lt; SL | Design pass — TP 690 > SL 550 |
| Geometry / payoff | Design pass — RR≈1.25 held in probe |
| Hit-rate / Stage 0 | Design prior WR 51.4% > BWR 44.4% — **confirm on blotter** |
| Regime filter active | ATR 54–155 + BBW 0.25–1.80 · session 14–20 · skip Tue |

**Accept to iterate:** tip n≥30 · WR > BWR · E_N > 0 · EF>0 after measured Leak.  
**Reject geometry:** only if blotter shows TP&lt;SL theatre or R collapses — not indicated by probe.

---

## 7. Explicit non-claims

- Probe is a **design prior**, not a Strategy Tester blotter / G0–G5 gate.  
- Tip is meanrev-MISMATCH overall — do not claim cross-regime robustness with gates closed.  
- TSLA / META / MSFT M15 balanced remain separate sleeves (different ATR scale).  
- Do not raise `f` / MaxLevels until a scored blotter clears Stage 1 (`EF>0` after measured Leak).  
- May–Jun FRAGILE and Aug–Oct MISMATCH months are intentionally partially blocked by ATR/BBW.
