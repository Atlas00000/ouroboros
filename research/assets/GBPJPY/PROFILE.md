# GBPJPY — Asset profile dossier

> Research / advisory only · Ouroboros `profile.v1` + `regimes.rule_v1` + `fit.map_v0`  
> Generated `2026-10-18T14:34:59Z` · data `2024-09-12` → `2026-09-11` (25 calendar months, M1 depth ≈ 730d)

Canvas cover (open beside chat): `canvases/gbpjpy-asset-profile.canvas.tsx` in the Cursor project.

---

## Identity

| Field | Value |
| --- | --- |
| Symbol | `GBPJPY` |
| Display | British Pound / Japanese Yen |
| Class | fx |
| Quote | JPY |
| MT5 ticker | `GBPJPY` |
| Sessions | sydney, tokyo, london, new_york · `UTC` · UTC 22:00–22:00 |

FX approx Sun 22:00–Fri 22:00 UTC; session names from calendar module.

---

## Two clocks

### Nowcast (H1 state)

| Metric | Value |
| --- | --- |
| Confirmed regime | **high_volatility** |
| Vol percentile | 78.3 |
| Trend ER | -0.432 |
| Confidence | 0.641 |
| As-of | 2026-09-11 20:00:00+00:00 |
| Stale | False |

Soft probabilities (nowcast — may disagree with confirmed label when confidence is low):

| Regime | P |
| --- | ---: |
| trending_up | 1.9% |
| trending_down | 32.1% |
| ranging | 1.9% |
| high_volatility | 64.1% |

### Live fit gate (ex-post 30d H1 shares → dominant tag)

| Family | Tag | MATCH | MISMATCH | FRAGILE | Bars |
| --- | --- | ---: | ---: | ---: | ---: |
| `meanrev` | **MATCH** | 53.9% | 17.0% | 29.1% | 529 |
| `trendfollow` | **MISMATCH** | 17.0% | 53.9% | 29.1% | 529 |

Interpretation: last ~30d H1 mass is **ranging-led** → meanrev **MATCH**, trendfollow **MISMATCH**. FRAGILE share ≈ 29%.

---

## Character (`profile.v1`)

### Volatility & liquidity

| Field | Value |
| --- | --- |
| ATR pctile 30d | 76.7 |
| Realized vol pctile 30d | 93.3 |
| Typical daily range | 1.31390 JPY |
| Range pctile 30d (liq proxy) | 76.7 |
| True spread | deferred |

_true bid/ask spread deferred until quote ingestion; range proxies (high-low) only_

### Regime distribution (history clock)

Confirmed-label share over the profile sample (H1 preferred when depth gate passes):

| Regime | Share |
| --- | ---: |
| trending_up | 17.5% |
| trending_down | 10.0% |
| ranging | 47.9% |
| high_volatility | 24.6% |

**Read:** ranging (48%) + high_volatility (25%) · net trending (up+down) ≈ 28%. This is a **meanrev-leaning** FX cross on H1 history — with a material fragile/high-vol sleeve.

### Peer correlations (H1 ~30d)

| Peer | ρ |
| --- | ---: |
| EURJPY | +0.953 |
| USDJPY | +0.904 |
| EURUSD | -0.294 |
| NZDUSD | -0.212 |
| AUDUSD | -0.197 |
| GBPUSD | -0.170 |
| USDCAD | +0.168 |
| EURGBP | -0.154 |

Strongest |ρ| peers: EURJPY (+0.95), USDJPY (+0.90), EURUSD (-0.29), NZDUSD (-0.21). Notable negatives: EURUSD (-0.29), NZDUSD (-0.21), AUDUSD (-0.20).

### Event sensitivities

Event move multiples: CPI: —; GDP: 2.14× ATR; central_bank: —.

---

## Path

Monthly D1 path return over the window: **+11.7%** (open 185.83800 → last close 207.50600).

| Month | Ret % | Close |
| --- | ---: | ---: |
| 2024-09 | +3.36 | 192.07300 |
| 2024-10 | +2.04 | 195.99800 |
| 2024-11 | -2.78 | 190.55100 |
| 2024-12 | +3.27 | 196.60700 |
| 2025-01 | -2.22 | 192.33000 |
| 2025-02 | -0.46 | 189.41800 |
| 2025-03 | +2.14 | 193.63200 |
| 2025-04 | -1.59 | 190.53900 |
| 2025-05 | +1.70 | 193.77900 |
| 2025-06 | +2.02 | 197.60500 |
| 2025-07 | +0.74 | 199.06000 |
| 2025-08 | -0.20 | 198.65500 |
| 2025-09 | +0.07 | 198.79600 |
| 2025-10 | +1.84 | 202.50300 |
| 2025-11 | +2.08 | 206.41600 |
| 2025-12 | +2.24 | 211.04800 |
| 2026-01 | +0.61 | 211.79100 |
| 2026-02 | -1.06 | 210.38200 |
| 2026-03 | +0.27 | 209.95000 |
| 2026-04 | +1.71 | 213.53000 |
| 2026-05 | +0.38 | 214.33900 |
| 2026-06 | +0.53 | 215.47400 |
| 2026-07 | -1.56 | 212.10400 |
| 2026-08 | +2.13 | 216.42300 |
| 2026-09 | -4.12 | 207.50600 |

---

## Narrative pressure

- Sentiment score: **0.116** on [−1, +1] · 2 items · 24h window
- As-of: 2026-10-09 13:03:38.491856+00:00 · stale=True
- Mapped news articles: **71**
- Insight: _GBPJPY: high volatility context_ — GBPJPY is currently classified as high volatility with realized volatility near the 78th pct of its recent window. News sentiment over the last 24h is +0.13 on a [-1, +1] scale. This narrative summarizes deterministic analytics only and is not a trade signal.

Recent headlines:

- 2026-10-09 · forexfactory.calendar — Prelim Machine Tool Orders y/y
- 2026-10-08 · forexfactory.calendar — Household Spending y/y
- 2026-10-08 · forexfactory.calendar — MPC Member Lombardelli Speaks
- 2026-10-08 · Forexlive — Morning Kickstart: Stocks fall as oil and yields rise; USD edges higher
- 2026-10-08 · forexfactory.calendar — BOE Gov Bailey Speaks
- 2026-10-08 · forexfactory.calendar — MPC Member Pill Speaks
- 2026-10-08 · Yahoo — Why Black Hills (BKH) Is Up 8.2% After Inking Long-Term Google Data Center Power Deal
- 2026-10-08 · forexfactory.calendar — MPC Member Greene Speaks

---

## Provenance

- Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`
- Profile confidence: 0.99 · stale=False
- Sources: mt5.prices, metrics.v1, regimes.rule_v1
- Raw export: [`audit.json`](./audit.json) · monthly boards: [`regime-audit.md`](./regime-audit.md)

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
