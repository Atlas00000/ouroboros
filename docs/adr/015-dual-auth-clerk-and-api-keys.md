# ADR-015: Dual auth — Clerk (humans) + API keys (machines)

- **Status:** Accepted
- **Date:** 2026-09-11
- **Roadmap ref:** Decision #15

## Context

The dashboard is used by people; EPG and quant platforms are machines. One auth mechanism fits neither well: shared API keys are bad for humans; interactive Clerk sessions are bad for services.

## Options

1. API keys only (dashboard uses a browser-held key)
2. Clerk only (services mint Clerk machine tokens)
3. Dual auth: Clerk JWT for humans; hashed API keys for machines on the same API

## Decision

Option 3.

```
Browser → Clerk session → Authorization: Bearer <JWT> → API (JWKS verify)
EPG/Quant → X-API-Key: <key> → API (hash lookup)
```

Roles for humans: `viewer` | `analyst` | `admin` | `ops`. Machine keys never ship in the browser bundle. Org is invite-only in v1.

## Consequences

- FastAPI dependency resolves either scheme into `HumanPrincipal` | `ServicePrincipal`
- OpenAPI documents both security schemes
- Slightly more auth code; clearer security boundary and audit trail (`auth_method`)
