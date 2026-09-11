# ADR-012: Walking skeleton continuous deploy on Railway

- **Status:** Accepted
- **Date:** 2026-09-11
- **Roadmap ref:** Decision #12

## Context

Deploying only after weeks of local work concentrates infrastructure risk (Timescale image, networking, secrets, CORS) into one “big bang” day.

## Options

1. Local-only until Phase 3, then first Railway deploy
2. Deploy a minimal health endpoint + DB + Redis to Railway staging in Week 1 and keep continuous deploy thereafter

## Decision

Option 2 (walking skeleton). Staging is live from W1·D5; every later phase lands on real infrastructure as it is built.

## Consequences

- Need Railway account and secrets early
- Faster feedback on ops issues
- Backend freeze (W8) is a soak, not a first deploy
