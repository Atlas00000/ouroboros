# USDJPY — Regime audit & fit tagging (monthly, 2y)

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
| `H1|meanrev` | 18 | 3 | 4 |
| `H1|trendfollow` | 3 | 18 | 4 |
| `D1|meanrev` | 12 | 6 | 6 |
| `D1|trendfollow` | 6 | 12 | 6 |

Dominant-regime months (H1): {'ranging': 21, 'high_volatility': 4}  
Dominant-regime months (D1): {'ranging': 12, 'high_volatility': 7, 'trending_up': 4, 'trending_down': 1}

## H1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-09 | ranging | **MATCH** | **MISMATCH** | 149 | 59.1% | 13.4% | 4.7% | 22.8% |
| 2024-10 | ranging | **MATCH** | **MISMATCH** | 552 | 49.6% | 33.3% | 10.0% | 7.1% |
| 2024-11 | high_volatility | **FRAGILE** | **FRAGILE** | 501 | 26.1% | 13.8% | 16.2% | 43.9% |
| 2024-12 | ranging | **MATCH** | **MISMATCH** | 506 | 45.1% | 20.4% | 11.3% | 23.3% |
| 2025-01 | ranging | **MATCH** | **MISMATCH** | 526 | 51.5% | 12.2% | 8.6% | 27.8% |
| 2025-02 | ranging | **MATCH** | **MISMATCH** | 480 | 40.4% | 12.9% | 22.7% | 24.0% |
| 2025-03 | ranging | **MATCH** | **MISMATCH** | 503 | 44.7% | 16.7% | 8.7% | 29.8% |
| 2025-04 | high_volatility | **FRAGILE** | **FRAGILE** | 528 | 38.4% | 9.5% | 11.6% | 40.5% |
| 2025-05 | ranging | **MATCH** | **MISMATCH** | 526 | 48.3% | 16.2% | 25.1% | 10.5% |
| 2025-06 | ranging | **MATCH** | **MISMATCH** | 506 | 52.8% | 20.4% | 17.4% | 9.5% |
| 2025-07 | ranging | **MISMATCH** | **MATCH** | 539 | 38.2% | 23.9% | 15.0% | 22.8% |
| 2025-08 | ranging | **MISMATCH** | **MATCH** | 504 | 36.1% | 23.6% | 14.9% | 25.4% |
| 2025-09 | ranging | **MATCH** | **MISMATCH** | 528 | 44.3% | 16.3% | 19.9% | 19.5% |
| 2025-10 | ranging | **MATCH** | **MISMATCH** | 548 | 43.6% | 15.7% | 8.8% | 31.9% |
| 2025-11 | ranging | **MATCH** | **MISMATCH** | 482 | 52.1% | 17.6% | 14.7% | 15.6% |
| 2025-12 | ranging | **MISMATCH** | **MATCH** | 522 | 41.0% | 21.3% | 21.5% | 16.3% |
| 2026-01 | high_volatility | **FRAGILE** | **FRAGILE** | 502 | 38.8% | 12.0% | 5.2% | 44.0% |
| 2026-02 | ranging | **MATCH** | **MISMATCH** | 472 | 44.7% | 15.7% | 3.0% | 36.7% |
| 2026-03 | ranging | **MATCH** | **MISMATCH** | 529 | 51.4% | 29.1% | 8.1% | 11.3% |
| 2026-04 | ranging | **MATCH** | **MISMATCH** | 528 | 59.7% | 13.8% | 6.2% | 20.3% |
| 2026-05 | ranging | **MATCH** | **MISMATCH** | 504 | 52.4% | 28.6% | 1.8% | 17.3% |
| 2026-06 | ranging | **MATCH** | **MISMATCH** | 528 | 55.7% | 23.7% | 0.8% | 19.9% |
| 2026-07 | ranging | **MATCH** | **MISMATCH** | 549 | 41.3% | 20.0% | 2.9% | 35.7% |
| 2026-08 | ranging | **MATCH** | **MISMATCH** | 507 | 49.9% | 21.7% | 6.7% | 21.7% |
| 2026-09 | high_volatility | **FRAGILE** | **FRAGILE** | 359 | 20.6% | 18.9% | 3.1% | 57.4% |

