# TSLA — Regime audit & fit tagging (monthly, 2y)

> Ex-post calendar-month boards · `regimes.rule_v1` labels → `fit.map_v0`  
> Window: 2024-10 → 2026-10 (24 H1 months with confirmed bars after warmup)

## Method

1. Load H1 / D1 OHLCV (~800d lookback; M1 depth gate passes).
2. Run `regime_feature_frame` → confirmed regime per bar.
3. Slice each calendar month; map regimes → MATCH / MISMATCH / FRAGILE per edge family.
4. Dominant tag = largest fit-share (ties break MISMATCH > FRAGILE > MATCH).

Families: **meanrev** home=`ranging`; **trendfollow** home=`trending_up|trending_down`; both treat `high_volatility` as FRAGILE.

## Tag summary (months with bars)

| TF × family | MATCH | MISMATCH | FRAGILE |
| --- | ---: | ---: | ---: |
| `H1|meanrev` | 8 | 10 | 6 |
| `H1|trendfollow` | 10 | 8 | 6 |
| `D1|meanrev` | 12 | 5 | 7 |
| `D1|trendfollow` | 5 | 12 | 7 |

Dominant-regime months (H1): {'high_volatility': 8, 'ranging': 12, 'trending_down': 2, 'trending_up': 2}
Dominant-regime months (D1): {'high_volatility': 7, 'trending_up': 3, 'ranging': 12, 'trending_down': 2}

## H1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-11 | high_volatility | **FRAGILE** | **FRAGILE** | 110 | 8.2% | 14.5% | 10.9% | 66.4% |
| 2024-12 | high_volatility | **MISMATCH** | **MATCH** | 152 | 3.3% | 38.8% | 15.1% | 42.8% |
| 2025-01 | ranging | **MISMATCH** | **MATCH** | 146 | 40.4% | 6.8% | 37.0% | 15.8% |
| 2025-02 | trending_down | **MISMATCH** | **MATCH** | 134 | 15.7% | 5.2% | 47.0% | 32.1% |
| 2025-03 | high_volatility | **FRAGILE** | **FRAGILE** | 147 | 13.6% | 24.5% | 5.4% | 56.5% |
| 2025-04 | high_volatility | **FRAGILE** | **FRAGILE** | 147 | 19.0% | 0.0% | 8.8% | 72.1% |
| 2025-05 | ranging | **MATCH** | **MISMATCH** | 147 | 56.5% | 40.1% | 3.4% | 0.0% |
| 2025-06 | ranging | **MATCH** | **MISMATCH** | 140 | 47.1% | 20.7% | 16.4% | 15.7% |
| 2025-07 | ranging | **MISMATCH** | **MATCH** | 151 | 38.4% | 35.8% | 25.8% | 0.0% |
| 2025-08 | ranging | **MISMATCH** | **MATCH** | 147 | 42.2% | 39.5% | 18.4% | 0.0% |
| 2025-09 | ranging | **MATCH** | **MISMATCH** | 147 | 63.9% | 25.2% | 6.8% | 4.1% |
| 2025-10 | high_volatility | **FRAGILE** | **FRAGILE** | 161 | 36.6% | 16.8% | 8.1% | 38.5% |
| 2025-11 | high_volatility | **FRAGILE** | **FRAGILE** | 130 | 18.5% | 6.2% | 12.3% | 63.1% |
| 2025-12 | ranging | **MISMATCH** | **MATCH** | 150 | 35.3% | 23.3% | 15.3% | 26.0% |
| 2026-01 | trending_down | **MISMATCH** | **MATCH** | 140 | 35.0% | 17.1% | 38.6% | 9.3% |
| 2026-02 | ranging | **MATCH** | **MISMATCH** | 133 | 58.6% | 16.5% | 12.0% | 12.8% |
| 2026-03 | ranging | **MATCH** | **MISMATCH** | 154 | 61.7% | 1.9% | 36.4% | 0.0% |
| 2026-04 | high_volatility | **MISMATCH** | **MATCH** | 140 | 32.1% | 10.0% | 24.3% | 33.6% |
| 2026-05 | trending_up | **MISMATCH** | **MATCH** | 140 | 17.1% | 35.7% | 12.9% | 34.3% |
| 2026-06 | high_volatility | **FRAGILE** | **FRAGILE** | 147 | 23.1% | 7.5% | 28.6% | 40.8% |
| 2026-07 | ranging | **MATCH** | **MISMATCH** | 154 | 41.6% | 6.5% | 29.2% | 22.7% |
| 2026-08 | ranging | **MATCH** | **MISMATCH** | 147 | 56.5% | 25.9% | 4.1% | 13.6% |
| 2026-09 | ranging | **MATCH** | **MISMATCH** | 147 | 66.7% | 17.0% | 13.6% | 2.7% |
| 2026-10 | trending_up | **MISMATCH** | **MATCH** | 30 | 26.7% | 70.0% | 3.3% | 0.0% |

