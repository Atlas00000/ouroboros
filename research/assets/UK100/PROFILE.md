# UK100 — Asset profile dossier

> Research / advisory only · Ouroboros `profile.v1` + `regimes.rule_v1` + `fit.map_v0`  
> Generated `2026-10-12T00:05:39Z` · data `2025-12-17` → `2026-10-11` (11 calendar months, M1 depth ≈ 298d)

Canvas cover (open beside chat): [`uk100-asset-profile.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/uk100-asset-profile.canvas.tsx).

> **Depth note:** requested 2y monthly audit; YWO MT5 `UK100` index CFD only exposes M1/H1/D1 from `2025-12-17` (≈298d). Boards below cover available history.

---

## Identity

| Field | Value |
| --- | --- |
| Symbol | `UK100` |
| Display | UK 100 (FTSE) |
| Class | index |
| Quote | GBP |
| MT5 ticker | `UK100` |
| Sessions | new_york, london · `UTC` · UTC 13:30–20:00 |

Index cash hours approximate (US RTH for US500/US30/NAS100; London/Frankfurt/Tokyo cash for regional indices). Broker CFD session may trade nearly 24h — treat as research proxy.

---

## Two clocks

### Nowcast (H1 state)

| Metric | Value |
| --- | --- |
| Confirmed regime | **trending_up** |
| Vol percentile | 49.3 |
| Trend ER | 0.251 |
| Confidence | 0.712 |
| As-of | 2026-10-11 23:00:00+00:00 |
| Stale | False |

Soft probabilities (nowcast — may disagree with confirmed label when confidence is low):

| Regime | P |
| --- | ---: |
| trending_up | 71.2% |
| trending_down | 2.8% |
| ranging | 23.2% |
| high_volatility | 2.8% |

### Live fit gate (ex-post 30d H1 shares → dominant tag)

| Family | Tag | MATCH | MISMATCH | FRAGILE | Bars |
| --- | --- | ---: | ---: | ---: | ---: |
| `meanrev` | **FRAGILE** | 32.5% | 24.2% | 43.3% | 462 |
| `trendfollow` | **FRAGILE** | 24.2% | 32.5% | 43.3% | 462 |

Interpretation: last ~30d H1 mass is **ranging-contested** — meanrev=FRAGILE (32.5% MATCH / 24.2% MISMATCH), trendfollow=FRAGILE (24.2% MATCH). FRAGILE sleeve 43.3%.

---

## Character (`profile.v1`)

### Volatility & liquidity

| Field | Value |
| --- | --- |
| ATR pctile 30d | 43.3 |
| Realized vol pctile 30d | 36.7 |
| Typical daily range | 100.53 GBP |
| Range pctile 30d (liq proxy) | 3.3 |
| True spread | deferred |

_true bid/ask spread deferred until quote ingestion; range proxies (high-low) only_

### Regime distribution (history clock)

Confirmed-label share over the profile sample (H1 preferred when depth gate passes):

| Regime | Share |
| --- | ---: |
| trending_up | 13.2% |
| trending_down | 11.1% |
| ranging | 46.5% |
| high_volatility | 29.2% |

**Read:** ranging (46.5%) + high_volatility (29.2%) vs net trending (24.3%). On this sample UK100 is **meanrev-leaning** on H1 history — with a material fragile/high-vol sleeve.

### Peer correlations (H1 ~30d)

| Peer | ρ |
| --- | ---: |
| DE40 | +0.807 |
| US30 | +0.617 |
| US500 | +0.530 |
| NAS100 | +0.385 |
| JP225 | +0.325 |

Closest sleeves this window: DE40 (+0.81), US30 (+0.62), US500 (+0.53), NAS100 (+0.38).

### Event sensitivities

Taxonomy present (CPI / GDP / central_bank — BoE / UK prints) but **ATR multiples empty** — calendar hits scored for UK100 are below the ≥3-window gate. Honest gap until index event windows are scored.

---

## Path

Monthly D1 path return over the window: **+7.6%** (open 9834.35 → last close 10583.51).

| Month | Ret % | Close |
| --- | ---: | ---: |
| 2025-12 | +0.98 | 9930.35 |
| 2026-01 | +2.86 | 10222.60 |
| 2026-02 | +6.51 | 10868.00 |
| 2026-03 | -4.81 | 10293.38 |
| 2026-04 | +0.82 | 10366.73 |
| 2026-05 | -0.00 | 10370.33 |
| 2026-06 | +1.30 | 10511.58 |
| 2026-07 | +3.29 | 10850.52 |
| 2026-08 | -0.72 | 10818.54 |
| 2026-09 | -1.59 | 10597.03 |
| 2026-10 | +0.04 | 10583.51 |

---

## Narrative pressure

- Sentiment score: **0.160** on [−1, +1] · 1 items · 24h window
- As-of: 2026-10-09 12:03:38.495291+00:00 · stale=True
- Mapped news articles: **3**
- Insight: _UK100: trending down context_ — UK100 is currently classified as trending down with realized volatility near the 70th pct of its recent window. News sentiment over the last 24h is +0.16 on a [-1, +1] scale. This narrative summarizes deterministic analytics only and is not a trade signal.

Recent headlines:

- 2026-10-08 · Forexlive — Morning Kickstart: Stocks fall as oil and yields rise; USD edges higher
- 2026-10-08 · Yahoo — MARKETS LIVE: London shares retreat as Tesco bucks the decline
- 2026-10-07 · Yahoo — 2 Vanguard ETFs Outpacing the S&P 500 and Nasdaq-100 This Year but Facing Near-Term Tests

---

## Provenance

- Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`
- Profile confidence: 0.99 · stale=False
- Sources: mt5.prices, metrics.v1, regimes.rule_v1
- Raw export: [`audit.json`](./audit.json) · monthly boards: [`regime-audit.md`](./regime-audit.md)

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
