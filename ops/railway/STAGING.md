# Railway staging — walking skeleton (W1·D5)

Goal: health endpoint live on Railway with TimescaleDB + Redis + API, continuous deploy from `main`.

## One-time setup (dashboard)

1. Create a Railway project: **ouroboros-staging**
2. Add services:
   - **Postgres** — use Docker image `timescale/timescaledb:latest-pg16` (not plain Railway Postgres; Timescale extension required)
   - **Redis** — Railway Redis plugin or `redis:7-alpine` image
   - **API** — deploy from this repo, **Root Directory = `server`**, Dockerfile builder (see `server/railway.toml`)
3. Private networking: set API env from internal URLs
   - `DATABASE_URL` = Timescale private URL (use `postgresql+psycopg://…` or plain `postgresql://` — server normalizes)
   - `REDIS_URL` = Redis private URL
   - `APP_ENV=staging`
   - `CORS_ORIGINS=http://localhost:3000` (expand when Vercel previews exist)
4. Generate a public domain for the API service
5. Confirm: `GET https://<api-domain>/v1/health` → postgres + redis `ok`
6. Enable auto-deploy from GitHub `main` on the API service

## CLI (optional)

```bash
npm i -g @railway/cli
railway login
railway link
# from server/
railway up
```

## Notes

- Worker service (same image, `python -m app.scheduler`) is added in Phase 2 (W5·D4)
- Secrets (`CLERK_*`, `RESEND_*`, MT5, LLM) stay empty until their phases
- Local Docker remains the primary Day-1/Day-5 verify path until Railway is linked
