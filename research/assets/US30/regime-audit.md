# US30 — Regime audit & fit tagging (monthly)

> Ex-post calendar-month boards · `regimes.rule_v1` labels → `fit.map_v0`  
> Window: 2024-09 → 2026-10 (25 H1 months with confirmed bars after warmup)

> Broker depth: YWO `US30` M1 starts `2024-09-12` (≈755d ≈ 2.1y). Aug 2025 may be thin/missing after confirmed-regime warmup.

## Method

1. Load H1 / D1 OHLCV (~800d lookback request; broker depth binds).
2. Run `regime_feature_frame` → confirmed regime per bar.
3. Slice each calendar month; map regimes → MATCH / MISMATCH / FRAGILE per edge family.
4. Dominant tag = largest fit-share (ties break MISMATCH > FRAGILE > MATCH).

Families: **meanrev** home=`ranging`; **trendfollow** home=`trending_up|trending_down`; both treat `high_volatility` as FRAGILE.

## Tag summary (months with bars)

| TF × family | MATCH | MISMATCH | FRAGILE |
| --- | ---: | ---: | ---: |
| `H1|meanrev` | 10 | 9 | 6 |
| `H1|trendfollow` | 9 | 10 | 6 |
| `D1|meanrev` | 9 | 5 | 10 |
| `D1|trendfollow` | 5 | 10 | 9 |

Dominant-regime months (H1): {'ranging': 15, 'high_volatility': 9, 'trending_down': 1}
Dominant-regime months (D1): {'high_volatility': 10, 'trending_up': 3, 'ranging': 9, 'trending_down': 2}

## H1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-09 | ranging | **MATCH** | **MISMATCH** | 132 | 60.6% | 14.4% | 5.3% | 19.7% |
| 2024-10 | ranging | **MISMATCH** | **MATCH** | 541 | 35.5% | 26.8% | 15.0% | 22.7% |
| 2024-11 | high_volatility | **MISMATCH** | **MATCH** | 491 | 24.2% | 22.2% | 23.8% | 29.7% |
| 2024-12 | trending_down | **MISMATCH** | **MATCH** | 490 | 19.6% | 15.3% | 42.4% | 22.7% |
| 2025-01 | ranging | **MATCH** | **MISMATCH** | 512 | 39.1% | 23.2% | 3.7% | 34.0% |
| 2025-02 | ranging | **MATCH** | **MISMATCH** | 452 | 49.8% | 15.7% | 20.4% | 14.2% |
| 2025-03 | high_volatility | **FRAGILE** | **FRAGILE** | 483 | 24.6% | 16.8% | 11.0% | 47.6% |
| 2025-04 | high_volatility | **FRAGILE** | **FRAGILE** | 480 | 35.4% | 12.5% | 7.9% | 44.2% |
| 2025-05 | ranging | **MATCH** | **MISMATCH** | 496 | 60.3% | 21.4% | 15.9% | 2.4% |
| 2025-06 | ranging | **MATCH** | **MISMATCH** | 476 | 59.7% | 20.0% | 5.3% | 15.1% |
| 2025-07 | ranging | **MISMATCH** | **MATCH** | 241 | 42.7% | 28.2% | 24.1% | 5.0% |
| 2025-09 | ranging | **MATCH** | **MISMATCH** | 353 | 45.9% | 21.0% | 17.0% | 16.1% |
| 2025-10 | high_volatility | **MISMATCH** | **MATCH** | 523 | 28.9% | 23.3% | 13.0% | 34.8% |
| 2025-11 | high_volatility | **FRAGILE** | **FRAGILE** | 442 | 29.9% | 21.7% | 12.7% | 35.7% |
| 2025-12 | ranging | **MISMATCH** | **MATCH** | 493 | 42.8% | 25.2% | 23.1% | 8.9% |
| 2026-01 | ranging | **MISMATCH** | **MATCH** | 478 | 32.2% | 21.3% | 24.3% | 22.2% |
| 2026-02 | high_volatility | **FRAGILE** | **FRAGILE** | 455 | 34.3% | 14.9% | 9.5% | 41.3% |
| 2026-03 | high_volatility | **FRAGILE** | **FRAGILE** | 508 | 30.9% | 3.0% | 13.2% | 53.0% |
| 2026-04 | ranging | **MATCH** | **MISMATCH** | 499 | 50.5% | 23.2% | 14.4% | 11.8% |
| 2026-05 | ranging | **MISMATCH** | **MATCH** | 479 | 41.3% | 26.9% | 21.5% | 10.2% |
| 2026-06 | ranging | **MATCH** | **MISMATCH** | 502 | 42.2% | 15.1% | 5.0% | 37.6% |
| 2026-07 | ranging | **MATCH** | **MISMATCH** | 523 | 57.9% | 17.0% | 6.9% | 18.2% |
| 2026-08 | ranging | **MATCH** | **MISMATCH** | 485 | 62.9% | 13.8% | 15.1% | 8.2% |
| 2026-09 | high_volatility | **MISMATCH** | **MATCH** | 411 | 18.5% | 10.7% | 34.1% | 36.7% |
| 2026-10 | high_volatility | **FRAGILE** | **FRAGILE** | 107 | 18.7% | 10.3% | 2.8% | 68.2% |

