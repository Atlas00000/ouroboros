# AUDUSD — Asset profile dossier

> Research / advisory only · Ouroboros `profile.v1` + `regimes.rule_v1` + `fit.map_v0`  
> Generated `2026-10-18T23:39:55Z` · data `2024-09-12` → `2026-09-21` (25 calendar months, M1 depth ≈ 740d)

Canvas cover (open beside chat): [`audusd-asset-profile.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/audusd-asset-profile.canvas.tsx).

---

## Identity

| Field | Value |
| --- | --- |
| Symbol | `AUDUSD` |
| Display | Australian Dollar / US Dollar |
| Class | fx |
| Quote | USD |
| MT5 ticker | `AUDUSD` |
| Sessions | sydney, tokyo, london, new_york · `UTC` · UTC 22:00–22:00 |

FX approx Sun 22:00–Fri 22:00 UTC; session names from calendar module.

---

## Two clocks

### Nowcast (H1 state)

| Metric | Value |
| --- | --- |
| Confirmed regime | **ranging** |
| Vol percentile | 22.2 |
| Trend ER | -0.025 |
| Confidence | 0.939 |
| As-of | 2026-09-21 22:00:00+00:00 |
| Stale | True |

Soft probabilities (nowcast — may disagree with confirmed label when confidence is low):

| Regime | P |
| --- | ---: |
| trending_up | 2.1% |
| trending_down | 2.1% |
| ranging | 93.8% |
| high_volatility | 2.1% |

### Live fit gate (ex-post 30d H1 shares → dominant tag)

| Family | Tag | MATCH | MISMATCH | FRAGILE | Bars |
| --- | --- | ---: | ---: | ---: | ---: |
| `meanrev` | **MATCH** | 56.5% | 23.9% | 19.5% | 451 |
| `trendfollow` | **MISMATCH** | 23.9% | 56.5% | 19.5% | 451 |

Interpretation: last ~30d H1 mass is **ranging-led** → meanrev **MATCH**, trendfollow **MISMATCH**. FRAGILE share ≈ 20%.

---

## Character (`profile.v1`)

### Volatility & liquidity

| Field | Value |
| --- | --- |
| ATR pctile 30d | 3.3 |
| Realized vol pctile 30d | 33.3 |
| Typical daily range | 0.00320 USD |
| Range pctile 30d (liq proxy) | 46.7 |
| True spread | deferred |

_true bid/ask spread deferred until quote ingestion; range proxies (high-low) only_

### Regime distribution (history clock)

Confirmed-label share over the profile sample (H1 preferred when depth gate passes):

| Regime | Share |
| --- | ---: |
| trending_up | 14.6% |
| trending_down | 12.8% |
| ranging | 47.7% |
| high_volatility | 25.0% |

**Read:** ranging (48%) + high_volatility (25%) · net trending (up+down) ≈ 27%. This is a **meanrev-leaning** FX major on H1 history — with a material fragile/high-vol sleeve.

### Peer correlations (H1 ~30d)

| Peer | ρ |
| --- | ---: |
| NZDUSD | +0.783 |
| GBPUSD | +0.729 |
| EURUSD | +0.682 |
| USDCAD | -0.520 |
| USDJPY | -0.479 |
| EURGBP | -0.251 |
| EURJPY | -0.219 |
| GBPJPY | -0.197 |

Strongest |ρ| peers: NZDUSD (+0.78), GBPUSD (+0.73), EURUSD (+0.68), USDCAD (-0.52). Notable negatives: USDCAD (-0.52), USDJPY (-0.48), EURGBP (-0.25).

### Event sensitivities

Event move multiples: NFP: —; CPI: 1.49× ATR; FOMC: —; central_bank: —.

---

## Path

Monthly D1 path return over the window: **+6.7%** (open 0.66755 → last close 0.71196).

| Month | Ret % | Close |
| --- | ---: | ---: |
| 2024-09 | +3.61 | 0.69163 |
| 2024-10 | -4.92 | 0.65761 |
| 2024-11 | -1.02 | 0.65093 |
| 2024-12 | -5.13 | 0.61768 |
| 2025-01 | +0.40 | 0.62100 |
| 2025-02 | +0.89 | 0.62047 |
| 2025-03 | +0.51 | 0.62410 |
| 2025-04 | +2.68 | 0.64081 |
| 2025-05 | +0.31 | 0.64283 |
| 2025-06 | +2.34 | 0.65813 |
| 2025-07 | -2.36 | 0.64258 |
| 2025-08 | +1.79 | 0.65411 |
| 2025-09 | +1.10 | 0.66128 |
| 2025-10 | -1.08 | 0.65419 |
| 2025-11 | +0.15 | 0.65510 |
| 2025-12 | +1.84 | 0.66717 |
| 2026-01 | +4.34 | 0.69595 |
| 2026-02 | +2.39 | 0.71134 |
| 2026-03 | -1.77 | 0.69197 |
| 2026-04 | +4.06 | 0.71999 |
| 2026-05 | -0.29 | 0.71793 |
| 2026-06 | -3.73 | 0.69112 |
| 2026-07 | +1.43 | 0.70104 |
| 2026-08 | +1.86 | 0.71701 |
| 2026-09 | -0.70 | 0.71196 |

---

## Narrative pressure

- Sentiment score: **-0.043** on [−1, +1] · 7 items · 24h window
- As-of: 2026-10-09 13:03:38.491856+00:00 · stale=True
- Mapped news articles: **155**
- Insight: _AUDUSD: ranging context_ — AUDUSD is currently classified as ranging with realized volatility near the 22th pct of its recent window. News sentiment over the last 24h is -0.04 on a [-1, +1] scale. This narrative summarizes deterministic analytics only and is not a trade signal.

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
