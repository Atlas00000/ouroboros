# USDCAD — Regime audit & fit tagging (monthly, 2y)

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
| `H1|meanrev` | 20 | 3 | 2 |
| `H1|trendfollow` | 3 | 20 | 2 |
| `D1|meanrev` | 9 | 7 | 8 |
| `D1|trendfollow` | 6 | 10 | 8 |

Dominant-regime months (H1): {'ranging': 22, 'high_volatility': 2, 'trending_up': 1}
Dominant-regime months (D1): {'trending_up': 2, 'high_volatility': 8, 'ranging': 12, 'trending_down': 2}

## H1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-09 | ranging | **MISMATCH** | **MATCH** | 149 | 39.6% | 21.5% | 18.8% | 20.1% |
| 2024-10 | ranging | **MISMATCH** | **MATCH** | 552 | 41.8% | 37.7% | 5.6% | 14.9% |
| 2024-11 | high_volatility | **FRAGILE** | **FRAGILE** | 501 | 27.3% | 3.8% | 13.0% | 55.9% |
| 2024-12 | ranging | **MATCH** | **MISMATCH** | 505 | 44.6% | 13.7% | 3.6% | 38.2% |
| 2025-01 | high_volatility | **FRAGILE** | **FRAGILE** | 526 | 34.4% | 17.3% | 1.9% | 46.4% |
| 2025-02 | ranging | **MATCH** | **MISMATCH** | 480 | 55.8% | 13.1% | 9.2% | 21.9% |
| 2025-03 | ranging | **MATCH** | **MISMATCH** | 503 | 42.9% | 15.3% | 16.7% | 25.0% |
| 2025-04 | ranging | **MATCH** | **MISMATCH** | 528 | 53.2% | 9.7% | 7.8% | 29.4% |
| 2025-05 | ranging | **MATCH** | **MISMATCH** | 526 | 54.0% | 23.8% | 17.7% | 4.6% |
| 2025-06 | ranging | **MATCH** | **MISMATCH** | 506 | 46.2% | 16.4% | 15.4% | 21.9% |
| 2025-07 | ranging | **MATCH** | **MISMATCH** | 539 | 45.8% | 26.0% | 11.1% | 17.1% |
| 2025-08 | ranging | **MATCH** | **MISMATCH** | 504 | 57.5% | 15.9% | 10.7% | 15.9% |
| 2025-09 | ranging | **MATCH** | **MISMATCH** | 528 | 46.0% | 23.7% | 8.7% | 21.6% |
| 2025-10 | ranging | **MATCH** | **MISMATCH** | 548 | 52.6% | 10.9% | 2.0% | 34.5% |
| 2025-11 | ranging | **MATCH** | **MISMATCH** | 482 | 46.9% | 13.9% | 11.2% | 28.0% |
| 2025-12 | ranging | **MATCH** | **MISMATCH** | 522 | 59.8% | 6.7% | 15.1% | 18.4% |
| 2026-01 | ranging | **MATCH** | **MISMATCH** | 504 | 34.5% | 13.7% | 17.5% | 34.3% |
| 2026-02 | ranging | **MATCH** | **MISMATCH** | 480 | 46.0% | 14.0% | 7.5% | 32.5% |
| 2026-03 | ranging | **MATCH** | **MISMATCH** | 531 | 45.8% | 20.3% | 6.2% | 27.7% |
| 2026-04 | ranging | **MATCH** | **MISMATCH** | 528 | 43.6% | 10.8% | 31.8% | 13.8% |
| 2026-05 | ranging | **MATCH** | **MISMATCH** | 504 | 50.6% | 24.0% | 0.8% | 24.6% |
| 2026-06 | ranging | **MATCH** | **MISMATCH** | 528 | 39.8% | 22.7% | 4.5% | 33.0% |
| 2026-07 | ranging | **MATCH** | **MISMATCH** | 549 | 53.7% | 13.7% | 8.0% | 24.6% |
| 2026-08 | ranging | **MATCH** | **MISMATCH** | 507 | 47.5% | 10.8% | 21.1% | 20.5% |
| 2026-09 | trending_up | **MISMATCH** | **MATCH** | 304 | 22.4% | 35.9% | 20.4% | 21.4% |

