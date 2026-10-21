# EURGBP — Regime audit & fit tagging (monthly, 2y)

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
| `H1|meanrev` | 21 | 1 | 3 |
| `H1|trendfollow` | 1 | 21 | 3 |
| `D1|meanrev` | 8 | 6 | 10 |
| `D1|trendfollow` | 6 | 8 | 10 |

Dominant-regime months (H1): {'ranging': 22, 'high_volatility': 3}
Dominant-regime months (D1): {'ranging': 9, 'high_volatility': 10, 'trending_up': 1, 'trending_down': 4}

## H1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-09 | ranging | **MISMATCH** | **MATCH** | 147 | 29.3% | 16.3% | 29.3% | 25.2% |
| 2024-10 | ranging | **MATCH** | **MISMATCH** | 552 | 41.3% | 5.1% | 21.0% | 32.6% |
| 2024-11 | ranging | **MATCH** | **MISMATCH** | 501 | 39.1% | 9.2% | 16.8% | 34.9% |
| 2024-12 | ranging | **MATCH** | **MISMATCH** | 506 | 39.7% | 9.1% | 20.8% | 30.4% |
| 2025-01 | ranging | **MATCH** | **MISMATCH** | 526 | 53.2% | 4.9% | 7.0% | 34.8% |
| 2025-02 | ranging | **MATCH** | **MISMATCH** | 480 | 59.6% | 9.4% | 21.5% | 9.6% |
| 2025-03 | ranging | **MATCH** | **MISMATCH** | 503 | 42.3% | 6.6% | 13.7% | 37.4% |
| 2025-04 | high_volatility | **FRAGILE** | **FRAGILE** | 528 | 32.4% | 7.0% | 20.3% | 40.3% |
| 2025-05 | ranging | **MATCH** | **MISMATCH** | 526 | 69.6% | 5.7% | 19.0% | 5.7% |
| 2025-06 | ranging | **MATCH** | **MISMATCH** | 506 | 51.8% | 17.2% | 8.1% | 22.9% |
| 2025-07 | ranging | **MATCH** | **MISMATCH** | 539 | 38.2% | 14.8% | 14.3% | 32.7% |
| 2025-08 | ranging | **MATCH** | **MISMATCH** | 504 | 48.4% | 19.2% | 15.5% | 16.9% |
| 2025-09 | ranging | **MATCH** | **MISMATCH** | 528 | 63.3% | 5.1% | 14.0% | 17.6% |
| 2025-10 | high_volatility | **FRAGILE** | **FRAGILE** | 548 | 39.2% | 14.1% | 6.2% | 40.5% |
| 2025-11 | ranging | **MATCH** | **MISMATCH** | 482 | 54.6% | 10.6% | 12.9% | 22.0% |
| 2025-12 | ranging | **MATCH** | **MISMATCH** | 522 | 60.9% | 16.1% | 11.1% | 11.9% |
| 2026-01 | ranging | **MATCH** | **MISMATCH** | 504 | 54.0% | 7.3% | 11.1% | 27.6% |
| 2026-02 | ranging | **MATCH** | **MISMATCH** | 480 | 50.0% | 6.0% | 9.8% | 34.2% |
| 2026-03 | ranging | **MATCH** | **MISMATCH** | 531 | 65.2% | 2.8% | 11.5% | 20.5% |
| 2026-04 | ranging | **MATCH** | **MISMATCH** | 526 | 73.8% | 5.3% | 12.9% | 8.0% |
| 2026-05 | ranging | **MATCH** | **MISMATCH** | 504 | 50.2% | 8.1% | 12.9% | 28.8% |
| 2026-06 | ranging | **MATCH** | **MISMATCH** | 528 | 56.8% | 7.2% | 17.4% | 18.6% |
| 2026-07 | high_volatility | **FRAGILE** | **FRAGILE** | 549 | 34.6% | 8.9% | 13.1% | 43.4% |
| 2026-08 | ranging | **MATCH** | **MISMATCH** | 507 | 65.7% | 16.2% | 14.2% | 3.9% |
| 2026-09 | ranging | **MATCH** | **MISMATCH** | 213 | 49.8% | 19.2% | 6.1% | 24.9% |

