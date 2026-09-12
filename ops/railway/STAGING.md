# Railway staging — walking skeleton (W1·D5)

Goal: health endpoint live on Railway with TimescaleDB + Redis + API, continuous deploy from `main`.

## One-time setup (dashboard)

1. Create a Railway project: **ouroboros-staging**
2. Add services:
   - **Postgres** — use Docker image `timescale/timescaledb:latest-pg16` (not plain Railway Postgres; Timescale extension required)
   - **Redis** — Railway Redis plugin or `redis:7-alpine` image
   - **API** — deploy from this repo, **Root Directory = repository root**, Dockerfile `server/Dockerfile` (see `server/railway.toml`)
   - **Worker** — same image/build as API; **start command** `python -m app.scheduler` (see `server/railway.worker.toml`). No public domain.
3. Private networking: set API + worker env from internal URLs
   - `DATABASE_URL` = Timescale private URL (use `postgresql+psycopg://…` or plain `postgresql://` — server normalizes)
   - `REDIS_URL` = Redis private URL
   - `APP_ENV=staging`
   - `CORS_ORIGINS=http://localhost:3000` (API only; expand when Vercel previews exist)
4. Generate a public domain for the API service
5. Confirm: `GET https://<api-domain>/v1/health` → postgres + redis `ok`
6. Enable auto-deploy from GitHub `main` on API + worker
7. Worker dry-run (one-off): set temporary start command  
   `python -m app.scheduler --once --jobs regime_log profile_events prune_profiles`  
   then restore `python -m app.scheduler`

## CLI (optional)

```bash
npm i -g @railway/cli
railway login
railway link
# from repo root (Dockerfile expects monorepo context)
railway up
```

## Notes

- Build context must include `packages/contracts` (Dockerfile installs it before the server package)
- Local: `docker-compose --profile worker up -d` or `cd server && python -m app.scheduler --once`
- Secrets (`CLERK_*`, `RESEND_*`, MT5, LLM) stay empty until their phases
- Local Docker remains the primary verify path until Railway worker is linked
