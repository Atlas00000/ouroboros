# BMRG M5 USDCAD ~6M — Chart Preset (Balanced Geometry + ATR Regime)

**Status:** RESEARCH CHART PRESET / UNTESTED  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Preset:** `Presets/BMRG-M5-USDCAD-6M-P0_balanced_chart.set`  
**Tester dir:** `Profiles/Tester/BMRG/USDCAD/`  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md`  
**Ouroboros audit:** `Ouroboros/research/assets/USDCAD/bmrg_m5_6m_audit.json`

| Field | Value |
| --- | --- |
| EA | BMRG (Bollinger Mean-Reversion Grid) v1.21 |
| Class | Mean reversion fade (FIXED_RR) · **regime-filtered** |
| Symbol | USDCAD (fx loonie major · Point ≈ 0.00001) |
| Chart TF | **M5** |
| Window | **2026.04.01 → 2026.09.21** (~6 months of available tip) |
| Aggregation | G0 basket events (`MaxLevels=1`, `MaxEntries=1`) |
| Magic | **26101905** |

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

**Read:** May–Aug on-home for meanrev. **Apr + Sep MISMATCH** — ATR max gate required so M5 fires stay inside quieter ATR, not the off-home tip. Live 30d fit tip is meanrev **MISMATCH** (trending_up-led).

**M5 ATR (points, Point=0.00001):** p50 ≈ 25.5 · p75 ≈ 33.9 · p90 ≈ 43.8 · mean ≈ 28.1.  
≈ half of USDCAD M15 ATR (p50 ≈ 47.5) — do **not** import M15 SL 140 or EURUSD M5 SL 250.

---

## 2. Unified Edge Framework geometry (design)

```text
never TP < SL          →  InpTP_Points ≥ InpSL_Points
RR_design = TP / SL    →  80 / 65 ≈ 1.23
BWR = 1 / (1 + R)      →  ≈44.8% if R ≈ RR
E_N = WR × (R + 1) − 1
BM  = WR − BWR
Leak = c_R / (R + 1)
EF  = BM − Leak
```

| Piece | Choice | Intent |
| --- | --- | --- |
| SL | **65** pts | ~2.5× M5 ATR p50 — structural 1R |
| TP | **80** pts | **TP > SL** · designed RR **≈1.23** (mix WR + returns) |
| BB | 20 / **2.2σ** | Signal threshold (2.4 also Stage-1 ok; 2.2 wins EF here) |
| Session | **12:00–20:00** server | London/NY overlap |
| Skip Tue | **true** | Weekday cut |
| Cooldown | **2** bars | M5 fire-count |
| ATR regime | **ON · max 25** | ≈ p50 tight — cut high-vol / MISMATCH tip |
| BB-width | OFF | Avoid double-filter starvation |
| MaxSpread | **20** | Cost prior **15–18 pts** RT |
| Grid | depth **1** | Clean G0 events |
| AOS | **OFF** | Chart sleeve = engine only |

**Why not M15 SL 140?** Wrong TF scale — M5 ATR p50 ≈ 25.5.  
**Why ATR max 25?** Declared **regime-filtered** (Gate G3): tight cap is what lifts WR to **63.3%** and Stage-1 **EF ≈ +6.0pp** (cost18) / **+8.1pp** (cost15). Wider ATR≤34 still Stage-1 positive with more n (BB 2.4 · 65/80 · n=98 · EF≈+1.9pp) — kept as fire-count alt.

---

## 3. M5* probe scorecard (design evidence — not Tester blotter)

Closed-bar fade → next open · fixed TP/SL · session 12–20 · skip Tue · ~6m M1→M5* resample · cost prior **18 pts** RT (also scored at 15).

| Sleeve | n | WR | RR | BWR | BM | EF@18 | EF@15 | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **P0 65/80 BB2.2 + ATR≤25 (chosen)** | 49 | 63.3% | 1.23 | 44.8% | +18.4pp | **+6.0pp** | **+8.1pp** | **+0.411R** | Stage-1 |
| RR1.30 65/85 BB2.2 + ATR≤25 | 49 | 59.2% | 1.31 | 43.3% | +15.9pp | +3.9pp | +5.9pp | +0.366R | Stage-1 |
| 75/95 BB2.2 + ATR≤25 | 48 | 58.3% | 1.27 | 44.1% | +14.3pp | +3.6pp | +5.4pp | +0.322R | Stage-1 |
| BB2.4 · 75/100 + ATR≤34 | 97 | 56.7% | 1.33 | 42.9% | +13.8pp | +3.6pp | +5.3pp | +0.323R | more n |
| BB2.4 · 65/80 + ATR≤34 | 98 | 59.2% | 1.23 | 44.8% | +14.3pp | +1.9pp | +4.0pp | +0.320R | fire-count alt |
| BB2.2 · 75/95 + ATR≤34 | 156 | 55.8% | 1.27 | 44.1% | +11.7pp | +1.1pp | +2.8pp | +0.264R | highest n |

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP &lt; SL | **TP 80 > SL 65** |
| 2 | Designed RR ≥ 1.0 | **≈1.23** |
| 3 | WR can clear BWR | Probe WR 63.3% > BWR 44.8%; E_N ≫ 0 |
| 4 | Not WR-theatre (token SL) | SL 65 ≈ 2.5× M5 ATR p50 |
| 5 | Not lottery RR | RR 1.23, not ≥3 |
| 6 | G0 single-leg events | MaxLevels=1 / MaxEntries=1 |
| 7 | Filters protect edge, not starve | Session + ATR≤25; n≈49 (≥40) |
| 8 | Regime filter declared | ATR≤25 · meanrev home · Apr/Sep MISMATCH cut |
| 9 | AOS not required for geometry claim | AOS OFF |
| 10 | Incomplete tip noted | Bars end 2026-09-21 |

Stage-1 **EF ≈ +6.0pp** (cost18) on the chosen tip. Geometry / WR / E_N are **not** restricted by design. Re-score blotter Leak before promoting.

---

## 5. Load path (chart)

1. Open **USDCAD M5** chart.  
2. Attach `Experts\BMRG\BMRG.ex5`.  
3. Inputs → **Load** →  
   `Experts\BMRG\Presets\BMRG-M5-USDCAD-6M-P0_balanced_chart.set`  
4. Confirm: `SL=65` · `TP=80` · `BBDev=2.2` · time **12–20** · **Tue off** · **ATR max=25** · magic **26101905** · AOS off · MaxSpread **20**.  
5. Optional visual: Bollinger(20, 2.2) on chart.

### Tester

Load from **`Profiles/Tester/BMRG/USDCAD/BMRG-M5-USDCAD-6M-P0_balanced_chart.set`**.  
Dates **2026.04.01 – 2026.09.21**. Model: every tick / real ticks if available. Deposit ≥ 500.

---

## 6. Post-run fill (framework Stage 0–1)

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
**Reject geometry:** TP&lt;SL theatre, or WR≪BWR with OK R, or EF≤0 after measured Leak with no regime excuse.

### Sleeve ladder (Tester)

| Sleeve | Magic | Delta | Status |
| --- | ---: | --- | --- |
| **P0** | **26101905** | BB 2.2 · RR ≈1.23 (65/80) · ATR≤25 · CD 2 | **NEXT — chart / Tester** |
| P0 fire-count | 26101906 | BB 2.4 · RR 1.23 (65/80) · ATR≤34 | more n · thinner EF |
| P0 RR1.30 | 26101907 | BB 2.2 · RR 1.31 (65/85) · ATR≤25 | slightly higher RR |

---

## 7. Explicit non-claims

- Probe is a **design prior**, not a Strategy Tester blotter / G0–G5 gate.  
- Distinct from the USDCAD **M15** selective sleeve (magic 26101901 · SL 140 / TP 175).  
- Do not raise `f` / MaxLevels until a scored blotter clears Stage 1.  
- `regime_filtered=true` for Gate G3 — ATR≤25 is load-bearing.  
- Live tip meanrev is **MISMATCH** — research chart sleeve for on-home windows, not capital-scale into a trending tip.
