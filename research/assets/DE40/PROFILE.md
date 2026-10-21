# DE40 — Asset profile dossier

> Research / advisory only · Ouroboros `profile.v1` + `regimes.rule_v1` + `fit.map_v0`  
> Generated `2026-10-18T23:48:31Z` · data `2025-06-05` → `2026-10-07` (17 calendar months, M1 depth ≈ 489d)

Canvas cover (open beside chat): [`de40-asset-profile.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/de40-asset-profile.canvas.tsx).

> **Depth note:** requested 2y monthly audit; YWO MT5 `DE40` / `DE30` index CFD only exposes M1/H1/D1 from `2025-06-05` (≈489d). Boards below cover available history.

---

## Identity

| Field | Value |
| --- | --- |
| Symbol | `DE40` |
| Display | Germany 40 (DAX) |
| Class | index |
| Quote | EUR |
| MT5 ticker | `DE30` |
| Sessions | new_york, london · `UTC` · UTC 13:30–20:00 |

Index cash hours approximate (US RTH for US500/US30/NAS100; London/Frankfurt/Tokyo cash for regional indices). Broker CFD session may trade nearly 24h — treat as research proxy.

---

## Two clocks

### Nowcast (H1 state)

| Metric | Value |
| --- | --- |
| Confirmed regime | **high_volatility** |
| Vol percentile | 77.6 |
| Trend ER | -0.496 |
| Confidence | 0.608 |
| As-of | 2026-10-07 14:00:00+00:00 |
| Stale | False |

Soft probabilities (nowcast — may disagree with confirmed label when confidence is low):

| Regime | P |
| --- | ---: |
| trending_up | 1.9% |
| trending_down | 35.4% |
| ranging | 1.9% |
| high_volatility | 60.8% |

### Live fit gate (ex-post 30d H1 shares → dominant tag)

| Family | Tag | MATCH | MISMATCH | FRAGILE | Bars |
| --- | --- | ---: | ---: | ---: | ---: |
| `meanrev` | **FRAGILE** | 25.6% | 19.0% | 55.4% | 504 |
| `trendfollow` | **FRAGILE** | 19.0% | 25.6% | 55.4% | 504 |

Interpretation: last ~30d H1 mass is **ranging-contested** — meanrev=FRAGILE (25.6% MATCH / 19.0% MISMATCH), trendfollow=FRAGILE (19.0% MATCH). FRAGILE sleeve 55.4%.

---

## Character (`profile.v1`)

### Volatility & liquidity

| Field | Value |
| --- | --- |
| ATR pctile 30d | 86.7 |
| Realized vol pctile 30d | 83.3 |
| Typical daily range | 289.63 EUR |
| Range pctile 30d (liq proxy) | 73.3 |
| True spread | deferred |

_true bid/ask spread deferred until quote ingestion; range proxies (high-low) only_

### Regime distribution (history clock)

Confirmed-label share over the profile sample (H1 preferred when depth gate passes):

| Regime | Share |
| --- | ---: |
| trending_up | 18.4% |
| trending_down | 12.1% |
| ranging | 43.7% |
| high_volatility | 25.7% |

**Read:** ranging (43.7%) + high_volatility (25.7%) vs net trending (30.5%). On this sample DE40 is **meanrev-leaning** on H1 history — with a material fragile/high-vol sleeve.

### Peer correlations (H1 ~30d)

| Peer | ρ |
| --- | ---: |
| UK100 | +0.807 |
| US30 | +0.637 |
| US500 | +0.630 |
| NAS100 | +0.531 |
| JP225 | +0.437 |

Closest sleeves this window: UK100 (+0.81), US30 (+0.64), US500 (+0.63), NAS100 (+0.53).

### Event sensitivities

Taxonomy present (CPI / GDP / central_bank — ECB / DE / EZ prints) but **ATR multiples empty** — calendar hits scored for DE40 are below the ≥3-window gate. Honest gap until index event windows are scored.

---

## Path

Monthly D1 path return over the window: **+2.7%** (open 24405.40 → last close 25058.10).

| Month | Ret % | Close |
| --- | ---: | ---: |
| 2025-06 | -1.89 | 23944.15 |
| 2025-07 | +0.13 | 23982.35 |
| 2025-08 | +0.05 | 23997.25 |
| 2025-09 | -0.38 | 23916.65 |
| 2025-10 | +0.27 | 23982.45 |
| 2025-11 | -0.60 | 23845.75 |
| 2025-12 | +3.04 | 24571.74 |
| 2026-01 | +0.02 | 24468.30 |
| 2026-02 | +3.12 | 25129.76 |
| 2026-03 | -7.54 | 23083.15 |
| 2026-04 | +5.28 | 24301.43 |
| 2026-05 | +2.91 | 25090.02 |
| 2026-06 | -0.37 | 25000.72 |
| 2026-07 | +2.57 | 25643.04 |
| 2026-08 | +1.36 | 26209.91 |
| 2026-09 | -3.88 | 25162.66 |
| 2026-10 | -0.45 | 25058.10 |

---

## Narrative pressure

- Sentiment score: **0.160** on [−1, +1] · 1 items · 24h window
- As-of: 2026-10-09 12:03:38.495291+00:00 · stale=True
- Mapped news articles: **1**
- Insight: _DE40: high volatility context_ — DE40 is currently classified as high volatility with realized volatility near the 78th pct of its recent window. News sentiment over the last 24h is +0.16 on a [-1, +1] scale. This narrative summarizes deterministic analytics only and is not a trade signal.

Recent headlines:

- 2026-10-08 · Forexlive — Morning Kickstart: Stocks fall as oil and yields rise; USD edges higher

---

## Provenance

- Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`
- Profile confidence: 0.99 · stale=False
- Sources: mt5.prices, metrics.v1, regimes.rule_v1
- Raw export: [`audit.json`](./audit.json) · monthly boards: [`regime-audit.md`](./regime-audit.md)

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
