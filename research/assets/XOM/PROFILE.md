# XOM — Asset profile dossier

> Research / advisory only · Ouroboros `profile.v1` + `regimes.rule_v1` + `fit.map_v0`  
> Generated `2026-10-18T23:50:02Z` · data `2024-10-07` → `2026-10-07` (25 calendar months, M1 depth ≈ 730d)

Canvas cover (open beside chat): [`xom-asset-profile.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/xom-asset-profile.canvas.tsx).

---

## Identity

| Field | Value |
| --- | --- |
| Symbol | `XOM` |
| Display | Exxon Mobil Corporation |
| Class | equity |
| Quote | USD |
| MT5 ticker | `Exxon` |
| Sessions | new_york · `America/New_York` · UTC 13:30–20:00 |

US cash RTH approx 09:30–16:00 America/New_York (13:30–20:00 UTC during EST; 14:30–21:00 UTC during EDT). Broker CFD hours may extend; DST shifts open/close UTC.

---

## Two clocks

### Nowcast (H1 state)

| Metric | Value |
| --- | --- |
| Confirmed regime | **ranging** |
| Vol percentile | 63.2 |
| Trend ER | 0.027 |
| Confidence | 0.938 |
| As-of | 2026-10-07 14:00:00+00:00 |
| Stale | False |

Soft probabilities (nowcast — may disagree with confirmed label when confidence is low):

| Regime | P |
| --- | ---: |
| trending_up | 2.1% |
| trending_down | 2.1% |
| ranging | 93.8% |
| high_volatility | 2.1% |

### Live fit gate (ex-post 30d H1 shares → dominant tag)

| Family | Tag | MATCH | MISMATCH | FRAGILE | Bars |
| --- | --- | ---: | ---: | ---: | ---: |
| `meanrev` | **MATCH** | 59.7% | 38.3% | 2.0% | 149 |
| `trendfollow` | **MISMATCH** | 38.3% | 59.7% | 2.0% | 149 |

Interpretation: last ~30d H1 mass is **ranging-contested** — meanrev=MATCH (59.7% MATCH / 38.3% MISMATCH), trendfollow=MISMATCH (38.3% MATCH). FRAGILE sleeve 2.0%.

---

## Character (`profile.v1`)

### Volatility & liquidity

| Field | Value |
| --- | --- |
| ATR pctile 30d | 20.0 |
| Realized vol pctile 30d | 6.7 |
| Typical daily range | 3.56 USD |
| Range pctile 30d (liq proxy) | 30.0 |
| True spread | deferred |

_true bid/ask spread deferred until quote ingestion; range proxies (high-low) only_

### Regime distribution (history clock)

Confirmed-label share over the profile sample (H1 preferred when depth gate passes):

| Regime | Share |
| --- | ---: |
| trending_up | 23.2% |
| trending_down | 12.2% |
| ranging | 34.3% |
| high_volatility | 30.3% |

**Read:** ranging (34.3%) + high_volatility (30.3%) vs net trending (35.4%). On this sample XOM is **trend-leaning** on H1 history — energy beta often shows as a large fragile/high-vol sleeve beside ranging mass.

### Peer correlations (H1 ~30d)

| Peer | ρ |
| --- | ---: |
| AAPL | -0.242 |
| NAS100 | -0.218 |
| JPM | -0.187 |
| TSLA | -0.122 |
| AMZN | -0.077 |
| GOOGL | -0.071 |
| US500 | +0.046 |
| AVGO | -0.040 |
| MSFT | +0.020 |
| META | +0.014 |
| NVDA | -0.003 |

Energy sleeve vs growth/tech this window (largest |ρ|): AAPL (-0.24), NAS100 (-0.22), JPM (-0.19), TSLA (-0.12). Broad negative to mega-cap tech/NAS100: AAPL (-0.24), NAS100 (-0.22), JPM (-0.19), TSLA (-0.12).

### Event sensitivities

Taxonomy present (NFP / CPI / FOMC) but **ATR multiples empty** — calendar hits scored for XOM are below the ≥3-window gate. Energy-equity earnings / OPEC / inventory windows are not yet a separate scored plane.

---

## Path

Monthly D1 path return over the window: **+30.9%** (open 125.26 → last close 163.98).

| Month | Ret % | Close |
| --- | ---: | ---: |
| 2024-10 | -6.83 | 116.70 |
| 2024-11 | -1.74 | 117.62 |
| 2024-12 | -8.73 | 107.61 |
| 2025-01 | -0.94 | 106.59 |
| 2025-02 | +4.64 | 111.41 |
| 2025-03 | +6.35 | 118.51 |
| 2025-04 | -10.89 | 105.55 |
| 2025-05 | -2.55 | 102.17 |
| 2025-06 | +3.99 | 107.63 |
| 2025-07 | +3.57 | 111.57 |
| 2025-08 | +2.27 | 114.20 |
| 2025-09 | -0.96 | 112.59 |
| 2025-10 | +1.87 | 114.24 |
| 2025-11 | +1.50 | 115.85 |
| 2025-12 | +3.68 | 120.12 |
| 2026-01 | +18.08 | 141.40 |
| 2026-02 | +9.56 | 152.45 |
| 2026-03 | +6.48 | 169.48 |
| 2026-04 | -6.24 | 154.27 |
| 2026-05 | -1.66 | 149.53 |
| 2026-07 | +13.57 | 155.28 |
| 2026-08 | +5.07 | 160.87 |
| 2026-09 | -0.13 | 162.51 |
| 2026-10 | +1.85 | 163.98 |

---

## Narrative pressure

- Sentiment score: **-0.020** on [−1, +1] · 1 items · 24h window
- As-of: 2026-10-09 12:33:38.491239+00:00 · stale=True
- Mapped news articles: **132**
- Insight: _XOM: ranging context_ — XOM is currently classified as ranging with realized volatility near the 63th pct of its recent window. News sentiment over the last 24h is -0.02 on a [-1, +1] scale. This narrative summarizes deterministic analytics only and is not a trade signal.

Recent headlines:

- 2026-10-08 · ChartMill — These S&P500 stocks that are showing activity before the opening bell on Thursday.
- 2026-10-08 · Yahoo — Oil Is Already at $100. Now a Hurricane Could Shut Down Gulf Production
- 2026-10-08 · SeekingAlpha — What Investors Might Expect From September's Inflation Report
- 2026-10-08 · Yahoo — Is Helmerich & Payne (HP) Undervalued Following High End Margin Guidance And ExxonMobil Expansion?
- 2026-10-07 · Yahoo — America Got Addicted to Cheap Money — Now the Economy Is Cracking as Rates Exceed 5%
- 2026-10-07 · Yahoo — ExxonMobil Surges 44% in a Year: Should Investors Bet on the Momentum?
- 2026-10-07 · Yahoo — Treasury Bills Beat Exxon’s Dividend Yield. Does That Make Them the Better Buy?
- 2026-10-07 · Yahoo — Why Sozzi just added McDonald's to the 'Wall of Underperformers'

---

## Provenance

- Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`
- Profile confidence: 0.99 · stale=False
- Sources: mt5.prices, metrics.v1, regimes.rule_v1
- Raw export: [`audit.json`](./audit.json) · monthly boards: [`regime-audit.md`](./regime-audit.md)

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
