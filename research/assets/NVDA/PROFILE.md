# NVDA — Asset profile dossier

> Research / advisory only · Ouroboros `profile.v1` + `regimes.rule_v1` + `fit.map_v0`  
> Generated `2026-10-19T00:01:40Z` · data `2026-01-14` → `2026-10-16` (10 calendar months, M1 depth ≈ 275d)

Canvas cover (open beside chat): [`nvda-asset-profile.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/nvda-asset-profile.canvas.tsx).

> **Depth note:** requested 2y monthly audit; YWO MT5 `NVDA` CFD only exposes usable M1/H1/D1 from `2026-01-14` (≈275d). Boards below cover available history.

---

## Identity

| Field | Value |
| --- | --- |
| Symbol | `NVDA` |
| Display | NVIDIA Corporation |
| Class | equity |
| Quote | USD |
| MT5 ticker | `NVDA` |
| Sessions | new_york · `America/New_York` · UTC 13:30–20:00 |

US cash RTH approx 09:30–16:00 America/New_York (13:30–20:00 UTC during EST; 14:30–21:00 UTC during EDT). Broker CFD hours may extend; DST shifts open/close UTC.

---

## Two clocks

### Nowcast (H1 state)

| Metric | Value |
| --- | --- |
| Confirmed regime | **trending_down** |
| Vol percentile | 54.7 |
| Trend ER | -0.414 |
| Confidence | 0.943 |
| As-of | 2026-10-16 19:00:00+00:00 |
| Stale | False |

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
| `meanrev` | **MISMATCH** | 35.5% | 64.5% | 0.0% | 155 |
| `trendfollow` | **MATCH** | 64.5% | 35.5% | 0.0% | 155 |

Interpretation: last ~30d H1 mass is **trend-led** — meanrev=MISMATCH (35.5% MATCH / 64.5% MISMATCH), trendfollow=MATCH (64.5% MATCH). FRAGILE sleeve 0.0%.

---

## Character (`profile.v1`)

### Volatility & liquidity

| Field | Value |
| --- | --- |
| ATR pctile 30d | 43.3 |
| Realized vol pctile 30d | 16.7 |
| Typical daily range | 4.78 USD |
| Range pctile 30d (liq proxy) | 76.7 |
| True spread | deferred |

_true bid/ask spread deferred until quote ingestion; range proxies (high-low) only_

### Regime distribution (history clock)

Confirmed-label share over the profile sample (H1 preferred when depth gate passes):

| Regime | Share |
| --- | ---: |
| trending_up | 20.6% |
| trending_down | 21.1% |
| ranging | 37.1% |
| high_volatility | 21.2% |

**Read:** ranging (37.1%) + high_volatility (21.2%) vs net trending (41.7%; up 20.6% / down 21.1%). On this sample NVDA is **trend-leaning** on H1 history — with roughly balanced up/down trend sleeves and a material fragile/high-vol share.

### Peer correlations (H1 ~30d)

| Peer | ρ |
| --- | ---: |
| NAS100 | +0.736 |
| AVGO | +0.624 |
| MSFT | +0.494 |
| TSLA | +0.326 |
| AAPL | +0.323 |
| AMZN | +0.305 |
| GOOGL | +0.196 |
| US500 | +0.157 |
| JPM | +0.136 |
| META | +0.105 |
| XOM | +0.009 |

Closest sleeves this window: NAS100 (+0.74), AVGO (+0.62), MSFT (+0.49), TSLA (+0.33). No meaningful negative sleeve in this peer set.

### Event sensitivities

Taxonomy present (NFP / CPI / FOMC) but **ATR multiples empty** — calendar hits scored for NVDA are below the ≥3-window gate. Honest gap until equity event windows are scored.

---

## Path

Monthly D1 path return over the window: **+17.7%** (open 181.85 → last close 213.96).

| Month | Ret % | Close |
| --- | ---: | ---: |
| 2026-01 | +5.05 | 191.04 |
| 2026-02 | -5.45 | 177.27 |
| 2026-03 | -0.95 | 174.43 |
| 2026-04 | +14.05 | 199.47 |
| 2026-05 | +5.20 | 211.44 |
| 2026-06 | -7.81 | 199.83 |
| 2026-07 | +3.15 | 200.89 |
| 2026-08 | +11.30 | 220.78 |
| 2026-09 | +5.47 | 228.42 |
| 2026-10 | -6.63 | 213.96 |

---

## Narrative pressure

- Sentiment score: **-0.060** on [−1, +1] · 1 items · 24h window
- As-of: 2026-10-09 11:48:38.496883+00:00 · stale=True
- Mapped news articles: **364**
- Insight: _NVDA: ranging context_ — NVDA is currently classified as ranging with realized volatility near the 11th pct of its recent window. News sentiment over the last 24h is -0.06 on a [-1, +1] scale. This narrative summarizes deterministic analytics only and is not a trade signal.

Recent headlines:

- 2026-10-08 · Yahoo — Elon Musk Just Shared Bad News for Intel Shareholders
- 2026-10-08 · Yahoo — TSMC Q3 2026 revenue hits record on AI chip demand
- 2026-10-08 · Yahoo — $10,000 in 10-Year Treasuries vs. $10,000 in SCHD -- Which Pays More Passive Income By 2036?
- 2026-10-08 · Yahoo — Prediction: These 2 Stocks Will Be Worth More Than Palantir 5 Years From Now
- 2026-10-08 · Yahoo — Not SpaceX. Not Blue Origin. The Space Titan That Morgan Stanley Calls an Undervalued Launch Play.
- 2026-10-08 · Yahoo — Jensen Huang: 'Nvidia was founded because of Windows'
- 2026-10-08 · Yahoo — Dell Turned $1,000 Into $11,641 in Five Years as AI Servers Crushed the S&P 500
- 2026-10-08 · Yahoo — 1 Reason Nvidia Is a Screaming Buy in October, and 1 Reason Investors Should Be Cautious

---

## Provenance

- Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`
- Profile confidence: 0.99 · stale=False
- Sources: mt5.prices, metrics.v1, regimes.rule_v1
- Raw export: [`audit.json`](./audit.json) · monthly boards: [`regime-audit.md`](./regime-audit.md)

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
