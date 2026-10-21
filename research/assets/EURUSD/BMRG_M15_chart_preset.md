# BMRG M15 EURUSD ~6M — Chart Preset (Balanced Geometry + ATR Regime)

**Status:** RESEARCH · **P2 light chart sleeve** (tip blotter Stage 0 pass · not G0–G5 / live)  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Preset (chart):** `Presets/BMRG-M15-EURUSD-6M-P2_light_selective_chart.set` · magic **26101817**  
**Scored:** P0 `…P0_balanced…` · 26101815 · P1 `…P1_selective…` · 26101816 (reject)  
**Tester dir:** `Profiles/Tester/BMRG/EURUSD/`  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md` · BMRG `system_profile.md`  
**Ouroboros audit:** `Ouroboros/research/assets/EURUSD/bmrg_m15_6m_audit.json`

| Field | Value |
| --- | --- |
| EA | BMRG (Bollinger Mean-Reversion Grid) v1.21 |
| Class | Mean reversion fade (FIXED_RR) · regime-filtered · **light** selectivity |
| Symbol | EURUSD (fx major · Point ≈ 0.00001) |
| Chart TF | **M15** |
| Window | **2026.05.01 → 2026.10.07** (~6 months tip) |
| Aggregation | G0 basket events (`MaxLevels=1`, `MaxEntries=1`) |
| Magic (NEXT) | **26101817** (P2) |

---

## 1. Last-6m asset context (Ouroboros)

`regimes.rule_v1` → `fit.map_v0` **meanrev** on H1 (home cell for BMRG):

| Month | Tag | MATCH% | FRAGILE% |
| --- | --- | ---: | ---: |
| 2026-05 | MATCH | 43.7 | 23.6 |
| 2026-06 | MATCH | 45.6 | 33.3 |
| 2026-07 | MATCH | 47.5 | 23.9 |
| 2026-08 | MATCH | 57.4 | 15.2 |
| 2026-09 | MATCH | 42.0 | 35.2 |
| 2026-10 | **FRAGILE** | 0.0 | **95.5** |

**Read:** May–Sep on-home for meanrev. **Oct tip FRAGILE** (high-vol) is the off-home sleeve — ATR max gate keeps the chart trading inside regime. Live 30d fit is also FRAGILE (high_vol-led).

**M15 ATR (points, Point=0.00001):** p50 ≈ 46 · p75 ≈ 58 · p90 ≈ 74 · mean ≈ 49.

---

## 2. Unified Edge Framework geometry (design)

Hard rules from framework + factory:

```text
never TP < SL          →  InpTP_Points ≥ InpSL_Points
RR_design = TP / SL    →  375 / 300 = 1.25
BWR = 1 / (1 + R)      →  44.44% if R ≈ RR
E_N = WR × (R + 1) − 1
BM  = WR − BWR
Leak = c_R / (R + 1)
EF  = BM − Leak
```

| Piece | Choice | Intent |
| --- | --- | --- |
| SL | **300** pts | Structural 1R on major (~6.5× M15 ATR p50 — not token SL) |
| TP | **375** pts | **TP > SL** · designed RR **1.25** |
| BB | 20 / **2.2σ** | Signal threshold |
| Session | **12:00–20:00** server | London/NY overlap (required) |
| Skip Tue | **true** | Weekday cut (champ pattern) |
| ATR regime | **ON · max 74** | ≈ M15 p90 — cut Oct tip FRAGILE without starving n |
| BB-width | OFF | Avoid fire starvation |
| MaxSpread | **30** | Keep realized Leak near 20pt RT prior |
| Grid | depth **1** | Clean G0 events |
| AOS | **OFF** | Chart sleeve = engine only |

**Why not Harvest RR=1.0?** Higher WR theatre, lower payoff; user target = mix WR + returns.  
**Why not RR≥1.5 Growth?** Probe EF thinner / WR often fails BWR on this tip.  
**Why ATR max 74 ON?** Declared **regime-filtered** (framework Gate G3): Oct tip is FRAGILE; p75 cap (≈58) starves n≈20; p90 keeps n≥40 and Stage-1 EF>0.  
**Why not prior 320/400 no-ATR?** Still design-positive (EF≈+1.4pp) but weaker than 300/375 + ATR gate (EF≈+2.6pp, WR 50%).

---

## 3. M15* probe scorecard (design evidence — not Tester blotter)

Closed-bar fade → next open · fixed TP/SL · session 12–20 · skip Tue · ~6m M1→M15* resample · cost prior **20 pts** RT.

| Sleeve | n | WR | RR | BWR | BM | Leak† | EF | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **P0 balanced 300/375 + ATR≤74 (chosen)** | 52 | 50.0% | 1.25 | 44.4% | +5.6pp | ~3.0pp | **+2.6pp** | **+0.125R** | Stage-1 ok |
| P0 300/390 RR1.30 (no ATR) | 77 | 48.1% | 1.30 | 43.5% | +4.6pp | ~2.9pp | +1.7pp | +0.105R | more fires |
| Prior 320/400 no ATR | 72 | 48.6% | 1.25 | 44.4% | +4.2pp | ~2.8pp | +1.4pp | +0.094R | legacy |
| WR-lean 280/365 RR1.30 + ATR≤74 | 55 | 49.1% | 1.30 | 43.5% | +5.6pp | ~3.1pp | +2.6pp | +0.131R | alt |
| 400/500 RR1.25 (no ATR) | 41 | 53.7% | 1.25 | 44.4% | +9.3pp | ~2.2pp | +7.0pp | +0.207R | thin n |
| ATR≤58 (p75) on 300/375 | 22 | 50.0% | 1.25 | 44.4% | +5.6pp | ~3.0pp | +2.6pp | +0.125R | starved |
| no-session Growth-scale | — | ≪BWR | — | — | — | — | **&lt;0** | &lt;0 | reject |

† `c_R` prior ≈ 20 pts round-trip / SL pts (framework Stage 1 — replace with blotter).

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP &lt; SL | **TP 375 > SL 300** |
| 2 | Designed RR ≥ 1.0 | **1.25** |
| 3 | WR can clear BWR | Probe WR 50.0% > BWR 44.4%; E_N ≫ 0 |
| 4 | Not WR-theatre (token SL) | SL 300 structural on major FX |
| 5 | Not lottery RR | RR 1.25, not ≥3 |
| 6 | G0 single-leg events | MaxLevels=1 / MaxEntries=1 |
| 7 | Filters protect edge, not starve | Session + ATR≤74; n≈52 (≥40) |
| 8 | Regime filter declared | ATR≤74 · meanrev home · Oct FRAGILE cut |
| 9 | AOS not required for geometry claim | AOS OFF |
| 10 | Incomplete tip noted | Oct month thin / bars end 2026-10-07 |

Stage-1 **EF ≈ +2.6pp** under a 20pt cost prior. Geometry / WR / E_N are **not** restricted; re-score blotter Leak before promoting.

---

## 5. Load path (chart)

1. Open **EURUSD M15** chart.  
2. Attach `Experts\BMRG\BMRG.ex5`.  
3. Inputs → **Load** →  
   `Experts\BMRG\Presets\BMRG-M15-EURUSD-6M-P0_balanced_chart.set`  
4. Confirm: `SL=300` · `TP=375` · `BBDev=2.2` · time **12–20** · **Tue off** · **ATR max=74** · magic **26101815** · AOS off · MaxSpread **30**.  
5. Optional visual: Bollinger(20, 2.2) on chart (EA uses its own handles).

### Tester

Load from **`Profiles/Tester/BMRG/EURUSD/BMRG-M15-EURUSD-6M-P0_balanced_chart.set`**.  
Dates **2026.05.01 – 2026.10.07**. Model: every tick / real ticks if available. Deposit ≥ 500.

---

## 6. Post-run fill (framework Stage 0–1)

Scored from Tester log `20261018.log` · magic **26101815** · deal-pair events (G0) · Leak prior 20pt RT.  
Script: `research/assets/EURUSD/_score_magic_26101815.py` → `tester_magic_26101815_score.json`.

| Run | Window | n | WR | R | BWR | BM | EF† | E_N | Final‡ | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 2025.01.01→2026.09.30 | 132 | 43.2% | 1.241 | 44.6% | −1.4pp | −4.4pp | −0.032R | 487.09 | **WR &lt; BWR** |
| 2 | 2025.05.01→2026.08.31 | 112 | 43.8% | 1.240 | 44.6% | −0.9pp | −3.9pp | −0.020R | 493.24 | **WR &lt; BWR** |
| 3 | 2025.01.01→2026.08.31 | 121 | 43.8% | 1.241 | 44.6% | −0.8pp | −3.8pp | −0.019R | 493.17 | **WR &lt; BWR** |

† Leak prior ≈ 3.0pp (20/300)/(R+1). ‡ Deposit not parsed in log header; finals imply ~500 start.

**Design tip slice** (2026.05–2026.10 from run1 deals): n=48 · WR **33.3%** · E_N **−0.26R** · Aug 2026 WR 14% (sumR −5.1). Worse than closed-bar probe (WR≈50%).

| Check | Result |
| --- | --- |
| Never TP &lt; SL | **Pass** — 0 opens with TP&lt;SL; exits TP/SL only (R≈1.24 ≈ RR 1.25) |
| Geometry / payoff | **Pass** — R holds near design |
| Hit-rate / Stage 0 | **Fail** — WR &lt; BWR on all three runs |
| Regime filter active | **Yes** — ATR&gt;max blocks 355–486; session/weekday dominate block counts |

**Accept to iterate:** raise WR (deeper BB / longer CD / tighter ATR) before changing RR.  
**Reject geometry:** not indicated — failure is hit-rate, not TP&lt;SL theatre.

### P1 selective (REJECTED — too restrictive)

Preset: `Presets/BMRG-M15-EURUSD-6M-P1_selective_chart.set` · magic **26101816**

| Tip window (2026.05–08) | P0 | P1 |
| --- | ---: | ---: |
| n | ~48 | **6** (starved) |
| WR | ~33% | **33%** (no lift) |
| Extra blocks | — | ATR≤68 + **BBw gate** + BB 2.4 |

Stacked filters cut fires without raising WR. Do **not** promote.

### P2 light selective (NEXT)

Preset: `Presets/BMRG-M15-EURUSD-6M-P2_light_selective_chart.set` · magic **26101817**

| Field | P0 | P1 (reject) | **P2** |
| --- | --- | --- | --- |
| BBDev | 2.2 | 2.4 | **2.3** |
| CooldownBars | 2 | 3 | **3** |
| ATR max | 74 | 68 | **74** (restore) |
| BB-width min | off | 0.30% | **off** |
| SL / TP / RR | 300/375/1.25 | same | **same** |

**Intent:** nudge WR with mild BB + longer CD only — keep tip fire-count alive (target n≥30).  
**Accept:** tip n≥30 · WR &gt; BWR · E_N &gt; 0 · magic 26101817.

#### P2 blotter fill (magic 26101817 · `20261018.log`)

| Run | Window | n | WR | R | BWR | BM | EF† | E_N | Final | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Tip | 2026.05→10.07 | **43** | **46.5%** | 1.23 | 44.8% | **+1.7pp** | −1.3pp | **+0.038R** | 507–521 | **Stage 0 pass** |
| YTD’26 | 2026.01→10.17 | 73 | 49.3% | 1.22 | 45.1% | +4.3pp | **+1.3pp** | +0.094R | 520.91 | Stage 0–1 ok |
| Full | 2025.01→2026.10 | 120 | 47.5% | 1.23 | 44.8% | +2.7pp | −0.3pp | +0.060R | 521.60 | Stage 0 ok |
| CY2025 | 2025.01→12.31 | 46 | 43.5% | 1.25 | 44.5% | −1.0pp | −4.0pp | −0.022R | 496.94 | fail (old year) |

† Leak prior 20pt RT. Tip monthly: Jul best (WR 57%); May/Jun/Aug ~43–44%.  
vs P0 tip WR≈33% n≈48 · vs P1 tip WR≈33% n≈6 — **P2 restores n and clears WR&gt;BWR**.

### Sleeve ladder (Tester)

| Sleeve | Magic | Delta | Status |
| --- | ---: | --- | --- |
| P0 | 26101815 | BB 2.2 · ATR≤74 · CD 2 | WR &lt; BWR |
| P1 selective | 26101816 | BB 2.4 · ATR≤68 · BBw 0.30% · CD 3 | reject — starved |
| **P2 light** | **26101817** | BB **2.3** · CD **3** · ATR≤**74** · BBw **off** | **chart sleeve — tip Stage 0 pass** |
| Legacy | 26092415 | 320/400 · ATR off | superseded |

---

## 7. Explicit non-claims

- Probe is a **design prior**, not a Strategy Tester blotter / G0–G5 gate.  
- EURGBP / XAUUSD M15 balanced remain separate sleeves.  
- Do not raise `f` / MaxLevels until a scored blotter clears Stage 1 (`EF>0` after measured Leak).  
- `regime_filtered=true` for Gate G3 scoring — do not claim cross-regime robustness without re-open ATR gate tests (esp. Oct FRAGILE).
