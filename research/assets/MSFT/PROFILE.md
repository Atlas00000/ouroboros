# MSFT — Asset profile dossier

> Research / advisory only · Ouroboros `profile.v1` + `regimes.rule_v1` + `fit.map_v0`  
> Generated `2026-10-18T23:42:18Z` · data `2024-10-07` → `2026-10-07` (25 calendar months, M1 depth ≈ 730d)

Canvas cover (open beside chat): [`msft-asset-profile.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/msft-asset-profile.canvas.tsx).

---

## Identity

| Field | Value |
| --- | --- |
| Symbol | `MSFT` |
| Display | Microsoft Corporation |
| Class | equity |
| Quote | USD |
| MT5 ticker | `Microsoft` |
| Sessions | new_york · `America/New_York` · UTC 13:30–20:00 |

US cash RTH approx 09:30–16:00 America/New_York (13:30–20:00 UTC during EST; 14:30–21:00 UTC during EDT). Broker CFD hours may extend; DST shifts open/close UTC.

---

## Two clocks

### Nowcast (H1 state)

| Metric | Value |
| --- | --- |
| Confirmed regime | **trending_up** |
| Vol percentile | 4.9 |
| Trend ER | 0.304 |
| Confidence | 0.919 |
| As-of | 2026-10-07 14:00:00+00:00 |
| Stale | False |

Soft probabilities (nowcast — may disagree with confirmed label when confidence is low):

| Regime | P |
| --- | ---: |
| trending_up | 91.9% |
| trending_down | 2.7% |
| ranging | 2.7% |
| high_volatility | 2.7% |

### Live fit gate (ex-post 30d H1 shares → dominant tag)

| Family | Tag | MATCH | MISMATCH | FRAGILE | Bars |
| --- | --- | ---: | ---: | ---: | ---: |
| `meanrev` | **MATCH** | 64.4% | 24.8% | 10.7% | 149 |
| `trendfollow` | **MISMATCH** | 24.8% | 64.4% | 10.7% | 149 |

Interpretation: last ~30d H1 mass is **ranging-contested** — meanrev=MATCH (64.4% MATCH / 24.8% MISMATCH), trendfollow=MISMATCH (24.8% MATCH). FRAGILE sleeve 10.7%.

---

## Character (`profile.v1`)

### Volatility & liquidity

| Field | Value |
| --- | --- |
| ATR pctile 30d | 43.3 |
| Realized vol pctile 30d | 10.0 |
| Typical daily range | 9.99 USD |
| Range pctile 30d (liq proxy) | 3.3 |
| True spread | deferred |

_true bid/ask spread deferred until quote ingestion; range proxies (high-low) only_

### Regime distribution (history clock)

Confirmed-label share over the profile sample (H1 preferred when depth gate passes):

| Regime | Share |
| --- | ---: |
| trending_up | 18.5% |
| trending_down | 12.5% |
| ranging | 37.6% |
| high_volatility | 31.3% |

**Read:** ranging (37.6%) + high_volatility (31.3%) vs net trending (31.0%). On this sample MSFT is **meanrev-leaning** on H1 history — with a material fragile/high-vol sleeve.

### Peer correlations (H1 ~30d)

| Peer | ρ |
| --- | ---: |
| NAS100 | +0.577 |
| AMZN | +0.513 |
| US500 | +0.504 |
| NVDA | +0.498 |
| AVGO | +0.327 |
| META | +0.321 |
| GOOGL | +0.312 |
| TSLA | +0.229 |
| AAPL | +0.219 |
| JPM | +0.040 |
| XOM | +0.020 |

Closest sleeves this window: NAS100 (+0.58), AMZN (+0.51), US500 (+0.50), NVDA (+0.50).

### Event sensitivities

Taxonomy present (NFP / CPI / FOMC) but **ATR multiples empty** — calendar hits scored for MSFT are below the ≥3-window gate. Honest gap until equity event windows are scored.

---

## Path

Monthly D1 path return over the window: **+26.5%** (open 416.05 → last close 526.48).

| Month | Ret % | Close |
| --- | ---: | ---: |
| 2024-10 | -2.32 | 406.40 |
| 2024-11 | +3.31 | 422.52 |
| 2024-12 | +0.05 | 421.71 |
| 2025-01 | -1.55 | 415.06 |
| 2025-02 | -3.57 | 397.01 |
| 2025-03 | -5.76 | 374.91 |
| 2025-04 | +5.00 | 393.22 |
| 2025-05 | +6.61 | 459.60 |
| 2025-06 | +8.63 | 496.99 |
| 2025-07 | +7.55 | 533.59 |
| 2025-08 | -5.38 | 506.39 |
| 2025-09 | +3.46 | 517.45 |
| 2025-10 | +0.59 | 517.64 |
| 2025-11 | -5.47 | 491.07 |
| 2025-12 | -0.31 | 486.20 |
| 2026-01 | -11.15 | 430.08 |
| 2026-02 | -8.68 | 392.61 |
| 2026-03 | -5.75 | 369.99 |
| 2026-04 | +9.22 | 407.51 |
| 2026-05 | +0.21 | 412.44 |
| 2026-07 | +19.94 | 464.58 |
| 2026-08 | +5.95 | 506.38 |
| 2026-09 | +2.64 | 512.41 |
| 2026-10 | +1.39 | 526.48 |

---

## Narrative pressure

- Sentiment score: **0.032** on [−1, +1] · 45 items · 24h window
- As-of: 2026-10-08 16:35:35.242914+00:00 · stale=True
- Mapped news articles: **272**
- Insight: _MSFT: trending up context_ — MSFT is currently classified as trending up with realized volatility near the 5th pct of its recent window. News sentiment over the last 24h is +0.03 on a [-1, +1] scale. This narrative summarizes deterministic analytics only and is not a trade signal.

Recent headlines:

- 2026-10-08 · Yahoo — 3 Unprofitable Stocks with Questionable Fundamentals
- 2026-10-08 · Yahoo — Jensen Huang: 'Nvidia was founded because of Windows'
- 2026-10-08 · Yahoo — Nvidia Stock Slips. A Big Options Trade Signals Where It Might Go Next.
- 2026-10-08 · Yahoo — Jeff Bezos Says He Usually Tells Retired Investors To Buy The Same Thing, And It’s Not Just AI Stocks
- 2026-10-08 · Yahoo — Application Virtualization Market to Reach US$10.9 Billion by 2032 at 16.3% CAGR, Driven by Remote Work and Hybrid Cloud
- 2026-10-08 · Yahoo — Dan Ives Names 5 Tech Stocks for 2027, Including One That Doubled in 2026
- 2026-10-08 · Yahoo — These 3 Catalysts Make Microsoft Stock a Bargain Before Year-End
- 2026-10-08 · Yahoo — MSFT Stock On 4-Day Winning Streak: Microsoft Takes On Apple's Macs With Nvidia-Powered Surface Ultra, More On-Device AI

---

## Provenance

- Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`
- Profile confidence: 0.99 · stale=False
- Sources: mt5.prices, metrics.v1, regimes.rule_v1
- Raw export: [`audit.json`](./audit.json) · monthly boards: [`regime-audit.md`](./regime-audit.md)

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
