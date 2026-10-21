# AAPL — Regime audit & fit tagging (monthly, 2y)

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
| `H1|meanrev` | 12 | 5 | 7 |
| `H1|trendfollow` | 5 | 12 | 7 |
| `D1|meanrev` | 11 | 6 | 7 |
| `D1|trendfollow` | 5 | 11 | 8 |

Dominant-regime months (H1): {'ranging': 14, 'trending_up': 2, 'high_volatility': 8}
Dominant-regime months (D1): {'ranging': 11, 'trending_up': 4, 'high_volatility': 8, 'trending_down': 1}

## H1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-11 | ranging | **MATCH** | **MISMATCH** | 110 | 39.1% | 27.3% | 0.0% | 33.6% |
| 2024-12 | trending_up | **MISMATCH** | **MATCH** | 152 | 10.5% | 45.4% | 11.2% | 32.9% |
| 2025-01 | high_volatility | **FRAGILE** | **FRAGILE** | 146 | 8.2% | 0.0% | 18.5% | 73.3% |
| 2025-02 | high_volatility | **FRAGILE** | **FRAGILE** | 134 | 14.2% | 19.4% | 0.0% | 66.4% |
| 2025-03 | high_volatility | **FRAGILE** | **FRAGILE** | 147 | 12.2% | 6.8% | 5.4% | 75.5% |
| 2025-04 | high_volatility | **FRAGILE** | **FRAGILE** | 147 | 11.6% | 18.4% | 5.4% | 64.6% |
| 2025-05 | ranging | **MISMATCH** | **MATCH** | 147 | 36.7% | 20.4% | 34.7% | 8.2% |
| 2025-06 | ranging | **MATCH** | **MISMATCH** | 140 | 70.0% | 15.7% | 14.3% | 0.0% |
| 2025-07 | ranging | **MATCH** | **MISMATCH** | 151 | 61.6% | 21.2% | 17.2% | 0.0% |
| 2025-08 | ranging | **MATCH** | **MISMATCH** | 147 | 38.1% | 15.0% | 18.4% | 28.6% |
| 2025-09 | ranging | **MISMATCH** | **MATCH** | 147 | 42.9% | 38.1% | 15.0% | 4.1% |
| 2025-10 | ranging | **MATCH** | **MISMATCH** | 161 | 54.7% | 28.0% | 3.1% | 14.3% |
| 2025-11 | ranging | **MATCH** | **MISMATCH** | 130 | 62.3% | 10.0% | 0.0% | 27.7% |
| 2025-12 | ranging | **MATCH** | **MISMATCH** | 150 | 51.3% | 4.7% | 18.7% | 25.3% |
| 2026-01 | high_volatility | **FRAGILE** | **FRAGILE** | 140 | 31.4% | 4.3% | 28.6% | 35.7% |
| 2026-02 | high_volatility | **FRAGILE** | **FRAGILE** | 133 | 24.8% | 16.5% | 2.3% | 56.4% |
| 2026-03 | high_volatility | **MISMATCH** | **MATCH** | 153 | 22.2% | 11.8% | 30.1% | 35.9% |
| 2026-04 | high_volatility | **FRAGILE** | **FRAGILE** | 140 | 30.7% | 16.4% | 5.0% | 47.9% |
| 2026-05 | trending_up | **MISMATCH** | **MATCH** | 140 | 45.7% | 54.3% | 0.0% | 0.0% |
| 2026-06 | ranging | **MATCH** | **MISMATCH** | 147 | 52.4% | 4.1% | 0.0% | 43.5% |
| 2026-07 | ranging | **MATCH** | **MISMATCH** | 154 | 46.1% | 38.3% | 5.2% | 10.4% |
| 2026-08 | ranging | **MATCH** | **MISMATCH** | 147 | 46.3% | 17.7% | 10.2% | 25.9% |
| 2026-09 | ranging | **MATCH** | **MISMATCH** | 147 | 49.7% | 19.7% | 2.0% | 28.6% |
| 2026-10 | ranging | **MATCH** | **MISMATCH** | 30 | 76.7% | 0.0% | 23.3% | 0.0% |

