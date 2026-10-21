# XOM — Regime audit & fit tagging (monthly, 2y)

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
| `H1|meanrev` | 7 | 7 | 9 |
| `H1|trendfollow` | 7 | 7 | 9 |
| `D1|meanrev` | 11 | 4 | 8 |
| `D1|trendfollow` | 3 | 13 | 7 |

Dominant-regime months (H1): {'high_volatility': 9, 'ranging': 11, 'trending_up': 3}
Dominant-regime months (D1): {'ranging': 11, 'trending_down': 2, 'high_volatility': 9, 'trending_up': 1}

## H1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-11 | high_volatility | **FRAGILE** | **FRAGILE** | 109 | 7.3% | 0.0% | 28.4% | 64.2% |
| 2024-12 | ranging | **MATCH** | **MISMATCH** | 152 | 42.1% | 0.0% | 30.3% | 27.6% |
| 2025-01 | ranging | **MATCH** | **MISMATCH** | 146 | 44.5% | 17.1% | 5.5% | 32.9% |
| 2025-02 | ranging | **MATCH** | **MISMATCH** | 134 | 37.3% | 21.6% | 10.4% | 30.6% |
| 2025-03 | high_volatility | **FRAGILE** | **FRAGILE** | 147 | 22.4% | 23.8% | 0.0% | 53.7% |
| 2025-04 | high_volatility | **FRAGILE** | **FRAGILE** | 148 | 21.6% | 2.7% | 5.4% | 70.3% |
| 2025-05 | ranging | **MATCH** | **MISMATCH** | 147 | 44.9% | 10.9% | 29.3% | 15.0% |
| 2025-06 | trending_up | **MISMATCH** | **MATCH** | 140 | 40.0% | 44.3% | 0.7% | 15.0% |
| 2025-07 | trending_up | **MISMATCH** | **MATCH** | 151 | 26.5% | 46.4% | 21.9% | 5.3% |
| 2025-08 | ranging | **MATCH** | **MISMATCH** | 147 | 48.3% | 31.3% | 10.2% | 10.2% |
| 2025-09 | ranging | **MISMATCH** | **MATCH** | 147 | 39.5% | 38.8% | 21.8% | 0.0% |
| 2025-10 | ranging | **MATCH** | **MISMATCH** | 161 | 56.5% | 21.1% | 16.8% | 5.6% |
| 2025-11 | high_volatility | **FRAGILE** | **FRAGILE** | 130 | 36.9% | 16.9% | 8.5% | 37.7% |
| 2025-12 | ranging | **MISMATCH** | **MATCH** | 150 | 46.0% | 34.7% | 19.3% | 0.0% |
| 2026-01 | high_volatility | **FRAGILE** | **FRAGILE** | 140 | 11.4% | 36.4% | 0.0% | 52.1% |
| 2026-02 | high_volatility | **FRAGILE** | **FRAGILE** | 133 | 24.8% | 15.0% | 0.0% | 60.2% |
| 2026-03 | high_volatility | **FRAGILE** | **FRAGILE** | 154 | 7.1% | 16.9% | 1.9% | 74.0% |
| 2026-04 | high_volatility | **FRAGILE** | **FRAGILE** | 140 | 43.6% | 8.6% | 0.0% | 47.9% |
| 2026-05 | high_volatility | **FRAGILE** | **FRAGILE** | 49 | 8.2% | 6.1% | 0.0% | 85.7% |
| 2026-07 | trending_up | **MISMATCH** | **MATCH** | 140 | 27.9% | 42.9% | 5.0% | 24.3% |
| 2026-08 | ranging | **MISMATCH** | **MATCH** | 147 | 38.1% | 28.6% | 23.8% | 9.5% |
| 2026-09 | ranging | **MISMATCH** | **MATCH** | 147 | 42.9% | 32.7% | 22.4% | 2.0% |
| 2026-10 | ranging | **MATCH** | **MISMATCH** | 30 | 90.0% | 10.0% | 0.0% | 0.0% |

