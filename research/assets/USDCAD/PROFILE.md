# USDCAD — Asset profile dossier

> Research / advisory only · Ouroboros `profile.v1` + `regimes.rule_v1` + `fit.map_v0`  
> Generated `2026-10-18T23:37:24Z` · data `2024-09-12` → `2026-09-21` (25 calendar months, M1 depth ≈ 740d)

Canvas covers (open beside chat):

- Asset profile: [`usdcad-asset-profile.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/usdcad-asset-profile.canvas.tsx)
- BMRG M15 preset: [`bmrg-usdcad-m15-preset.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-usdcad-m15-preset.canvas.tsx)
- BMRG M5 preset: [`bmrg-usdcad-m5-preset.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-usdcad-m5-preset.canvas.tsx)

BMRG chart presets (never TP &lt; SL):

| TF | Card | Magic | Geometry |
| --- | --- | ---: | --- |
| M15 | [`BMRG_M15_chart_preset.md`](./BMRG_M15_chart_preset.md) | **26101901** | SL 140 / TP 175 · ATR≤59 · BB 2.4 |
| M5 | [`BMRG_M5_chart_preset.md`](./BMRG_M5_chart_preset.md) | **26101905** | SL 65 / TP 80 · ATR≤25 · BB 2.2 |

---

## Identity

| Field | Value |
| --- | --- |
| Symbol | `USDCAD` |
| Display | US Dollar / Canadian Dollar |
| Class | fx |
| Quote | CAD |
| MT5 ticker | `USDCAD` |
| Sessions | sydney, tokyo, london, new_york · `UTC` · UTC 22:00–22:00 |

FX approx Sun 22:00–Fri 22:00 UTC; session names from calendar module.

---

## Two clocks

### Nowcast (H1 state)

| Metric | Value |
| --- | --- |
| Confirmed regime | **trending_up** |
| Vol percentile | 67.8 |
| Trend ER | 0.284 |
| Confidence | 0.722 |
| As-of | 2026-09-21 22:00:00+00:00 |
| Stale | True |

Soft probabilities (nowcast — may disagree with confirmed label when confidence is low):

| Regime | P |
| --- | ---: |
| trending_up | 72.2% |
| trending_down | 2.7% |
| ranging | 6.1% |
| high_volatility | 18.9% |

### Live fit gate (ex-post 30d H1 shares → dominant tag)

| Family | Tag | MATCH | MISMATCH | FRAGILE | Bars |
| --- | --- | ---: | ---: | ---: | ---: |
| `meanrev` | **MISMATCH** | 24.4% | 51.0% | 24.6% | 451 |
| `trendfollow` | **MATCH** | 51.0% | 24.4% | 24.6% | 451 |

Interpretation: last ~30d H1 mass is **trending_up-led** → meanrev **MISMATCH**, trendfollow **MATCH**. FRAGILE share ≈ 25%.

---

## Character (`profile.v1`)

### Volatility & liquidity

| Field | Value |
| --- | --- |
| ATR pctile 30d | 13.3 |
| Realized vol pctile 30d | 10.0 |
| Typical daily range | 0.00464 CAD |
| Range pctile 30d (liq proxy) | 46.7 |
| True spread | deferred |

_true bid/ask spread deferred until quote ingestion; range proxies (high-low) only_

### Regime distribution (history clock)

Confirmed-label share over the profile sample (H1 preferred when depth gate passes):

| Regime | Share |
| --- | ---: |
| trending_up | 17.1% |
| trending_down | 11.0% |
| ranging | 45.9% |
| high_volatility | 26.0% |

**Read:** ranging (46%) + high_volatility (26%) · net trending (up+down) ≈ 28%. This is a **meanrev-leaning** FX major on H1 history — with a material fragile/high-vol sleeve.

### Peer correlations (H1 ~30d)

| Peer | ρ |
| --- | ---: |
| GBPUSD | -0.602 |
| EURUSD | -0.543 |
| AUDUSD | -0.520 |
| NZDUSD | -0.480 |
| USDJPY | +0.319 |
| EURGBP | +0.173 |
| GBPJPY | +0.168 |
| EURJPY | +0.107 |

Strongest |ρ| peers: GBPUSD (-0.60), EURUSD (-0.54), AUDUSD (-0.52), NZDUSD (-0.48). Notable negatives: GBPUSD (-0.60), EURUSD (-0.54), AUDUSD (-0.52).

### Event sensitivities

Event move multiples: NFP: —; CPI: 2.13× ATR; FOMC: —; central_bank: —.

---

## Path

Monthly D1 path return over the window: **+3.3%** (open 1.35819 → last close 1.40314).

| Month | Ret % | Close |
| --- | ---: | ---: |
| 2024-09 | -0.42 | 1.35245 |
| 2024-10 | +3.04 | 1.39351 |
| 2024-11 | +0.44 | 1.39958 |
| 2024-12 | +2.76 | 1.43770 |
| 2025-01 | +1.13 | 1.45370 |
| 2025-02 | -1.85 | 1.44627 |
| 2025-03 | -0.34 | 1.43897 |
| 2025-04 | -4.19 | 1.37862 |
| 2025-05 | -0.35 | 1.37373 |
| 2025-06 | -0.99 | 1.36065 |
| 2025-07 | +1.91 | 1.38668 |
| 2025-08 | -0.92 | 1.37397 |
| 2025-09 | +1.32 | 1.39204 |
| 2025-10 | +0.61 | 1.40056 |
| 2025-11 | -0.21 | 1.39704 |
| 2025-12 | -1.79 | 1.37203 |
| 2026-01 | -0.75 | 1.36127 |
| 2026-02 | +0.20 | 1.36228 |
| 2026-03 | +1.90 | 1.39036 |
| 2026-04 | -2.33 | 1.35798 |
| 2026-05 | +1.60 | 1.37969 |
| 2026-06 | +2.98 | 1.42078 |
| 2026-07 | -1.36 | 1.40150 |
| 2026-08 | -1.07 | 1.38520 |
| 2026-09 | +1.30 | 1.40314 |

---

## Narrative pressure

- Sentiment score: **-0.089** on [−1, +1] · 9 items · 24h window
- As-of: 2026-10-09 13:03:38.491856+00:00 · stale=True
- Mapped news articles: **140**
- Insight: _USDCAD: trending up context_ — USDCAD is currently classified as trending up with realized volatility near the 68th pct of its recent window. News sentiment over the last 24h is -0.09 on a [-1, +1] scale. This narrative summarizes deterministic analytics only and is not a trade signal.

Recent headlines:

- 2026-10-09 · forexfactory.calendar — FOMC Member Collins Speaks
- 2026-10-09 · forexfactory.calendar — Prelim UoM Consumer Sentiment
- 2026-10-09 · forexfactory.calendar — Prelim UoM Inflation Expectations
- 2026-10-09 · forexfactory.calendar — Employment Change
- 2026-10-09 · forexfactory.calendar — Unemployment Rate
- 2026-10-08 · forexfactory.calendar — FOMC Member Musalem Speaks
- 2026-10-08 · forexfactory.calendar — 30-y Bond Auction
- 2026-10-08 · forexfactory.calendar — Natural Gas Storage

---

## Provenance

- Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`
- Profile confidence: 0.99 · stale=False
- Sources: mt5.prices, metrics.v1, regimes.rule_v1
- Raw export: [`audit.json`](./audit.json) · monthly boards: [`regime-audit.md`](./regime-audit.md)

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
