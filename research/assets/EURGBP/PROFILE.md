# EURGBP — Asset profile dossier

> Research / advisory only · Ouroboros `profile.v1` + `regimes.rule_v1` + `fit.map_v0`  
> Generated `2026-10-11T23:42:51Z` · data `2024-09-12` → `2026-09-11` (25 calendar months, M1 depth ≈ 730d)

Canvas cover (open beside chat): `canvases/eurgbp-asset-profile.canvas.tsx` in the Cursor project.

---

## Identity

| Field | Value |
| --- | --- |
| Symbol | `EURGBP` |
| Display | Euro / British Pound |
| Class | fx |
| Quote | GBP |
| MT5 ticker | `EURGBP` |
| Sessions | sydney, tokyo, london, new_york · `UTC` · UTC 22:00–22:00 |

FX approx Sun 22:00–Fri 22:00 UTC; session names from calendar module.

---

## Two clocks

### Nowcast (H1 state)

| Metric | Value |
| --- | --- |
| Confirmed regime | **trending_down** |
| Vol percentile | 70.8 |
| Trend ER | -0.467 |
| Confidence | 0.681 |
| As-of | 2026-09-11 20:00:00+00:00 |
| Stale | True |

Soft probabilities (nowcast — may disagree with confirmed label when confidence is low):

| Regime | P |
| --- | ---: |
| trending_up | 1.9% |
| trending_down | 68.1% |
| ranging | 1.9% |
| high_volatility | 28.0% |

### Live fit gate (ex-post 30d H1 shares → dominant tag)

| Family | Tag | MATCH | MISMATCH | FRAGILE | Bars |
| --- | --- | ---: | ---: | ---: | ---: |
| `meanrev` | **MATCH** | 59.7% | 26.5% | 13.8% | 529 |
| `trendfollow` | **MISMATCH** | 26.5% | 59.7% | 13.8% | 529 |

Interpretation: last ~30d H1 mass is **ranging-led** → meanrev **MATCH**, trendfollow **MISMATCH**. FRAGILE share ≈ 14%.

---

## Character (`profile.v1`)

### Volatility & liquidity

| Field | Value |
| --- | --- |
| ATR pctile 30d | 50.0 |
| Realized vol pctile 30d | 16.7 |
| Typical daily range | 0.00212 GBP |
| Range pctile 30d (liq proxy) | 86.7 |
| True spread | deferred |

_true bid/ask spread deferred until quote ingestion; range proxies (high-low) only_

### Regime distribution (history clock)

Confirmed-label share over the profile sample (H1 preferred when depth gate passes):

| Regime | Share |
| --- | ---: |
| trending_up | 9.6% |
| trending_down | 14.2% |
| ranging | 51.1% |
| high_volatility | 25.1% |

**Read:** ranging (51%) + high_volatility (25%) · net trending (up+down) ≈ 24%. This is a **meanrev-leaning** FX cross on H1 history — with a material fragile/high-vol sleeve.

### Peer correlations (H1 ~30d)

| Peer | ρ |
| --- | ---: |
| GBPUSD | -0.443 |
| AUDUSD | -0.251 |
| USDCAD | +0.173 |
| GBPJPY | -0.154 |
| EURJPY | +0.138 |
| EURUSD | +0.123 |
| NZDUSD | -0.101 |
| USDJPY | +0.065 |

Strongest |ρ| peers: GBPUSD (-0.44), AUDUSD (-0.25), USDCAD (+0.17), GBPJPY (-0.15). Notable negatives: GBPUSD (-0.44), AUDUSD (-0.25), GBPJPY (-0.15).

### Event sensitivities

Event move multiples: CPI: —; GDP: —; central_bank: 1.36× ATR.

---

## Path

Monthly D1 path return over the window: **+1.5%** (open 0.84453 → last close 0.85722).

| Month | Ret % | Close |
| --- | ---: | ---: |
| 2024-09 | -1.41 | 0.83261 |
| 2024-10 | +1.35 | 0.84383 |
| 2024-11 | -1.65 | 0.82992 |
| 2024-12 | -0.34 | 0.82789 |
| 2025-01 | +1.16 | 0.83600 |
| 2025-02 | -0.94 | 0.82466 |
| 2025-03 | +1.38 | 0.83725 |
| 2025-04 | +1.51 | 0.84992 |
| 2025-05 | -0.83 | 0.84289 |
| 2025-06 | +1.89 | 0.85813 |
| 2025-07 | +0.73 | 0.86442 |
| 2025-08 | +0.12 | 0.86549 |
| 2025-09 | +0.83 | 0.87265 |
| 2025-10 | +0.49 | 0.87693 |
| 2025-11 | -0.11 | 0.87626 |
| 2025-12 | -0.55 | 0.87139 |
| 2026-01 | -0.70 | 0.86554 |
| 2026-02 | +1.26 | 0.87566 |
| 2026-03 | -0.38 | 0.87379 |
| 2026-04 | -1.33 | 0.86217 |
| 2026-05 | +0.44 | 0.86593 |
| 2026-06 | -0.54 | 0.86129 |
| 2026-07 | -0.78 | 0.85453 |
| 2026-08 | +0.38 | 0.85745 |
| 2026-09 | -0.03 | 0.85722 |

---

## Narrative pressure

- Sentiment score: **-0.069** on [−1, +1] · 2 items · 24h window
- As-of: 2026-10-09 13:03:38.491856+00:00 · stale=True
- Mapped news articles: **108**
- Insight: _EURGBP: trending down context_ — EURGBP is currently classified as trending down with realized volatility near the 71th pct of its recent window. News sentiment over the last 24h is -0.03 on a [-1, +1] scale. This narrative summarizes deterministic analytics only and is not a trade signal.

Recent headlines:

- 2026-10-09 · forexfactory.calendar — ECOFIN Meetings
- 2026-10-09 · forexfactory.calendar — Italian Industrial Production m/m
- 2026-10-08 · forexfactory.calendar — MPC Member Lombardelli Speaks
- 2026-10-08 · Forexlive — Morning Kickstart: Stocks fall as oil and yields rise; USD edges higher
- 2026-10-08 · forexfactory.calendar — BOE Gov Bailey Speaks
- 2026-10-08 · forexfactory.calendar — ECB Monetary Policy Meeting Accounts
- 2026-10-08 · forexfactory.calendar — MPC Member Pill Speaks
- 2026-10-08 · Yahoo — JPMorgan sees strong Q3 for EU oil and gas, favors these major stocks

---

## Provenance

- Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`
- Profile confidence: 0.99 · stale=False
- Sources: mt5.prices, metrics.v1, regimes.rule_v1
- Raw export: [`audit.json`](./audit.json) · monthly boards: [`regime-audit.md`](./regime-audit.md)

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
