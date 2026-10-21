# AVGO — Asset profile dossier

> Research / advisory only · Ouroboros `profile.v1` + `regimes.rule_v1` + `fit.map_v0`  
> Generated `2026-10-11T23:39:37Z` · data `2026-02-26` → `2026-10-09` (9 calendar months, M1 depth ≈ 225d)

Canvas cover (open beside chat): [`avgo-asset-profile.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/avgo-asset-profile.canvas.tsx).

> **Depth note:** requested 2y monthly audit; YWO MT5 `Broadcom` CFD only exposes M1/H1/D1 from `2026-02-26` (≈225d). Boards below cover available history.

---

## Identity

| Field | Value |
| --- | --- |
| Symbol | `AVGO` |
| Display | Broadcom Inc. |
| Class | equity |
| Quote | USD |
| MT5 ticker | `Broadcom` |
| Sessions | new_york · `America/New_York` · UTC 13:30–20:00 |

US cash RTH approx 09:30–16:00 America/New_York (13:30–20:00 UTC during EST; 14:30–21:00 UTC during EDT). Broker CFD hours may extend; DST shifts open/close UTC.

---

## Two clocks

### Nowcast (H1 state)

| Metric | Value |
| --- | --- |
| Confirmed regime | **trending_up** |
| Vol percentile | 58.0 |
| Trend ER | 0.429 |
| Confidence | 0.943 |
| As-of | 2026-10-07 14:00:00+00:00 |
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
| `meanrev` | **MISMATCH** | 47.7% | 50.3% | 1.9% | 155 |
| `trendfollow` | **MATCH** | 50.3% | 47.7% | 1.9% | 155 |

Interpretation: last ~30d H1 mass is **trend-contested** — meanrev=MISMATCH (47.7% MATCH / 50.3% MISMATCH), trendfollow=MATCH (50.3% MATCH). FRAGILE sleeve 1.9%.

---

## Character (`profile.v1`)

### Volatility & liquidity

| Field | Value |
| --- | --- |
| ATR pctile 30d | 30.0 |
| Realized vol pctile 30d | 86.7 |
| Typical daily range | 8.67 USD |
| Range pctile 30d (liq proxy) | 16.7 |
| True spread | deferred |

_true bid/ask spread deferred until quote ingestion; range proxies (high-low) only_

### Regime distribution (history clock)

Confirmed-label share over the profile sample (H1 preferred when depth gate passes):

| Regime | Share |
| --- | ---: |
| trending_up | 20.5% |
| trending_down | 15.7% |
| ranging | 42.5% |
| high_volatility | 21.3% |

**Read:** ranging (42.5%) + high_volatility (21.3%) vs net trending (36.2%). On this sample AVGO is **meanrev-leaning** on H1 history — with a material fragile/high-vol sleeve.

### Peer correlations (H1 ~30d)

| Peer | ρ |
| --- | ---: |
| US500 | +0.717 |
| NAS100 | +0.662 |
| NVDA | +0.584 |
| AMZN | +0.407 |
| TSLA | +0.374 |
| MSFT | +0.327 |
| GOOGL | +0.299 |
| JPM | +0.292 |
| META | +0.290 |
| AAPL | +0.288 |
| XOM | -0.040 |

Closest sleeves this window: US500 (+0.72), NAS100 (+0.66), NVDA (+0.58), AMZN (+0.41).

### Event sensitivities

Taxonomy present (NFP / CPI / FOMC) but **ATR multiples empty** — calendar hits scored for AVGO are below the ≥3-window gate. Honest gap until equity event windows are scored.

---

## Path

Monthly D1 path return over the window: **+14.2%** (open 316.55 → last close 361.36).

| Month | Ret % | Close |
| --- | ---: | ---: |
| 2026-02 | +1.00 | 319.73 |
| 2026-03 | +0.66 | 309.21 |
| 2026-04 | +33.38 | 417.13 |
| 2026-05 | +8.01 | 446.73 |
| 2026-06 | -15.13 | 377.16 |
| 2026-07 | +4.59 | 389.25 |
| 2026-08 | -3.00 | 370.17 |
| 2026-09 | -3.53 | 351.03 |
| 2026-10 | +2.35 | 361.36 |

---

## Narrative pressure

- Sentiment score: **-0.074** on [−1, +1] · 21 items · 24h window
- As-of: 2026-10-08 16:35:35.242914+00:00 · stale=True
- Mapped news articles: **244**
- Insight: _AVGO: trending up context_ — AVGO is currently classified as trending up with realized volatility near the 58th pct of its recent window. News sentiment over the last 24h is -0.07 on a [-1, +1] scale. This narrative summarizes deterministic analytics only and is not a trade signal.

Recent headlines:

- 2026-10-08 · Yahoo — Could This Chipmaker Really Overtake Intel in Revenue by 2031?
- 2026-10-08 · Yahoo — VCSEL Market to Reach US$1.96 Billion by 2032 at 8.8% CAGR, Driven by AI Data Centers and 3D Sensing in Smartphones
- 2026-10-08 · Yahoo — TSMC Sales Are a Big Win for the AI Trade. Why AMD and Other Chip Stocks Are Falling Anyway.
- 2026-10-08 · Yahoo — Sercomm Makes RDK Set-Top Box Available as Reference Hardware
- 2026-10-08 · Yahoo — Broadcom Is Arranging $50 Billion So OpenAI Can Buy Its Chips
- 2026-10-08 · SeekingAlpha — Baskin Financial Q3 2026 Newsletter
- 2026-10-07 · Yahoo — Broadcom, Oracle And SpaceX Tap Private Credit For AI Hardware: Report
- 2026-10-07 · Yahoo — Broadcom (AVGO) Is Seen As Resilient To 32 Gigawatt Power Shortfalls

---

## Provenance

- Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`
- Profile confidence: 0.99 · stale=False
- Sources: mt5.prices, metrics.v1, regimes.rule_v1
- Raw export: [`audit.json`](./audit.json) · monthly boards: [`regime-audit.md`](./regime-audit.md)

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
