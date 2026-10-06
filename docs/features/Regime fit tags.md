# Regime fit tags

> **Feature class brief** · research / engineering  
> **Status:** `live` (R0–R4 + Desk overlays + fit stickiness scoring) · forward `P(tag)` still planned  
> **Related:** [`features.md`](./features.md) · [`Regime fit tags roadmap.md`](./Regime%20fit%20tags%20roadmap.md) · [`preset-factory-roadmap.md`](../../preset-factory-roadmap.md) · ADR-017  
> **Last updated:** 2026-10-06

---

## Thesis

Raw regimes answer “what is the market doing?”  
Fit tags answer “is that environment good, bad, or fragile for *this* edge family?”

`regimes.rule_v1` is a **nowcaster** (vol × ER + persistence). Today’s forecast log scores **label stickiness** one bar later — not “will next month be a MATCH month.” Preset Factory proved that sibling EAs need a second vocabulary: **MATCH / MISMATCH / FRAGILE** conditioned on edge family (`meanrev`, `trendfollow`, …) and timeframe. Without that layer, you either over-trust monthly boards or can’t gate research books honestly.

**Core claim:** fit is a mapping + audit problem first, a forecasting problem second. Ship a deterministic, auditable fit layer before any forward `P(tag)`.

---

## Feature class

| Feature | Intent | Maturity |
| --- | --- | --- |
| **Family map** | Regime → {MATCH, MISMATCH, FRAGILE} given edge family + home TF | Research probes; not productized |
| **Multi-TF fit stack** | Same symbol, tags per M5/M15/H1/D1 (not one global tag) | Probes showed TF context is mandatory |
| **Ex-post boards** | Dominant-share tag over a closed window (month / 7d / 30d) | Canvas / offline |
| **Live gate** | Nowcast fit: ON only while decision TF is non-kill | Research helper shipped (`fit.gate` + `fit.entry_gate`); DV.mq5 v1.01 consumer |
| **Fit shares API** | `symbol × TF × family →` current tag + share history | Planned (factory Phase 1 consumer) |
| **Forward `P(tag)`** | Calibrated probs @ 7d / 30d / 60d + drivers | Planned grow-into; gated by scoring |
| **Fit scoring** | Brier/calibration vs persistence; costlier miss on kill-side | Planned before factory trusts probs |
| **Desk / research surface** | Boards + soft overlays (not a Jade Desk v1 page yet) | Planned |

**Out of this class:** trade signals, preset emit, geometry policy — those are Preset Factory / Edge Framework. Fit tags are the **context contract** they consume.

### Tag vocabulary

| Tag | Meaning (factory / research) |
| --- | --- |
| **MATCH** | Environment fits the family’s home cell |
| **MISMATCH** | Kill / adverse regime for that family |
| **FRAGILE** | Event / vol-cluster caution — size or pause |

---

## Systems / subsystems

```
prices / caggs
    → regimes.rule_v1 (nowcast) + state.v1
         → fit mapper (family + TF + calendar overlay)
              → fit store / forecast_log call_type (or dedicated table)
                   → scoring job (realized share vs predicted)
                        → API + Streams (+ optional desk)
                             → Preset Factory / EPG / research
```

| Subsystem | Role |
| --- | --- |
| **Regime engine** (exists) | Deterministic labels + soft probs |
| **Family registry** (new) | Edge class profiles: home cell, kill regimes, FRAGILE rules |
| **Fit mapper** (new) | Pure function: state(+calendar) → tag; versioned (`fit.map_v0`) |
| **Board builder** (partial offline) | Windowed dominant share → monthly/rolling boards |
| **Fit forecast store** (new) | Immutable predictions + delayed realized (same provenance pattern as regime log) |
| **Fit scorer** (new) | Horizon accuracy + calibration; separate MATCH/MISMATCH/FRAGILE scores |
| **Serve** | REST (+ later events); provenance + research disclaimer |
| **Consumers** | Preset Factory gate/tier; sibling quant; optional Desk overlay |

**Upstream (already live):** Timescale bars, calendar/high-impact news, forecast_log patterns, weekly scoring pipeline.  
**Downstream:** factory emit stays **off** until contracts + scoring gates exist.

---

## Requirements

### Functional

1. Define at least `meanrev` and `trendfollow` family maps (invert fit on same regime path where appropriate).
2. Tag object is always **symbol × timeframe × family** — never symbol-only.
3. Three tags only in v0: MATCH / MISMATCH / FRAGILE.
4. Ex-post board: dominant confirmed-regime share over window → mapped tag.
5. Live gate: current nowcast → tag for decision TF (hours–days trust band).
6. API: current fit + optional history/shares; every payload has provenance + disclaimer.
7. Forward layer (later): `P(tag | …)` @ {7d, 30d, 60d}; never a hard binary emit trigger by default.
8. Scoring before promotion: beat persistence on Brier @ 30d; report calibration; kill-side misses weighted higher for trendfollow ON.

### Non-functional / honesty

- Deterministic fit map is testable with fixtures (same bar as regimes).
- No LLM in the fit path.
- No execution semantics; language is research / gate / size-pause only.
- Monthly MATCH is not a profit claim; forward `argmax` is not permission to drop EF geometry.

### Explicit non-requirements (v0)

- HMM in the fit path  
- Desk page as a blocker  
- Auto-emit presets from tags  
- Single “next month” prophecy tag  

---

## Design stance

1. **Two clocks:** nowcast stickiness (live today) ≠ calendar-month outlook (ex-post / future probs).  
2. **Family conditioning is first-class** — same EURUSD D1 can be MATCH for meanrev and MISMATCH for trendfollow.  
3. **TF is part of the key** — Trend Catcher boards showed intraday MISMATCH all year while D1 occasionally MATCH.  
4. **Ship map → boards → API → live gate → forward probs** — not the reverse.  
5. **Factory may read nowcast+boards now; may size/pause from `P(tag)` only after the scoring gate.**

### Trust by horizon

| Horizon | Trust today | Factory use |
| --- | --- | --- |
| Hours → few days | Higher | Live / research **gate**: stay ON only while home TF stays non-kill |
| Rest of *current* month | Medium | Soft update as bars accumulate |
| Next calendar month as one hard tag | Low | Scenario / odds only — not a binary emit trigger |
| Month +2 as one hard tag | Very low | Structural prior at best — not a product claim |

---

## Suggested next engineering slice

See the phased build plan: [`Regime fit tags roadmap.md`](./Regime%20fit%20tags%20roadmap.md).

**v0:** family registry + `fit.map_v0` + offline board builder with golden fixtures.  
API after the map is frozen.

---

## Changelog

| Date | Change |
| --- | --- |
| 2026-10-03 | `fit.entry_gate` + DV NAS100 G1c (live MATCH + anti-drift); monthly boards not a gate |
| 2026-10-03 | R0–R4 shipped — see roadmap |
| 2026-10-03 | Linked build roadmap |
| 2026-10-03 | Initial brief captured from feature-class design chat |