## D1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-10 | trending_up | **MISMATCH** | **MATCH** | 12 | 0.0% | 100.0% | 0.0% | 0.0% |
| 2024-11 | high_volatility | **FRAGILE** | **FRAGILE** | 25 | 0.0% | 28.0% | 0.0% | 72.0% |
| 2024-12 | ranging | **MATCH** | **MISMATCH** | 27 | 44.4% | 22.2% | 0.0% | 33.3% |
| 2025-01 | ranging | **MATCH** | **MISMATCH** | 27 | 77.8% | 22.2% | 0.0% | 0.0% |
| 2025-02 | high_volatility | **FRAGILE** | **FRAGILE** | 24 | 12.5% | 0.0% | 0.0% | 87.5% |
| 2025-03 | ranging | **MATCH** | **MISMATCH** | 26 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2025-04 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 15.4% | 0.0% | 3.8% | 80.8% |
| 2025-05 | ranging | **MATCH** | **MISMATCH** | 26 | 84.6% | 0.0% | 15.4% | 0.0% |
| 2025-06 | trending_down | **MISMATCH** | **MATCH** | 26 | 42.3% | 0.0% | 57.7% | 0.0% |
| 2025-07 | ranging | **MATCH** | **MISMATCH** | 27 | 92.6% | 7.4% | 0.0% | 0.0% |
| 2025-08 | ranging | **MISMATCH** | **MISMATCH** | 26 | 50.0% | 50.0% | 0.0% | 0.0% |
| 2025-09 | ranging | **MATCH** | **MISMATCH** | 26 | 88.5% | 11.5% | 0.0% | 0.0% |
| 2025-10 | ranging | **MATCH** | **MISMATCH** | 27 | 59.3% | 40.7% | 0.0% | 0.0% |
| 2025-11 | high_volatility | **FRAGILE** | **FRAGILE** | 25 | 28.0% | 0.0% | 0.0% | 72.0% |
| 2025-12 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 0.0% | 0.0% | 30.8% | 69.2% |
| 2026-01 | ranging | **MISMATCH** | **MATCH** | 26 | 38.5% | 30.8% | 15.4% | 15.4% |
| 2026-02 | high_volatility | **FRAGILE** | **FRAGILE** | 24 | 41.7% | 0.0% | 0.0% | 58.3% |
| 2026-03 | ranging | **MATCH** | **MISMATCH** | 27 | 85.2% | 14.8% | 0.0% | 0.0% |
| 2026-04 | ranging | **MISMATCH** | **MATCH** | 26 | 34.6% | 34.6% | 26.9% | 3.8% |
| 2026-05 | ranging | **MATCH** | **MISMATCH** | 26 | 42.3% | 23.1% | 0.0% | 34.6% |
| 2026-06 | trending_up | **MISMATCH** | **MATCH** | 26 | 0.0% | 61.5% | 0.0% | 38.5% |
| 2026-07 | trending_down | **MISMATCH** | **MATCH** | 27 | 11.1% | 0.0% | 51.9% | 37.0% |
| 2026-08 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 11.5% | 0.0% | 23.1% | 65.4% |
| 2026-09 | high_volatility | **FRAGILE** | **FRAGILE** | 17 | 35.3% | 0.0% | 0.0% | 64.7% |

## Audit takeaways

1. **H1 meanrev MATCH in 20/25 months** vs trendfollow MATCH in 3/25 — modal H1 month regime is `ranging` (22/25).
2. **Fragile months** are present but do not form long consecutive clusters on H1.
3. **Trend MATCH months** (dominant trending_*): 2026-09.
4. **TF disagreement is expected** when dominant regime is ranging but trend shares outvote ranging on the fit map (or the reverse).
5. First/last months may be thin after regime warmup (2024-09 / 2026-09).
6. Monthly MATCH is **ex-post**, not a forward signal. Live research gate should use nowcast + 30d shares, not calendar-month prophecy.

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
