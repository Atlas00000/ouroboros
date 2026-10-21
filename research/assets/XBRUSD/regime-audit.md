# XBRUSD — Regime audit & fit tagging (monthly, 2y)

> Ex-post calendar-month boards · `regimes.rule_v1` labels → `fit.map_v0`  
> Window: 2024-10 → 2026-10 (25 H1 months with confirmed bars after warmup)

## Method

1. Load H1 / D1 OHLCV (~800d lookback; M1 depth gate passes).
2. Run `regime_feature_frame` → confirmed regime per bar.
3. Slice each calendar month; map regimes → MATCH / MISMATCH / FRAGILE per edge family.
4. Dominant tag = largest fit-share (ties break MISMATCH > FRAGILE > MATCH).

Families: **meanrev** home=`ranging`; **trendfollow** home=`trending_up|trending_down`; both treat `high_volatility` as FRAGILE.

## Tag summary (months with bars)

| TF × family | MATCH | MISMATCH | FRAGILE |
| --- | ---: | ---: | ---: |
| `H1|meanrev` | 17 | 2 | 6 |
| `H1|trendfollow` | 2 | 17 | 6 |
| `D1|meanrev` | 11 | 5 | 8 |
| `D1|trendfollow` | 5 | 11 | 8 |

Dominant-regime months (H1): {'ranging': 19, 'high_volatility': 6}
Dominant-regime months (D1): {'ranging': 12, 'trending_up': 2, 'trending_down': 2, 'high_volatility': 8}

## H1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-10 | ranging | **MATCH** | **MISMATCH** | 224 | 62.5% | 22.3% | 6.2% | 8.9% |
| 2024-11 | ranging | **MATCH** | **MISMATCH** | 416 | 60.8% | 13.9% | 12.7% | 12.5% |
| 2024-12 | ranging | **MATCH** | **MISMATCH** | 417 | 59.5% | 24.2% | 13.2% | 3.1% |
| 2025-01 | high_volatility | **FRAGILE** | **FRAGILE** | 439 | 38.5% | 17.3% | 2.5% | 41.7% |
| 2025-02 | ranging | **MATCH** | **MISMATCH** | 400 | 44.5% | 17.5% | 15.8% | 22.2% |
| 2025-03 | ranging | **MATCH** | **MISMATCH** | 424 | 51.9% | 16.5% | 6.1% | 25.5% |
| 2025-04 | high_volatility | **FRAGILE** | **FRAGILE** | 422 | 24.2% | 5.0% | 13.3% | 57.6% |
| 2025-05 | ranging | **MATCH** | **MISMATCH** | 439 | 47.6% | 22.1% | 13.9% | 16.4% |
| 2025-06 | ranging | **MATCH** | **MISMATCH** | 418 | 45.5% | 12.9% | 1.7% | 40.0% |
| 2025-07 | ranging | **MATCH** | **MISMATCH** | 458 | 45.4% | 28.6% | 14.4% | 11.6% |
| 2025-08 | ranging | **MATCH** | **MISMATCH** | 420 | 48.8% | 16.9% | 15.2% | 19.0% |
| 2025-09 | ranging | **MISMATCH** | **MATCH** | 438 | 34.2% | 21.0% | 16.7% | 28.1% |
| 2025-10 | high_volatility | **FRAGILE** | **FRAGILE** | 464 | 39.2% | 4.5% | 16.4% | 39.9% |
| 2025-11 | ranging | **MATCH** | **MISMATCH** | 414 | 51.9% | 16.7% | 10.4% | 21.0% |
| 2025-12 | ranging | **MATCH** | **MISMATCH** | 447 | 61.1% | 15.0% | 19.2% | 4.7% |
| 2026-01 | high_volatility | **FRAGILE** | **FRAGILE** | 439 | 23.2% | 13.0% | 7.7% | 56.0% |
| 2026-02 | high_volatility | **FRAGILE** | **FRAGILE** | 420 | 34.5% | 19.8% | 8.3% | 37.4% |
| 2026-03 | high_volatility | **FRAGILE** | **FRAGILE** | 467 | 11.1% | 12.2% | 0.6% | 76.0% |
| 2026-04 | ranging | **MATCH** | **MISMATCH** | 449 | 48.1% | 27.6% | 10.2% | 14.0% |
| 2026-05 | ranging | **MATCH** | **MISMATCH** | 448 | 49.8% | 12.7% | 23.2% | 14.3% |
| 2026-06 | ranging | **MATCH** | **MISMATCH** | 467 | 44.1% | 10.9% | 30.2% | 14.8% |
| 2026-07 | ranging | **MISMATCH** | **MATCH** | 488 | 30.9% | 27.7% | 11.9% | 29.5% |
| 2026-08 | ranging | **MATCH** | **MISMATCH** | 451 | 55.9% | 24.4% | 7.8% | 12.0% |
| 2026-09 | ranging | **MATCH** | **MISMATCH** | 466 | 39.7% | 13.1% | 12.0% | 35.2% |
| 2026-10 | ranging | **MATCH** | **MISMATCH** | 101 | 50.5% | 18.8% | 10.9% | 19.8% |

