# GBPJPY — Regime audit & fit tagging (monthly, 2y)

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
| `D1|meanrev` | 12 | 3 | 9 |
| `D1|trendfollow` | 3 | 12 | 9 |

Dominant-regime months (H1): {'ranging': 20, 'high_volatility': 5}
Dominant-regime months (D1): {'ranging': 13, 'high_volatility': 9, 'trending_up': 1, 'trending_down': 1}

## H1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-09 | ranging | **MATCH** | **MISMATCH** | 149 | 47.0% | 30.2% | 0.0% | 22.8% |
| 2024-10 | ranging | **MATCH** | **MISMATCH** | 552 | 51.4% | 29.0% | 15.6% | 4.0% |
| 2024-11 | ranging | **MATCH** | **MISMATCH** | 501 | 42.5% | 9.6% | 15.6% | 32.3% |
| 2024-12 | ranging | **MATCH** | **MISMATCH** | 504 | 52.0% | 18.3% | 6.9% | 22.8% |
| 2025-01 | ranging | **MATCH** | **MISMATCH** | 526 | 43.3% | 15.6% | 10.3% | 30.8% |
| 2025-02 | high_volatility | **FRAGILE** | **FRAGILE** | 480 | 32.9% | 11.7% | 15.4% | 40.0% |
| 2025-03 | ranging | **MATCH** | **MISMATCH** | 503 | 44.9% | 17.3% | 13.5% | 24.3% |
| 2025-04 | ranging | **MATCH** | **MISMATCH** | 528 | 52.1% | 9.3% | 5.1% | 33.5% |
| 2025-05 | ranging | **MATCH** | **MISMATCH** | 526 | 50.4% | 24.1% | 20.2% | 5.3% |
| 2025-06 | ranging | **MATCH** | **MISMATCH** | 506 | 45.5% | 26.3% | 12.6% | 15.6% |
| 2025-07 | ranging | **MATCH** | **MISMATCH** | 539 | 53.4% | 12.6% | 8.5% | 25.4% |
| 2025-08 | ranging | **MATCH** | **MISMATCH** | 504 | 56.0% | 16.1% | 5.4% | 22.6% |
| 2025-09 | ranging | **MATCH** | **MISMATCH** | 528 | 62.7% | 15.5% | 11.0% | 10.8% |
| 2025-10 | high_volatility | **FRAGILE** | **FRAGILE** | 548 | 26.5% | 7.1% | 11.7% | 54.7% |
| 2025-11 | ranging | **MATCH** | **MISMATCH** | 482 | 60.6% | 19.1% | 1.2% | 19.1% |
| 2025-12 | ranging | **MATCH** | **MISMATCH** | 522 | 64.0% | 15.5% | 8.4% | 12.1% |
| 2026-01 | high_volatility | **FRAGILE** | **FRAGILE** | 504 | 28.6% | 19.8% | 11.7% | 39.9% |
| 2026-02 | high_volatility | **FRAGILE** | **FRAGILE** | 479 | 28.2% | 20.5% | 12.3% | 39.0% |
| 2026-03 | ranging | **MATCH** | **MISMATCH** | 530 | 61.3% | 13.8% | 12.6% | 12.3% |
| 2026-04 | ranging | **MATCH** | **MISMATCH** | 522 | 49.6% | 32.6% | 4.6% | 13.2% |
| 2026-05 | ranging | **MATCH** | **MISMATCH** | 503 | 45.3% | 17.7% | 4.8% | 32.2% |
| 2026-06 | ranging | **MATCH** | **MISMATCH** | 528 | 47.7% | 18.9% | 9.1% | 24.2% |
| 2026-07 | ranging | **MATCH** | **MISMATCH** | 549 | 53.0% | 16.9% | 10.7% | 19.3% |
| 2026-08 | ranging | **MATCH** | **MISMATCH** | 507 | 51.7% | 18.9% | 9.3% | 20.1% |
| 2026-09 | high_volatility | **FRAGILE** | **FRAGILE** | 213 | 37.1% | 0.0% | 0.0% | 62.9% |

