# JP225 — Regime audit & fit tagging (monthly)

> Ex-post calendar-month boards · `regimes.rule_v1` labels → `fit.map_v0`  
> Window: 2024-10 → 2026-10 (25 H1 months with confirmed bars after warmup)

> Broker depth: YWO `JP225`/`JPN225` M1 starts `2024-10-07` (≈730d ≈ 2y). Boards cover available broker history.

## Method

1. Load H1 / D1 OHLCV (~800d lookback request; broker depth binds).
2. Run `regime_feature_frame` → confirmed regime per bar.
3. Slice each calendar month; map regimes → MATCH / MISMATCH / FRAGILE per edge family.
4. Dominant tag = largest fit-share (ties break MISMATCH > FRAGILE > MATCH).

Families: **meanrev** home=`ranging`; **trendfollow** home=`trending_up|trending_down`; both treat `high_volatility` as FRAGILE.

## Tag summary (months with bars)

| TF × family | MATCH | MISMATCH | FRAGILE |
| --- | ---: | ---: | ---: |
| `H1|meanrev` | 16 | 2 | 7 |
| `H1|trendfollow` | 2 | 16 | 7 |
| `D1|meanrev` | 9 | 6 | 9 |
| `D1|trendfollow` | 4 | 11 | 9 |

Dominant-regime months (H1): {'ranging': 16, 'high_volatility': 8, 'trending_up': 1}
Dominant-regime months (D1): {'ranging': 11, 'high_volatility': 9, 'trending_up': 4}

## H1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-10 | ranging | **MATCH** | **MISMATCH** | 262 | 54.2% | 8.0% | 3.8% | 34.0% |
| 2024-11 | ranging | **MATCH** | **MISMATCH** | 474 | 46.8% | 15.4% | 8.2% | 29.5% |
| 2024-12 | ranging | **MATCH** | **MISMATCH** | 480 | 56.0% | 20.4% | 16.2% | 7.3% |
| 2025-01 | ranging | **MATCH** | **MISMATCH** | 501 | 45.9% | 11.2% | 6.2% | 36.7% |
| 2025-02 | ranging | **MATCH** | **MISMATCH** | 456 | 48.7% | 10.1% | 18.0% | 23.2% |
| 2025-03 | ranging | **MATCH** | **MISMATCH** | 484 | 38.8% | 11.2% | 14.7% | 35.3% |
| 2025-04 | ranging | **MATCH** | **MISMATCH** | 484 | 45.0% | 9.7% | 2.9% | 42.4% |
| 2025-05 | ranging | **MATCH** | **MISMATCH** | 501 | 57.3% | 20.6% | 18.2% | 4.0% |
| 2025-06 | ranging | **MATCH** | **MISMATCH** | 483 | 47.8% | 29.8% | 7.0% | 15.3% |
| 2025-07 | ranging | **MATCH** | **MISMATCH** | 512 | 54.1% | 10.7% | 22.3% | 12.9% |
| 2025-08 | high_volatility | **FRAGILE** | **FRAGILE** | 483 | 27.5% | 24.0% | 9.3% | 39.1% |
| 2025-09 | ranging | **MATCH** | **MISMATCH** | 503 | 45.5% | 23.3% | 5.6% | 25.6% |
| 2025-10 | high_volatility | **FRAGILE** | **FRAGILE** | 528 | 25.8% | 29.5% | 7.0% | 37.7% |
| 2025-11 | high_volatility | **FRAGILE** | **FRAGILE** | 454 | 39.9% | 11.5% | 7.7% | 41.0% |
| 2025-12 | ranging | **MATCH** | **MISMATCH** | 495 | 61.0% | 18.8% | 16.6% | 3.6% |
| 2026-01 | high_volatility | **FRAGILE** | **FRAGILE** | 478 | 32.6% | 13.8% | 11.3% | 42.3% |
| 2026-02 | ranging | **MATCH** | **MISMATCH** | 455 | 40.0% | 20.2% | 9.2% | 30.5% |
| 2026-03 | high_volatility | **FRAGILE** | **FRAGILE** | 508 | 31.5% | 8.5% | 15.9% | 44.1% |
| 2026-04 | ranging | **MATCH** | **MISMATCH** | 499 | 51.9% | 27.1% | 12.0% | 9.0% |
| 2026-05 | high_volatility | **FRAGILE** | **FRAGILE** | 480 | 33.1% | 25.0% | 4.0% | 37.9% |
| 2026-06 | high_volatility | **FRAGILE** | **FRAGILE** | 503 | 31.8% | 15.5% | 9.7% | 42.9% |
| 2026-07 | high_volatility | **MISMATCH** | **MATCH** | 524 | 29.0% | 16.0% | 24.0% | 30.9% |
| 2026-08 | ranging | **MATCH** | **MISMATCH** | 485 | 61.2% | 16.9% | 9.5% | 12.4% |
| 2026-09 | ranging | **MATCH** | **MISMATCH** | 500 | 47.0% | 23.8% | 16.0% | 13.2% |
| 2026-10 | trending_up | **MISMATCH** | **MATCH** | 107 | 37.4% | 50.5% | 6.5% | 5.6% |

