# AUDUSD — Regime audit & fit tagging (monthly, 2y)

> Ex-post calendar-month boards · `regimes.rule_v1` labels → `fit.map_v0`  
> Window: 2024-09 → 2026-09 (25 H1 months with confirmed bars after warmup)

## Method

1. Load H1 / D1 OHLCV (~800d lookback; M1 depth gate passes).
2. Run `regime_feature_frame` → confirmed regime per bar.
3. Slice each calendar month; map regimes → MATCH / MISMATCH / FRAGILE per edge family.
4. Dominant tag = largest fit-share (ties break MISMATCH > FRAGILE > MATCH).

Families: **meanrev** home=`ranging`; **trendfollow** home=`trending_up|trending_down`; both treat `high_volatility` as FRAGILE.

## Tag summary (months with bars)

| TF × family | MATCH | MISMATCH | FRAGILE |
| --- | ---: | ---: | ---: |
| `H1|meanrev` | 20 | 0 | 5 |
| `H1|trendfollow` | 0 | 20 | 5 |
| `D1|meanrev` | 11 | 6 | 7 |
| `D1|trendfollow` | 6 | 11 | 7 |

Dominant-regime months (H1): {'high_volatility': 5, 'ranging': 20}
Dominant-regime months (D1): {'trending_down': 3, 'high_volatility': 7, 'ranging': 11, 'trending_up': 3}

## H1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-09 | high_volatility | **FRAGILE** | **FRAGILE** | 149 | 24.8% | 27.5% | 9.4% | 38.3% |
| 2024-10 | ranging | **MATCH** | **MISMATCH** | 552 | 54.2% | 6.3% | 27.4% | 12.1% |
| 2024-11 | ranging | **MATCH** | **MISMATCH** | 501 | 42.7% | 13.6% | 9.6% | 34.1% |
| 2024-12 | ranging | **MATCH** | **MISMATCH** | 506 | 51.6% | 3.8% | 16.2% | 28.5% |
| 2025-01 | ranging | **MATCH** | **MISMATCH** | 526 | 57.2% | 3.6% | 7.6% | 31.6% |
| 2025-02 | ranging | **MATCH** | **MISMATCH** | 480 | 50.0% | 19.8% | 15.6% | 14.6% |
| 2025-03 | ranging | **MATCH** | **MISMATCH** | 503 | 44.7% | 13.3% | 18.9% | 23.1% |
| 2025-04 | high_volatility | **FRAGILE** | **FRAGILE** | 528 | 40.2% | 8.7% | 6.2% | 44.9% |
| 2025-05 | ranging | **MATCH** | **MISMATCH** | 526 | 48.9% | 20.5% | 21.5% | 9.1% |
| 2025-06 | ranging | **MATCH** | **MISMATCH** | 506 | 49.8% | 20.0% | 7.1% | 23.1% |
| 2025-07 | ranging | **MATCH** | **MISMATCH** | 539 | 48.8% | 15.4% | 15.4% | 20.4% |
| 2025-08 | ranging | **MATCH** | **MISMATCH** | 504 | 59.1% | 14.7% | 13.1% | 13.1% |
| 2025-09 | ranging | **MATCH** | **MISMATCH** | 528 | 50.8% | 18.0% | 8.0% | 23.3% |
| 2025-10 | ranging | **MATCH** | **MISMATCH** | 548 | 43.6% | 17.0% | 9.1% | 30.3% |
| 2025-11 | ranging | **MATCH** | **MISMATCH** | 482 | 41.1% | 17.8% | 8.3% | 32.8% |
| 2025-12 | ranging | **MATCH** | **MISMATCH** | 522 | 61.3% | 24.9% | 7.3% | 6.5% |
| 2026-01 | high_volatility | **FRAGILE** | **FRAGILE** | 504 | 27.4% | 12.7% | 10.9% | 49.0% |
| 2026-02 | high_volatility | **FRAGILE** | **FRAGILE** | 480 | 35.8% | 15.6% | 4.0% | 44.6% |
| 2026-03 | high_volatility | **FRAGILE** | **FRAGILE** | 531 | 31.6% | 12.1% | 20.0% | 36.3% |
| 2026-04 | ranging | **MATCH** | **MISMATCH** | 528 | 53.4% | 26.7% | 7.0% | 12.9% |
| 2026-05 | ranging | **MATCH** | **MISMATCH** | 504 | 39.9% | 15.9% | 19.4% | 24.8% |
| 2026-06 | ranging | **MATCH** | **MISMATCH** | 528 | 57.4% | 6.4% | 16.5% | 19.7% |
| 2026-07 | ranging | **MATCH** | **MISMATCH** | 549 | 56.6% | 6.2% | 13.5% | 23.7% |
| 2026-08 | ranging | **MATCH** | **MISMATCH** | 507 | 48.3% | 22.9% | 13.0% | 15.8% |
| 2026-09 | ranging | **MATCH** | **MISMATCH** | 304 | 58.9% | 8.9% | 8.9% | 23.4% |