## D1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-10 | ranging | **MATCH** | **MISMATCH** | 15 | 80.0% | 20.0% | 0.0% | 0.0% |
| 2024-11 | ranging | **MATCH** | **MISMATCH** | 25 | 84.0% | 4.0% | 12.0% | 0.0% |
| 2024-12 | ranging | **MISMATCH** | **MATCH** | 27 | 33.3% | 33.3% | 33.3% | 0.0% |
| 2025-01 | high_volatility | **FRAGILE** | **FRAGILE** | 27 | 14.8% | 22.2% | 0.0% | 63.0% |
| 2025-02 | high_volatility | **FRAGILE** | **FRAGILE** | 24 | 41.7% | 0.0% | 0.0% | 58.3% |
| 2025-03 | ranging | **MATCH** | **MISMATCH** | 26 | 73.1% | 26.9% | 0.0% | 0.0% |
| 2025-04 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 30.8% | 0.0% | 0.0% | 69.2% |
| 2025-05 | ranging | **MATCH** | **MISMATCH** | 26 | 57.7% | 42.3% | 0.0% | 0.0% |
| 2025-06 | ranging | **MATCH** | **MISMATCH** | 26 | 92.3% | 7.7% | 0.0% | 0.0% |
| 2025-07 | ranging | **MATCH** | **MISMATCH** | 27 | 85.2% | 14.8% | 0.0% | 0.0% |
| 2025-08 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 7.7% | 15.4% | 0.0% | 76.9% |
| 2025-09 | ranging | **MATCH** | **MISMATCH** | 26 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2025-10 | high_volatility | **FRAGILE** | **FRAGILE** | 27 | 18.5% | 18.5% | 0.0% | 63.0% |
| 2025-11 | ranging | **MATCH** | **MISMATCH** | 25 | 60.0% | 8.0% | 0.0% | 32.0% |
| 2025-12 | trending_up | **MISMATCH** | **MATCH** | 26 | 0.0% | 80.8% | 0.0% | 19.2% |
| 2026-01 | ranging | **MATCH** | **MISMATCH** | 26 | 50.0% | 30.8% | 0.0% | 19.2% |
| 2026-02 | high_volatility | **FRAGILE** | **FRAGILE** | 24 | 12.5% | 0.0% | 0.0% | 87.5% |
| 2026-03 | ranging | **MATCH** | **MISMATCH** | 27 | 88.9% | 0.0% | 0.0% | 11.1% |
| 2026-04 | ranging | **MATCH** | **MISMATCH** | 26 | 61.5% | 19.2% | 0.0% | 19.2% |
| 2026-05 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 19.2% | 3.8% | 0.0% | 76.9% |
| 2026-06 | ranging | **MATCH** | **MISMATCH** | 26 | 80.8% | 0.0% | 0.0% | 19.2% |
| 2026-07 | high_volatility | **FRAGILE** | **FRAGILE** | 27 | 25.9% | 14.8% | 0.0% | 59.3% |
| 2026-08 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 38.5% | 19.2% | 0.0% | 42.3% |
| 2026-09 | trending_down | **MISMATCH** | **MATCH** | 10 | 0.0% | 40.0% | 60.0% | 0.0% |

## Audit takeaways

1. **H1 meanrev MATCH in 20/25 months** vs trendfollow MATCH in 0/25 — modal H1 month regime is `ranging` (20/25).
2. **Fragile clusters** (both families FRAGILE): 2026-01–2026-02.
3. **Trend MATCH months** with a trending_* dominant regime are scarce in this window.
4. **TF disagreement is expected** when dominant regime is ranging but trend shares outvote ranging on the fit map (or the reverse).
5. First/last months may be thin after regime warmup (2024-09 / 2026-09).
6. Monthly MATCH is **ex-post**, not a forward signal. Live research gate should use nowcast + 30d shares, not calendar-month prophecy.

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
