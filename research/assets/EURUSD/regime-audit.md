# EURUSD — Regime audit & fit tagging (monthly, 2y)

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
| `H1|meanrev` | 19 | 1 | 6 |
| `H1|trendfollow` | 1 | 19 | 6 |
| `D1|meanrev` | 8 | 9 | 8 |
| `D1|trendfollow` | 9 | 9 | 7 |

Dominant-regime months (H1): {'high_volatility': 6, 'ranging': 20}
Dominant-regime months (D1): {'trending_down': 4, 'high_volatility': 9, 'ranging': 8, 'trending_up': 4}

## H1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-09 | high_volatility | **FRAGILE** | **FRAGILE** | 146 | 20.5% | 19.2% | 11.0% | 49.3% |
| 2024-10 | ranging | **MATCH** | **MISMATCH** | 552 | 54.2% | 8.7% | 28.6% | 8.5% |
| 2024-11 | high_volatility | **FRAGILE** | **FRAGILE** | 501 | 23.6% | 7.0% | 4.4% | 65.1% |
| 2024-12 | ranging | **MATCH** | **MISMATCH** | 505 | 60.8% | 10.5% | 7.1% | 21.6% |
| 2025-01 | ranging | **MATCH** | **MISMATCH** | 526 | 40.5% | 13.5% | 11.6% | 34.4% |
| 2025-02 | ranging | **MATCH** | **MISMATCH** | 480 | 45.4% | 21.2% | 11.2% | 22.1% |
| 2025-03 | ranging | **MATCH** | **MISMATCH** | 503 | 58.6% | 19.1% | 9.3% | 12.9% |
| 2025-04 | high_volatility | **FRAGILE** | **FRAGILE** | 528 | 40.3% | 13.1% | 2.5% | 44.1% |
| 2025-05 | ranging | **MATCH** | **MISMATCH** | 526 | 50.6% | 19.6% | 17.1% | 12.7% |
| 2025-06 | ranging | **MATCH** | **MISMATCH** | 506 | 51.2% | 24.3% | 10.1% | 14.4% |
| 2025-07 | ranging | **MATCH** | **MISMATCH** | 539 | 46.6% | 16.0% | 10.2% | 27.3% |
| 2025-08 | ranging | **MATCH** | **MISMATCH** | 504 | 42.7% | 20.8% | 18.7% | 17.9% |
| 2025-09 | ranging | **MISMATCH** | **MATCH** | 528 | 39.6% | 28.4% | 17.2% | 14.8% |
| 2025-10 | ranging | **MATCH** | **MISMATCH** | 548 | 48.4% | 13.0% | 18.1% | 20.6% |
| 2025-11 | ranging | **MATCH** | **MISMATCH** | 482 | 53.5% | 11.0% | 16.2% | 19.3% |
| 2025-12 | ranging | **MATCH** | **MISMATCH** | 522 | 58.8% | 19.2% | 5.9% | 16.1% |
| 2026-01 | high_volatility | **FRAGILE** | **FRAGILE** | 504 | 26.0% | 8.1% | 14.1% | 51.8% |
| 2026-02 | ranging | **MATCH** | **MISMATCH** | 480 | 57.7% | 10.8% | 16.7% | 14.8% |
| 2026-03 | high_volatility | **FRAGILE** | **FRAGILE** | 531 | 33.9% | 3.6% | 17.5% | 45.0% |
| 2026-04 | ranging | **MATCH** | **MISMATCH** | 528 | 53.2% | 18.6% | 15.7% | 12.5% |
| 2026-05 | ranging | **MATCH** | **MISMATCH** | 504 | 43.7% | 9.9% | 22.8% | 23.6% |
| 2026-06 | ranging | **MATCH** | **MISMATCH** | 528 | 45.6% | 9.8% | 11.2% | 33.3% |
| 2026-07 | ranging | **MATCH** | **MISMATCH** | 549 | 47.5% | 5.6% | 23.0% | 23.9% |
| 2026-08 | ranging | **MATCH** | **MISMATCH** | 507 | 57.4% | 13.2% | 14.2% | 15.2% |
| 2026-09 | ranging | **MATCH** | **MISMATCH** | 528 | 42.0% | 10.0% | 12.7% | 35.2% |
| 2026-10 | high_volatility | **FRAGILE** | **FRAGILE** | 112 | 0.0% | 0.0% | 4.5% | 95.5% |

