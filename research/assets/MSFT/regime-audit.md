# MSFT — Regime audit & fit tagging (monthly, 2y)

> Ex-post calendar-month boards · `regimes.rule_v1` labels → `fit.map_v0`  
> Window: 2024-10 → 2026-10 (23 H1 months with confirmed bars after warmup)

## Method

1. Load H1 / D1 OHLCV (~800d lookback; M1 depth gate passes).
2. Run `regime_feature_frame` → confirmed regime per bar.
3. Slice each calendar month; map regimes → MATCH / MISMATCH / FRAGILE per edge family.
4. Dominant tag = largest fit-share (ties break MISMATCH > FRAGILE > MATCH).

Families: **meanrev** home=`ranging`; **trendfollow** home=`trending_up|trending_down`; both treat `high_volatility` as FRAGILE.

## Tag summary (months with bars)

| TF × family | MATCH | MISMATCH | FRAGILE |
| --- | ---: | ---: | ---: |
| `H1|meanrev` | 11 | 3 | 9 |
| `H1|trendfollow` | 2 | 12 | 9 |
| `D1|meanrev` | 7 | 6 | 10 |
| `D1|trendfollow` | 5 | 8 | 10 |

Dominant-regime months (H1): {'high_volatility': 10, 'ranging': 13}
Dominant-regime months (D1): {'high_volatility': 10, 'trending_up': 4, 'trending_down': 1, 'ranging': 8}

## H1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-11 | high_volatility | **MISMATCH** | **MATCH** | 110 | 29.1% | 30.9% | 8.2% | 31.8% |
| 2024-12 | ranging | **MISMATCH** | **MATCH** | 152 | 33.6% | 32.2% | 11.8% | 22.4% |
| 2025-01 | high_volatility | **FRAGILE** | **FRAGILE** | 146 | 14.4% | 24.0% | 13.0% | 48.6% |
| 2025-02 | ranging | **MATCH** | **MISMATCH** | 134 | 51.5% | 11.2% | 26.9% | 10.4% |
| 2025-03 | high_volatility | **FRAGILE** | **FRAGILE** | 147 | 27.2% | 6.8% | 8.2% | 57.8% |
| 2025-04 | high_volatility | **FRAGILE** | **FRAGILE** | 148 | 13.5% | 15.5% | 11.5% | 59.5% |
| 2025-05 | ranging | **MATCH** | **MISMATCH** | 147 | 62.6% | 32.0% | 0.0% | 5.4% |
| 2025-06 | ranging | **MISMATCH** | **MISMATCH** | 140 | 50.0% | 50.0% | 0.0% | 0.0% |
| 2025-07 | ranging | **MATCH** | **MISMATCH** | 151 | 55.6% | 31.8% | 12.6% | 0.0% |
| 2025-08 | ranging | **MATCH** | **MISMATCH** | 147 | 49.0% | 12.9% | 29.9% | 8.2% |
| 2025-09 | high_volatility | **FRAGILE** | **FRAGILE** | 147 | 34.7% | 17.7% | 4.1% | 43.5% |
| 2025-10 | ranging | **MATCH** | **MISMATCH** | 161 | 44.1% | 17.4% | 5.0% | 33.5% |
| 2025-11 | high_volatility | **FRAGILE** | **FRAGILE** | 130 | 8.5% | 10.8% | 14.6% | 66.2% |
| 2025-12 | ranging | **MATCH** | **MISMATCH** | 150 | 43.3% | 28.7% | 6.0% | 22.0% |
| 2026-01 | high_volatility | **FRAGILE** | **FRAGILE** | 140 | 23.6% | 8.6% | 13.6% | 54.3% |
| 2026-02 | high_volatility | **FRAGILE** | **FRAGILE** | 133 | 27.8% | 6.0% | 14.3% | 51.9% |
| 2026-03 | ranging | **MATCH** | **MISMATCH** | 153 | 41.8% | 0.0% | 38.6% | 19.6% |
| 2026-04 | high_volatility | **FRAGILE** | **FRAGILE** | 140 | 29.3% | 19.3% | 3.6% | 47.9% |
| 2026-05 | ranging | **MATCH** | **MISMATCH** | 49 | 61.2% | 0.0% | 0.0% | 38.8% |
| 2026-07 | high_volatility | **FRAGILE** | **FRAGILE** | 140 | 20.0% | 5.0% | 15.0% | 60.0% |
| 2026-08 | ranging | **MATCH** | **MISMATCH** | 147 | 44.2% | 25.9% | 14.3% | 15.6% |
| 2026-09 | ranging | **MATCH** | **MISMATCH** | 147 | 68.7% | 8.8% | 17.7% | 4.8% |
| 2026-10 | ranging | **MATCH** | **MISMATCH** | 30 | 46.7% | 23.3% | 0.0% | 30.0% |

