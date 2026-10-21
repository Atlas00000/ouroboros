# USDJPY — Asset profile dossier

> Research / advisory only · Ouroboros `profile.v1` + `regimes.rule_v1` + `fit.map_v0`  
> Generated `2026-10-18T14:44:24Z` · data `2024-09-12` → `2026-09-21` (25 calendar months, M1 depth ≈ 740d)

Canvas cover (open beside chat): [`usdjpy-asset-profile.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/usdjpy-asset-profile.canvas.tsx).

---

## Identity

| Field | Value |
| --- | --- |
| Symbol | `USDJPY` |
| Display | US Dollar / Japanese Yen |
| Class | fx |
| Quote | JPY |
| MT5 ticker | `USDJPY` |
| Sessions | sydney, tokyo, london, new_york · `UTC` · UTC 22:00–22:00 |

FX approx Sun 22:00–Fri 22:00 UTC; session names from calendar module.

---

## Two clocks

### Nowcast (H1 state)

| Metric | Value |
| --- | --- |
| Confirmed regime | **trending_up** |
| Vol percentile | 21.1 |
| Trend ER | 0.429 |
| Confidence | 0.943 |
| As-of | 2026-09-21 22:00:00+00:00 |
| Stale | True |

Soft probabilities (nowcast — may disagree with confirmed label when confidence is low):

| Regime | P |
| --- | ---: |
| trending_up | 94.3% |
| trending_down | 1.9% |
| ranging | 1.9% |
| high_volatility | 1.9% |

### Live fit gate (ex-post 30d H1 shares → dominant tag)

| Family | Tag | MATCH | MISMATCH | FRAGILE | Bars |
| --- | --- | ---: | ---: | ---: | ---: |
| `meanrev` | **FRAGILE** | 34.6% | 24.7% | 40.7% | 506 |
| `trendfollow` | **FRAGILE** | 24.7% | 34.6% | 40.7% | 506 |

Interpretation: last ~30d H1 mass is **high_volatility-led** (40.7%) with ranging 34.6% and net trend ≈ 24.7% → both families **FRAGILE**. Confirmed state says trending_up but is **stale** relative to the pipe cut.

---

## Character (`profile.v1`)

### Volatility & liquidity

| Field | Value |
| --- | --- |
| ATR pctile 30d | 66.7 |
| Realized vol pctile 30d | 86.7 |
| Typical daily range | 1.28355 JPY |
| Range pctile 30d (liq proxy) | 56.7 |
| True spread | deferred |

_true bid/ask spread deferred until quote ingestion; range proxies (high-low) only_

### Regime distribution (history clock)

Confirmed-label share over the profile sample (H1 preferred when depth gate passes):

| Regime | Share |
| --- | ---: |
| trending_up | 19.0% |
| trending_down | 11.0% |
| ranging | 45.0% |
| high_volatility | 25.0% |

**Read:** ranging (45%) + high_volatility (25%) · net trending (up+down) ≈ 30%. This is a **meanrev-leaning** USDJPY on H1 history — with a material fragile/high-vol sleeve and occasional trend-MATCH months when combined trend shares edge ranging.

### Peer correlations (H1 ~30d)

| Peer | ρ |
| --- | ---: |
| GBPJPY | +0.904 |
| EURJPY | +0.898 |
| EURUSD | -0.588 |
| GBPUSD | -0.570 |
| AUDUSD | -0.479 |
| NZDUSD | -0.473 |
| USDCAD | +0.319 |
| EURGBP | +0.065 |

Strongest |ρ| peers: GBPJPY (+0.90), EURJPY (+0.90), EURUSD (−0.59), GBPUSD (−0.57). Notable negatives: dollar majors (EUR/GBP/AUD/NZD vs USD) — USDJPY moves with the yen sleeve and against USD strength proxies in this window.

### Event sensitivities

Event move multiples: CPI: 1.36× ATR; NFP: —; FOMC: —; GDP: —; central_bank: —.

---

## Path

Monthly D1 path return over the window: **+10.3%** (open 142.68300 → last close 157.34800).

| Month | Ret % | Close |
| --- | ---: | ---: |
| 2024-09 | +0.61 | 143.55700 |
| 2024-10 | +5.87 | 151.97900 |
| 2024-11 | -1.53 | 149.66000 |
| 2024-12 | +4.95 | 157.06100 |
| 2025-01 | -1.24 | 155.18000 |
| 2025-02 | -2.71 | 150.60800 |
| 2025-03 | -0.49 | 149.88500 |
| 2025-04 | -4.58 | 143.00800 |
| 2025-05 | +0.70 | 144.00700 |
| 2025-06 | +0.09 | 143.90900 |
| 2025-07 | +4.75 | 150.73600 |
| 2025-08 | -2.40 | 147.12400 |
| 2025-09 | +0.53 | 147.90900 |
| 2025-10 | +4.10 | 153.97100 |
| 2025-11 | +1.26 | 155.90900 |
| 2025-12 | +0.47 | 156.63500 |
| 2026-01 | -1.25 | 154.76800 |
| 2026-02 | +0.56 | 156.05200 |
| 2026-03 | +1.24 | 158.58600 |
| 2026-04 | -1.01 | 156.98900 |
| 2026-05 | +1.51 | 159.35800 |
| 2026-06 | +2.05 | 162.63000 |
| 2026-07 | -3.30 | 157.27000 |
| 2026-08 | +1.68 | 159.74700 |
| 2026-09 | -1.50 | 157.34800 |

---

## Narrative pressure

- Sentiment score: **−0.009** on [−1, +1] · 9 items · 24h window
- As-of: 2026-10-09 13:03:38.491856+00:00 · stale=True
- Mapped news articles: **163**
- Insight: _USDJPY: trending up context_ — USDJPY is currently classified as trending up with realized volatility near the 21st pct of its recent window. News sentiment over the last 24h is −0.01 on a [−1, +1] scale. This narrative summarizes deterministic analytics only and is not a trade signal.

Recent headlines:

- 2026-10-09 · forexfactory.calendar — FOMC Member Collins Speaks
- 2026-10-09 · forexfactory.calendar — Prelim UoM Consumer Sentiment
- 2026-10-09 · forexfactory.calendar — Prelim UoM Inflation Expectations
- 2026-10-09 · forexfactory.calendar — Prelim Machine Tool Orders y/y
- 2026-10-08 · forexfactory.calendar — Household Spending y/y
- 2026-10-08 · forexfactory.calendar — FOMC Member Musalem Speaks
- 2026-10-08 · forexfactory.calendar — 30-y Bond Auction
- 2026-10-08 · forexfactory.calendar — Natural Gas Storage

---

## Provenance

- Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`
- Profile confidence: 0.99 · stale=False
- Sources: mt5.prices, metrics.v1, regimes.rule_v1
- Raw export: [`audit.json`](./audit.json) · monthly boards: [`regime-audit.md`](./regime-audit.md)

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
