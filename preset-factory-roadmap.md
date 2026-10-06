# Preset Factory Roadmap

> **Version:** 0.2 · **Date:** 2026-09-15 · **Status:** Draft (post Dark Venus + Trend Catcher probes)  
> **Related:** [`roadmap.md`](roadmap.md) (Ouroboros platform) · Edge Framework (`unified_edge_framework.md`) · sibling EAs (Dark Venus, Trend Catcher, EPG, …)

## One-liner

A **preset factory** turns an established quant system’s design + inputs into **survivable, Edge-aligned tester/live presets**, using **Ouroboros** as the market-context brain and **Edge Framework** as the geometry / survival / decay contract. It does **not** execute trades and does **not** replace Ouroboros’s “no execution” boundary.

## Why this exists

Manual probe (2026-09-15) on **Dark Venus MT5** × EURUSD showed:

1. **Ouroboros regimes** can label MATCH / MISMATCH / FRAGILE for a declared edge family (meanrev for Dark Venus; trendfollow for EPG).
2. An unbounded Market preset (stop off, 50-leg grid, 50pt step) **fails survival** inside a month tagged MATCH — ruin masks edge decay.
3. An **EF-G1** preset (declared 1R, RR ≥ 1.5, max 3 legs, wider step, Friday flatten, monetary fuse) **survives** full boards, scales linearly with lots, and makes tag accuracy + decay measurable.

Conclusion: Ouroboros can **serve** systems like Dark Venus with context; a thin factory layer on top can **emit presets** when given system profile + input schema + Edge policy.

## Scope boundaries

| In scope | Out of scope |
|----------|----------------|
| Regime / profile fit for a declared edge class | Trade execution / order routing |
| Edge geometry rules (1R, RR, basket depth, fuses) | Optimizing for max profit / WR alone |
| Emit `.set` / JSON presets for known EA templates | Claiming live edge or investment advice |
| Score presets vs Ouroboros tags + Tester blotters | Shipping machine API keys in browsers |
| Internal research tooling for sibling platforms | Public / external subscribers (v1) |

**Hard geometry rule:** never emit a preset with designed **TP &lt; SL** (negative expectancy by design). Minimum designed **RR ≥ 1.0**; default research target **RR ≥ 1.5** unless the EA’s Edge adapter explicitly documents a high-WR meanrev exception *and* the operator overrides — default path stays RR ≥ 1.5.

## Architecture (three layers)

```
┌─────────────────────────────────────────────────────────┐
│  Preset Factory (sibling service / workspace tooling)   │
│  - EA adapters (input schema, .set emitter)             │
│  - Edge geometry policy (1R, RR, depth, fuses)          │
│  - Validation (Tester log / blotter → health vector)    │
└────────────▲────────────────────────────▲───────────────┘
             │ context                    │ blotter / score
┌────────────┴────────────┐    ┌──────────┴───────────────┐
│  Ouroboros              │    │  Edge Framework          │
│  regimes, profiles,     │    │  E_N, EF, Leak, 1R,      │
│  events, scoring APIs   │    │  survival, decay (L5)    │
│  (no execution)         │    │                          │
└─────────────────────────┘    └──────────────────────────┘
             │
             ▼
      Existing EAs (Dark Venus, EPG, …)
      MT5 Strategy Tester / demo charts
```

- **Ouroboros** = market brain (what regime is it?).
- **Edge Framework** = survival & expectancy contract (is the geometry legal / measurable?).
- **Preset Factory** = adapter + emitter + validate loop (produce the `.set`, prove it).

## Inputs the factory needs (per system)

1. **System profile** — edge class (`meanrev` | `trendfollow` | …), symbol(s), chart TF(s), trade-cycle (scalp / intraday / swing), kill regimes, declared home cell.
2. **Input schema** — full EA inputs with types, enums, defaults, units (points vs pips), and which knobs define TP / SL / grid / sessions.
3. **Edge adapter metadata** — how **1R** is defined (hard stop vs declared max basket risk), max legs per event, whether legs share one `group_id`.
4. **Operator constraints** — deposit class, max DD fuse, lot policy, “never TP &lt; SL”, Friday policy, spread cap.
5. **Optional:** prior blowup / baseline `.set` for regression (“must not ruin on known impulse window”).

