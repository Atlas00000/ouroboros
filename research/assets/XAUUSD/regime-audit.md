# XAUUSD — Regime audit & fit tagging (monthly, 2y)

> Ex-post calendar-month boards · `regimes.rule_v1` labels → `fit.map_v0`  
> Window: 2024-09 → 2026-10 (26 H1 months with confirmed bars after warmup)

## Method

1. Load H1 / D1 OHLCV (~800d lookback; M1 depth gate passes).
2. Run `regime_feature_frame` → confirmed regime per bar.
3. Slice each calendar month; map regimes → MATCH / MISMATCH / FRAGILE per edge family.
4. Dominant tag = largest fit-share (ties break MISMATCH > FRAGILE > MATCH).

Families: **meanrev** home=`ranging`; **trendfollow** home=`trending_up|trending_down`; both treat `high_volatility` as FRAGILE.

## Tag summary (months with bars)

| TF × family | MATCH | MISMATCH | FRAGILE |
| --- | ---: | ---: | ---: |
| `H1|meanrev` | 15 | 3 | 8 |
| `H1|trendfollow` | 3 | 15 | 8 |
| `D1|meanrev` | 12 | 5 | 8 |
| `D1|trendfollow` | 5 | 12 | 8 |

Dominant-regime months (H1): {'ranging': 16, 'high_volatility': 8, 'trending_up': 1, 'trending_down': 1}
Dominant-regime months (D1): {'ranging': 12, 'high_volatility': 8, 'trending_up': 4, 'trending_down': 1}

## H1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-09 | ranging | **MATCH** | **MISMATCH** | 136 | 48.5% | 9.6% | 9.6% | 32.4% |
| 2024-10 | ranging | **MATCH** | **MISMATCH** | 530 | 47.0% | 32.3% | 2.6% | 18.1% |
| 2024-11 | high_volatility | **FRAGILE** | **FRAGILE** | 477 | 34.4% | 21.2% | 5.9% | 38.6% |
| 2024-12 | ranging | **MATCH** | **MISMATCH** | 480 | 46.7% | 18.1% | 17.5% | 17.7% |
| 2025-01 | trending_up | **MISMATCH** | **MATCH** | 502 | 37.8% | 38.8% | 11.4% | 12.0% |
| 2025-02 | high_volatility | **FRAGILE** | **FRAGILE** | 458 | 21.6% | 19.9% | 1.7% | 56.8% |
| 2025-03 | ranging | **MATCH** | **MISMATCH** | 484 | 46.7% | 25.0% | 1.0% | 27.3% |
| 2025-04 | high_volatility | **FRAGILE** | **FRAGILE** | 483 | 17.2% | 10.4% | 1.4% | 71.0% |
| 2025-05 | ranging | **MATCH** | **MISMATCH** | 503 | 43.5% | 17.5% | 20.7% | 18.3% |
| 2025-06 | ranging | **MATCH** | **MISMATCH** | 482 | 71.0% | 10.8% | 16.4% | 1.9% |
| 2025-07 | ranging | **MATCH** | **MISMATCH** | 512 | 51.2% | 25.0% | 15.0% | 8.8% |
| 2025-08 | ranging | **MATCH** | **MISMATCH** | 483 | 49.7% | 9.5% | 6.8% | 34.0% |
| 2025-09 | high_volatility | **FRAGILE** | **FRAGILE** | 504 | 34.7% | 24.6% | 5.4% | 35.3% |
| 2025-10 | high_volatility | **FRAGILE** | **FRAGILE** | 527 | 15.9% | 21.4% | 1.1% | 61.5% |
| 2025-11 | ranging | **MATCH** | **MISMATCH** | 459 | 57.7% | 26.1% | 3.7% | 12.4% |
| 2025-12 | ranging | **MATCH** | **MISMATCH** | 498 | 60.6% | 19.9% | 3.2% | 16.3% |
| 2026-01 | high_volatility | **FRAGILE** | **FRAGILE** | 480 | 39.4% | 18.8% | 0.6% | 41.2% |
| 2026-02 | ranging | **MATCH** | **MISMATCH** | 457 | 49.0% | 15.3% | 5.0% | 30.6% |
| 2026-03 | high_volatility | **FRAGILE** | **FRAGILE** | 508 | 38.2% | 10.0% | 12.8% | 39.0% |
| 2026-04 | ranging | **MATCH** | **MISMATCH** | 483 | 57.8% | 17.8% | 15.3% | 9.1% |
| 2026-05 | ranging | **MATCH** | **MISMATCH** | 482 | 51.9% | 15.6% | 14.9% | 17.6% |
| 2026-06 | high_volatility | **FRAGILE** | **FRAGILE** | 503 | 26.6% | 8.7% | 19.9% | 44.7% |
| 2026-07 | ranging | **MISMATCH** | **MATCH** | 524 | 40.6% | 20.0% | 23.5% | 15.8% |
| 2026-08 | ranging | **MATCH** | **MISMATCH** | 485 | 48.9% | 19.4% | 8.5% | 23.3% |
| 2026-09 | ranging | **MATCH** | **MISMATCH** | 340 | 44.4% | 10.0% | 7.4% | 38.2% |
| 2026-10 | trending_down | **MISMATCH** | **MATCH** | 41 | 36.6% | 0.0% | 63.4% | 0.0% |