## D1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-11 | ranging | **MATCH** | **MISMATCH** | 16 | 68.8% | 0.0% | 0.0% | 31.2% |
| 2024-12 | trending_down | **MISMATCH** | **MATCH** | 22 | 13.6% | 0.0% | 77.3% | 9.1% |
| 2025-01 | trending_down | **MISMATCH** | **MATCH** | 21 | 0.0% | 14.3% | 57.1% | 28.6% |
| 2025-02 | high_volatility | **FRAGILE** | **FRAGILE** | 20 | 10.0% | 0.0% | 0.0% | 90.0% |
| 2025-03 | high_volatility | **FRAGILE** | **FRAGILE** | 21 | 23.8% | 0.0% | 0.0% | 76.2% |
| 2025-04 | high_volatility | **FRAGILE** | **FRAGILE** | 22 | 0.0% | 13.6% | 0.0% | 86.4% |
| 2025-05 | ranging | **MATCH** | **MISMATCH** | 21 | 71.4% | 0.0% | 19.0% | 9.5% |
| 2025-06 | ranging | **MATCH** | **MISMATCH** | 20 | 65.0% | 15.0% | 0.0% | 20.0% |
| 2025-07 | high_volatility | **FRAGILE** | **MISMATCH** | 22 | 50.0% | 0.0% | 0.0% | 50.0% |
| 2025-08 | ranging | **MATCH** | **MISMATCH** | 21 | 71.4% | 0.0% | 28.6% | 0.0% |
| 2025-09 | high_volatility | **MISMATCH** | **MISMATCH** | 21 | 33.3% | 33.3% | 0.0% | 33.3% |
| 2025-10 | ranging | **MATCH** | **MISMATCH** | 23 | 82.6% | 0.0% | 0.0% | 17.4% |
| 2025-11 | ranging | **MATCH** | **MISMATCH** | 19 | 57.9% | 42.1% | 0.0% | 0.0% |
| 2025-12 | high_volatility | **FRAGILE** | **FRAGILE** | 22 | 31.8% | 0.0% | 0.0% | 68.2% |
| 2026-01 | high_volatility | **FRAGILE** | **FRAGILE** | 20 | 0.0% | 0.0% | 0.0% | 100.0% |
| 2026-02 | high_volatility | **FRAGILE** | **FRAGILE** | 19 | 0.0% | 31.6% | 0.0% | 68.4% |
| 2026-03 | ranging | **MATCH** | **MISMATCH** | 22 | 54.5% | 27.3% | 0.0% | 18.2% |
| 2026-04 | high_volatility | **FRAGILE** | **FRAGILE** | 20 | 0.0% | 25.0% | 10.0% | 65.0% |
| 2026-05 | ranging | **MATCH** | **MISMATCH** | 7 | 71.4% | 0.0% | 28.6% | 0.0% |
| 2026-07 | ranging | **MATCH** | **MISMATCH** | 20 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2026-08 | trending_up | **MISMATCH** | **MATCH** | 21 | 23.8% | 76.2% | 0.0% | 0.0% |
| 2026-09 | ranging | **MATCH** | **MISMATCH** | 21 | 57.1% | 0.0% | 0.0% | 42.9% |
| 2026-10 | ranging | **MATCH** | **MISMATCH** | 5 | 100.0% | 0.0% | 0.0% | 0.0% |

## Audit takeaways

1. **H1 meanrev MATCH in 7/23 months** vs trendfollow MATCH in 7/23 — roughly balanced research gates on H1; modal month regime is **ranging** (11/23). D1 tips meanrev (MATCH-heavy) vs trendfollow MISMATCH-heavy.
2. **Fragile months:** 2024-11, 2025-03, 2025-04, 2025-11, 2026-01, 2026-02, 2026-03, 2026-04, 2026-05 (high_vol-dominant → both families FRAGILE).
3. **Trendfollow MATCH months:** 2025-06, 2025-07, 2025-09, 2025-12, 2026-07, 2026-08, 2026-09 (ex-post; not forward signals).
4. **Live gate vs nowcast:** confirmed H1=ranging (conf 0.938) while 30d shares tag meanrev=MATCH / trendfollow=MISMATCH — use 30d shares for the research gate, not the single-bar confirmed label alone.
5. **Partial / missing months:** regime warmup and broker gaps (e.g. thin May 2026, missing Jun 2026 bars) can drop months from confirmed boards.
6. Monthly MATCH is **ex-post**, not a forward signal. Live research gate should use nowcast + 30d shares, not calendar-month prophecy.

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
