# EPG M15 EURUSD ~6M — Chart Preset (Deep Pullback Geometry)

**Status:** RESEARCH · **P2 light selective chart sleeve** (P1 hit-rate fail · not G0–G5 / live)  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Preset (chart):** `Presets/EPG-M15-EURUSD-6M-P2_light_selective_chart.set` · magic **26101823**  
**Scored:** P0 26101821 (EMA50 scratch) · P1 26101822 (WR &lt; BWR)  
**Tester dir:** `Profiles/Tester/EPG/EURUSD/`  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md`  
**Ouroboros audit:** `Ouroboros/research/assets/EURUSD/epg_m15_6m_audit.json`

| Field | Value |
| --- | --- |
| EA | EPG (EMA Pullback Grid) Phase 1 |
| Class | Trend-follow pullback (FIXED_RR) · native EMA/H1 regime · session sleeve |
| Symbol | EURUSD (fx major · Point ≈ 0.00001) |
| Chart TF | **M15** |
| Window | **2026.05.01 → 2026.10.07** (~6 months tip) |
| Aggregation | G0 single-leg (`MaxLevels=1`) |
| Magic (NEXT) | **26101823** (P2) |

---

## 1. Last-6m asset context (Ouroboros)

`regimes.rule_v1` → `fit.map_v0` **trendfollow** on H1 (home cell for EPG):

| Month | Tag | MATCH% | FRAGILE% |
| --- | --- | ---: | ---: |
| 2026-05 | MISMATCH | 32.7 | 23.6 |
| 2026-06 | MISMATCH | 21.0 | 33.3 |
| 2026-07 | MISMATCH | 28.6 | 23.9 |
| 2026-08 | MISMATCH | 27.4 | 15.2 |
| 2026-09 | MISMATCH | 22.7 | 35.2 |
| 2026-10 | **FRAGILE** | 4.5 | **95.5** |

**Read:** Tip is **off-home** for trendfollow (range-led). EPG must stay selective — deep L1 + London/NY session + native FLAT when M15/H1 disagree. Dense fire-count is not expected.

**M15 ATR (points):** p50 ≈ 46 · p75 ≈ 58 · p90 ≈ 74 · mean ≈ 49.

---

## 2. Unified Edge Framework geometry (design)

```text
never TP < SL          →  InpTakeProfitPoints ≥ InpStopLossPoints
RR_design = TP / SL    →  310 / 250 = 1.24
BWR = 1 / (1 + R)      →  ≈44.6% if R ≈ RR
E_N = WR × (R + 1) − 1
BM  = WR − BWR
Leak = c_R / (R + 1)
EF  = BM − Leak
```

| Piece | Choice | Intent |
| --- | --- | --- |
| SL | **250** pts | Structural 1R (~5.5× M15 ATR p50) |
| TP | **310** pts | **TP > SL** · designed RR **≈1.24** |
| L1 ATR | **1.0×** | Deep pullback (shallow 0.5 failed tip WR) |
| Grid | **MaxLevels=1** | Clean G0 events |
| Basket money TP | **OFF (0)** | Hard SL/TP define R |
| Session | **12:00–20:00** server | London/NY (required for Stage-1) |
| Skip Tue | **true** | Weekday cut |
| ATR max | **OFF (0)** | ATR≤74 preserves WR but tip n→16; native FLAT is regime gate |
| MaxSpread | **30** | Keep Leak near 20pt RT prior |

**Why not shallow L1=0.5 + 300/375?** Tip probe WR≈36–42% &lt; BWR → E_N &lt; 0.  
**Why not Harvest RR=1.0?** User target = mix WR + returns.  
**Why ATR OFF?** Stage-1 winner; high-vol Oct FRAGILE is already cut by sparse deep-L1 fires + native FLAT. Revisit ATR≤74 only if blotter shows FRAGILE overrun without starving n≥25.

---

## 3. M15* probe scorecard (design evidence — not Tester blotter)

Closed-bar pullback → next open · fixed TP/SL · ~6m M1→M15* · cost prior **20 pts** RT.

| Sleeve | n | WR | RR | BWR | EF | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **P0 L1.0 · 250/310 · s12–20 · atrOff** | 26 | 50.0% | 1.24 | 44.6% | **+1.8pp** | **+0.12R** | **Stage-1 ok** |
| L1.5 · 300/375 · all-hours · atrOff | 25 | 48.0% | 1.25 | 44.4% | +0.6pp | +0.08R | alt thin |
| L1.5 · 280/350 · all · atrOff | 27 | 48.1% | 1.25 | 44.4% | +0.5pp | +0.08R | alt |
| L0.5 · 250/310 · s13–21 · atr≤74 | 32 | 46.9% | 1.24 | 44.6% | −1.3pp | +0.05R | E_N&gt;0 / EF&lt;0 |
| L0.5 · 300/375 · s12–20 · atr≤74 | 28 | 35.7% | 1.25 | 44.4% | −11.7pp | −0.20R | reject |
| L1.0 · 250/310 · s12–20 · atr≤74 | 16 | 50.0% | 1.24 | 44.6% | +1.8pp | +0.12R | starved n |

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP &lt; SL | **TP 310 > SL 250** |
| 2 | Designed RR ≥ 1.0 | **≈1.24** |
| 3 | WR can clear BWR | Probe WR 50% > BWR 44.6%; E_N ≫ 0 |
| 4 | Not WR-theatre (token SL) | SL 250 structural on major FX |
| 5 | Not lottery RR | RR ≈1.24, not ≥3 |
| 6 | G0 single-leg events | MaxLevels=1 |
| 7 | Filters protect edge, not starve | Session + deep L1; n≈26 (≥25) |
| 8 | Regime filter declared | Native EMA/H1 FLAT + session; tip off-home noted |
| 9 | Incomplete tip noted | Oct month thin / bars end 2026-10-07 |

---

## 5. Load path (chart)

1. **Recompile** `Experts\EPG\EPG.mq5` in MetaEditor (`InpUseEmaInvalidation` + hard SL/TP).  
2. Open **EURUSD M15** chart.  
3. Attach `Experts\EPG\EPG.ex5`.  
4. Inputs → **Load** →  
   `Experts\EPG\Presets\EPG-M15-EURUSD-6M-P2_light_selective_chart.set`  
5. Confirm: `L1=1.0` · `SL=250` · `TP=310` · **emaInv=OFF** · **ATR max=74** · **CD=900** · time **12–20** · magic **26101823**.

### Tester

Load from **`Profiles/Tester/EPG/EURUSD/EPG-M15-EURUSD-6M-P2_light_selective_chart.set`**.  
Dates **2026.05.01 – 2026.10.07** (or full Jan→tip). Model: every tick / real ticks if available. Deposit ≥ 500.  
Init log: `emaInv=OFF` · `ATRMax=74`. Score: `_score_magic_26101823.py`.

---

## 6. Post-run fill (framework Stage 0–1)

Scored from Tester log `20261018.log` · magic **26101821** · deal-pair events (G0) · Leak prior 20pt RT.  
Script: `research/assets/EURUSD/_score_magic_26101821.py` → `tester_magic_26101821_score.json`.

| Run | Window | n | WR | R | kinds | Final‡ | Verdict |
| --- | --- | ---: | ---: | ---: | --- | ---: | --- |
| 1–2 | 2026.01.01→2026.10.17 | 135 | **0%** | ~0 | **other 135** (0 TP / 0 SL) | 493.30 | **FAIL** |
| tip slice | 2026.05–2026.10.07 | 74 | **0%** | ~0 | all other | — | **FAIL** |

‡ Deposit not parsed in log header; finals imply ~500 start (−6.70).

| Check | Result |
| --- | --- |
| Never TP &lt; SL | **Pass** — 0 opens with TP&lt;SL; opens carry SL250/TP310 |
| Geometry / payoff | **Not realised** — 0 broker TP/SL hits |
| Hit-rate / Stage 0 | **Fail** — WR=0; all exits `Basket closed: EMA50 invalidation` (same-bar / immediate) |
| Session filter | Active — outside session 355 · Tue 110 · spread 29 |

**Root cause:** EMA50 invalidation exits every fill before TP/SL can work (typical R≈−0.02 to −0.03). Closed-bar probe assumed fixed TP/SL holds — blotter does not.

### P1 hard stops (NEXT)

Preset: `Presets/EPG-M15-EURUSD-6M-P1_hardStops_chart.set` · magic **26101822**

| Field | P0 | **P1** |
| --- | --- | --- |
| L1 / SL / TP / session | 1.0 · 250/310 · 12–20 | **same** |
| `InpUseEmaInvalidation` | (always on) | **false** |
| Exit path | EMA50 scratch | **broker SL/TP only** |

**Intent:** let FIXED_RR geometry realise; deep L1 + price-vs-EMA50 are incompatible.  
**RECOMPILE** `EPG.mq5` so `InpUseEmaInvalidation` exists; confirm init log `emaInv=OFF`.

Scored from Tester log `20261018.log` · magic **26101822** · `emaInv=OFF` · Leak prior 20pt RT.  
Script: `_score_magic_26101822.py` → `tester_magic_26101822_score.json`.

| Run | Window | n | WR | R | BWR | EF† | E_N | kinds | Final‡ | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | --- |
| 1 | 2026.01.01→2026.10.17 | 58 | 41.4% | 1.27 | 44.0% | −6.1pp | −0.059R | TP23 / SL34 / o1 | 491.41 | **WR &lt; BWR** |
| 2 (tip) | 2026.05.01→2026.10.17 | 34 | 41.2% | 1.17 | 46.0% | −8.5pp | −0.105R | TP13 / SL20 / o1 | 491.06 | **WR &lt; BWR** |
| tip slice | 2026.05–10.07 | 32 | 40.6% | 1.24 | 44.6% | — | −0.089R | — | — | **WR &lt; BWR** |

† Leak prior ≈ 20/250/(R+1). ‡ Deposit not parsed; finals imply ~500 start.

| Check | Result |
| --- | --- |
| Never TP &lt; SL | **Pass** — 0 opens TP&lt;SL |
| Exit path | **Pass** — 0 EMA50 closes; broker TP/SL dominate |
| Geometry / R | **Pass** — R≈1.17–1.27 ≈ RR 1.24 |
| Hit-rate / Stage 0 | **Fail** — WR &lt; BWR on full + tip |
| Tip fire-count | **Pass** — n=32 (≥25) |

Tip monthly: May WR0% (−5.0R) · Jun 29% · Jul 43% · **Aug 75%** · **Sep 71%** · Oct 0% (n=2).  
Ex-May tip ≈27 events · WR≈48% &gt; BWR — selectivity should cut toxic high-vol / SL-chain fires.

### P2 light selective (NEXT)

Preset: `Presets/EPG-M15-EURUSD-6M-P2_light_selective_chart.set` · magic **26101823**

| Field | P1 | **P2** |
| --- | --- | --- |
| L1 / SL / TP / session / emaInv | 1.0 · 250/310 · 12–20 · OFF | **same** |
| ATR max | 0 (off) | **74** (≈M15 p90) |
| Cooldown | 60s | **900s** (≥1 M15 bar) |

**Intent:** one light selectivity stack — restore regime ATR gate + cut same-session SL chains. Do **not** re-enable emaInv or change RR.  
Score: `_score_magic_26101823.py` → `tester_magic_26101823_score.json`.

Scored from Tester log `20261018.log` · magic **26101823** · `emaInv=OFF` · ATRMax=74 · CD=900.

| Run | Window | n | WR | R | BWR | EF† | E_N | Final‡ | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 tip | 2026.05→10.17 | 25 | **40.0%** | 1.16 | 46.3% | −10.0pp | **−0.14R** | 491.28 | **FAIL tip** |
| tip slice | 2026.05–10.07 | 24 | **37.5%** | 1.23 | 44.9% | — | **−0.16R** | — | **worse than P1** |
| 2 | 2026.01→10.17 | 35 | 45.7% | 1.21 | 45.3% | −3.2pp | +0.01R | 500.83 | Stage-0 thin · EF&lt;0 |
| 3 | 2025.01→2026.10 | 60 | 46.7% | 1.22 | 45.1% | −2.0pp | +0.04R | 505.43 | Stage-0 thin · EF&lt;0 |

† Leak prior 20pt RT. ‡ Deposit ~500 implied.

| Check | Result |
| --- | --- |
| Never TP &lt; SL / emaInv OFF | **Pass** — 0 TP&lt;SL · 0 EMA50 closes |
| Tip fire-count | Borderline n=24–25 (not starved &lt;20) |
| Tip hit-rate | **Fail** — WR dropped vs P1 (40.6%→37.5%); May still WR0% |
| Longer windows | WR barely &gt; BWR but **EF&lt;0** under cost prior |

P2 filters cut Aug/Sep winners (Aug 4→3, Sep 7→5) without fixing May (−4.2R). **Do not promote P2 for tip sleeve.**

### 2024 calendar window (same P2 inputs · magic 26101823)

| Window | n | WR | R | BWR | EF† | E_N | Final | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **2024.01.01→2024.12.31** | 35 | **54.3%** | 1.21 | 45.2% | **+5.5pp** | **+0.20R** | **518.10** | **Stage-0/1 pass** |

Monthly blotter (2024): Jan/Apr weak · **May–Oct strong** (Oct n=4 WR100% +5.0R) · Nov quiet · Dec flat.

**Regime read (H1 `fit.map_v0` trendfollow):** tip **and** available 2024 H1 months are still calendar-tag **MISMATCH** (range-led; MATCH≈23–37%). DB regime warmup only covers ~2024-09→; early-2024 tags sparse. So 2024 is a **blotter-fit / trend-impulse year**, not an H1 monthly MATCH board — EPG still harvested pullbacks in trending legs (esp. H2’24). Tip 2026 is the same off-home tag **with** failed hit-rate.

| Window | H1 TF tag | MATCH% | Blotter |
| --- | --- | ---: | --- |
| 2024 calendar | MISMATCH (partial H1) | ~23% | **pass** WR54% E_N+0.20 |
| 2025 | MISMATCH | ~31% | thin / mixed |
| tip 2026.05–10 | MISMATCH | ~26% | **fail** WR≈38–41% |

**Iterate options:** treat EPG EURUSD as **regime-gated research book** (enable on nowcast/30d MATCH or when rolling TF MATCH↑) — tip sleeve alone is the wrong validation cell; keep BMRG as H1 meanrev home. Do **not** stack more tip filters.