## D1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-10 | high_volatility | **FRAGILE** | **FRAGILE** | 17 | 0.0% | 35.3% | 0.0% | 64.7% |
| 2024-11 | high_volatility | **FRAGILE** | **FRAGILE** | 25 | 0.0% | 16.0% | 0.0% | 84.0% |
| 2024-12 | trending_up | **MISMATCH** | **MATCH** | 27 | 14.8% | 44.4% | 29.6% | 11.1% |
| 2025-01 | high_volatility | **FRAGILE** | **FRAGILE** | 27 | 33.3% | 29.6% | 0.0% | 37.0% |
| 2025-02 | ranging | **MATCH** | **MISMATCH** | 24 | 62.5% | 37.5% | 0.0% | 0.0% |
| 2025-03 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 19.2% | 0.0% | 0.0% | 80.8% |
| 2025-04 | high_volatility | **FRAGILE** | **FRAGILE** | 25 | 0.0% | 0.0% | 0.0% | 100.0% |
| 2025-05 | ranging | **MATCH** | **MISMATCH** | 26 | 46.2% | 38.5% | 0.0% | 15.4% |
| 2025-06 | ranging | **MATCH** | **MISMATCH** | 26 | 96.2% | 3.8% | 0.0% | 0.0% |
| 2025-07 | trending_up | **MISMATCH** | **MATCH** | 14 | 0.0% | 78.6% | 0.0% | 21.4% |
| 2025-09 | trending_up | **MISMATCH** | **MATCH** | 19 | 0.0% | 100.0% | 0.0% | 0.0% |
| 2025-10 | high_volatility | **FRAGILE** | **FRAGILE** | 27 | 0.0% | 40.7% | 0.0% | 59.3% |
| 2025-11 | ranging | **MATCH** | **MISMATCH** | 25 | 40.0% | 36.0% | 0.0% | 24.0% |
| 2025-12 | ranging | **MATCH** | **MISMATCH** | 26 | 53.8% | 26.9% | 0.0% | 19.2% |
| 2026-01 | ranging | **MATCH** | **MISMATCH** | 26 | 46.2% | 23.1% | 0.0% | 30.8% |
| 2026-02 | high_volatility | **FRAGILE** | **MISMATCH** | 24 | 50.0% | 0.0% | 0.0% | 50.0% |
| 2026-03 | trending_down | **MISMATCH** | **MATCH** | 27 | 22.2% | 0.0% | 77.8% | 0.0% |
| 2026-04 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 0.0% | 30.8% | 0.0% | 69.2% |
| 2026-05 | ranging | **MATCH** | **MISMATCH** | 26 | 92.3% | 7.7% | 0.0% | 0.0% |
| 2026-06 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 19.2% | 34.6% | 0.0% | 46.2% |
| 2026-07 | ranging | **MATCH** | **MISMATCH** | 27 | 55.6% | 40.7% | 0.0% | 3.7% |
| 2026-08 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 38.5% | 0.0% | 0.0% | 61.5% |
| 2026-09 | ranging | **MATCH** | **MISMATCH** | 23 | 65.2% | 0.0% | 34.8% | 0.0% |
| 2026-10 | trending_down | **MISMATCH** | **MATCH** | 6 | 0.0% | 0.0% | 100.0% | 0.0% |

## Audit takeaways

1. **H1 meanrev MATCH in 10/25 months** vs trendfollow MATCH in 9/25 — modal H1 month regime is **ranging** (15/25).
2. **Fragile months:** 2025-03, 2025-04, 2025-11, 2026-02, 2026-03, 2026-10 (high_vol-dominant → both families FRAGILE).
3. **Trendfollow MATCH months:** 2024-10, 2024-11, 2024-12, 2025-07, 2025-10, 2025-12, 2026-01, 2026-05, 2026-09 (ex-post; not forward signals).
4. **Live gate vs character:** nowcast can lean trending_down while history clock stays ranging-led — use 30d shares for the research gate.
5. **Partial months:** early/late months may have few confirmed bars after regime warmup (e.g. Mar / Oct).
6. Monthly MATCH is **ex-post**, not a forward signal. Live research gate should use nowcast + 30d shares, not calendar-month prophecy.

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
