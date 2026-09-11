# ADR-001: Hard client/server deploy split

- **Status:** Accepted
- **Date:** 2026-09-11
- **Roadmap ref:** Decision #10

## Context

Ouroboros will host the UI on Vercel and the API/worker/database on Railway. A monorepo that mixes roots or shares a single Dockerfile forces a painful split later.

## Options

1. Single app folder with coupled deploy
2. Separate `client/` and `server/` roots from day one, each with its own Dockerfile, env template, and lockfile

## Decision

Option 2. Vercel project root = `client/`. Railway root = `server/`. Shared artifacts only: `packages/contracts` and the OpenAPI-generated client. No cross-imports between client and server source.

## Consequences

- Week 12 production cutover is configuration, not refactoring
- Slightly more boilerplate early; compose profiles wire local Docker optionally
- Client always uses absolute `NEXT_PUBLIC_API_URL`