## D1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-10 | trending_down | **MISMATCH** | **MATCH** | 17 | 0.0% | 0.0% | 100.0% | 0.0% |
| 2024-11 | high_volatility | **FRAGILE** | **FRAGILE** | 25 | 20.0% | 0.0% | 4.0% | 76.0% |
| 2024-12 | ranging | **MATCH** | **MISMATCH** | 27 | 77.8% | 0.0% | 14.8% | 7.4% |
| 2025-01 | ranging | **MATCH** | **MISMATCH** | 27 | 51.9% | 0.0% | 11.1% | 37.0% |
| 2025-02 | high_volatility | **FRAGILE** | **FRAGILE** | 24 | 29.2% | 0.0% | 0.0% | 70.8% |
| 2025-03 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 7.7% | 38.5% | 0.0% | 53.8% |
| 2025-04 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 26.9% | 3.8% | 0.0% | 69.2% |
| 2025-05 | ranging | **MATCH** | **MISMATCH** | 26 | 84.6% | 15.4% | 0.0% | 0.0% |
| 2025-06 | trending_up | **MISMATCH** | **MATCH** | 26 | 19.2% | 46.2% | 0.0% | 34.6% |
| 2025-07 | trending_up | **MISMATCH** | **MATCH** | 27 | 48.1% | 51.9% | 0.0% | 0.0% |
| 2025-08 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 15.4% | 0.0% | 0.0% | 84.6% |
| 2025-09 | ranging | **MATCH** | **MISMATCH** | 26 | 80.8% | 0.0% | 0.0% | 19.2% |
| 2025-10 | ranging | **MATCH** | **MISMATCH** | 27 | 85.2% | 0.0% | 14.8% | 0.0% |
| 2025-11 | ranging | **MATCH** | **MISMATCH** | 25 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2025-12 | trending_up | **MISMATCH** | **MATCH** | 26 | 46.2% | 53.8% | 0.0% | 0.0% |
| 2026-01 | high_volatility | **MISMATCH** | **MATCH** | 26 | 26.9% | 15.4% | 26.9% | 30.8% |
| 2026-02 | high_volatility | **FRAGILE** | **MISMATCH** | 24 | 50.0% | 0.0% | 0.0% | 50.0% |
| 2026-03 | trending_down | **MISMATCH** | **MATCH** | 27 | 14.8% | 0.0% | 48.1% | 37.0% |
| 2026-04 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 19.2% | 19.2% | 0.0% | 61.5% |
| 2026-05 | ranging | **MATCH** | **MISMATCH** | 26 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2026-06 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 26.9% | 0.0% | 34.6% | 38.5% |
| 2026-07 | ranging | **MATCH** | **MISMATCH** | 27 | 63.0% | 0.0% | 11.1% | 25.9% |
| 2026-08 | trending_up | **MISMATCH** | **MATCH** | 26 | 46.2% | 50.0% | 0.0% | 3.8% |
| 2026-09 | trending_down | **MISMATCH** | **MATCH** | 26 | 0.0% | 0.0% | 53.8% | 46.2% |
| 2026-10 | trending_down | **MISMATCH** | **MATCH** | 6 | 0.0% | 0.0% | 100.0% | 0.0% |

## Audit takeaways

1. **H1 meanrev MATCH in 19/26 months** vs trendfollow MATCH in 1/26 — modal H1 month regime is `ranging` (20/26).
2. **Fragile months** are present but do not form long consecutive clusters on H1.
3. **Trend MATCH months** with a trending_* dominant regime are scarce in this window.
4. **TF disagreement is expected** when dominant regime is ranging but trend shares outvote ranging on the fit map (or the reverse).
5. First/last months may be thin after regime warmup (2024-09 / 2026-10).
6. Monthly MATCH is **ex-post**, not a forward signal. Live research gate should use nowcast + 30d shares, not calendar-month prophecy.

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