## D1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-10 | trending_down | **MISMATCH** | **MATCH** | 16 | 43.8% | 0.0% | 56.2% | 0.0% |
| 2024-11 | high_volatility | **FRAGILE** | **FRAGILE** | 25 | 0.0% | 0.0% | 28.0% | 72.0% |
| 2024-12 | trending_down | **MISMATCH** | **MATCH** | 27 | 22.2% | 0.0% | 55.6% | 22.2% |
| 2025-01 | ranging | **MATCH** | **MISMATCH** | 27 | 63.0% | 0.0% | 37.0% | 0.0% |
| 2025-02 | high_volatility | **FRAGILE** | **FRAGILE** | 24 | 41.7% | 0.0% | 0.0% | 58.3% |
| 2025-03 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 46.2% | 0.0% | 0.0% | 53.8% |
| 2025-04 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 19.2% | 3.8% | 0.0% | 76.9% |
| 2025-05 | ranging | **MATCH** | **MISMATCH** | 26 | 73.1% | 26.9% | 0.0% | 0.0% |
| 2025-06 | ranging | **MATCH** | **MISMATCH** | 26 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2025-07 | ranging | **MATCH** | **MISMATCH** | 27 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2025-08 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 46.2% | 0.0% | 0.0% | 53.8% |
| 2025-09 | ranging | **MATCH** | **MISMATCH** | 26 | 69.2% | 30.8% | 0.0% | 0.0% |
| 2025-10 | high_volatility | **FRAGILE** | **FRAGILE** | 27 | 48.1% | 0.0% | 0.0% | 51.9% |
| 2025-11 | ranging | **MATCH** | **MISMATCH** | 25 | 88.0% | 0.0% | 12.0% | 0.0% |
| 2025-12 | trending_up | **MISMATCH** | **MATCH** | 26 | 23.1% | 65.4% | 0.0% | 11.5% |
| 2026-01 | ranging | **MATCH** | **MISMATCH** | 26 | 76.9% | 0.0% | 0.0% | 23.1% |
| 2026-02 | high_volatility | **FRAGILE** | **FRAGILE** | 24 | 33.3% | 0.0% | 0.0% | 66.7% |
| 2026-03 | ranging | **MATCH** | **MISMATCH** | 27 | 66.7% | 0.0% | 0.0% | 33.3% |
| 2026-04 | trending_up | **MISMATCH** | **MATCH** | 26 | 11.5% | 38.5% | 15.4% | 34.6% |
| 2026-05 | ranging | **MATCH** | **MISMATCH** | 26 | 76.9% | 23.1% | 0.0% | 0.0% |
| 2026-06 | ranging | **MATCH** | **MISMATCH** | 26 | 61.5% | 0.0% | 38.5% | 0.0% |
| 2026-07 | trending_down | **MISMATCH** | **MATCH** | 27 | 33.3% | 18.5% | 48.1% | 0.0% |
| 2026-08 | ranging | **MATCH** | **MISMATCH** | 26 | 65.4% | 23.1% | 0.0% | 11.5% |
| 2026-09 | trending_up | **MISMATCH** | **MATCH** | 17 | 23.5% | 76.5% | 0.0% | 0.0% |

## Audit takeaways

1. **H1 meanrev MATCH in 20/25 months** vs trendfollow MATCH in 0/25 — modal H1 month regime is `ranging` (20/25).
2. **Fragile clusters** (both families FRAGILE): 2026-01–2026-03.
3. **Trend MATCH months** with a trending_* dominant regime are scarce in this window.
4. **TF disagreement is expected** when dominant regime is ranging but trend shares outvote ranging on the fit map (or the reverse).
5. First/last months may be thin after regime warmup (2024-09 / 2026-09).
6. Monthly MATCH is **ex-post**, not a forward signal. Live research gate should use nowcast + 30d shares, not calendar-month prophecy.

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
