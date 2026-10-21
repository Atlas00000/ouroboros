# UK100 — Regime audit & fit tagging (monthly)

> Ex-post calendar-month boards · `regimes.rule_v1` labels → `fit.map_v0`  
> Window: 2025-12 → 2026-10 (11 H1 months with confirmed bars after warmup)

> Broker depth: YWO `UK100` M1 starts `2025-12-17` (≈298d). Full 2y not available from this feed.

## Method

1. Load H1 / D1 OHLCV (~800d lookback request; broker depth binds).
2. Run `regime_feature_frame` → confirmed regime per bar.
3. Slice each calendar month; map regimes → MATCH / MISMATCH / FRAGILE per edge family.
4. Dominant tag = largest fit-share (ties break MISMATCH > FRAGILE > MATCH).

Families: **meanrev** home=`ranging`; **trendfollow** home=`trending_up|trending_down`; both treat `high_volatility` as FRAGILE.

## Tag summary (months with bars)

| TF × family | MATCH | MISMATCH | FRAGILE |
| --- | ---: | ---: | ---: |
| `H1|meanrev` | 8 | 1 | 2 |
| `H1|trendfollow` | 1 | 8 | 2 |
| `D1|meanrev` | 5 | 1 | 4 |
| `D1|trendfollow` | 0 | 5 | 5 |

Dominant-regime months (H1): {'trending_up': 1, 'ranging': 8, 'high_volatility': 2}
Dominant-regime months (D1): {'high_volatility': 5, 'ranging': 5}

## H1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2025-12 | trending_up | **MISMATCH** | **MATCH** | 10 | 30.0% | 70.0% | 0.0% | 0.0% |
| 2026-01 | ranging | **MATCH** | **MISMATCH** | 470 | 45.3% | 19.6% | 9.6% | 25.5% |
| 2026-02 | ranging | **MATCH** | **MISMATCH** | 450 | 39.6% | 22.9% | 2.2% | 35.3% |
| 2026-03 | high_volatility | **FRAGILE** | **FRAGILE** | 506 | 21.3% | 6.9% | 8.9% | 62.8% |
| 2026-04 | ranging | **MATCH** | **MISMATCH** | 458 | 55.7% | 11.1% | 19.7% | 13.5% |
| 2026-05 | ranging | **MATCH** | **MISMATCH** | 432 | 51.4% | 16.0% | 16.4% | 16.2% |
| 2026-06 | ranging | **MATCH** | **MISMATCH** | 506 | 51.2% | 13.2% | 9.7% | 25.9% |
| 2026-07 | ranging | **MATCH** | **MISMATCH** | 527 | 43.6% | 11.8% | 8.7% | 35.9% |
| 2026-08 | ranging | **MATCH** | **MISMATCH** | 459 | 79.3% | 8.3% | 9.4% | 3.1% |
| 2026-09 | ranging | **MATCH** | **MISMATCH** | 503 | 44.7% | 12.1% | 14.9% | 28.2% |
| 2026-10 | high_volatility | **FRAGILE** | **FRAGILE** | 161 | 18.0% | 4.3% | 14.3% | 63.4% |

## D1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2026-01 | high_volatility | **FRAGILE** | **FRAGILE** | 8 | 0.0% | 0.0% | 0.0% | 100.0% |
| 2026-02 | high_volatility | **FRAGILE** | **FRAGILE** | 24 | 0.0% | 4.2% | 0.0% | 95.8% |
| 2026-03 | high_volatility | **FRAGILE** | **FRAGILE** | 27 | 0.0% | 14.8% | 11.1% | 74.1% |
| 2026-04 | high_volatility | **MISMATCH** | **FRAGILE** | 23 | 13.0% | 39.1% | 4.3% | 43.5% |
| 2026-05 | ranging | **MATCH** | **MISMATCH** | 22 | 77.3% | 0.0% | 0.0% | 22.7% |
| 2026-06 | ranging | **MATCH** | **MISMATCH** | 26 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2026-07 | ranging | **MATCH** | **MISMATCH** | 27 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2026-08 | ranging | **MATCH** | **MISMATCH** | 24 | 54.2% | 45.8% | 0.0% | 0.0% |
| 2026-09 | ranging | **MATCH** | **MISMATCH** | 26 | 61.5% | 0.0% | 0.0% | 38.5% |
| 2026-10 | high_volatility | **FRAGILE** | **FRAGILE** | 9 | 0.0% | 0.0% | 0.0% | 100.0% |

## Audit takeaways

1. **H1 meanrev MATCH in 8/11 months** vs trendfollow MATCH in 1/11 — modal H1 month regime is **ranging** (8/11).
2. **Fragile months:** 2026-03, 2026-10 (high_vol-dominant → both families FRAGILE).
3. **Trendfollow MATCH months:** 2025-12 (ex-post; not forward signals).
4. **Live gate vs character:** nowcast can lean trending_up while history clock stays ranging-led — use 30d shares for the research gate.
5. **Partial months:** early/late months may have few confirmed bars after regime warmup (e.g. Mar / Oct).
6. Monthly MATCH is **ex-post**, not a forward signal. Live research gate should use nowcast + 30d shares, not calendar-month prophecy.

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