## Outputs

| Artifact | Purpose |
|----------|---------|
| `*.set` (MT5) or versioned JSON preset | Load in Tester / chart |
| Geometry card (RR, 1R, depth, fuses) | Human audit |
| Fit report (Ouroboros MATCH/MISMATCH/FRAGILE shares) | Environment context |
| Validation report (survival, monthly tag score, `E_N` stub) | Accept / reject preset |
| Magic / comment identity | Keep books separable |

## Proven loop (Dark Venus reference)

| Step | What happened |
|------|----------------|
| Map family | Dark Venus BB counter-trend → Edge **meanrev** (native = range) |
| Context | Ouroboros `regimes.rule_v1` on M1 / M5 / M15 / D1 → monthly tags |
| Emit | `Profiles/Tester/Dark Venus/DV-M5-EF-G1_tagAccuracy.set` |
| Contrast | Baseline 50/500 stop-off → June ruin; EF-G1 → year boards survive |
| Score | ~9/13 months on crude sign rule; lot scale linear on MATCH month |

Preset path (reference):  
`MQL5/Profiles/Tester/Dark Venus/DV-M5-EF-G1_tagAccuracy.set`

## Impact on survival and edge decay

| | Unbounded preset | Factory / EF geometry |
|--|------------------|------------------------|
| **Survival** | Ruin on one impulse; MaxDD / `f` undefined | Declared 1R, capped depth → Stage 3 capital math possible |
| **Edge decay (L5)** | Masked by account death | Rolling `E_N` / freq / `RR−R` observable |
| **Regime tags** | Can’t validate after ruin | Partial accuracy; better as entry-time gate than month-max alone |

Factory success = presets that are **survivable and auditable**, not max backtest profit.

## What Ouroboros could grow into (forward probabilistic tag layer)

### Honest baseline (today)

`regimes.rule_v1` is a **nowcaster**: vol percentile × Kaufman ER + short bar persistence. The forecast log mostly scores whether a label still holds **one bar later** (H1 ≈ 60m, D1 ≈ 1 day) — stickiness, not a calendar-month outlook. Monthly MATCH / MISMATCH / FRAGILE boards used by the factory are **ex-post** (largest regime share after the month closes).

| Horizon | Trust today | Factory use |
|---------|-------------|-------------|
| Hours → few days | Higher | Live / research **gate**: stay ON only while home TF stays non-kill |
| Rest of *current* month | Medium | Soft update as bars accumulate |
| Next calendar month as one hard tag | Low | Scenario / odds only — not a binary emit trigger |
| Month +2 as one hard tag | Very low | Structural prior at best — not a product claim |

Trend Catcher 3y EURUSD board reinforced this: D1 MATCH months were sparse (~10/36) and did **not** form long ON streaks a naive “continue last month” rule could ride. Intraday TFs can stay MISMATCH all year while swing D1 occasionally MATCH — so a single forward tag without TF context is the wrong object.

### Target capability (grow-into)

A **probabilistic forward tag layer** — not a single prophesied MATCH/MISMATCH for “next month”:

```
P(tag_{TF,family} | state_now, structure, calendar)  over horizons H ∈ {7d, 30d, 60d}
```

Emits for the factory (examples):

| Output | Meaning |
|--------|---------|
| `P(D1 MATCH \| trendfollow)` @ 30d | Odds swing gate opens / stays useful |
| `P(M5 MISMATCH \| trendfollow)` @ 30d | Odds kill regime dominates intraday book |
| `P(FRAGILE)` @ 7d / 30d | Event / vol-cluster caution → size or pause |
| Confidence + drivers | Why (vol term, flip rate, days-to-FOMC, …) — audit trail |

**Factory consumption rule:** use probabilities to **size, pause, or choose preset tier** (full EF-G1 vs flat-lot only vs off). Never treat `argmax` of a 30d/60d distribution as a guarantee of profit or as permission to disable survival geometry.

### Feature sketch (research)

Inputs that respect market structure without pretending FX has a clean monthly cycle:

1. **State now** — confirmed regime + soft probs (rule_v1), multi-TF stack (M5/M15/H1/D1).
2. **Dynamics** — recent flip rate, days-in-regime, ER / vol-percentile trajectory (not just level).
3. **Vol structure** — realized vs trailing percentile; optional range expansion after shocks (mean-revert prior for FRAGILE → non-FRAGILE).
4. **Calendar / event distance** — high-impact FX events (already on Ouroboros ingestion path) as FRAGILE lift near the window.
5. **Family conditioning** — separate heads or calibrated maps for `trendfollow` vs `meanrev` (same regime path, inverted fit).

Model stance: start with **calibrated classifiers / ordinal models** scored at fixed horizons; revisit HMM / generative paths only if they beat rule-conditioned baselines on **agreement + horizon accuracy** (see ADR-017 spirit: interpretability gate stays).

### Scoring contract (must exist before factory trusts it)

| Horizon | Realized label | Hit definition (v0) |
|---------|----------------|---------------------|
| 7d | Dominant confirmed regime share over next 7d on that TF | Predicted mass on realized bucket |
| 30d / 60d | Monthly-style share or dominant tag over the forward window | Brier / log-loss + calibration; optional sign gate accuracy for factory |

Ship as `forecast` call_type rows (or a dedicated forward table) with immutable prediction JSON and delayed `realized_json` — same provenance pattern as today’s regime log, **different horizon**.

Promotion gate (factory may subscribe only after):

1. Better than persistence baseline (“tomorrow = today”, “next month = this month”) on Brier at 30d.  
2. Calibration band reported (not only accuracy).  
3. Separate scores for MATCH vs MISMATCH vs FRAGILE (kill-side misses are costlier for trendfollow ON decisions).  
4. Explicit disclaimer in API: research odds, not execution signals.

### Factory integration (when ready)

```
Ouroboros nowcast (gate live) ──┐
                                ├──► preset emit / tier / size recommendation
Ouroboros P(tag) @ 30d/60d ─────┘        (still no orders)
Edge geometry policy (EF-G1) ───────────► always applied if ON
```

- **Phase A (now):** factory + live gate = nowcast + ex-post boards only.  
- **Phase B:** forward probs as **soft overlays** on research dashboards.  
- **Phase C:** emit path may auto-select “reduced risk” preset when P(kill) high — still never TP &lt; SL, still no execution.

Until Phase B scoring clears the gate, forward-month tags remain **research hypotheses** in canvases/docs, not factory inputs.

## Phased roadmap

### Phase 0 — Capture (done / in progress)

- [x] Dark Venus probe: regime tags canvas + monthly board  
- [x] EF-G1 preset + README under Tester profiles  
- [x] Multi-window / multi-lot log review (survival vs baseline)  
- [x] Document this roadmap  
- [ ] Freeze “geometry policy v0” (RR ≥ 1.5, max legs ≤ 3, stop required, Friday policy)

### Phase 1 — Contracts

- [ ] `docs/data-contracts` (or sibling) for `SystemProfile`, `EaInputSchema`, `PresetSpec`, `GeometryCard`
- [ ] Edge adapter checklist: G0 (declared 1R), basket = one event, designed RR vs realised R
- [ ] Ouroboros API consumers: regime series + monthly fit shares for symbol×TF×family
- [ ] ADR: Preset Factory is a sibling workflow; Ouroboros remains no-execution

### Phase 2 — First automated emitter (Dark Venus)

- [ ] Formalize Dark Venus input schema from Market EA (enums for StopTargetMode, BB strategies, …)
- [ ] Template emitter: profile + policy → `.set` (magic, comment, geometry knobs only; signal defaults frozen)
- [ ] Golden tests: refuse TP &lt; SL; refuse stop disabled; refuse max legs &gt; policy
- [ ] Validation script: parse Tester log → deposit/final, SO/NM counts, monthly P&L vs Ouroboros tags

### Phase 3 — Second system (EPG)

- [ ] Reuse factory with EPG profile (M5 chart, H1 bias, trendfollow family)
- [ ] Emit EPG `.set` variants under existing Profiles/Tester conventions
- [ ] Compare tag accuracy trendfollow vs meanrev on same EURUSD window