## D1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-11 | high_volatility | **FRAGILE** | **FRAGILE** | 15 | 0.0% | 0.0% | 0.0% | 100.0% |
| 2024-12 | trending_up | **MISMATCH** | **MATCH** | 22 | 13.6% | 77.3% | 0.0% | 9.1% |
| 2025-01 | trending_down | **MISMATCH** | **MATCH** | 21 | 28.6% | 0.0% | 42.9% | 28.6% |
| 2025-02 | high_volatility | **FRAGILE** | **FRAGILE** | 20 | 20.0% | 0.0% | 30.0% | 50.0% |
| 2025-03 | ranging | **MATCH** | **MISMATCH** | 21 | 61.9% | 0.0% | 38.1% | 0.0% |
| 2025-04 | high_volatility | **FRAGILE** | **FRAGILE** | 22 | 36.4% | 0.0% | 0.0% | 63.6% |
| 2025-05 | trending_up | **MISMATCH** | **MATCH** | 21 | 0.0% | 71.4% | 0.0% | 28.6% |
| 2025-06 | trending_up | **MISMATCH** | **MATCH** | 20 | 0.0% | 100.0% | 0.0% | 0.0% |
| 2025-07 | trending_up | **MISMATCH** | **MATCH** | 22 | 0.0% | 100.0% | 0.0% | 0.0% |
| 2025-08 | high_volatility | **FRAGILE** | **FRAGILE** | 21 | 0.0% | 4.8% | 0.0% | 95.2% |
| 2025-09 | ranging | **MATCH** | **MISMATCH** | 21 | 52.4% | 0.0% | 38.1% | 9.5% |
| 2025-10 | ranging | **MATCH** | **MISMATCH** | 23 | 56.5% | 43.5% | 0.0% | 0.0% |
| 2025-11 | high_volatility | **FRAGILE** | **FRAGILE** | 19 | 0.0% | 0.0% | 0.0% | 100.0% |
| 2025-12 | high_volatility | **FRAGILE** | **FRAGILE** | 22 | 36.4% | 0.0% | 0.0% | 63.6% |
| 2026-01 | ranging | **MATCH** | **MISMATCH** | 20 | 65.0% | 0.0% | 15.0% | 20.0% |
| 2026-02 | high_volatility | **FRAGILE** | **FRAGILE** | 19 | 0.0% | 0.0% | 21.1% | 78.9% |
| 2026-03 | ranging | **MATCH** | **MISMATCH** | 22 | 77.3% | 0.0% | 22.7% | 0.0% |
| 2026-04 | high_volatility | **FRAGILE** | **FRAGILE** | 20 | 0.0% | 0.0% | 40.0% | 60.0% |
| 2026-05 | high_volatility | **FRAGILE** | **FRAGILE** | 7 | 0.0% | 0.0% | 0.0% | 100.0% |
| 2026-07 | ranging | **MISMATCH** | **MISMATCH** | 20 | 40.0% | 0.0% | 40.0% | 20.0% |
| 2026-08 | high_volatility | **FRAGILE** | **FRAGILE** | 21 | 0.0% | 28.6% | 0.0% | 71.4% |
| 2026-09 | ranging | **MATCH** | **MISMATCH** | 21 | 95.2% | 4.8% | 0.0% | 0.0% |
| 2026-10 | ranging | **MATCH** | **MISMATCH** | 5 | 100.0% | 0.0% | 0.0% | 0.0% |

## Audit takeaways

1. **H1 meanrev MATCH in 11/23 months** vs trendfollow MATCH in 2/23 — modal H1 month regime is **ranging** (13/23).
2. **Fragile months:** 2025-01, 2025-03, 2025-04, 2025-09, 2025-11, 2026-01, 2026-02, 2026-04, 2026-07 (high_vol-dominant → both families FRAGILE).
3. **Trendfollow MATCH months:** 2024-11, 2024-12 (ex-post; not forward signals).
4. **Live gate vs nowcast:** confirmed H1=trending_up (conf 0.919) while 30d shares tag meanrev=MATCH / trendfollow=MISMATCH — use 30d shares for the research gate, not the single-bar confirmed label alone.
5. **Partial / missing months:** regime warmup and broker gaps (e.g. thin May 2026, missing Jun 2026 bars) can drop months from confirmed boards.
6. Monthly MATCH is **ex-post**, not a forward signal. Live research gate should use nowcast + 30d shares, not calendar-month prophecy.

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