## D1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-10 | ranging | **MATCH** | **MISMATCH** | 15 | 80.0% | 0.0% | 0.0% | 20.0% |
| 2024-11 | high_volatility | **FRAGILE** | **FRAGILE** | 25 | 0.0% | 0.0% | 0.0% | 100.0% |
| 2024-12 | ranging | **MATCH** | **MISMATCH** | 27 | 88.9% | 11.1% | 0.0% | 0.0% |
| 2025-01 | trending_up | **MISMATCH** | **MATCH** | 27 | 33.3% | 48.1% | 0.0% | 18.5% |
| 2025-02 | high_volatility | **FRAGILE** | **FRAGILE** | 24 | 0.0% | 25.0% | 0.0% | 75.0% |
| 2025-03 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 26.9% | 30.8% | 0.0% | 42.3% |
| 2025-04 | high_volatility | **FRAGILE** | **FRAGILE** | 25 | 0.0% | 20.0% | 0.0% | 80.0% |
| 2025-05 | ranging | **MATCH** | **MISMATCH** | 26 | 84.6% | 0.0% | 0.0% | 15.4% |
| 2025-06 | ranging | **MATCH** | **MISMATCH** | 26 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2025-07 | ranging | **MATCH** | **MISMATCH** | 27 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2025-08 | ranging | **MATCH** | **MISMATCH** | 26 | 61.5% | 0.0% | 0.0% | 38.5% |
| 2025-09 | trending_up | **MISMATCH** | **MATCH** | 26 | 7.7% | 80.8% | 0.0% | 11.5% |
| 2025-10 | trending_up | **MISMATCH** | **MATCH** | 27 | 0.0% | 55.6% | 0.0% | 44.4% |
| 2025-11 | ranging | **MATCH** | **MISMATCH** | 25 | 60.0% | 4.0% | 0.0% | 36.0% |
| 2025-12 | trending_up | **MISMATCH** | **MATCH** | 25 | 20.0% | 80.0% | 0.0% | 0.0% |
| 2026-01 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 19.2% | 0.0% | 0.0% | 80.8% |
| 2026-02 | high_volatility | **FRAGILE** | **FRAGILE** | 24 | 20.8% | 0.0% | 0.0% | 79.2% |
| 2026-03 | ranging | **MATCH** | **MISMATCH** | 27 | 63.0% | 0.0% | 37.0% | 0.0% |
| 2026-04 | ranging | **MATCH** | **MISMATCH** | 25 | 52.0% | 0.0% | 4.0% | 44.0% |
| 2026-05 | ranging | **MATCH** | **MISMATCH** | 26 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2026-06 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 34.6% | 0.0% | 0.0% | 65.4% |
| 2026-07 | ranging | **MATCH** | **MISMATCH** | 27 | 85.2% | 0.0% | 0.0% | 14.8% |
| 2026-08 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 23.1% | 0.0% | 0.0% | 76.9% |
| 2026-09 | ranging | **MATCH** | **MISMATCH** | 26 | 61.5% | 0.0% | 26.9% | 11.5% |
| 2026-10 | trending_down | **MISMATCH** | **MATCH** | 4 | 0.0% | 0.0% | 100.0% | 0.0% |

## Audit takeaways

1. **H1 meanrev MATCH in 15/26 months** vs trendfollow MATCH in 3/26 — modal H1 month regime is `ranging` (16/26).
2. **Fragile clusters** (both families FRAGILE): 2025-09–2025-10.
3. **Trend MATCH months** (dominant trending_*): 2025-01, 2026-10.
4. **TF disagreement is expected** when dominant regime is ranging but trend shares outvote ranging on the fit map (or the reverse).
5. First/last months may be thin after regime warmup (2024-09 / 2026-10).
6. Monthly MATCH is **ex-post**, not a forward signal. Live research gate should use nowcast + 30d shares, not calendar-month prophecy.

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
