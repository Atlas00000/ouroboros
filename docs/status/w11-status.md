# W11 status — System, Scoring, Admin + RoleGate (local)

**Date:** 2026-09-14  
**Scope:** W11·D1–D5 complete · tag `v0.5-client`

## Delivered

### API
- `GET /v1/ops/registry` — feed cadence snapshots (admin+)
- `GET /v1/ops/watchdog` — live check, alerts (admin+; no email)
- `GET /v1/ops/summary` — outbox depth, LLM day spend, lag strip (admin+)
- `GET /v1/scoring/weekly` — stored weekly accuracy reports
- `GET/POST /v1/admin/keys`, `POST /v1/admin/keys/{id}/revoke` — mint (plaintext once) / revoke
- Bootstrap: `OUROBOROS_API_KEY_CLIENT` → **admin** role (EPG/quant remain viewer)

### Client
- `RoleGate` + role-aware AppNav (System/Admin require admin+)
- System: `PipeHealthStrip` · `FeedRegistryTable` · `WatchdogAlertsList`
- Scoring: `ScoringResults`
- Admin: mint/revoke panel (Clerk JWT or local server actions)
- `AppShell`: skip link, `#main`, research disclaimer footer
- Empty/error/loading via `PageState`; focus-visible + `aria-current`
- `public/logo.svg` + metadata icon
- Playwright smoke (`client/e2e/smoke.spec.ts`) — sign-in gate, dashboard, asset detail, System role-denied via `e2e_role` cookie
- CI: client build + Playwright job in `.github/workflows/ci.yml`

## Smoke

| Check | Result |
|-------|--------|
| W11 API tests | passed |
| Live ops/scoring/admin | 200 |
| `pnpm build` | success |
| `pnpm test:e2e` (system Chrome locally) | 4/4 passed |

## Tag

`v0.5-client` — Phase 4 client baseline against `v0.4-api`.
