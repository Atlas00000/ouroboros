# NVDA — Regime audit & fit tagging (monthly)

> Ex-post calendar-month boards · `regimes.rule_v1` labels → `fit.map_v0`  
> Window: 2026-01 → 2026-10 (9 H1 months with confirmed bars after warmup)

> Broker depth: YWO `NVDA` M1 starts `2026-01-14` (≈275d). Full 2y not available from this feed.

## Method

1. Load H1 / D1 OHLCV (~800d lookback request; broker depth binds).
2. Run `regime_feature_frame` → confirmed regime per bar.
3. Slice each calendar month; map regimes → MATCH / MISMATCH / FRAGILE per edge family.
4. Dominant tag = largest fit-share (ties break MISMATCH > FRAGILE > MATCH).

Families: **meanrev** home=`ranging`; **trendfollow** home=`trending_up|trending_down`; both treat `high_volatility` as FRAGILE.

## Tag summary (months with bars)

| TF × family | MATCH | MISMATCH | FRAGILE |
| --- | ---: | ---: | ---: |
| `H1|meanrev` | 4 | 5 | 0 |
| `H1|trendfollow` | 5 | 4 | 0 |
| `D1|meanrev` | 6 | 0 | 3 |
| `D1|trendfollow` | 0 | 6 | 3 |

Dominant-regime months (H1): {'ranging': 5, 'trending_up': 2, 'high_volatility': 1, 'trending_down': 1}
Dominant-regime months (D1): {'ranging': 6, 'high_volatility': 3}

## H1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2026-02 | ranging | **MATCH** | **MISMATCH** | 48 | 58.3% | 31.2% | 10.4% | 0.0% |
| 2026-03 | ranging | **MATCH** | **MISMATCH** | 154 | 55.8% | 1.9% | 27.3% | 14.9% |
| 2026-04 | trending_up | **MISMATCH** | **MATCH** | 140 | 35.0% | 47.9% | 2.9% | 14.3% |
| 2026-05 | high_volatility | **MISMATCH** | **MATCH** | 140 | 18.6% | 18.6% | 27.1% | 35.7% |
| 2026-06 | ranging | **MATCH** | **MISMATCH** | 147 | 34.7% | 7.5% | 24.5% | 33.3% |
| 2026-07 | ranging | **MATCH** | **MISMATCH** | 154 | 49.4% | 10.4% | 1.9% | 38.3% |
| 2026-08 | trending_up | **MISMATCH** | **MATCH** | 147 | 25.9% | 34.7% | 25.9% | 13.6% |
| 2026-09 | ranging | **MISMATCH** | **MATCH** | 147 | 33.3% | 25.2% | 24.5% | 17.0% |
| 2026-10 | trending_down | **MISMATCH** | **MATCH** | 84 | 33.3% | 15.5% | 51.2% | 0.0% |

## D1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2026-02 | ranging | **MATCH** | **MISMATCH** | 8 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2026-03 | ranging | **MATCH** | **MISMATCH** | 22 | 86.4% | 0.0% | 0.0% | 13.6% |
| 2026-04 | ranging | **MATCH** | **MISMATCH** | 20 | 55.0% | 45.0% | 0.0% | 0.0% |
| 2026-05 | high_volatility | **FRAGILE** | **FRAGILE** | 20 | 0.0% | 25.0% | 0.0% | 75.0% |
| 2026-06 | high_volatility | **FRAGILE** | **FRAGILE** | 21 | 23.8% | 0.0% | 0.0% | 76.2% |
| 2026-07 | ranging | **MATCH** | **MISMATCH** | 22 | 77.3% | 0.0% | 0.0% | 22.7% |
| 2026-08 | ranging | **MATCH** | **MISMATCH** | 21 | 66.7% | 0.0% | 0.0% | 33.3% |
| 2026-09 | high_volatility | **FRAGILE** | **FRAGILE** | 21 | 23.8% | 0.0% | 0.0% | 76.2% |
| 2026-10 | ranging | **MATCH** | **MISMATCH** | 12 | 100.0% | 0.0% | 0.0% | 0.0% |

## Audit takeaways

1. **H1 meanrev MATCH in 4/9 months** vs trendfollow MATCH in 5/9 — modal H1 month regime is **ranging** (5/9), but trendfollow edges slightly ahead on monthly MATCH count.
2. **Fragile H1 months:** none — May 2026 is high_vol-dominant by share but trend mass still outvotes FRAGILE on the fit map. D1 is stricter: May / Jun / Sep are FRAGILE for both families.
3. **Trendfollow MATCH months:** 2026-04, 2026-05, 2026-08, 2026-09, 2026-10 (ex-post; Apr +14% and Aug +11% D1 path months are sharp).
4. **Live gate vs character:** nowcast is **trending_down** at high confidence while history clock stays ranging-led (~37%) — use 30d shares for the research gate (currently trendfollow MATCH).
5. **Partial months:** Jan 2026 drops from confirmed H1 boards (warmup); Oct 2026 is partial (~84 H1 bars).
6. Monthly MATCH is **ex-post**, not a forward signal. Live research gate should use nowcast + 30d shares, not calendar-month prophecy.

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
