# BMRG M15 XAUUSD ~6M — Chart Preset (Balanced Geometry + ATR Regime)

**Status:** RESEARCH CHART PRESET / UNTESTED  
**Not:** production sign-off · claimed live edge · AOS_LIVE  
**Preset:** `Presets/BMRG-M15-XAUUSD-6M-P0_balanced_chart.set`  
**Tester dir:** `Profiles/Tester/BMRG/XAUUSD/` (own symbol folder · `.set` + this card + README)  
**Framework:** Ouroboros `docs/framework/unified_edge_framework.md` · BMRG `system_profile.md`  
**Ouroboros audit:** `Ouroboros/research/assets/XAUUSD/bmrg_m15_6m_audit.json`

| Field | Value |
| --- | --- |
| EA | BMRG (Bollinger Mean-Reversion Grid) v1.21 |
| Class | Mean reversion fade (FIXED_RR) · **regime-filtered** |
| Symbol | XAUUSD (metal · Point ≈ 0.01) |
| Chart TF | **M15** |
| Window | **2026.05.01 → 2026.10.07** (~6 months of available tip) |
| Aggregation | G0 basket events (`MaxLevels=1`, `MaxEntries=1`) |
| Magic | **26100915** |

---

## 1. Last-6m asset context (Ouroboros)

`regimes.rule_v1` → `fit.map_v0` **meanrev** on H1 (home cell for BMRG):

| Month | Tag | MATCH% | MISMATCH% | FRAGILE% |
| --- | --- | ---: | ---: | ---: |
| 2026-05 | MATCH | 51.9 | 30.5 | 17.6 |
| 2026-06 | FRAGILE | 26.6 | 28.6 | 44.7 |
| 2026-07 | MISMATCH | 40.6 | 43.5 | 15.8 |
| 2026-08 | MATCH | 48.9 | 27.8 | 23.3 |
| 2026-09 | MATCH | 44.4 | 17.4 | 38.2 |
| 2026-10 | MISMATCH | 36.6 | 63.4 | 0.0 |

**Read:** May / Aug–Sep on-home for meanrev. **Jun FRAGILE** (high-vol) and **Jul / early-Oct MISMATCH** (trend) are off-home — ATR max gate + session sleeve reduce trading in those cells. Incomplete Oct tip is not admission evidence.

**M15 ATR (points, Point=0.01):** p50 ≈ 829 · p75 ≈ 1000 · p90 ≈ 1215 · mean ≈ 880.

---

## 2. Unified Edge Framework geometry (design)

Hard rules from framework + factory:

```text
never TP < SL          →  InpTP_Points ≥ InpSL_Points
RR_design = TP / SL    →  1500 / 1200 = 1.25
BWR = 1 / (1 + R)      →  44.44% if R ≈ RR
E_N = WR × (R + 1) − 1
BM  = WR − BWR
Leak = c_R / (R + 1)
EF  = BM − Leak
```

| Piece | Choice | Intent |
| --- | --- | --- |
| SL | **1200** pts | Structural 1R on gold M15 (~1.45× ATR p50) — not token |
| TP | **1500** pts | **TP > SL** · designed RR **1.25** |
| BB | 20 / **2.2σ** | Signal threshold |
| Session | **12:00–20:00** server | London/NY overlap |
| Skip Tue | **true** | Weekday cut (champ pattern) |
| ATR regime | **ON · max 1000** | ≈ ATR p75 — cut high-vol FRAGILE |
| BB-width | OFF | Avoid fire starvation |
| Grid | depth **1** | Clean G0 events |
| AOS | **OFF** | Chart sleeve = engine only |

**Why not ATR-p50 SL (830)?** Probe E_N negative (−0.02R) / EF &lt; 0 — geometry restricted by token stop vs gold noise.  
**Why not Harvest RR=1.0?** Lower E_N (+0.06R) and thinner EF — user target = mix WR + returns.  
**Why ATR max ON?** Declared **regime-filtered** (framework Gate G3): improves EF (+7.6pp vs +5.3pp unfiltered) while keeping n≥40.

---

## 3. M15* probe scorecard (design evidence — not Tester blotter)

Closed-bar fade → next open · fixed TP/SL · session 12–20 · skip Tue · BBDev 2.2 · ~6m M1→M15* resample · cost prior 35 pts RT.

