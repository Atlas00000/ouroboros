# Logging cheat-sheet (local debug)

Structured logs across **server**, **client**, and **Docker** for correlating slow or failed requests.

## Server (uvicorn)

JSON lines on stdout. Each request gets `request_id` (echoed as `X-Request-Id`).

```bash
cd server
# quieter default; use DEBUG for SQL + verbose HTTP
set LOG_LEVEL=INFO
py -3.12 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Useful fields: `msg=http_request`, `method`, `path`, `status`, `duration_ms`, `request_id`.

```bash
# PowerShell: filter API request lines
Get-Content -Wait ...\terminals\*.txt | Select-String '"msg": "http_request"'
```

Modules:

| File | Role |
|------|------|
| `server/app/observability/logging.py` | JSON formatter + request context |
| `server/app/observability/request_logging.py` | Middleware (id + duration) |

## Client (Next.js)

Env: `NEXT_PUBLIC_LOG_LEVEL=debug|info|warn|error` (default **info** in dev, **warn** in prod).

Browser / server console emits JSON with `scope`, `msg`, `request_id`. API calls log via `fetchApi` and send `X-Request-Id` so you can match server lines.

| File | Role |
|------|------|
| `client/src/lib/log/logger.ts` | Scoped logger + redaction |
| `client/src/lib/log/api-log.ts` | API timing helper |
| `client/src/lib/api/client.ts` | Wires request id + `logApiCall` |

## Docker (Postgres / Redis)

```bash
docker compose up -d postgres redis
docker compose logs -f postgres redis
docker logs --tail 200 ouroboros-postgres
docker logs --tail 200 ouroboros-redis
```

Compose sets:

- **json-file** driver with rotation (`10m` × 5 files)
- Postgres: connections + statements ≥ **500ms**
- Redis: `--loglevel notice`

Recreate after compose changes:

```bash
docker compose up -d --force-recreate postgres redis
```

## Correlate a bad call

1. Client log → copy `request_id`
2. Server log → same `request_id` on `http_request` (or exception)
3. If pool / DB stalls → Postgres log for slow statements around that timestamp
