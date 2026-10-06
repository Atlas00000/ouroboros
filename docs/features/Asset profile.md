# Asset profile

> **Feature class brief** · product / eng · Jade Desk dossier  
> **Status:** `live` (profile.v1 + living-plane Asset stack; generative / event ATR often thin)  
> **Route:** `/assets/[symbol]`  
> **Related:** [`features.md`](./features.md) · [`docs/pages.md`](../pages.md) · [`Regime fit tags.md`](./Regime%20fit%20tags.md) · `profile.v1` / `state.v1` / `fit.v1` / `sentiment.v1` / `insight.v1`  
> **Last updated:** 2026-10-06

---

## Thesis

The **asset profile** is the living research dossier for one instrument: market path, regime nowcast, durable character (vol, sessions, peers, event sensitivity), fit vs edge family, and labeled narrative context.

It is **advisory / research only** — never execution. Numbers come from deterministic analytics; LLM output is narrative / sentiment only and cannot write numeric fields.

**Core claim:** the page reads as one briefing for a symbol — sectioned living planes from real API cuts, not a stack of generic boxed panels. Contracts stayed; composition and clock-clarity shipped as modular desk fields.

---

## Two clocks

| Clock | Question | Primary source |
| --- | --- | --- |
| **Nowcast** | What is the market doing *now*? | Bars · `state.v1` · live fit tag |
| **Character / history** | What is this instrument *like*? | `profile.v1` (vol, sessions, correlations, regime share, event sensitivities) |
| **Narrative** | What is the news/LLM saying? | `sentiment.v1` · `insight.v1` |

Live regime probabilities (`RegimeNowcastField`) and profile regime-distribution shares (`RegimeHistoryField`) sit side-by-side under **Nowcast · history** with copy that keeps the clocks distinct.

---

## Product surface (Asset page)

Single route: `/assets/[symbol]`. Same composition for every symbol; depth and emptiness vary by data coverage (FX majors tend to be richest).

Desk voice: `ASSET_COPY` + `AssetSection` / `SectionWrap` — eyebrow + wrap per block, same honesty contract as the home desk.

### Sticky mast

| Element | Source | Notes |
| --- | --- | --- |
| Symbol (mono) | Route param | Always present |
| Display name | `profile.identity.display_name` | Optional |
| Regime badge | `state.regime` | Nowcast — not profile history |
| Stale badge | Any of bars / state / profile / sentiment / insight | Aggregate |
| Section wrap | `ASSET_COPY.mast` | “Instrument dossier · research only” |

**Still thin in mast:** no last price, session-open mark, or fit chip (fit lives in its own plane below).

### Section stack (top → bottom)

| # | Section | Plane component(s) | Intent | Key fields |
| --- | --- | --- | --- | --- |
| 1 | **Price path** | `PriceRegimeChart` | Interactive path with regime wash | OHLC/close · TF / chart type · last close · window % · regime tone · stale |
| 2 | **Regime fit** | `FitField` | Research gate vs edge family | Tag MATCH / MISMATCH / FRAGILE · `allow_on` · family toggle · TF · window shares ribbon · fragile reasons · focus probe · disclaimer |
| 3 | **Character · peers** | `ProfileDossier` + `CorrelationField` (`lg:grid-cols-2`) | Durable identity beside peer field | Identity · vol · liquidity proxy · sessions · peer coefficients · bipolar spectrum |
| 4 | **Nowcast · history** | `RegimeNowcastField` + `RegimeHistoryField` (`lg:grid-cols-2`) | Soft probs *now* vs confirmed *share* | Prob % · vol pctile · trend ER · confidence · `regime_distribution[].share` |
| 5 | **Event sensitivity** | `EventSensitivityField` | Calendar taxonomy ± measured move | `event_type` · `typical_move_atr_multiple` · notes · interactive rail |
| 6 | **Narrative pressure** | `SentimentField` + `DriverPress` (`lg:grid-cols-2`) | Score then headlines that moved it | Score [−1,+1] · item count · window · drivers (title · url · source · contribution) |
| 7 | **Desk insight** | `InsightBrief` | Labeled generative narrative | Type · title · body paragraphs · tags · related refs · disclaimer · model · as-of |

```text
NOWCAST     chart · mast badge · RegimeNowcastField · FitField
CHARACTER   ProfileDossier · CorrelationField · sessions · liquidity proxy
HISTORY     RegimeHistoryField · EventSensitivityField
NARRATIVE   SentimentField · DriverPress · InsightBrief
```

Composition is sectioned living planes (clip atmospheres, interactive focus, token tones) — not Bootstrap card stacks. Grid cells stay paired where noted; full-width planes (price, fit, events, insight) are height-capped so the dossier does not balloon.

---

## Data contracts & fetch

SSR payload (`fetchAssetDetailServer` + fit seed):

| Slice | Endpoint (typical) | Contract / model |
| --- | --- | --- |
| Bars | `GET /v1/bars?symbol=&timeframe=H1&lookback_days=45` | Bars + provenance |
| State | `GET /v1/state?symbol=&timeframe=H1` | `state.v1` |
| Profile | `GET /v1/assets/{symbol}/profile` | `profile.v1` |
| Sentiment | `GET /v1/sentiment?symbol=` | `sentiment.v1` |
| Insight | `GET /v1/insights?symbol=` | `insight.v1` |
| Fit | `GET /v1/fit?symbol=&family=&timeframe=H1&window=30d` | `fit.v1` |

Missing slices fail soft (`null`); each plane renders an empty state in place. Chart may client-refetch bars when the user changes timeframe. Fit family toggle client-refetches `/v1/fit` when Clerk JWT is available (SSR seed otherwise).

