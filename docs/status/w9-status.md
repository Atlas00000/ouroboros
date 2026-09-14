# W9 status — Next.js client scaffold (local)

**Date:** 2026-09-14  
**Scope:** W9·D1–D5 (local; Docker was off during this pass)

## Delivered

### W9·D1
- Next.js **16.3** + TS + Tailwind 4 + pnpm
- Dark theme + regime colors; Inter / JetBrains Mono
- Clerk shell + middleware (when keys set); sign-in/sign-up
- `client/Dockerfile` (standalone)

### W9·D2 (partial)
- `lib/api/client.ts` + types; `pnpm gen:api` script
- TanStack Query; Clerk JWT on client fetches
- Vercel connect deferred

### W9·D3–D5
- Nav: Dashboard · News · Scoring · System · Admin (baseline IA)
- **Dashboard:** enriched `AssetGrid` cards — Sparkline, StateBadge, VolPercentile, StaleBadge, SentimentGauge
- `MarketSummaryStrip` + `NewsTicker` → `/news`
- Routes: `/news`, `/scoring`, `/system`, `/admin/keys` (stubs for W11)
- Asset detail stub with live H1 state when SSR key set
- UI baseline: `docs/UIscreens-and-details.md`

## Run

```powershell
# Docker Desktop on, then:
docker start ouroboros-postgres ouroboros-redis
cd server; py -3.12 -m uvicorn app.main:app --reload --port 8000

cd client
# .env.local: NEXT_PUBLIC_API_URL + Clerk and/or OUROBOROS_SERVER_API_KEY
pnpm dev
```

## Next

**W10** — Asset detail panels per `docs/UIscreens-and-details.md` §3 (chart → profile → sentiment → insights).
