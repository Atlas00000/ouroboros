# TSLA — Asset profile dossier

> Research / advisory only · Ouroboros `profile.v1` + `regimes.rule_v1` + `fit.map_v0`  
> Generated `2026-10-18T23:46:14Z` · data `2024-10-07` → `2026-10-07` (25 calendar months, M1 depth ≈ 730d)

Canvas cover (open beside chat): [`tsla-asset-profile.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/tsla-asset-profile.canvas.tsx).

---

## Identity

| Field | Value |
| --- | --- |
| Symbol | `TSLA` |
| Display | Tesla Inc. |
| Class | equity |
| Quote | USD |
| MT5 ticker | `Tesla` |
| Sessions | new_york · `America/New_York` · UTC 13:30–20:00 |

US cash RTH approx 09:30–16:00 America/New_York (13:30–20:00 UTC during EST; 14:30–21:00 UTC during EDT). Broker CFD hours may extend; DST shifts open/close UTC.

---

## Two clocks

### Nowcast (H1 state)

| Metric | Value |
| --- | --- |
| Confirmed regime | **trending_up** |
| Vol percentile | 0.4 |
| Trend ER | 0.145 |
| Confidence | 0.211 |
| As-of | 2026-10-07 14:00:00+00:00 |
| Stale | False |

Soft probabilities (nowcast — may disagree with confirmed label when confidence is low):

| Regime | P |
| --- | ---: |
| trending_up | 21.1% |
| trending_down | 2.8% |
| ranging | 73.2% |
| high_volatility | 2.8% |

### Live fit gate (ex-post 30d H1 shares → dominant tag)

| Family | Tag | MATCH | MISMATCH | FRAGILE | Bars |
| --- | --- | ---: | ---: | ---: | ---: |
| `meanrev` | **MATCH** | 53.7% | 43.6% | 2.7% | 149 |
| `trendfollow` | **MISMATCH** | 43.6% | 53.7% | 2.7% | 149 |

Interpretation: last ~30d H1 mass is **ranging-contested** — meanrev=MATCH (53.7% MATCH / 43.6% MISMATCH), trendfollow=MISMATCH (43.6% MATCH). FRAGILE sleeve 2.7%.

---

## Character (`profile.v1`)

### Volatility & liquidity

| Field | Value |
| --- | --- |
| ATR pctile 30d | 6.7 |
| Realized vol pctile 30d | 6.7 |
| Typical daily range | 9.67 USD |
| Range pctile 30d (liq proxy) | 26.7 |
| True spread | deferred |

_true bid/ask spread deferred until quote ingestion; range proxies (high-low) only_

### Regime distribution (history clock)

Confirmed-label share over the profile sample (H1 preferred when depth gate passes):

| Regime | Share |
| --- | ---: |
| trending_up | 19.5% |
| trending_down | 18.6% |
| ranging | 36.5% |
| high_volatility | 25.4% |

**Read:** ranging (36.5%) + high_volatility (25.4%) vs net trending (38.1%). On this sample TSLA is **trend-leaning** on H1 history — with a material fragile/high-vol sleeve.

### Peer correlations (H1 ~30d)

| Peer | ρ |
| --- | ---: |
| US500 | +0.567 |
| NAS100 | +0.494 |
| NVDA | +0.403 |
| AVGO | +0.374 |
| AMZN | +0.365 |
| MSFT | +0.229 |
| META | +0.185 |
| AAPL | +0.148 |
| XOM | -0.122 |
| GOOGL | +0.109 |
| JPM | +0.102 |

Closest sleeves this window: US500 (+0.57), NAS100 (+0.49), NVDA (+0.40), AVGO (+0.37). Notable negative: XOM (-0.12).

### Event sensitivities

Taxonomy present (NFP / CPI / FOMC) but **ATR multiples empty** — calendar hits scored for TSLA are below the ≥3-window gate. Honest gap until equity event windows are scored.

---

## Path

Monthly D1 path return over the window: **+50.9%** (open 248.91 → last close 375.53).

| Month | Ret % | Close |
| --- | ---: | ---: |
| 2024-10 | +0.32 | 249.70 |
| 2024-11 | +37.03 | 344.92 |
| 2024-12 | +14.72 | 404.14 |
| 2025-01 | +0.13 | 404.54 |
| 2025-02 | -24.21 | 292.91 |
| 2025-03 | -13.83 | 258.78 |
| 2025-04 | +7.00 | 282.05 |
| 2025-05 | +23.71 | 345.73 |
| 2025-06 | -7.58 | 317.45 |
| 2025-07 | +3.37 | 308.14 |
| 2025-08 | +9.06 | 333.56 |
| 2025-09 | +35.36 | 444.37 |
| 2025-10 | +2.90 | 456.29 |
| 2025-11 | -5.63 | 429.81 |
| 2025-12 | +6.71 | 453.64 |
| 2026-01 | -5.90 | 430.37 |
| 2026-02 | -4.40 | 402.25 |
| 2026-03 | -4.88 | 371.56 |
| 2026-04 | +0.80 | 381.33 |
| 2026-05 | +13.95 | 435.45 |
| 2026-06 | -1.11 | 420.27 |
| 2026-07 | -26.73 | 310.90 |
| 2026-08 | +17.93 | 367.68 |
| 2026-09 | -1.35 | 354.66 |
| 2026-10 | +5.21 | 375.53 |

---

## Narrative pressure

- Sentiment score: **-0.060** on [−1, +1] · 1 items · 24h window
- As-of: 2026-10-09 11:48:38.496883+00:00 · stale=True
- Mapped news articles: **249**
- Insight: _TSLA: trending up context_ — TSLA is currently classified as trending up with realized volatility near the 0th pct of its recent window. News sentiment over the last 24h is -0.06 on a [-1, +1] scale. This narrative summarizes deterministic analytics only and is not a trade signal.

Recent headlines:

- 2026-10-08 · Yahoo — Elon Musk Just Shared Bad News for Intel Shareholders
- 2026-10-08 · Yahoo — Latest News In Energy Transition - Oracle Powers Up with Scout's Wind Energy Partnership
- 2026-10-08 · Yahoo — Elon Musk’s Two Companies: Divergent Paths on Bitcoin. Who Made the Smarter Move?
- 2026-10-08 · Yahoo — Tesla Delivered 486,532 Vehicles in Q3. Here's the Margin Math That Will Decide the Earnings Reaction.
- 2026-10-08 · Yahoo — Norway Electric Vehicle Market Size and Forecast 2026-2030 - Q2 2026 Databook | 13.8% CAGR to Lift Market to US$190.9 Million by 2030, Led by Affordable EVs and Fleet Charging
- 2026-10-08 · Yahoo — TSLA Stock Heads For Weekly Win: Dan Ives Sees Over 30% Upside From AI, UBS Calls Setup ‘Tactically Favorable’
- 2026-10-08 · Yahoo — Jim Cramer Says SPCX Could Come to Fruition Long Before Tesla After Goldman Sachs Raises Price Target: 'Real Company With Real Numbers'
- 2026-10-08 · Yahoo — Why Tesla (TSLA) Is Up 6.7% After Unveiling Terafab AI Chip Complex And Major New Credit Lines

---

## Provenance

- Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`
- Profile confidence: 0.99 · stale=False
- Sources: mt5.prices, metrics.v1, regimes.rule_v1
- Raw export: [`audit.json`](./audit.json) · monthly boards: [`regime-audit.md`](./regime-audit.md)

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