## D1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-10 | trending_up | **MISMATCH** | **MATCH** | 17 | 0.0% | 100.0% | 0.0% | 0.0% |
| 2024-11 | trending_up | **MISMATCH** | **MATCH** | 25 | 0.0% | 56.0% | 0.0% | 44.0% |
| 2024-12 | ranging | **MATCH** | **MISMATCH** | 27 | 48.1% | 33.3% | 11.1% | 7.4% |
| 2025-01 | ranging | **MATCH** | **MISMATCH** | 27 | 59.3% | 40.7% | 0.0% | 0.0% |
| 2025-02 | high_volatility | **FRAGILE** | **FRAGILE** | 24 | 29.2% | 0.0% | 12.5% | 58.3% |
| 2025-03 | ranging | **MATCH** | **MISMATCH** | 26 | 69.2% | 0.0% | 26.9% | 3.8% |
| 2025-04 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 15.4% | 0.0% | 0.0% | 84.6% |
| 2025-05 | ranging | **MATCH** | **MISMATCH** | 26 | 80.8% | 11.5% | 0.0% | 7.7% |
| 2025-06 | ranging | **MATCH** | **MISMATCH** | 26 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2025-07 | ranging | **MATCH** | **MISMATCH** | 27 | 70.4% | 29.6% | 0.0% | 0.0% |
| 2025-08 | ranging | **MATCH** | **MISMATCH** | 26 | 53.8% | 3.8% | 0.0% | 42.3% |
| 2025-09 | ranging | **MATCH** | **MISMATCH** | 26 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2025-10 | high_volatility | **FRAGILE** | **FRAGILE** | 27 | 25.9% | 11.1% | 0.0% | 63.0% |
| 2025-11 | trending_up | **MISMATCH** | **MATCH** | 25 | 32.0% | 68.0% | 0.0% | 0.0% |
| 2025-12 | ranging | **MATCH** | **MISMATCH** | 26 | 53.8% | 15.4% | 0.0% | 30.8% |
| 2026-01 | ranging | **MATCH** | **MISMATCH** | 25 | 60.0% | 12.0% | 0.0% | 28.0% |
| 2026-02 | high_volatility | **FRAGILE** | **FRAGILE** | 20 | 20.0% | 0.0% | 0.0% | 80.0% |
| 2026-03 | ranging | **MATCH** | **MISMATCH** | 26 | 53.8% | 46.2% | 0.0% | 0.0% |
| 2026-04 | ranging | **MATCH** | **MISMATCH** | 26 | 84.6% | 0.0% | 0.0% | 15.4% |
| 2026-05 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 15.4% | 19.2% | 0.0% | 65.4% |
| 2026-06 | trending_up | **MISMATCH** | **MATCH** | 26 | 0.0% | 100.0% | 0.0% | 0.0% |
| 2026-07 | high_volatility | **FRAGILE** | **FRAGILE** | 27 | 0.0% | 18.5% | 0.0% | 81.5% |
| 2026-08 | high_volatility | **MISMATCH** | **MATCH** | 26 | 0.0% | 19.2% | 34.6% | 46.2% |
| 2026-09 | trending_down | **MISMATCH** | **MATCH** | 18 | 0.0% | 22.2% | 72.2% | 5.6% |

## Audit takeaways

1. **H1 meanrev MATCH in 18/25 months** vs trendfollow MATCH in 3/25 — modal H1 month regime is `ranging` (21/25).
2. **H1 trend-MATCH pockets** when combined trend shares edge ranging: 2025-07, 2025-08, 2025-12 (dominant label still ranging).
3. **Fragile H1 months** (both families FRAGILE): 2024-11, 2025-04, 2026-01, 2026-09.
4. **D1 is more two-sided**: 6 trendfollow MATCH months and 6 fragile months; high_vol dominates 7/24 D1 months.
5. First/last months may be thin after regime warmup (2024-09 / 2026-09).
6. Monthly MATCH is **ex-post**, not a forward signal. Live research gate should use nowcast + 30d shares, not calendar-month prophecy.

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
