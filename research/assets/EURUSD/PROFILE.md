# EURUSD — Asset profile dossier

> Research / advisory only · Ouroboros `profile.v1` + `regimes.rule_v1` + `fit.map_v0`  
> Generated `2026-10-18T11:44:56Z` · data `2024-09-12` → `2026-10-07` (26 calendar months, M1 depth ≈ 755d)

Canvas cover (open beside chat): `canvases/eurusd-asset-profile.canvas.tsx` in the Cursor project.

---

## Identity

| Field | Value |
| --- | --- |
| Symbol | `EURUSD` |
| Display | Euro / US Dollar |
| Class | fx |
| Quote | USD |
| MT5 ticker | `EURUSD` |
| Sessions | sydney, tokyo, london, new_york · `UTC` · UTC 22:00–22:00 |

FX approx Sun 22:00–Fri 22:00 UTC; session names from calendar module.

---

## Two clocks

### Nowcast (H1 state)

| Metric | Value |
| --- | --- |
| Confirmed regime | **high_volatility** |
| Vol percentile | 87.5 |
| Trend ER | -0.505 |
| Confidence | 0.943 |
| As-of | 2026-10-07 15:00:00+00:00 |
| Stale | False |

Soft probabilities (nowcast — may disagree with confirmed label when confidence is low):

| Regime | P |
| --- | ---: |
| trending_up | 1.9% |
| trending_down | 1.9% |
| ranging | 1.9% |
| high_volatility | 94.3% |

### Live fit gate (ex-post 30d H1 shares → dominant tag)

| Family | Tag | MATCH | MISMATCH | FRAGILE | Bars |
| --- | --- | ---: | ---: | ---: | ---: |
| `meanrev` | **FRAGILE** | 35.0% | 13.8% | 51.2% | 529 |
| `trendfollow` | **FRAGILE** | 13.8% | 35.0% | 51.2% | 529 |

Interpretation: last ~30d H1 mass is **high_volatility-led** → meanrev **FRAGILE**, trendfollow **FRAGILE**. FRAGILE share ≈ 51%.

---

## Character (`profile.v1`)

### Volatility & liquidity

| Field | Value |
| --- | --- |
| ATR pctile 30d | 100.0 |
| Realized vol pctile 30d | 76.7 |
| Typical daily range | 0.00542 USD |
| Range pctile 30d (liq proxy) | 90.0 |
| True spread | deferred |

_true bid/ask spread deferred until quote ingestion; range proxies (high-low) only_

### Regime distribution (history clock)

Confirmed-label share over the profile sample (H1 preferred when depth gate passes):

| Regime | Share |
| --- | ---: |
| trending_up | 13.9% |
| trending_down | 13.9% |
| ranging | 46.0% |
| high_volatility | 26.2% |

**Read:** ranging (46%) + high_volatility (26%) · net trending (up+down) ≈ 28%. This is a **meanrev-leaning** FX major on H1 history — with a material fragile/high-vol sleeve.

### Peer correlations (H1 ~30d)

| Peer | ρ |
| --- | ---: |
| GBPUSD | +0.840 |
| NZDUSD | +0.684 |
| AUDUSD | +0.682 |
| USDJPY | -0.588 |
| USDCAD | -0.543 |
| GBPJPY | -0.294 |
| EURJPY | -0.190 |
| EURGBP | +0.123 |

Strongest |ρ| peers: GBPUSD (+0.84), NZDUSD (+0.68), AUDUSD (+0.68), USDJPY (-0.59). Notable negatives: USDJPY (-0.59), USDCAD (-0.54), GBPJPY (-0.29).

### Event sensitivities

Event move multiples: NFP: —; CPI: 1.53× ATR; FOMC: —; GDP: —; central_bank: 1.22× ATR.

---

## Path

Monthly D1 path return over the window: **+1.6%** (open 1.10101 → last close 1.11902).

| Month | Ret % | Close |
| --- | ---: | ---: |
| 2024-09 | +1.19 | 1.11414 |
| 2024-10 | -2.31 | 1.08839 |
| 2024-11 | -2.83 | 1.05755 |
| 2024-12 | -2.09 | 1.03493 |
| 2025-01 | +0.12 | 1.03640 |
| 2025-02 | +1.20 | 1.03743 |
| 2025-03 | +3.99 | 1.08179 |
| 2025-04 | +4.69 | 1.13250 |
| 2025-05 | +0.18 | 1.13457 |
| 2025-06 | +3.87 | 1.17852 |
| 2025-07 | -3.12 | 1.14172 |
| 2025-08 | +2.37 | 1.16880 |
| 2025-09 | +0.39 | 1.17332 |
| 2025-10 | -1.69 | 1.15361 |
| 2025-11 | +0.62 | 1.16009 |
| 2025-12 | +1.23 | 1.17434 |
| 2026-01 | +0.83 | 1.18461 |
| 2026-02 | -0.35 | 1.18076 |
| 2026-03 | -1.68 | 1.15735 |
| 2026-04 | +1.34 | 1.17285 |
| 2026-05 | -0.69 | 1.16484 |
| 2026-06 | -2.02 | 1.14128 |
| 2026-07 | +0.92 | 1.15176 |
| 2026-08 | +0.66 | 1.16179 |
| 2026-09 | -2.51 | 1.13266 |
| 2026-10 | -1.20 | 1.11902 |

---

## Narrative pressure

- Sentiment score: **-0.050** on [−1, +1] · 9 items · 24h window
- As-of: 2026-10-09 13:03:38.491856+00:00 · stale=True
- Mapped news articles: **193**
- Insight: _EURUSD: high volatility context_ — EURUSD is currently classified as high volatility with realized volatility near the 92th pct of its recent window. News sentiment over the last 24h is -0.05 on a [-1, +1] scale. This narrative summarizes deterministic analytics only and is not a trade signal.

Recent headlines:

- 2026-10-09 · forexfactory.calendar — FOMC Member Collins Speaks
- 2026-10-09 · forexfactory.calendar — Prelim UoM Consumer Sentiment
- 2026-10-09 · forexfactory.calendar — Prelim UoM Inflation Expectations
- 2026-10-09 · forexfactory.calendar — ECOFIN Meetings
- 2026-10-09 · forexfactory.calendar — Italian Industrial Production m/m
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