### Phase 4 — Productize lightly

- [ ] CLI or internal API: `preset emit --system dark-venus --policy ef-g1 --symbol EURUSD --tf M5`
- [ ] Store preset versions + validation reports next to scorecards (not in Ouroboros price DB)
- [ ] Optional: subscribe to Ouroboros `regime.changed` for **gate recommendations** (still no orders)
- [ ] Wire weekly scoring email / dashboard row: “preset health” for active research books

### Phase 4b — Forward probabilistic tags (Ouroboros grow-into)

- [ ] Spec `ForwardTagForecast` contract: symbol × TF × family × horizon ∈ {7d, 30d, 60d} → P(MATCH/MISMATCH/FRAGILE) + drivers
- [ ] Persistence / “same as current month” baselines + Brier/calibration scoring job
- [ ] Feature v0: multi-TF state, flip rate, vol trajectory, event-distance prior
- [ ] Dashboard / canvas: forward odds as soft overlay (not emit trigger)
- [ ] Promotion gate doc: beat baseline before factory may size/pause from P(kill)
- [ ] Only then: optional emit tiering from forward probs (geometry policy still mandatory)

### Phase 5 — Decay & capital (Edge Stage 2–3)

- [ ] Blotter → health vector (`n`, WR, R, E_N, Leak, freq_90d)
- [ ] FREQUENCY_STALL / temporal decay flags on factory-validated books only
- [ ] Monte Carlo stub: P95 MaxDD at operating `f` once 1R is stable
- [ ] Regime-conditional expectancy (MATCH vs MISMATCH slices) — replaces crude month sign score

## Success criteria (factory v1)

1. Given profile + schema + policy, emit a preset that **loads in MT5** without manual knob hunting.  
2. On a known ruin / **OOR stress** window, factory preset **survives** (no stop-out / margin-fail) — full multi-year profit is **not** required.  
3. On **in-regime** slices (MATCH at the EA’s decision TF), produce enough events for a health vector and target `E_N > 0` (maximize).  
4. Geometry card always shows **RR ≥ 1.0** (default ≥ 1.5) and enabled stop.  
5. Ouroboros remains unused for execution; factory only reads context APIs / offline regime exports.  
6. Score **regime-conditional** `E_N` (and stress survival) — never treat full-window PnL alone as pass/fail.

## Non-goals / anti-patterns

- Emitting “Market default” grids with stop disabled “because WR looks high.”  
- Using monthly MATCH as a guarantee of profit.  
- Requiring **full-window** profitability as a factory pass (regimes differ; ON-everywhere is a diagnostic, not the objective).  
- Treating next-month / month+2 **hard tags** as factory truth before horizon scoring beats persistence baselines.  
- Fitting presets only on the decay window that killed the prior book (Edge rediscovery rule).  
- Putting preset binaries or broker credentials into the Ouroboros repo.

## Open decisions

1. Host factory code in Ouroboros `tools/`, Edge_Framework repo, or a new `preset-factory` sibling?  
2. Persist validation reports in EA `doc/artifacts/` vs a shared research store?  
3. Promote RR ≥ 1.5 as hard policy or allow documented meanrev high-WR exceptions? (**Default: hard RR ≥ 1.5.**)  
4. Who owns magic-number / comment registry across EPG, Dark Venus, Trend Catcher, DVG?  
5. First forward horizon to productize for factory overlays: **30d** only, or ship 7d+30d together?

## References

- Ouroboros platform roadmap: [`roadmap.md`](roadmap.md)  
- Edge Framework: `Edge_Framework/unified_edge_framework.md` (1R, E_N, survival, L5 decay)  
- ADR-017: keep `regimes.rule_v1` over HMM until agreement / scored accuracy gates pass  
- Dark Venus probe canvas: `canvases/dark-venus-eurusd-regime-mismatch.canvas.tsx`  
- Trend Catcher probe canvas: `canvases/trend-catcher-eurusd-regime-mismatch.canvas.tsx`  
- EF-G1 presets: `…/Tester/Dark Venus/DV-M5-EF-G1_tagAccuracy.set`, `…/Tester/Trend Catcher/TC-M1-EF-G1_tagAccuracy.set`