## D1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-11 | ranging | **MATCH** | **MISMATCH** | 21 | 57.1% | 0.0% | 0.0% | 42.9% |
| 2024-12 | ranging | **MATCH** | **MISMATCH** | 27 | 77.8% | 22.2% | 0.0% | 0.0% |
| 2025-01 | ranging | **MATCH** | **MISMATCH** | 27 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2025-02 | ranging | **MATCH** | **MISMATCH** | 24 | 70.8% | 0.0% | 0.0% | 29.2% |
| 2025-03 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 0.0% | 0.0% | 38.5% | 61.5% |
| 2025-04 | high_volatility | **FRAGILE** | **FRAGILE** | 25 | 0.0% | 0.0% | 0.0% | 100.0% |
| 2025-05 | trending_up | **MISMATCH** | **MATCH** | 26 | 26.9% | 73.1% | 0.0% | 0.0% |
| 2025-06 | ranging | **MATCH** | **MISMATCH** | 26 | 80.8% | 19.2% | 0.0% | 0.0% |
| 2025-07 | high_volatility | **FRAGILE** | **FRAGILE** | 27 | 11.1% | 7.4% | 0.0% | 81.5% |
| 2025-08 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 0.0% | 30.8% | 0.0% | 69.2% |
| 2025-09 | trending_up | **MISMATCH** | **MATCH** | 26 | 46.2% | 53.8% | 0.0% | 0.0% |
| 2025-10 | high_volatility | **FRAGILE** | **FRAGILE** | 27 | 0.0% | 18.5% | 0.0% | 81.5% |
| 2025-11 | ranging | **MATCH** | **MISMATCH** | 25 | 60.0% | 40.0% | 0.0% | 0.0% |
| 2025-12 | ranging | **MATCH** | **MISMATCH** | 26 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2026-01 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 34.6% | 0.0% | 0.0% | 65.4% |
| 2026-02 | high_volatility | **FRAGILE** | **FRAGILE** | 24 | 16.7% | 37.5% | 0.0% | 45.8% |
| 2026-03 | high_volatility | **FRAGILE** | **FRAGILE** | 27 | 29.6% | 11.1% | 11.1% | 48.1% |
| 2026-04 | trending_up | **MISMATCH** | **MATCH** | 26 | 26.9% | 53.8% | 0.0% | 19.2% |
| 2026-05 | trending_up | **MISMATCH** | **MATCH** | 26 | 23.1% | 69.2% | 0.0% | 7.7% |
| 2026-06 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 0.0% | 11.5% | 0.0% | 88.5% |
| 2026-07 | ranging | **MISMATCH** | **MISMATCH** | 27 | 40.7% | 0.0% | 40.7% | 18.5% |
| 2026-08 | ranging | **MATCH** | **MISMATCH** | 26 | 76.9% | 0.0% | 0.0% | 23.1% |
| 2026-09 | ranging | **MATCH** | **MISMATCH** | 26 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2026-10 | ranging | **MISMATCH** | **MISMATCH** | 6 | 50.0% | 50.0% | 0.0% | 0.0% |

## Audit takeaways

1. **H1 meanrev MATCH in 16/25 months** vs trendfollow MATCH in 2/25 — modal H1 month regime is **ranging** (16/25).
2. **Fragile months:** 2025-08, 2025-10, 2025-11, 2026-01, 2026-03, 2026-05, 2026-06 (high_vol-dominant → both families FRAGILE).
3. **Trendfollow MATCH months:** 2026-07, 2026-10 (ex-post; not forward signals).
4. **Live gate vs character:** nowcast can lean trending_down (high confidence) while the 30d meanrev gate is MATCH and history stays ranging-led — use 30d shares for the research gate, not the soft label alone.
5. **Partial months:** early/late months may have few confirmed bars after regime warmup (e.g. first / last month).
6. Monthly MATCH is **ex-post**, not a forward signal. Live research gate should use nowcast + 30d shares, not calendar-month prophecy.

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