## D1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024-11 | ranging | **MATCH** | **MISMATCH** | 16 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2024-12 | trending_up | **MISMATCH** | **MATCH** | 22 | 4.5% | 95.5% | 0.0% | 0.0% |
| 2025-01 | high_volatility | **FRAGILE** | **FRAGILE** | 21 | 0.0% | 9.5% | 0.0% | 90.5% |
| 2025-02 | high_volatility | **FRAGILE** | **FRAGILE** | 20 | 10.0% | 25.0% | 0.0% | 65.0% |
| 2025-03 | ranging | **MATCH** | **MISMATCH** | 21 | 42.9% | 0.0% | 33.3% | 23.8% |
| 2025-04 | high_volatility | **FRAGILE** | **FRAGILE** | 22 | 0.0% | 0.0% | 0.0% | 100.0% |
| 2025-05 | ranging | **MATCH** | **MISMATCH** | 21 | 90.5% | 0.0% | 0.0% | 9.5% |
| 2025-06 | ranging | **MATCH** | **MISMATCH** | 20 | 75.0% | 0.0% | 25.0% | 0.0% |
| 2025-07 | ranging | **MATCH** | **MISMATCH** | 22 | 54.5% | 45.5% | 0.0% | 0.0% |
| 2025-08 | high_volatility | **FRAGILE** | **FRAGILE** | 21 | 9.5% | 0.0% | 14.3% | 76.2% |
| 2025-09 | ranging | **MATCH** | **MISMATCH** | 21 | 42.9% | 28.6% | 0.0% | 28.6% |
| 2025-10 | trending_up | **MISMATCH** | **MATCH** | 23 | 47.8% | 52.2% | 0.0% | 0.0% |
| 2025-11 | trending_up | **MISMATCH** | **MATCH** | 19 | 42.1% | 57.9% | 0.0% | 0.0% |
| 2025-12 | ranging | **MATCH** | **MISMATCH** | 22 | 86.4% | 13.6% | 0.0% | 0.0% |
| 2026-01 | trending_down | **MISMATCH** | **MATCH** | 20 | 0.0% | 0.0% | 65.0% | 35.0% |
| 2026-02 | high_volatility | **FRAGILE** | **FRAGILE** | 19 | 0.0% | 0.0% | 0.0% | 100.0% |
| 2026-03 | ranging | **MATCH** | **MISMATCH** | 22 | 59.1% | 0.0% | 27.3% | 13.6% |
| 2026-04 | ranging | **MATCH** | **MISMATCH** | 20 | 65.0% | 0.0% | 5.0% | 30.0% |
| 2026-05 | high_volatility | **MISMATCH** | **FRAGILE** | 20 | 0.0% | 50.0% | 0.0% | 50.0% |
| 2026-06 | high_volatility | **FRAGILE** | **FRAGILE** | 21 | 23.8% | 33.3% | 0.0% | 42.9% |
| 2026-07 | high_volatility | **FRAGILE** | **FRAGILE** | 22 | 0.0% | 18.2% | 0.0% | 81.8% |
| 2026-08 | ranging | **MATCH** | **MISMATCH** | 21 | 61.9% | 4.8% | 33.3% | 0.0% |
| 2026-09 | trending_up | **MISMATCH** | **MATCH** | 21 | 38.1% | 61.9% | 0.0% | 0.0% |
| 2026-10 | ranging | **MATCH** | **MISMATCH** | 5 | 100.0% | 0.0% | 0.0% | 0.0% |

## Audit takeaways

1. **H1 meanrev MATCH in 12/24 months** vs trendfollow MATCH in 5/24 — ranging is the modal month regime (14/24 H1).
2. **Fragile clusters:** Jan–Apr 2025 and Jan–Apr 2026 are high-vol dominant on H1 (both families FRAGILE for most of those months).
3. **Trend windows are rare but sharp:** Dec 2024 and May 2026 flip to trending_up-led MATCH for trendfollow.
4. **TF disagreement is expected:** e.g. May 2025 H1 dominant=ranging but meanrev=MISMATCH because trend shares outvote ranging on the fit map.
5. **2024-10** may appear in price but drop from confirmed boards (regime warmup). Partial **2026-10** has fewer bars.
6. Monthly MATCH is **ex-post**, not a forward signal. Live research gate should use nowcast + 30d shares, not calendar-month prophecy.

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
