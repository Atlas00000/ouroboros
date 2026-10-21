# BMRG M15 GBPJPY ~6M — Chart Preset (Balanced Geometry + ATR Regime)

**Status:** RESEARCH CHART PRESET / UNTESTED  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Preset:** `Presets/BMRG-M15-GBPJPY-6M-P0_balanced_chart.set`  
**Tester dir:** `Profiles/Tester/BMRG/GBPJPY/` (own symbol folder · `.set` + this card + README)  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md` · BMRG `system_profile.md`  
**Ouroboros audit:** `Ouroboros/research/assets/GBPJPY/bmrg_m15_6m_audit.json`

| Field | Value |
| --- | --- |
| EA | BMRG (Bollinger Mean-Reversion Grid) v1.21 |
| Class | Mean reversion fade (FIXED_RR) · **regime-filtered** |
| Symbol | GBPJPY (fx yen cross · Point ≈ 0.001) |
| Chart TF | **M15** |
| Window | **2026.04.01 → 2026.09.11** (~6 months of available tip) |
| Aggregation | G0 basket events (`MaxLevels=1`, `MaxEntries=1`) |
| Magic | **26101825** |

---

## 1. Last-6m asset context (Ouroboros)

`regimes.rule_v1` → `fit.map_v0` **meanrev** on H1 (home cell for BMRG):

| Month | Tag | MATCH% | FRAGILE% |
| --- | --- | ---: | ---: |
| 2026-04 | MATCH | 51.0 | 11.9 |
| 2026-05 | MATCH | 45.3 | 32.2 |
| 2026-06 | MATCH | 47.7 | 24.2 |
| 2026-07 | MATCH | 53.0 | 19.3 |
| 2026-08 | MATCH | 51.7 | 20.1 |
| 2026-09 | **FRAGILE** | 37.1 | **62.9** |

**Read:** Apr–Aug on-home for meanrev. **Sep FRAGILE** (high-vol tip) is the off-home month — ATR max gate is required so the sleeve trades inside regime. H1 state tip is as-of 2026-09-11 (confirmed high_volatility).

**M15 ATR (points, Point=0.001):** p50 ≈ 100 · p75 ≈ 126 · p90 ≈ 165 · mean ≈ 114.  
Yen cross — **do not import EURGBP 50pt or EURUSD 300pt SL floors** (wrong ATR scale).

---

## 2. Unified Edge Framework geometry (design)

Hard rules from framework + factory:

```text
never TP < SL          →  InpTP_Points ≥ InpSL_Points
RR_design = TP / SL    →  200 / 160 = 1.25
BWR = 1 / (1 + R)      →  44.44% if R ≈ RR
E_N = WR × (R + 1) − 1
BM  = WR − BWR
Leak = c_R / (R + 1)
EF  = BM − Leak
```

| Piece | Choice | Intent |
| --- | --- | --- |
| SL | **160** pts | ~1.6× ATR p50 — structural 1R on yen M15 |
| TP | **200** pts | **TP > SL** · designed RR **1.25** |
| BB | 20 / **2.2σ** | Signal threshold |
| Session | **12:00–20:00** server | London/NY overlap (Tokyo 02–12 failed probe) |
| Skip Tue | **true** | Weekday cut (champ pattern) |
| ATR regime | **ON · max 126** | ≈ p75 — cut Sep FRAGILE high-vol |
| BB-width | OFF | Avoid fire starvation (non-binding under ATR max) |
| MaxSpread | **35** | Keep realized Leak near 40pt RT prior |
| Grid | depth **1** | Clean G0 events |
| AOS | **OFF** | Chart sleeve = engine only |

**Why not EURGBP SL 50?** Probe would be token-SL WR theatre vs GBPJPY ATR≈100.  
**Why not Harvest RR=1.0?** Lower payoff; user target = mix WR + returns.  
**Why ATR max 126 ON?** Declared **regime-filtered** (framework Gate G3): Sep FRAGILE is the HV tip; ATR≤p75 lifts EF to **+3.9pp** with n=69. ATR≤100 (tight) starves (n=29). Full-window no-gate still Stage-1 thin/positive but weaker.

---

## 3. M15* probe scorecard (design evidence — not Tester blotter)

Closed-bar fade → next open · fixed TP/SL · session 12–20 · skip Tue · ~6m M1→M15* resample · cost prior **40 pts** RT (yen MaxSpread sleeve).

| Sleeve | n | WR | RR | BWR | BM | Leak† | EF | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **P0 balanced 160/200 + ATR≤126 (chosen)** | 69 | 59.4% | 1.25 | 44.4% | +15.0pp | ~11.1pp | **+3.9pp** | **+0.337R** | Stage-1 design-positive |
| P0 RR1.30 160/210 + ATR≤126 | 69 | 56.5% | 1.31 | 43.2% | +13.3pp | ~10.8pp | **+2.5pp** | **+0.307R** | returns-lean alt |
| Balanced 160/200 (no ATR gate) | 118 | 55.9% | 1.25 | 44.4% | +11.5pp | ~11.1pp | **+0.4pp** | +0.259R | weaker; Sep leak |
| ATR≤100 tight 160/200 | 29 | 51.7% | 1.25 | 44.4% | +7.3pp | ~11.1pp | −3.8pp | +0.164R | starved — reject |
| Session 02–12 Tokyo 160/200 | 207 | 42.5% | 1.25 | 44.4% | −1.9pp | ~11.1pp | −13.0pp | −0.044R | off-home session |
| Session 08–20 + ATR≤126 | 119 | 50.4% | 1.25 | 44.4% | +6.0pp | ~11.1pp | −5.1pp | +0.135R | wider session dilutes |

† `c_R` prior ≈ 40 pts round-trip / SL pts (framework Stage 1 — replace with blotter).

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP &lt; SL | **TP 200 > SL 160** (ConfigValidate enforces) |
| 2 | Designed RR ≥ 1.0 | **1.25** |
| 3 | WR can clear BWR | Probe WR 59.4% > BWR 44.4%; E_N ≫ 0 |
| 4 | Not WR-theatre (token SL) | SL 160 ≈ 1.6× yen ATR p50 |
| 5 | Not lottery RR | RR 1.25, not ≥3 |
| 6 | G0 single-leg events | MaxLevels=1 / MaxEntries=1 |
| 7 | Filters protect edge, not starve | Session + ATR≤126; n≈69 (≥30) |
| 8 | Regime filter declared | ATR≤126 · meanrev home · Sep FRAGILE cut |
| 9 | AOS not required for geometry claim | AOS OFF |
| 10 | Incomplete tip noted | Bars end 2026-09-11 |

Stage-1 **EF ≈ +3.9pp** on the full tip under a 40pt cost prior. Geometry / WR / E_N are **not** restricted by design. Re-score blotter Leak before promoting.

---

## 5. Load path (chart)

1. Open **GBPJPY M15** chart.  
2. Attach `Experts\BMRG\BMRG.ex5`.  
3. Inputs → **Load** →  
   `Experts\BMRG\Presets\BMRG-M15-GBPJPY-6M-P0_balanced_chart.set`  
4. Confirm: `SL=160` · `TP=200` · `BBDev=2.2` · time **12–20** · **Tue off** · **ATR max=126** · magic **26101825** · AOS off · MaxSpread **35**.  
5. Optional visual: Bollinger(20, 2.2) on chart (EA uses its own handles).

### Tester

Load from **`Profiles/Tester/BMRG/GBPJPY/BMRG-M15-GBPJPY-6M-P0_balanced_chart.set`**.  
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
| BM by ATR tercile / month (esp. Sep) | |

**Accept to iterate:** `E_N>0`, `WR>BWR`, `EF>0` preferred, `RR−R` not crushed, fires not starved.  
**Reject geometry:** TP&lt;SL theatre, or WR≪BWR with OK R and no cost excuse, or EF≤0 after measured Leak with no regime excuse.

### Sleeve ladder (Tester)

| Sleeve | Magic | Delta | Status |
| --- | ---: | --- | --- |
| P0 | 26101825 | BB 2.2 · CD 2 · MaxSpr 35 · Fade OFF | FAILED WR 41% &lt; BWR (n=46) |
| P1 WR-lift | 26101826 | BB 2.3 · CD 3 · MaxSpr 25 · Fade ON | FAILED starved (n=4) |
| **P1.5 light** | **26101827** | **same SL/TP** · BB **2.3** · CD **3** · MaxSpr **32** · Fade **OFF** | **NEXT** |
| P1.5b sell-only | 26101828 | P1.5 + AllowBuy=false | alt if buys stay soft |

---

## 7. P1 → P1.5 ladder (post blotter)

**Rule:** raise WR first; do **not** widen TP or shrink SL.

| Run | Magic | Result |
| --- | ---: | --- |
| P0 May→Oct | 26101825 | n=46 · WR 41.3% &lt; BWR · E_N −0.07R · hit-rate fail |
| P1 May→Oct | 26101826 | Fade ON + MaxSpr 25 → **n=4 starved** · WR 25% |
| P1 Jan→Oct | 26101826 | n=20 · WR 35% · still under BWR · Apr drag |

### P1.5 light (NEXT)

| Knob | Value | Intent |
| --- | --- | --- |
| SL / TP | **160 / 200 frozen** | geometry unchanged |
| BBDev | **2.3** | light selectivity vs P0 |
| Cooldown | **3** | less cluster re-entry |
| FadeConfirm | **OFF** | P1 reclaim+spread stack starved tip |
| MaxSpread | **32** | ≈P0 mean spr (~29); not 25 |
| ATR max | **126** | Gate G3 unchanged |
| Tester dates | **2026.05.01 – 2026.09.11** | no Oct / no Jan–Apr |

Load: `Presets/BMRG-M15-GBPJPY-6M-P1p5_light_chart.set` · magic **26101827**.

Probe prior (light BB2.3 CD3, design window): n≈35 · WR≈60% · E_N≈+0.35R · Leak≈16pp at blotter-like cost.

---

## 8. Explicit non-claims

- Probe is a **design prior**, not a Strategy Tester blotter / G0–G5 gate.  
- EURGBP / EURUSD / XAUUSD M15 balanced remain separate sleeves; this file is the **GBPJPY M15** yen-cross sleeve for the last ~6m tip.  
- Do not raise `f` / MaxLevels until a scored blotter clears Stage 1 (`EF>0` after measured Leak).  
- `regime_filtered=true` for Gate G3 scoring — do not claim cross-regime robustness without re-open ATR gate tests (esp. Sep FRAGILE).  
- P1.5 does not change RR; if blotter WR still &lt; BWR with n≥25, add sell-only before touching SL/TP.