**Auth:** RSC uses `OUROBOROS_SERVER_API_KEY`; browser fit refresh uses Clerk JWT when Clerk is enabled.

---

## profile.v1 on Desk

Builder: `profiles.v1` (`server/app/analytics/profiles.py`) · refresh via `daily_profiles` / `profile_events` · retention 180d.

| Block | Fields shown on Desk | Backend note |
| --- | --- | --- |
| **Identity** | Display name · asset class · base/quote · venues · version | `mt5_ticker` exists in contract; not shown on dossier |
| **Volatility** | ATR pct 30d · RV pct 30d · typical daily range | From D1 metrics |
| **Liquidity** | Range percentile 30d · notes | Proxy only — true bid/ask deferred |
| **Trading hours** | Sessions · timezone · open/close UTC · notes | Coarse defaults by asset class |
| **Correlations** | Peer coefficients (`CorrelationField`) | H1 ~30d matrix, depth-gated |
| **Regime distribution** | Share per regime (`RegimeHistoryField`) | Prefer H1 confirmed labels; else D1 |
| **Event sensitivities** | Event type · optional × ATR · notes (`EventSensitivityField`) | Calendar taxonomy; ATR multiple when ≥3 scored windows |
| **Provenance** | Model version · as-of · stale on each plane foot | Confidence / sources still light in UI |

---

## Regime fit on the dossier

See [`Regime fit tags.md`](./Regime%20fit%20tags.md).

On this page (`FitField`):

- Living plane (not a dedicated Fit page): tag stage triad · share ribbon · gate pulse · fragile rail · focus probe
- Families v0: `meanrev` · `trendfollow`
- Live tag + ex-post shares (`window=30d`) when the pipe has mass
- Language: research / gate / size-pause only — not an execution signal

---

## Emptiness & honesty

| Usually strong when pipe is up | Often empty or half-empty | Honest-by-design gaps |
| --- | --- | --- |
| Chart · live state · identity/vol · fit nowcast | Correlations · event ATR multiples (until profile rebuild) · sentiment/drivers · insight · sometimes historical regime shares | True spread · broker-true sessions · forward `P(tag)` · fit/regime scoring live on `/scoring` not here |

**Honesty rules already in product language:**

- Research disclaimer on mast and fit / insight surfaces  
- Stale badges on provenance; per-plane stale marks where relevant  
- Liquidity notes call out deferred bid/ask  
- Fit `allow_on` is MATCH-only research gate  
- Empty planes state the missing cut plainly — no placeholder metrics or emoji filler  

---

## Explicit non-goals (dossier)

- Trade execution, order routing, or position sizing automation  
- LLM-written numeric fields  
- Treating monthly MATCH boards or fit `argmax` as profit claims  
- Universe-scale N×API enrichment on this page (single-symbol focus only)  
- Dedicated Fit Desk page as a blocker for dossier usefulness  

---

## Composition stance (shipped + next)

**Shipped:**

1. **One dossier composition** — sticky mast + `AssetSection` stack with shared desk copy.  
2. **Separated clocks** — nowcast vs history labeled and paired in one section.  
3. **Profile as spine** — identity / vol / sessions beside peers; events as their own plane.  
4. **Living planes** — modular fields under `design/patterns/*` (atmosphere, mast, interactive focus, token tones, clip geometry).  
5. **Single-symbol focus** — no home-universe stampede patterns.

**Still open (product, not blockers):**

- Mast enrichment (last price / session mark / optional fit chip)  
- Richer ATR coverage after event-window scoring volume  
- Forward `P(tag)` stays out of this route until scoring gates exist  

---

## Key code map

| Path | Role |
| --- | --- |
| `client/src/app/assets/[symbol]/page.tsx` | Page composition |
| `client/src/design/patterns/asset-copy.ts` | Section eyebrows + wraps |
| `client/src/design/patterns/AssetSection.tsx` | Section chrome |
| `client/src/lib/queries/asset-detail.ts` | SSR fetch + TS profile/state types |
| `client/src/lib/queries/server.ts` | SSR fit seed (`fetchFitServer`) |
| `client/src/design/patterns/price-regime/` | Price + regime chart |
| `client/src/design/patterns/fit/` | `FitField` · chips · hero chip |
| `client/src/design/patterns/profile/` | `ProfileDossier` · event sensitivity exports |
| `client/src/design/patterns/correlation/` | `CorrelationField` peer plane |
| `client/src/design/patterns/regime-nowcast/` | Live soft-prob plane |
| `client/src/design/patterns/regime-history/` | Confirmed-share history plane |
| `client/src/design/patterns/event-sensitivity/` | Event sensitivity plane |
| `client/src/design/patterns/sentiment/` | `SentimentField` |
| `client/src/design/patterns/driver-press/` | Driver headlines plane |
| `client/src/design/patterns/insight-brief/` | `InsightBrief` narrative plane |
| `client/src/design/patterns/state/` | Re-exports nowcast / history for page imports |
| `server/app/analytics/profiles.py` | profile.v1 builder |
| `server/app/analytics/event_sensitivities.py` | Event taxonomy + ATR windows |
| `packages/contracts/contracts/profile_v1.py` | Contract |

---

## Changelog

| Date | Change |
| --- | --- |
| 2026-10-06 | Living-plane dossier inventory — FitField, ProfileDossier, CorrelationField, nowcast/history pair, EventSensitivityField, SentimentField, DriverPress, InsightBrief; code map + composition stance refreshed |
| 2026-10-06 | Initial brief — dossier inventory, clocks, profile.v1 Desk fields, rework stance |