| Sleeve | n | WR | RR | BWR | BM | Leak† | EF | E_N | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **Balanced 1200/1500 + ATR≤1000 (chosen)** | 75 | 53.3% | 1.25 | 44.4% | +8.9pp | ~1.3pp | **+7.6pp** | **+0.200R** | design-viable |
| Balanced 1200/1500 (no ATR gate) | 143 | 51.1% | 1.25 | 44.4% | +6.6pp | ~1.3pp | +5.3pp | +0.149R | alt / more fires |
| Growth 1200/1800 + ATR≤1000 | 75 | 45.3% | 1.50 | 40.0% | +5.3pp | ~1.2pp | +4.2pp | +0.133R | returns-leaning alt |
| Harvest 1200/1200 | 143 | 53.2% | 1.00 | 50.0% | +3.1pp | ~1.5pp | +1.7pp | +0.063R | hit-rate alt |
| Balanced **830/1040** (ATR p50) | 143 | 43.4% | 1.25 | 44.4% | −1.0pp | ~1.9pp | −2.9pp | −0.023R | **restricted** |

† `c_R` prior ≈ 35 pts round-trip / SL pts (framework Stage 1 cost spirit — replace with blotter).

---

## 4. Design-not-restricted checklist

| # | Rule | This preset |
| ---: | --- | --- |
| 1 | Never TP &lt; SL | **TP 1500 > SL 1200** (ConfigValidate enforces) |
| 2 | Designed RR ≥ 1.0 | **1.25** |
| 3 | WR can clear BWR after Leak prior | Probe WR 53.3% > BWR 44.4%; EF ≫ 0 |
| 4 | Not WR-theatre (token SL) | SL 1200 structural vs gold M15 ATR |
| 5 | Not lottery RR | RR 1.25, not ≥3 |
| 6 | G0 single-leg events | MaxLevels=1 / MaxEntries=1 |
| 7 | Filters protect edge, not starve fires | Session + ATR max; BB-width OFF; n≈75 |
| 8 | Regime filter declared | ATR≤p75 · meanrev home |
| 9 | AOS not required for geometry claim | AOS OFF |
| 10 | Incomplete tip not used for admission | Oct noted only |

---

## 5. Load path (chart)

1. Open **XAUUSD M15** chart.  
2. Attach `Experts\BMRG\BMRG.ex5`.  
3. Inputs → **Load** →  
   `Experts\BMRG\Presets\BMRG-M15-XAUUSD-6M-P0_balanced_chart.set`  
4. Confirm: `SL=1200` · `TP=1500` · `BBDev=2.2` · time **12–20** · **Tue off** · **ATR max=1000** · magic **26100915** · AOS off.  
5. Optional visual: Bollinger(20, 2.2) on chart (EA uses its own handles).

### Tester

Load from **`Profiles/Tester/BMRG/XAUUSD/BMRG-M15-XAUUSD-6M-P0_balanced_chart.set`**. Dates **2026.05.01 – 2026.10.07** (or through Sep end to skip Oct MISMATCH tip). Model: every tick / real ticks if available. Deposit ≥ 1000 (gold margin).

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
| BM by ATR tercile / ER cell | |

**Accept to iterate:** `E_N>0`, `WR>BWR`, `EF>0` preferred, `RR−R` not crushed, fires not starved.  
**Reject geometry:** TP&lt;SL theatre, or WR≪BWR with OK R and no cost excuse, or EF≤0 after measured Leak.

### Sleeve ladder (Tester)

| Sleeve | Magic | Delta | Status |
| --- | ---: | --- | --- |
| P0 | 26100915 | BB 2.2 · CD 2 · RR 1.25 | FAILED WR≈43% |
| P1 | 26100916 | BB 2.4 · CD 3 · BBw 0.35 · RR 1.25 | FAILED same WR |
| P2 | 26100917 | + fade confirm (v1.22) | FAILED WR≈20% |
| P3 | 26100918 | RR 1.35 (1200/1620) · lower BWR | Mixed; hi-vol/continuation DD |
| **P4** | **26100919** | **RR 1.0** (1200/1200) · ATR≤**800** · BBw≤**1.0%** · WR lab | **NEXT** |

Load P4: `Profiles/Tester/BMRG/XAUUSD/BMRG-M15-XAUUSD-6M-P4_wrFocus_RR1_chart.set`  
(also under `Experts/BMRG/Presets/`). Touch entry (fade OFF). **BWR=50%** — iterate regime until WR clears 50%.

---

## 7. Explicit non-claims

- Probe is a **design prior**, not a Strategy Tester blotter / G0–G5 gate.  
- EURUSD M15 balanced remains a separate sleeve; this file is the **XAUUSD M15 chart** balanced + ATR-regime sleeve for the last ~6m tip.  
- Do not raise `f` / MaxLevels until a scored blotter clears Stage 1.  
- `regime_filtered=true` for Gate G3 scoring — do not claim cross-regime robustness without re-open ATR gate tests.
