# XBRUSD — Asset profile dossier

> Research / advisory only · Ouroboros `profile.v1` + `regimes.rule_v1` + `fit.map_v0`  
> Generated `2026-10-12T00:01:11Z` · data `2024-10-07` → `2026-10-07` (25 calendar months, M1 depth ≈ 730d)

Canvas cover (open beside chat): `canvases/xbrusd-asset-profile.canvas.tsx` in the Cursor project.

---

## Identity

| Field | Value |
| --- | --- |
| Symbol | `XBRUSD` |
| Display | Brent Crude Oil |
| Class | metal |
| Quote | USD |
| MT5 ticker | `BRENT` |
| Sessions | sydney, tokyo, london, new_york · `UTC` · UTC 22:00–21:00 |

Metals/energy CFDs follow broker session (approx Sun 22:00–Fri 21:00 UTC); gap-aware metrics applied. Softs/inventory calendars deferred.

---

## Two clocks

### Nowcast (H1 state)

| Metric | Value |
| --- | --- |
| Confirmed regime | **trending_up** |
| Vol percentile | 10.0 |
| Trend ER | 0.369 |
| Confidence | 0.937 |
| As-of | 2026-10-07 14:00:00+00:00 |
| Stale | False |

Soft probabilities (nowcast — may disagree with confirmed label when confidence is low):

| Regime | P |
| --- | ---: |
| trending_up | 93.7% |
| trending_down | 2.1% |
| ranging | 2.1% |
| high_volatility | 2.1% |

### Live fit gate (ex-post 30d H1 shares → dominant tag)

| Family | Tag | MATCH | MISMATCH | FRAGILE | Bars |
| --- | --- | ---: | ---: | ---: | ---: |
| `meanrev` | **MATCH** | 43.5% | 25.1% | 31.5% | 467 |
| `trendfollow` | **MISMATCH** | 25.1% | 43.5% | 31.5% | 467 |

Interpretation: last ~30d H1 mass is **ranging-led** → meanrev **MATCH**, trendfollow **MISMATCH**. FRAGILE share ≈ 31%.

---

## Character (`profile.v1`)

### Volatility & liquidity

| Field | Value |
| --- | --- |
| ATR pctile 30d | 66.7 |
| Realized vol pctile 30d | 23.3 |
| Typical daily range | 3.55 USD |
| Range pctile 30d (liq proxy) | 20.0 |
| True spread | deferred |

_true bid/ask spread deferred until quote ingestion; range proxies (high-low) only_

### Regime distribution (history clock)

Confirmed-label share over the profile sample (H1 preferred when depth gate passes):

| Regime | Share |
| --- | ---: |
| trending_up | 17.3% |
| trending_down | 12.2% |
| ranging | 43.4% |
| high_volatility | 27.1% |

**Read:** ranging (43%) + high_volatility (27%) · net trending (up+down) ≈ 30%. This is a **meanrev-leaning** energy CFD on H1 history — with a material fragile/high-vol sleeve. (Universe seed class is `metal` for session defaults; desk voice treats XBRUSD as Brent energy.)

### Peer correlations (H1 ~30d)

| Peer | ρ |
| --- | ---: |
| XTIUSD | +0.957 |
| XAUUSD | -0.385 |
| XAGUSD | -0.337 |

Strongest |ρ| peers: XTIUSD (+0.96), XAUUSD (-0.38), XAGUSD (-0.34). Notable negatives: XAUUSD (-0.38), XAGUSD (-0.34).

### Event sensitivities

Taxonomy present (NFP / CPI / FOMC / GDP) but **ATR multiples empty** — calendar hits scored below the ≥3-window gate. Honest gap until event windows are scored.

---

## Path

Monthly D1 path return over the window: **+27.4%** (open 78.66 → last close 100.19).

| Month | Ret % | Close |
| --- | ---: | ---: |
| 2024-10 | -6.06 | 73.89 |
| 2024-11 | -1.69 | 72.75 |
| 2024-12 | +3.61 | 75.00 |
| 2025-01 | +1.99 | 76.79 |
| 2025-02 | -4.19 | 73.54 |
| 2025-03 | +1.88 | 75.23 |
| 2025-04 | -17.75 | 61.82 |
| 2025-05 | +2.11 | 63.34 |
| 2025-06 | +5.23 | 67.82 |
| 2025-07 | +7.03 | 72.48 |
| 2025-08 | -6.28 | 68.01 |
| 2025-09 | -1.77 | 66.75 |
| 2025-10 | -2.13 | 65.31 |
| 2025-11 | -2.57 | 63.95 |
| 2025-12 | -3.49 | 61.37 |
| 2026-01 | +13.76 | 69.60 |
| 2026-02 | +8.05 | 73.03 |
| 2026-03 | +36.88 | 106.63 |
| 2026-04 | +9.28 | 116.83 |
| 2026-05 | -18.37 | 95.21 |
| 2026-06 | -22.94 | 73.37 |
| 2026-07 | +21.66 | 89.31 |
| 2026-08 | +10.07 | 90.09 |
| 2026-09 | +8.01 | 97.41 |
| 2026-10 | +3.18 | 100.19 |

---

## Narrative pressure

- Sentiment score: **0.160** on [−1, +1] · 1 items · 24h window
- As-of: 2026-10-09 12:03:38.495291+00:00 · stale=True
- Mapped news articles: **83**
- Insight: _XBRUSD: trending up context_ — XBRUSD is currently classified as trending up with realized volatility near the 10th pct of its recent window. News sentiment over the last 24h is +0.16 on a [-1, +1] scale. This narrative summarizes deterministic analytics only and is not a trade signal.

Recent headlines:

- 2026-10-08 · Forexlive — Morning Kickstart: Stocks fall as oil and yields rise; USD edges higher
- 2026-10-08 · Yahoo — Dow Jones Futures Fall As Oil Prices, Treasury Yields Jump; Samsung, Micron, Taiwan Semi, Sandisk In Focus
- 2026-10-08 · Yahoo — Oil Is Already at $100. Now a Hurricane Could Shut Down Gulf Production
- 2026-10-08 · Yahoo — JPMorgan sees strong Q3 for EU oil and gas, favors these major stocks
- 2026-10-08 · Reuters — COMMENTARY: Battle for Mideast oil market share has already begun - Reuters
- 2026-10-08 · Reuters — Oil jumps as Middle East supply concerns persist amid shipping attacks - Reuters
- 2026-10-07 · Reuters — Oil price volatility tops list of earnings risks for Japan firms: Reuters poll - Reuters
- 2026-10-07 · Yahoo — Stock Market Falls After Hitting Record Highs. What Changed Overnight?

---

## Provenance

- Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`
- Profile confidence: 0.99 · stale=False
- Sources: mt5.prices, metrics.v1, regimes.rule_v1
- Raw export: [`audit.json`](./audit.json) · monthly boards: [`regime-audit.md`](./regime-audit.md)

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