## D1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-11 | ranging | **MATCH** | **MISMATCH** | 17 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2024-12 | ranging | **MATCH** | **MISMATCH** | 21 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2025-01 | trending_up | **MISMATCH** | **MATCH** | 22 | 13.6% | 45.5% | 0.0% | 40.9% |
| 2025-02 | trending_down | **MISMATCH** | **MATCH** | 20 | 0.0% | 0.0% | 55.0% | 45.0% |
| 2025-03 | high_volatility | **FRAGILE** | **FRAGILE** | 21 | 23.8% | 0.0% | 19.0% | 57.1% |
| 2025-04 | high_volatility | **FRAGILE** | **FRAGILE** | 21 | 19.0% | 0.0% | 0.0% | 81.0% |
| 2025-05 | ranging | **MATCH** | **MISMATCH** | 22 | 81.8% | 0.0% | 0.0% | 18.2% |
| 2025-06 | ranging | **MATCH** | **MISMATCH** | 21 | 52.4% | 0.0% | 0.0% | 47.6% |
| 2025-07 | ranging | **MATCH** | **MISMATCH** | 23 | 47.8% | 0.0% | 17.4% | 34.8% |
| 2025-08 | ranging | **MATCH** | **MISMATCH** | 21 | 90.5% | 0.0% | 9.5% | 0.0% |
| 2025-09 | ranging | **MATCH** | **MISMATCH** | 22 | 95.5% | 0.0% | 4.5% | 0.0% |
| 2025-10 | high_volatility | **FRAGILE** | **FRAGILE** | 23 | 0.0% | 0.0% | 0.0% | 100.0% |
| 2025-11 | ranging | **MATCH** | **MISMATCH** | 20 | 75.0% | 0.0% | 0.0% | 25.0% |
| 2025-12 | ranging | **MATCH** | **MISMATCH** | 22 | 90.9% | 0.0% | 0.0% | 9.1% |
| 2026-01 | high_volatility | **FRAGILE** | **FRAGILE** | 21 | 28.6% | 0.0% | 0.0% | 71.4% |
| 2026-02 | high_volatility | **FRAGILE** | **FRAGILE** | 20 | 0.0% | 0.0% | 0.0% | 100.0% |
| 2026-03 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 0.0% | 0.0% | 0.0% | 100.0% |
| 2026-04 | ranging | **MATCH** | **MISMATCH** | 25 | 56.0% | 0.0% | 0.0% | 44.0% |
| 2026-05 | ranging | **MATCH** | **MISMATCH** | 26 | 76.9% | 0.0% | 23.1% | 0.0% |
| 2026-06 | trending_down | **MISMATCH** | **MATCH** | 26 | 0.0% | 0.0% | 100.0% | 0.0% |
| 2026-07 | ranging | **MISMATCH** | **MATCH** | 27 | 29.6% | 25.9% | 29.6% | 14.8% |
| 2026-08 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 46.2% | 0.0% | 0.0% | 53.8% |
| 2026-09 | trending_up | **MISMATCH** | **MATCH** | 26 | 19.2% | 69.2% | 0.0% | 11.5% |
| 2026-10 | high_volatility | **FRAGILE** | **FRAGILE** | 6 | 33.3% | 0.0% | 0.0% | 66.7% |

## Audit takeaways

1. **H1 meanrev MATCH in 17/25 months** vs trendfollow MATCH in 2/25 — modal H1 month regime is `ranging` (19/25).
2. **Fragile clusters** (both families FRAGILE): 2026-01–2026-03.
3. **Trend MATCH months** with a trending_* dominant regime are scarce in this window.
4. **TF disagreement is expected** when dominant regime is ranging but trend shares outvote ranging on the fit map (or the reverse).
5. First/last months may be thin after regime warmup (2024-10 / 2026-10).
6. Monthly MATCH is **ex-post**, not a forward signal. Live research gate should use nowcast + 30d shares, not calendar-month prophecy.

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
