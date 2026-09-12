# W6·D1 status — dual-auth + assets/profiles API

**Date:** 2026-09-12  
**Phase 2 tag:** `v0.3-analytics` @ `d33f4d5`

## Delivered

- `app/auth/` — `api_keys.py`, `clerk_jwt.py`, `roles.py`, `dependencies.py`
- Migration `0008_api_keys` — hashed machine keys at rest
- RFC 9457 `application/problem+json` (`app/api/errors.py`)
- Cursor pagination helpers (`app/api/pagination.py`)
- Routers: `GET /v1/assets`, `GET /v1/assets/{symbol}/profile` (auth required)
- Health remains public
- OpenAPI security schemes: `bearerAuth` + `apiKeyAuth`
- Env bootstrap: `OUROBOROS_API_KEY_*` → hashed upsert on startup
- Local Clerk smoke: `CLERK_TEST_JWT_SECRET` (HS256) when JWKS empty
- Tests: `tests/test_auth_api_w6d1.py`
- Smoke: `scripts/smoke_auth_assets.py`

## Smoke

| Path | Result |
| --- | --- |
| `X-API-Key` → `/v1/assets` | 200, 15 items |
| Bearer test JWT → `/v1/assets` | 200 |
| API key → `/v1/assets/EURUSD/profile` | 200 (`profile.v1`) |
| No auth → `/v1/assets` | 401 problem+json |

## Next

**W6·D2** — `states` → `metrics` → `news` routers; p95 check; ops role stubs.
