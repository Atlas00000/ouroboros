# JP225 — Asset profile dossier

> Research / advisory only · Ouroboros `profile.v1` + `regimes.rule_v1` + `fit.map_v0`  
> Generated `2026-10-18T23:54:16Z` · data `2024-10-07` → `2026-10-07` (25 calendar months, M1 depth ≈ 730d)

Canvas cover (open beside chat): [`jp225-asset-profile.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/jp225-asset-profile.canvas.tsx).

> **Depth note:** requested 2y monthly audit; YWO MT5 `JP225` / `JPN225` index CFD only exposes M1/H1/D1 from `2024-10-07` (≈730d). Boards below cover available history.

---

## Identity

| Field | Value |
| --- | --- |
| Symbol | `JP225` |
| Display | Japan 225 (Nikkei) |
| Class | index |
| Quote | JPY |
| MT5 ticker | `JPN225` |
| Sessions | new_york, london · `UTC` · UTC 13:30–20:00 |

Index cash hours approximate (US RTH for US500/US30/NAS100; London/Frankfurt/Tokyo cash for regional indices). Broker CFD session may trade nearly 24h — treat as research proxy.

---

## Two clocks

### Nowcast (H1 state)

| Metric | Value |
| --- | --- |
| Confirmed regime | **trending_down** |
| Vol percentile | 6.9 |
| Trend ER | -0.601 |
| Confidence | 0.943 |
| As-of | 2026-10-07 14:00:00+00:00 |
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
| `meanrev` | **MATCH** | 45.1% | 42.3% | 12.6% | 501 |
| `trendfollow` | **MISMATCH** | 42.3% | 45.1% | 12.6% | 501 |

Interpretation: last ~30d H1 mass is **ranging-contested** — meanrev=MATCH (45.1% MATCH / 42.3% MISMATCH), trendfollow=MISMATCH (42.3% MATCH). FRAGILE sleeve 12.6%.

---

## Character (`profile.v1`)

### Volatility & liquidity

| Field | Value |
| --- | --- |
| ATR pctile 30d | 20.0 |
| Realized vol pctile 30d | 6.7 |
| Typical daily range | 1317.32 JPY |
| Range pctile 30d (liq proxy) | 83.3 |
| True spread | deferred |

_true bid/ask spread deferred until quote ingestion; range proxies (high-low) only_

### Regime distribution (history clock)

Confirmed-label share over the profile sample (H1 preferred when depth gate passes):

| Regime | Share |
| --- | ---: |
| trending_up | 18.1% |
| trending_down | 11.6% |
| ranging | 43.5% |
| high_volatility | 26.7% |

**Read:** ranging (43.5%) + high_volatility (26.7%) vs net trending (29.7%). On this sample JP225 is **meanrev-leaning** on H1 history — with a material fragile/high-vol sleeve.

### Peer correlations (H1 ~30d)

| Peer | ρ |
| --- | ---: |
| NAS100 | +0.676 |
| US500 | +0.592 |
| DE40 | +0.437 |
| US30 | +0.423 |
| UK100 | +0.325 |

Closest sleeves this window: NAS100 (+0.68), US500 (+0.59), DE40 (+0.44), US30 (+0.42).

### Event sensitivities

Taxonomy present (CPI / GDP / central_bank — BoJ / JP prints) but **ATR multiples empty** — calendar hits scored for JP225 are below the ≥3-window gate. Honest gap until index event windows are scored.

---

## Path

Monthly D1 path return over the window: **+77.6%** (open 39039.00 → last close 69341.50).

| Month | Ret % | Close |
| --- | ---: | ---: |
| 2024-10 | -2.07 | 38229.00 |
| 2024-11 | +0.14 | 38285.00 |
| 2024-12 | +2.94 | 39376.00 |
| 2025-01 | -0.24 | 39316.00 |
| 2025-02 | -3.32 | 37592.00 |
| 2025-03 | -4.50 | 35946.00 |
| 2025-04 | +0.88 | 36264.00 |
| 2025-05 | +3.87 | 37664.00 |
| 2025-06 | +7.07 | 40261.00 |
| 2025-07 | +1.17 | 40736.00 |
| 2025-08 | +3.58 | 42194.00 |
| 2025-09 | +6.30 | 44855.00 |
| 2025-10 | +16.47 | 52244.00 |
| 2025-11 | -3.85 | 50298.00 |
| 2025-12 | +0.08 | 50342.75 |
| 2026-01 | +6.04 | 53425.75 |
| 2026-02 | +9.12 | 58567.25 |
| 2026-03 | -7.66 | 53233.50 |
| 2026-04 | +12.08 | 59663.75 |
| 2026-05 | +11.09 | 66297.32 |
| 2026-06 | +7.27 | 71117.98 |
| 2026-07 | -11.44 | 62994.62 |
| 2026-08 | +4.03 | 65814.49 |
| 2026-09 | +1.97 | 67084.71 |
| 2026-10 | +3.36 | 69341.50 |

---

## Narrative pressure

- Mapped news articles: **0**
- Insight: _JP225: trending down context_ — JP225 is currently classified as trending down with realized volatility near the 7th pct of its recent window. News sentiment over the last 24h is n/a on a [-1, +1] scale. This narrative summarizes deterministic analytics only and is not a trade signal.

Recent headlines:


---

## Provenance

- Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`
- Profile confidence: 0.99 · stale=False
- Sources: mt5.prices, metrics.v1, regimes.rule_v1
- Raw export: [`audit.json`](./audit.json) · monthly boards: [`regime-audit.md`](./regime-audit.md)

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
