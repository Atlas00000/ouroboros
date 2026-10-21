# AAPL — Asset profile dossier

> Research / advisory only · Ouroboros `profile.v1` + `regimes.rule_v1` + `fit.map_v0`  
> Generated `2026-10-08T14:31:33Z` · data `2024-10-07` → `2026-10-07` (25 calendar months, M1 depth ≈ 730d)

Canvas cover (open beside chat): `canvases/aapl-asset-profile.canvas.tsx` in the Cursor project.

---

## Identity

| Field | Value |
| --- | --- |
| Symbol | `AAPL` |
| Display | Apple Inc. |
| Class | equity |
| Quote | USD |
| MT5 ticker | `Apple` |
| Sessions | new_york · `America/New_York` · UTC 13:30–20:00 |

US cash RTH approx 09:30–16:00 America/New_York (13:30–20:00 UTC during EST; 14:30–21:00 UTC during EDT). Broker CFD hours may extend; DST shifts open/close UTC.

---

## Two clocks

### Nowcast (H1 state)

| Metric | Value |
| --- | --- |
| Confirmed regime | **ranging** |
| Vol percentile | 6.3 |
| Trend ER | 0.252 |
| Confidence | 0.228 |
| As-of | 2026-10-07 14:00:00+00:00 |
| Stale | True |

Soft probabilities (nowcast — may disagree with confirmed label when confidence is low):

| Regime | P |
| --- | ---: |
| trending_up | 71.5% |
| trending_down | 2.8% |
| ranging | 22.8% |
| high_volatility | 2.8% |

### Live fit gate (ex-post 30d H1 shares → dominant tag)

| Family | Tag | MATCH | MISMATCH | FRAGILE | Bars |
| --- | --- | ---: | ---: | ---: | ---: |
| `meanrev` | **MATCH** | 59.1% | 14.8% | 26.2% | 149 |
| `trendfollow` | **MISMATCH** | 14.8% | 59.1% | 26.2% | 149 |

Interpretation: last ~30d H1 mass is **ranging-led** → mean-reversion research gate ON (MATCH), trend-follow OFF (MISMATCH). High-vol share still ~26% → FRAGILE weight is material.

---

## Character (`profile.v1`)

### Volatility & liquidity

| Field | Value |
| --- | --- |
| ATR pctile 30d | 3.3 |
| Realized vol pctile 30d | 23.3 |
| Typical daily range | 5.99 USD |
| Range pctile 30d (liq proxy) | 36.7 |
| True spread | deferred |

_true bid/ask spread deferred until quote ingestion; range proxies (high-low) only_

### Regime distribution (history clock)

Confirmed-label share over the profile sample (H1 preferred when depth gate passes):

| Regime | Share |
| --- | ---: |
| trending_up | 19.6% |
| trending_down | 11.0% |
| ranging | 37.9% |
| high_volatility | 31.5% |

**Read:** ranging (~38%) + high_volatility (~32%) dominate the 2y character. Net trending (up+down) ≈ 31%. This is a **meanrev-leaning** equity on H1 history — with a large fragile/high-vol sleeve.

### Peer correlations (H1 ~30d)

| Peer | ρ |
| --- | ---: |
| US500 | +0.303 |
| NAS100 | +0.297 |
| GOOGL | +0.232 |
| NVDA | +0.221 |
| AMZN | +0.215 |
| AVGO | +0.206 |
| XOM | -0.199 |
| MSFT | +0.170 |
| TSLA | +0.098 |
| META | +0.063 |
| JPM | +0.055 |

Beta-to-index is mild (~0.30 vs US500/NAS100). Closest single-name peers in this window: GOOGL / NVDA / AMZN / AVGO. XOM is the only notable negative sleeve (~−0.20).

### Event sensitivities

Taxonomy present (NFP / CPI / FOMC) but **ATR multiples empty** — calendar hits scored for AAPL are below the ≥3-window gate. Honest gap until equity event windows are scored.

---

## Path

Monthly D1 path return over the window: **+49.6%** (open 224.37 → last close 335.64).

| Month | Ret % | Close |
| --- | ---: | ---: |
| 2024-10 | +0.60 | 225.71 |
| 2024-11 | +7.58 | 237.31 |
| 2024-12 | +5.53 | 250.36 |
| 2025-01 | -5.79 | 235.87 |
| 2025-02 | +5.05 | 241.60 |
| 2025-03 | -8.20 | 221.91 |
| 2025-04 | -3.32 | 212.37 |
| 2025-05 | -3.94 | 200.65 |
| 2025-06 | +2.38 | 204.94 |
| 2025-07 | +0.56 | 207.68 |
| 2025-08 | +10.19 | 232.13 |
| 2025-09 | +11.04 | 254.41 |
| 2025-10 | +6.00 | 270.09 |
| 2025-11 | +3.13 | 278.67 |
| 2025-12 | -1.57 | 273.22 |
| 2026-01 | -4.90 | 258.59 |
| 2026-02 | +1.67 | 264.01 |
| 2026-03 | -3.28 | 253.67 |
| 2026-04 | +6.71 | 271.02 |
| 2026-05 | +11.98 | 311.88 |
| 2026-06 | -6.61 | 288.85 |
| 2026-07 | +6.82 | 309.99 |
| 2026-08 | +1.90 | 316.76 |
| 2026-09 | +5.32 | 333.20 |
| 2026-10 | +1.82 | 335.64 |

---

## Narrative pressure

- Sentiment score: **-0.012** on [−1, +1] · 31 items · 24h window
- As-of: 2026-10-08 14:20:35.241896+00:00 · stale=True
- Mapped news articles: **252**
- Insight: _AAPL: ranging context_ — AAPL is currently classified as ranging with realized volatility near the 6th pct of its recent window. News sentiment over the last 24h is -0.03 on a [-1, +1] scale. This narrative summarizes deterministic analytics only and is not a trade signal.

Recent headlines:

- 2026-10-08 · Yahoo — Dow Jones Futures Fall As Oil Prices, Treasury Yields Jump; Samsung, Micron, Taiwan Semi, Sandisk In Focus
- 2026-10-08 · Yahoo — TSMC Q3 2026 revenue hits record on AI chip demand
- 2026-10-08 · Yahoo — Meta Stock Falls as Florida Asks a Court to Switch Off Infinite Scroll for Teens
- 2026-10-08 · Yahoo — Meta Muse, Grok Bot, OpenAI Dots: Which AI agent should you use?
- 2026-10-08 · Yahoo — Warren Buffett's Biggest Mistake Has Now Cost Berkshire Hathaway Up to $112 Billion (but I Don't Blame Him)
- 2026-10-08 · Yahoo — If You Had Invested $10,000 in Apple Stock 10 Years Ago, Here's How Much You'd Have Today
- 2026-10-08 · Yahoo — OneKey Launches OneKey Pro 2: First Hardware Wallet With Portfolio View
- 2026-10-08 · Yahoo — Dan Ives Names 5 Tech Stocks for 2027, Including One That Doubled in 2026

---

## Provenance

- Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`
- Profile confidence: 0.99 · stale=False
- Sources: mt5.prices, metrics.v1, regimes.rule_v1
- Raw export: [`audit.json`](./audit.json) · monthly boards: [`regime-audit.md`](./regime-audit.md)

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