## D1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-10 | ranging | **MATCH** | **MISMATCH** | 17 | 76.5% | 0.0% | 0.0% | 23.5% |
| 2024-11 | high_volatility | **FRAGILE** | **FRAGILE** | 25 | 16.0% | 0.0% | 0.0% | 84.0% |
| 2024-12 | ranging | **MATCH** | **MISMATCH** | 27 | 51.9% | 0.0% | 14.8% | 33.3% |
| 2025-01 | trending_up | **MISMATCH** | **MATCH** | 27 | 33.3% | 55.6% | 0.0% | 11.1% |
| 2025-02 | trending_down | **MISMATCH** | **MATCH** | 24 | 37.5% | 0.0% | 62.5% | 0.0% |
| 2025-03 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 26.9% | 0.0% | 0.0% | 73.1% |
| 2025-04 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 23.1% | 0.0% | 0.0% | 76.9% |
| 2025-05 | trending_down | **MISMATCH** | **MATCH** | 26 | 15.4% | 0.0% | 84.6% | 0.0% |
| 2025-06 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 38.5% | 7.7% | 0.0% | 53.8% |
| 2025-07 | high_volatility | **FRAGILE** | **FRAGILE** | 27 | 7.4% | 44.4% | 0.0% | 48.1% |
| 2025-08 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 26.9% | 0.0% | 15.4% | 57.7% |
| 2025-09 | ranging | **MATCH** | **MISMATCH** | 26 | 65.4% | 30.8% | 3.8% | 0.0% |
| 2025-10 | ranging | **MATCH** | **MISMATCH** | 27 | 70.4% | 22.2% | 0.0% | 7.4% |
| 2025-11 | high_volatility | **FRAGILE** | **FRAGILE** | 25 | 4.0% | 0.0% | 0.0% | 96.0% |
| 2025-12 | ranging | **MATCH** | **MISMATCH** | 26 | 73.1% | 0.0% | 26.9% | 0.0% |
| 2026-01 | trending_down | **MISMATCH** | **MATCH** | 26 | 30.8% | 0.0% | 46.2% | 23.1% |
| 2026-02 | high_volatility | **FRAGILE** | **FRAGILE** | 24 | 37.5% | 4.2% | 0.0% | 58.3% |
| 2026-03 | ranging | **MISMATCH** | **MATCH** | 27 | 48.1% | 7.4% | 44.4% | 0.0% |
| 2026-04 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 15.4% | 0.0% | 19.2% | 65.4% |
| 2026-05 | trending_down | **MISMATCH** | **MATCH** | 26 | 30.8% | 0.0% | 38.5% | 30.8% |
| 2026-06 | ranging | **MATCH** | **MISMATCH** | 26 | 88.5% | 0.0% | 11.5% | 0.0% |
| 2026-07 | high_volatility | **FRAGILE** | **FRAGILE** | 27 | 7.4% | 0.0% | 11.1% | 81.5% |
| 2026-08 | ranging | **MATCH** | **MISMATCH** | 26 | 65.4% | 0.0% | 0.0% | 34.6% |
| 2026-09 | ranging | **MATCH** | **MISMATCH** | 10 | 100.0% | 0.0% | 0.0% | 0.0% |

## Audit takeaways

1. **H1 meanrev MATCH in 21/25 months** vs trendfollow MATCH in 1/25 — modal H1 month regime is `ranging` (22/25).
2. **Fragile months** are present but do not form long consecutive clusters on H1.
3. **Trend MATCH months** with a trending_* dominant regime are scarce in this window.
4. **TF disagreement is expected** when dominant regime is ranging but trend shares outvote ranging on the fit map (or the reverse).
5. First/last months may be thin after regime warmup (2024-09 / 2026-09).
6. Monthly MATCH is **ex-post**, not a forward signal. Live research gate should use nowcast + 30d shares, not calendar-month prophecy.

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
