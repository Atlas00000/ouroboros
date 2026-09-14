# Ouroboros client (Phase 4)

Next.js 16 App Router dashboard hugging the Phase 3 API (`v0.4-api`).

## Setup

```powershell
cd client
Copy-Item .env.example .env.local
# Fill Clerk keys (invite-only org) and optionally OUROBOROS_SERVER_API_KEY for SSR without a browser session
pnpm install
pnpm dev
```

Open http://localhost:3000. API default: `NEXT_PUBLIC_API_URL=http://localhost:8000`.

## Scripts

| Script | Purpose |
|--------|---------|
| `pnpm dev` | Local Next.js |
| `pnpm build` / `pnpm start` | Production |
| `pnpm gen:api` | Regenerate `src/lib/api/schema.d.ts` from live OpenAPI |

## Auth

- Browser: Clerk JWT only (never machine API keys in the bundle).
- Local SSR without Clerk: set server-only `OUROBOROS_SERVER_API_KEY`.

## Status

See `docs/status/w9-status.md` when present.
