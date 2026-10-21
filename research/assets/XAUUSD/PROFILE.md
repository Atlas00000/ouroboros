# XAUUSD — Asset profile dossier

> Research / advisory only · Ouroboros `profile.v1` + `regimes.rule_v1` + `fit.map_v0`  
> Generated `2026-10-09T12:39:24Z` · data `2024-09-12` → `2026-10-06` (26 calendar months, M1 depth ≈ 756d)

Canvas cover (open beside chat): `canvases/xauusd-asset-profile.canvas.tsx` in the Cursor project.

---

## Identity

| Field | Value |
| --- | --- |
| Symbol | `XAUUSD` |
| Display | Gold / US Dollar |
| Class | metal |
| Quote | USD |
| MT5 ticker | `XAUUSD` |
| Sessions | sydney, tokyo, london, new_york · `UTC` · UTC 22:00–21:00 |

Metals/energy CFDs follow broker session (approx Sun 22:00–Fri 21:00 UTC); gap-aware metrics applied. Softs/inventory calendars deferred.

---

## Two clocks

### Nowcast (H1 state)

| Metric | Value |
| --- | --- |
| Confirmed regime | **trending_down** |
| Vol percentile | 17.2 |
| Trend ER | -0.561 |
| Confidence | 0.943 |
| As-of | 2026-10-07 15:00:00+00:00 |
| Stale | True |

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
| `meanrev` | **MATCH** | 55.8% | 27.7% | 16.4% | 274 |
| `trendfollow` | **MISMATCH** | 27.7% | 55.8% | 16.4% | 274 |

Interpretation: last ~30d H1 mass is **ranging-led** → meanrev **MATCH**, trendfollow **MISMATCH**. FRAGILE share ≈ 16%.

---

## Character (`profile.v1`)

### Volatility & liquidity

| Field | Value |
| --- | --- |
| ATR pctile 30d | 6.7 |
| Realized vol pctile 30d | 3.3 |
| Typical daily range | 71.33 USD |
| Range pctile 30d (liq proxy) | 50.0 |
| True spread | deferred |

_true bid/ask spread deferred until quote ingestion; range proxies (high-low) only_

### Regime distribution (history clock)

Confirmed-label share over the profile sample (H1 preferred when depth gate passes):

| Regime | Share |
| --- | ---: |
| trending_up | 19.0% |
| trending_down | 9.5% |
| ranging | 42.9% |
| high_volatility | 28.5% |

**Read:** ranging (43%) + high_volatility (29%) · net trending (up+down) ≈ 29%. This is a **meanrev-leaning** metal on H1 history — with a material fragile/high-vol sleeve.

### Peer correlations (H1 ~30d)

| Peer | ρ |
| --- | ---: |
| XAGUSD | +0.883 |
| XTIUSD | -0.367 |
| XBRUSD | -0.360 |

Strongest |ρ| peers: XAGUSD (+0.88), XTIUSD (-0.37), XBRUSD (-0.36). Notable negatives: XTIUSD (-0.37), XBRUSD (-0.36).

### Event sensitivities

Event move multiples: NFP: —; CPI: 1.58× ATR; FOMC: —.

---

## Path

Monthly D1 path return over the window: **+65.8%** (open 2513.17 → last close 4165.92).

| Month | Ret % | Close |
| --- | ---: | ---: |
| 2024-09 | +4.85 | 2634.94 |
| 2024-10 | +4.24 | 2746.65 |
| 2024-11 | -3.51 | 2650.33 |
| 2024-12 | -1.04 | 2624.43 |
| 2025-01 | +6.63 | 2798.47 |
| 2025-02 | +1.96 | 2859.06 |
| 2025-03 | +9.27 | 3122.80 |
| 2025-04 | +4.84 | 3273.97 |
| 2025-05 | +0.44 | 3288.72 |
| 2025-06 | +0.40 | 3311.45 |
| 2025-07 | -0.50 | 3295.00 |
| 2025-08 | +4.71 | 3450.27 |
| 2025-09 | +11.88 | 3860.07 |
| 2025-10 | +3.67 | 4002.14 |
| 2025-11 | +5.82 | 4221.93 |
| 2025-12 | +2.36 | 4321.16 |
| 2026-01 | +12.92 | 4883.02 |
| 2026-02 | +9.77 | 5280.15 |
| 2026-03 | -11.04 | 4696.36 |
| 2026-04 | -1.49 | 4626.55 |
| 2026-05 | -1.88 | 4539.70 |
| 2026-06 | -11.76 | 4005.66 |
| 2026-07 | +1.05 | 4047.75 |
| 2026-08 | +9.07 | 4452.32 |
| 2026-09 | -6.65 | 4156.02 |
| 2026-10 | +0.24 | 4165.92 |

---

## Narrative pressure

- Sentiment score: **-0.043** on [−1, +1] · 7 items · 24h window
- As-of: 2026-10-09 12:33:38.491239+00:00 · stale=True
- Mapped news articles: **65**
- Insight: _XAUUSD: trending down context_ — XAUUSD is currently classified as trending down with realized volatility near the 17th pct of its recent window. News sentiment over the last 24h is -0.02 on a [-1, +1] scale. This narrative summarizes deterministic analytics only and is not a trade signal.

Recent headlines:

- 2026-10-09 · forexfactory.calendar — FOMC Member Collins Speaks
- 2026-10-09 · forexfactory.calendar — Prelim UoM Inflation Expectations
- 2026-10-09 · forexfactory.calendar — Prelim UoM Consumer Sentiment
- 2026-10-08 · forexfactory.calendar — FOMC Member Musalem Speaks
- 2026-10-08 · forexfactory.calendar — 30-y Bond Auction
- 2026-10-08 · forexfactory.calendar — Natural Gas Storage
- 2026-10-08 · forexfactory.calendar — Final Wholesale Inventories m/m
- 2026-10-08 · forexfactory.calendar — Unemployment Claims

---

## Provenance

- Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`
- Profile confidence: 0.99 · stale=False
- Sources: mt5.prices, metrics.v1, regimes.rule_v1
- Raw export: [`audit.json`](./audit.json) · monthly boards: [`regime-audit.md`](./regime-audit.md)

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