## D1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-11 | high_volatility | **FRAGILE** | **FRAGILE** | 12 | 0.0% | 33.3% | 0.0% | 66.7% |
| 2024-12 | trending_up | **MISMATCH** | **MATCH** | 22 | 0.0% | 100.0% | 0.0% | 0.0% |
| 2025-01 | ranging | **MATCH** | **MISMATCH** | 21 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2025-02 | trending_down | **MISMATCH** | **MATCH** | 20 | 40.0% | 0.0% | 60.0% | 0.0% |
| 2025-03 | high_volatility | **FRAGILE** | **FRAGILE** | 21 | 0.0% | 0.0% | 19.0% | 81.0% |
| 2025-04 | high_volatility | **FRAGILE** | **FRAGILE** | 22 | 27.3% | 0.0% | 0.0% | 72.7% |
| 2025-05 | trending_up | **MISMATCH** | **MATCH** | 21 | 33.3% | 66.7% | 0.0% | 0.0% |
| 2025-06 | ranging | **MATCH** | **MISMATCH** | 20 | 40.0% | 25.0% | 0.0% | 35.0% |
| 2025-07 | ranging | **MATCH** | **MISMATCH** | 22 | 77.3% | 0.0% | 0.0% | 22.7% |
| 2025-08 | ranging | **MATCH** | **MISMATCH** | 21 | 90.5% | 9.5% | 0.0% | 0.0% |
| 2025-09 | ranging | **MATCH** | **MISMATCH** | 21 | 38.1% | 28.6% | 0.0% | 33.3% |
| 2025-10 | high_volatility | **FRAGILE** | **FRAGILE** | 23 | 30.4% | 0.0% | 0.0% | 69.6% |
| 2025-11 | ranging | **MATCH** | **MISMATCH** | 19 | 52.6% | 0.0% | 0.0% | 47.4% |
| 2025-12 | ranging | **MATCH** | **MISMATCH** | 22 | 50.0% | 45.5% | 0.0% | 4.5% |
| 2026-01 | ranging | **MATCH** | **MISMATCH** | 20 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2026-02 | ranging | **MATCH** | **MISMATCH** | 19 | 52.6% | 0.0% | 0.0% | 47.4% |
| 2026-03 | ranging | **MATCH** | **MISMATCH** | 22 | 95.5% | 0.0% | 0.0% | 4.5% |
| 2026-04 | high_volatility | **FRAGILE** | **FRAGILE** | 20 | 10.0% | 0.0% | 0.0% | 90.0% |
| 2026-05 | trending_up | **MISMATCH** | **MATCH** | 20 | 40.0% | 60.0% | 0.0% | 0.0% |
| 2026-06 | high_volatility | **FRAGILE** | **FRAGILE** | 21 | 19.0% | 9.5% | 0.0% | 71.4% |
| 2026-07 | high_volatility | **FRAGILE** | **FRAGILE** | 22 | 27.3% | 0.0% | 0.0% | 72.7% |
| 2026-08 | trending_down | **MISMATCH** | **MATCH** | 21 | 0.0% | 23.8% | 66.7% | 9.5% |
| 2026-09 | ranging | **MATCH** | **MISMATCH** | 21 | 76.2% | 23.8% | 0.0% | 0.0% |
| 2026-10 | ranging | **MATCH** | **MISMATCH** | 5 | 100.0% | 0.0% | 0.0% | 0.0% |

## Audit takeaways

1. **H1 meanrev MATCH in 8/24 months** vs trendfollow MATCH in 10/24 — modal H1 month regime is **ranging** (12/24).
2. **Fragile months:** 2024-11, 2025-03, 2025-04, 2025-10, 2025-11, 2026-06 (high_vol-dominant → both families FRAGILE).
3. **Trendfollow MATCH months:** 2024-12, 2025-01, 2025-02, 2025-07, 2025-08, 2025-12, 2026-01, 2026-04, 2026-05, 2026-10 (ex-post; not forward signals).
4. **Live gate vs nowcast:** confirmed H1=trending_up (conf 0.211) while 30d shares tag meanrev=MATCH / trendfollow=MISMATCH — use 30d shares for the research gate, not the single-bar confirmed label alone.
5. **Partial / missing months:** regime warmup and broker gaps (e.g. thin May 2026, missing Jun 2026 bars) can drop months from confirmed boards.
6. Monthly MATCH is **ex-post**, not a forward signal. Live research gate should use nowcast + 30d shares, not calendar-month prophecy.

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
