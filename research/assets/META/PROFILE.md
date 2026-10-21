# META — Asset profile dossier

> Research / advisory only · Ouroboros `profile.v1` + `regimes.rule_v1` + `fit.map_v0`  
> Generated `2026-10-11T23:59:47Z` · data `2026-07-06` → `2026-10-09` (4 calendar months, M1 depth ≈ 95d)

Canvas cover (open beside chat): [`meta-asset-profile.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/meta-asset-profile.canvas.tsx).

> **Depth note:** requested 2y monthly audit; YWO MT5 `Meta` CFD only exposes M1/H1/D1 from `2026-07-06` (≈95d). Boards below cover available history.

---

## Identity

| Field | Value |
| --- | --- |
| Symbol | `META` |
| Display | Meta Platforms Inc. |
| Class | equity |
| Quote | USD |
| MT5 ticker | `Meta` |
| Sessions | new_york · `America/New_York` · UTC 13:30–20:00 |

US cash RTH approx 09:30–16:00 America/New_York (13:30–20:00 UTC during EST; 14:30–21:00 UTC during EDT). Broker CFD hours may extend; DST shifts open/close UTC.

---

## Two clocks

### Nowcast (H1 state)

| Metric | Value |
| --- | --- |
| Confirmed regime | **trending_down** |
| Vol percentile | 6.9 |
| Trend ER | -0.125 |
| Confidence | 0.116 |
| As-of | 2026-10-09 19:00:00+00:00 |
| Stale | False |

Soft probabilities (nowcast — may disagree with confirmed label when confidence is low):

| Regime | P |
| --- | ---: |
| trending_up | 2.8% |
| trending_down | 11.6% |
| ranging | 82.7% |
| high_volatility | 2.8% |

### Live fit gate (ex-post 30d H1 shares → dominant tag)

| Family | Tag | MATCH | MISMATCH | FRAGILE | Bars |
| --- | --- | ---: | ---: | ---: | ---: |
| `meanrev` | **MATCH** | 43.9% | 38.1% | 18.1% | 155 |
| `trendfollow` | **MISMATCH** | 38.1% | 43.9% | 18.1% | 155 |

Interpretation: last ~30d H1 mass is **ranging-contested** — meanrev=MATCH (43.9% MATCH / 38.1% MISMATCH), trendfollow=MISMATCH (38.1% MATCH). FRAGILE sleeve 18.1%.

---

## Character (`profile.v1`)

### Volatility & liquidity

| Field | Value |
| --- | --- |
| ATR pctile 30d | 53.3 |
| Realized vol pctile 30d | 73.3 |
| Typical daily range | 21.82 USD |
| Range pctile 30d (liq proxy) | 10.0 |
| True spread | deferred |

_true bid/ask spread deferred until quote ingestion; range proxies (high-low) only_

### Regime distribution (history clock)

Confirmed-label share over the profile sample (H1 preferred when depth gate passes):

| Regime | Share |
| --- | ---: |
| trending_up | 25.3% |
| trending_down | 14.7% |
| ranging | 47.2% |
| high_volatility | 12.8% |

**Read:** ranging (47.2%) + high_volatility (12.8%) vs net trending (40.0%). On this sample META is **meanrev-leaning** on H1 history — with a material fragile/high-vol sleeve.

### Peer correlations (H1 ~30d)

| Peer | ρ |
| --- | ---: |
| US500 | +0.460 |
| NAS100 | +0.440 |
| GOOGL | +0.358 |
| MSFT | +0.321 |
| AMZN | +0.318 |
| AVGO | +0.258 |
| NVDA | +0.199 |
| TSLA | +0.185 |
| AAPL | +0.145 |
| JPM | +0.100 |
| XOM | +0.014 |

Closest sleeves this window: US500 (+0.46), NAS100 (+0.44), GOOGL (+0.36), MSFT (+0.32).

### Event sensitivities

Taxonomy present (NFP / CPI / FOMC) but **ATR multiples empty** — calendar hits scored for META are below the ≥3-window gate. Honest gap until equity event windows are scored.

---

## Path

Monthly D1 path return over the window: **+21.1%** (open 593.04 → last close 718.11).

| Month | Ret % | Close |
| --- | ---: | ---: |
| 2026-07 | -6.26 | 555.89 |
| 2026-08 | +1.53 | 571.31 |
| 2026-09 | +29.78 | 725.30 |
| 2026-10 | -1.75 | 718.11 |

---

## Narrative pressure

- Sentiment score: **0.160** on [−1, +1] · 1 items · 24h window
- As-of: 2026-10-09 12:03:38.495291+00:00 · stale=True
- Mapped news articles: **277**
- Insight: _META: ranging context_ — META is currently classified as ranging with realized volatility near the 1th pct of its recent window. News sentiment over the last 24h is +0.16 on a [-1, +1] scale. This narrative summarizes deterministic analytics only and is not a trade signal.

Recent headlines:

- 2026-10-08 · Forexlive — Morning Kickstart: Stocks fall as oil and yields rise; USD edges higher
- 2026-10-08 · Yahoo — Meta Stock Falls as Florida Asks a Court to Switch Off Infinite Scroll for Teens
- 2026-10-08 · Yahoo — Meta Muse, Grok Bot, OpenAI Dots: Which AI agent should you use?
- 2026-10-08 · Yahoo — Meta's Muse Reached More Than Half of Customers Cequence Studied in Two Weeks Without Identifying Itself as an AI Agent
- 2026-10-08 · Yahoo — Meta Critical Minerals Initiates Maiden Drill Program At Table Mountain High-Purity Silica Project, British Columbia
- 2026-10-08 · Yahoo — AI startup Manus raises $500m after Meta acquisition blocked by China
- 2026-10-08 · Yahoo — AMD (AMD) Stock May Be Fully Valued On Citi's $800 Target
- 2026-10-08 · Yahoo — Meta Platforms (META) Commits $300 Million To Biohub And Backs Indiana Solar

---

## Provenance

- Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`
- Profile confidence: 0.99 · stale=False
- Sources: mt5.prices, metrics.v1, regimes.rule_v1
- Raw export: [`audit.json`](./audit.json) · monthly boards: [`regime-audit.md`](./regime-audit.md)

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
