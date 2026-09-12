# ADR-017: Keep rule-based regimes; do not promote HMM spike

- **Status:** Accepted
- **Date:** 2026-09-12
- **Roadmap ref:** Phase 2 W5·D5; locked baseline HMM row

## Context

`regimes.rule_v1` (vol percentile × Kaufman ER grid + N=3 persistence) meets flip-rate budgets on H1/D1. W5·D5 timeboxed a 4-state Gaussian HMM (`hmmlearn`) on the same features as a `regimes.hmm_v1` candidate. Promotion required: better flip-rate **without** losing accuracy / interpretability.

## Options

1. **Promote HMM** to production classifier (`regimes.hmm_v1`), keep rule as fallback
2. **Keep rule_v1** in production; retain HMM code as experimental spike only
3. Hybrid: HMM soft probs, rule hard labels

## Evidence (H1, ~400d, 14 depth-eligible symbols)

| Metric | rule_v1 | hmm_v1 |
| --- | ---: | ---: |
| Avg flips / day | 0.989 | **0.849** |
| Symbols within ≤2/day budget | 14/14 | 14/14 |
| Avg label agreement | — | **0.490** |

Source: `ops/analytics/compare_hmm_regimes.py` → `docs/status/w5d5-hmm-summary.json`.

HMM slightly reduces flips but **agreement with the interpretable rule is ~49%** (below the spike gate of 0.55). State→label mapping via emission means is unstable across symbols (label collisions / reordering). No external ground-truth accuracy metric exists yet (scoring lands in W8).

## Decision

**Option 2.** Production remains `regimes.rule_v1`. HMM stays optional (`pip install ouroboros-server[hmm]`), not wired into the worker or forecast log by default.

Promotion gate (unchanged): mean HMM flip-rate strictly better, all symbols within budget, **and** mean agreement ≥ 0.55 (or a later scored accuracy metric from W8).

## Consequences

- Profiles, forecast log, and scheduler continue to use rule classifications
- `app/analytics/hmm_regimes.py` + compare CLI kept for future revisits
- Tag Phase 2 closeout as `v0.3-analytics` after the analytics commit lands
