# Ouroboros

Independent asset-intelligence platform: market data → profiles, regimes, sentiment, insights → feeds sibling platforms (EPG, quant). **Does not execute trades.**

| Deployable | Host | Path |
|---|---|---|
| Client (Next.js) | Vercel | `client/` |
| API + worker | Railway | `server/` |
| Postgres/Timescale + Redis | Railway (prod) / Docker (local) | compose at repo root |

## Docs

- [concept.md](./concept.md) — product concept
- [roadmap.md](./roadmap.md) — full roadmap (v1.3)
- [docs/adr/](./docs/adr/) — architecture decisions

## Local services (Phase 0)

```bash
# Start Postgres (Timescale) + Redis only
docker-compose up -d

# Defaults publish host ports 5433 (Postgres) and 6380 (Redis)
# to avoid clashes with other local services on 5432/6379.

# Copy env templates (never commit real secrets)
copy server\.env.example server\.env
copy client\.env.example client\.env.local
```

Client and server apps are scaffolded in later Phase 0 days; they run natively (`pnpm` / `uv`) or via their own Dockerfiles under `client/` and `server/`.

## Dual auth (preview)

- **Humans** → Clerk (social + email) on the dashboard
- **Machines** (EPG, quant) → hashed API keys

See [ADR-015](./docs/adr/015-dual-auth-clerk-and-api-keys.md).

## License

Private — internal use.
