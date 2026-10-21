# US30 — Asset profile dossier

> Research / advisory only · Ouroboros `profile.v1` + `regimes.rule_v1` + `fit.map_v0`  
> Generated `2026-10-18T23:55:50Z` · data `2024-09-12` → `2026-10-07` (26 calendar months, M1 depth ≈ 755d)

Canvas cover (open beside chat): [`us30-asset-profile.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/us30-asset-profile.canvas.tsx).

> **Depth note:** requested 2y monthly audit; YWO MT5 `US30` M1/H1/D1 span `2024-09-12` → `2026-10-07` (≈755d ≈ 2.1y). Boards cover full available history.

---

## Identity

| Field | Value |
| --- | --- |
| Symbol | `US30` |
| Display | Dow Jones Industrial Average |
| Class | index |
| Quote | USD |
| MT5 ticker | `US30` |
| Sessions | new_york, london · `UTC` · UTC 13:30–20:00 |

Index cash hours approximate (US RTH for US500/US30/NAS100; London/Frankfurt/Tokyo cash for regional indices). Broker CFD session may trade nearly 24h — treat as research proxy.

---

## Two clocks

### Nowcast (H1 state)

| Metric | Value |
| --- | --- |
| Confirmed regime | **trending_down** |
| Vol percentile | 15.8 |
| Trend ER | -0.633 |
| Confidence | 0.943 |
| As-of | 2026-10-07 14:00:00+00:00 |
| Stale | True |

Soft probabilities (nowcast — may disagree with confirmed label when confidence is low):

| Regime | P |
| --- | ---: |
| trending_up | 1.9% |
| trending_down | 94.3% |
| ranging | 1.9% |
| high_volatility | 1.9% |

### Live fit gate (ex-post 30d H1 shares → dominant tag)

| Family | Tag | MATCH | MISMATCH | FRAGILE | Bars |
| --- | --- | ---: | ---: | ---: | ---: |
| `meanrev` | **FRAGILE** | 20.6% | 26.7% | 52.7% | 412 |
| `trendfollow` | **FRAGILE** | 26.7% | 20.6% | 52.7% | 412 |

Interpretation: last ~30d H1 mass is **trend-contested** — meanrev=FRAGILE (20.6% MATCH / 26.7% MISMATCH), trendfollow=FRAGILE (26.7% MATCH). FRAGILE sleeve 52.7%.

---

## Character (`profile.v1`)

### Volatility & liquidity

| Field | Value |
| --- | --- |
| ATR pctile 30d | 80.0 |
| Realized vol pctile 30d | 33.3 |
| Typical daily range | 455.19 USD |
| Range pctile 30d (liq proxy) | 80.0 |
| True spread | deferred |

_true bid/ask spread deferred until quote ingestion; range proxies (high-low) only_

### Regime distribution (history clock)

Confirmed-label share over the profile sample (H1 preferred when depth gate passes):

| Regime | Share |
| --- | ---: |
| trending_up | 18.8% |
| trending_down | 15.9% |
| ranging | 39.6% |
| high_volatility | 25.7% |

**Read:** ranging (39.6%) + high_volatility (25.7%) vs net trending (34.7%). On this sample US30 is **meanrev-leaning** on H1 history — with a material fragile/high-vol sleeve.

### Peer correlations (H1 ~30d)

| Peer | ρ |
| --- | ---: |
| US500 | +0.823 |
| DE40 | +0.637 |
| UK100 | +0.617 |
| NAS100 | +0.536 |
| JP225 | +0.423 |

Closest sleeves this window: US500 (+0.82), DE40 (+0.64), UK100 (+0.62), NAS100 (+0.54).

### Event sensitivities

| Event | × ATR | Notes |
| --- | ---: | --- |
| NFP | — | Relevant for US30; need ≥3 scored windows (have 0 moves from 0 calendar hits). |
| CPI | 2.53 | Median H1 range / ATR over 4 events (4h window). |
| FOMC | — | Relevant for US30; need ≥3 scored windows (have 2 moves from 6 calendar hits). |
| GDP | — | Relevant for US30; need ≥3 scored windows (have 0 moves from 0 calendar hits). |

---

## Path

Monthly D1 path return over the window: **+24.7%** (open 40867.77 → last close 50945.77).

| Month | Ret % | Close |
| --- | ---: | ---: |
| 2024-09 | +3.44 | 42271.79 |
| 2024-10 | -1.12 | 41798.63 |
| 2024-11 | +7.39 | 44888.50 |
| 2024-12 | -4.63 | 42889.62 |
| 2025-01 | +3.70 | 44479.36 |
| 2025-02 | -0.53 | 43817.20 |
| 2025-03 | -4.29 | 41915.50 |
| 2025-04 | -2.76 | 40756.90 |
| 2025-05 | +3.53 | 42196.90 |
| 2025-06 | +4.51 | 44035.10 |
| 2025-07 | -0.17 | 43958.80 |
| 2025-09 | +1.64 | 46327.50 |
| 2025-10 | +2.72 | 47587.10 |
| 2025-11 | +0.14 | 47664.90 |
| 2025-12 | +0.83 | 48064.20 |
| 2026-01 | +1.49 | 48830.55 |
| 2026-02 | +0.24 | 48858.53 |
| 2026-03 | -4.20 | 46398.53 |
| 2026-04 | +7.25 | 49760.23 |
| 2026-05 | +2.58 | 51044.88 |
| 2026-06 | +2.25 | 52195.08 |
| 2026-07 | +0.33 | 52366.97 |
| 2026-08 | +1.02 | 53222.12 |
| 2026-09 | -4.02 | 51084.70 |
| 2026-10 | -0.27 | 50945.77 |

---

## Narrative pressure

- Sentiment score: **-0.043** on [−1, +1] · 7 items · 24h window
- As-of: 2026-10-09 13:03:38.491856+00:00 · stale=True
- Mapped news articles: **208**
- Insight: _US30: trending down context_ — US30 is currently classified as trending down with realized volatility near the 16th pct of its recent window. News sentiment over the last 24h is -0.04 on a [-1, +1] scale. This narrative summarizes deterministic analytics only and is not a trade signal.

Recent headlines:

- 2026-10-09 · forexfactory.calendar — FOMC Member Collins Speaks
- 2026-10-09 · forexfactory.calendar — Prelim UoM Consumer Sentiment
- 2026-10-09 · forexfactory.calendar — Prelim UoM Inflation Expectations
- 2026-10-08 · forexfactory.calendar — FOMC Member Musalem Speaks
- 2026-10-08 · forexfactory.calendar — 30-y Bond Auction
- 2026-10-08 · forexfactory.calendar — Natural Gas Storage
- 2026-10-08 · forexfactory.calendar — Final Wholesale Inventories m/m
- 2026-10-08 · forexfactory.calendar — Unemployment Claims

---

## Provenance

- Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`
- Profile confidence: 0.99 · stale=False
- Sources: mt5.prices, metrics.v1, regimes.rule_v1
- Raw export: [`audit.json`](./audit.json) · monthly boards: [`regime-audit.md`](./regime-audit.md)

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
