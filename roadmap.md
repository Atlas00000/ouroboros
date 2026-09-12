# Ouroboros — Project Report & Implementation Roadmap

> **Version:** 1.4 · **Date:** 2026-09-12 · **Status:** Planning
> **One-liner:** An independent asset-intelligence platform that ingests real-time and historical market data, builds living asset profiles, detects market states/regimes, digests news into sentiment and insight, and serves all of it to sibling platforms (EPG, quant platforms) via versioned APIs and durable events. **It does not execute trades.**
> **Hosting model:** `client/` deploys to **Vercel** · `server/` (API + worker) + database deploy to **Railway** · local services (Postgres, Redis) run in **Docker** · staging is live from **Week 1** (walking skeleton, continuously deployed).
> **Human auth & email:** **Clerk** (social + email login for dashboard users) · **Resend** (alerts, digests, invite/lifecycle mail). Machine consumers keep **hashed API keys**.

---

## 1. Project Report

### 1.1 Purpose

Ouroboros is the shared "contextual awareness" layer for our platform family. Instead of EPG and each quant platform independently ingesting data and forming a view of the market, Ouroboros does it once, well, and feeds everyone:

- **Asset profiles** — living, versioned dossiers per instrument (identity, liquidity, volatility character, event sensitivity, correlations, regime history).
- **Market states & regimes** — current classification (trending-up / trending-down / ranging / high-volatility) with probabilities and model versioning.
- **Metrics** — volatility stats, trend strength, correlation matrices, spread/liquidity measures.
- **News & sentiment** — real-time news digestion, decay-weighted sentiment scores with drivers.
- **Insights & narratives** — AI-generated readable summaries built *on top of* deterministic outputs.
- **Charts & infographics** — presentation layer (built last; consumers may also render from raw data).

### 1.2 Explicit non-goals

- No trade execution, order routing, or position management. Ever.
- No external/public subscribers in v1 (keeps us out of investment-advice regulatory territory; internal research tool only).
- No tick-level infrastructure in v1 (1-minute bars; upgrade only when a consumer proves the need).

### 1.3 Core design decisions


| #   | Decision                                                                                                                                                                                                                                                  | Rationale                                                                                                                                                                    |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **Hybrid pull + push communication** — REST API for on-demand queries; **Redis Streams** (consumer groups, acknowledgement, replay) for events, fed via a **transactional outbox**                                                                        | Consumers need both "ask now" and "tell me when"; plain pub/sub is fire-and-forget — a disconnected consumer loses events forever, which is unacceptable for a feed platform |
| 2   | **Versioned data contracts first** — JSON Schema definitions (`profile.v1`, `state.v1`) in a shared package before any pipeline code                                                                                                                      | EPG/quant teams can mock and build in parallel                                                                                                                               |
| 3   | **Two-tier AI split** — deterministic tier produces all numbers (metrics, regimes); generative tier (LLM) produces only labeled narratives/sentiment                                                                                                      | Contains hallucination risk; numbers stay testable and reproducible                                                                                                          |
| 4   | **Provenance + confidence on every output** — `sources[]`, `generated_at`, `model_version`, `confidence`, `stale` flag                                                                                                                                    | Downstream platforms can't safely consume unvalidated signals                                                                                                                |
| 5   | **TimescaleDB as single store** — hypertables for prices (with native compression + retention policies from day one), regular tables for everything else                                                                                                  | One database for MVP; continuous aggregates give rollups free; compression saves ~90% on old M1 chunks                                                                       |
| 6   | **Migration-first database governance** — every schema change is a versioned migration (Alembic); no manual DDL, ever; expand–contract for live changes                                                                                                   | Reproducible environments, auditable schema history, safe rollbacks, zero-downtime changes                                                                                   |
| 7   | **Staleness watchdog** — every feed has an expected cadence; outputs are marked `stale: true` and alerts fire when a feed dies                                                                                                                            | A monitoring platform that fails silently is worse than none                                                                                                                 |
| 8   | **Start with 10–30 instruments** — major FX + gold + 1–2 indices, canonical internal symbol IDs mapped to per-source tickers                                                                                                                              | Expansion becomes config, not code                                                                                                                                           |
| 9   | **Backend first, frontend hugs the backend** — the UI is built only against real, stable API endpoints, never against mocks of our own API                                                                                                                | Prevents drift between UI expectations and API reality                                                                                                                       |
| 10  | **Hard client/server separation from day one** — `client/` (Vercel) and `server/` (Railway) are independent deployables with their own Dockerfiles, configs, and env vars; they share only the contracts package and the OpenAPI spec                     | Zero refactoring when deploying to split hosting                                                                                                                             |
| 11  | **Modular, single-file implementation workflow** — one component/module per file; during implementation, complete one file at a time                                                                                                                      | Small reviewable steps; avoids oversized multi-file edits, tool-call storms, and timeouts                                                                                    |
| 12  | **Walking skeleton + continuous deployment** — a near-empty system (health endpoint, DB, migrations) deploys to Railway staging in Week 1 and stays continuously deployed thereafter                                                                      | Infra surprises (Timescale image quirks, networking, CORS, env vars) surface one at a time in Week 1, not all at once at a Week 8 "big bang" deploy                          |
| 13  | **API and worker are separate services** — same codebase, same Docker image, different entrypoints (`uvicorn app.main` vs `python -m app.scheduler`)                                                                                                      | An in-API scheduler double-fires jobs the moment the API scales to two replicas, and dies mid-job on restarts                                                                |
| 14  | **UTC everywhere + explicit trading calendar** — all timestamps stored UTC; a trading-calendar module owns sessions, holidays, and the MT5 server-time offset (typically UTC+2/+3, DST-shifting)                                                          | Ignoring MT5 server-time DST shifts silently corrupts daily bars and session-based metrics                                                                                   |
| 15  | **Dual auth: humans via Clerk, machines via API keys** — dashboard users authenticate with Clerk (social + email); sibling platforms (EPG, quant) use hashed API keys. Same Railway API accepts either `Authorization: Bearer <Clerk JWT>` or `X-API-Key` | Humans need sessions, roles, invite/revoke; machines need durable, non-interactive credentials. Mixing them creates either shared passwords or brittle service JWTs          |
| 16  | **Resend for human-facing email** — watchdog alerts, regime/news digests, weekly scoring reports, and Clerk-adjacent lifecycle mail (invites)                                                                                                             | A monitoring platform that only alerts inside the UI fails when nobody is looking; email closes the loop without replacing Telegram/webhook options                          |


### 1.4 Success criteria

1. **Freshness:** 99% of price data < 2 minutes old during market hours; zero silent staleness incidents.
2. **Regime quality:** labels pass human/backtest review at an agreed threshold after a 1-month baseline; flip-rate within noise budget.
3. **Adoption:** EPG or a quant platform consumes ≥ 1 Ouroboros feed in a real workflow by end of roadmap.

---

## 2. Requirements

### 2.1 Functional requirements


| ID  | Requirement                                                                                                                                                                                                                  |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| F1  | Ingest 1-minute OHLCV price data from MT5 for the configured asset universe (live + 2–5 years history backfill)                                                                                                              |
| F2  | Ingest news/economic-calendar items from ≥ 1 API (e.g., Finnhub/Marketaux) within ~1 minute of publication                                                                                                                   |
| F3  | Ingest macro series from FRED (daily cadence)                                                                                                                                                                                |
| F4  | Compute deterministic metrics per asset per timeframe: realized vol, ATR percentiles, trend strength, rolling correlations, spread stats                                                                                     |
| F5  | Classify market state/regime per asset per timeframe (trending-up, trending-down, ranging, high-vol) with probabilities                                                                                                      |
| F6  | Score sentiment per asset in [-1, +1], decay-weighted 24h, with top-driver article references; per-article scores cached (never pay to score the same headline twice)                                                        |
| F7  | Generate daily asset profiles (regenerated daily + event-triggered refresh)                                                                                                                                                  |
| F8  | Generate LLM insight narratives, labeled `type: narrative`, never feeding numeric fields; daily LLM budget cap with alerting                                                                                                 |
| F9  | Serve REST API: `GET /assets`, `/assets/{symbol}/profile`, `/state`, `/metrics`, `/sentiment`, `/insights`, `/news`                                                                                                          |
| F10 | Publish durable events via **transactional outbox → Redis Streams** (`regime.changed`, `sentiment.spike`, `news.high_impact`, `profile.updated`) with consumer groups, acks, and replay of missed events                     |
| F11 | Log every regime call and forecast to an immutable table; weekly scoring job compares to realized outcomes                                                                                                                   |
| F12 | Staleness watchdog: per-source cadence expectations, `stale: true` propagation, alerting                                                                                                                                     |
| F13 | Web dashboard (client): asset list, asset detail (profile, state, chart, sentiment, insights), system health page                                                                                                            |
| F14 | All outputs carry provenance (`sources[]`, `generated_at`, `model_version`, `confidence`) and a disclaimer field                                                                                                             |
| F15 | Trading-calendar module: all storage in UTC; sessions/holidays/MT5 server-time offset handled explicitly                                                                                                                     |
| F16 | **Human auth (Clerk):** invite-only org; social login (e.g. Google/GitHub) + email login; client pages protected; roles at minimum `viewer` / `analyst` / `admin` / `ops` (ops → `/system`; admin → API-key management)      |
| F17 | **Dual-auth API:** every protected endpoint accepts Clerk JWT *or* hashed API key; identity + auth method recorded in request context / audit logs                                                                           |
| F18 | **Email (Resend):** send staleness/watchdog alerts, optional high-impact/regime digests, weekly scoring summary; `EMAIL_FROM` / allowlisted recipients; alert channel selectable (`telegram` | `webhook` | `resend` | multi) |


### 2.2 Non-functional requirements


| ID  | Requirement                                                                                                                                                                                                                                                                 |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| N1  | Price freshness: 99% < 2 min during market hours; sentiment refresh ≤ 5 min; profiles daily                                                                                                                                                                                 |
| N2  | API p95 latency < 300 ms for profile/state reads                                                                                                                                                                                                                            |
| N3  | All schema changes via migrations; CI blocks merge if models and migrations diverge; expand–contract pattern + `lock_timeout` for live changes                                                                                                                              |
| N4  | Every deterministic computation unit-tested; regression fixtures for regime classifier; `schemathesis` contract tests against the OpenAPI spec in CI                                                                                                                        |
| N5  | **Split deployment:** client on Vercel; API service, worker service, database, and Redis on Railway. **Local dev:** Postgres and Redis always via Docker Compose; client and server each runnable natively (pnpm / uv) *or* via their own Dockerfile in their own directory |
| N6  | Observability: structured JSON logging, **Sentry** error tracking on server and client from Phase 0, Prometheus-style `/metrics` (ingestion lag, event publish counts, LLM spend) from Phase 3, health endpoints per service                                                |
| N7  | API versioned under `/v1/`; schemas versioned (`profile.v1`); breaking changes require new version, not mutation                                                                                                                                                            |
| N8  | CORS locked to known client origins (Vercel domains + localhost); client always uses absolute API URL                                                                                                                                                                       |
| N9  | **RPO/RTO defined:** prices RPO ≤ 24h (re-backfillable from MT5 — documented assumption); irreplaceable tables (sentiment history, forecast log, outbox, profiles) RPO ≤ 1h via frequent targeted dumps; RTO ≤ 4h. Restore drill executed in **Week 2**, not Week 12        |
| N10 | API standards fixed before consumers exist: `application/problem+json` (RFC 9457) error format; cursor-based pagination                                                                                                                                                     |
| N11 | Security in CI from Week 1: Dependabot, `pip-audit` + `pnpm audit`, container image scanning; API keys stored **hashed**; dual auth (Clerk JWT + API keys) built with the first protected routers, not retrofitted                                                          |
| N12 | Connection pooling (PgBouncer or equivalent) in front of Postgres — API + worker + MT5 worker + pollers must not exhaust connections                                                                                                                                        |
| N13 | Clerk org is **invite-only** in v1 (no public sign-up); CORS + Clerk allowed origins locked to known client URLs; machine API keys never embedded in the browser                                                                                                            |
| N14 | Resend domain authenticated (SPF/DKIM/DMARC); alert emails rate-limited; secrets (`CLERK_*`, `RESEND_API_KEY`) only in Vercel/Railway/local uncommitted env — never in git                                                                                                  |


---

## 3. Tech Stack


| Layer                       | Choice                                                                                                                                           | Notes                                                                                                                                                                                          |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Language (server)           | **Python 3.12**                                                                                                                                  | Ecosystem fit for market data + ML; local dev via uv/venv                                                                                                                                      |
| API framework               | **FastAPI**                                                                                                                                      | Async, auto OpenAPI docs, Pydantic-native                                                                                                                                                      |
| Data validation / contracts | **Pydantic v2 + JSON Schema export**                                                                                                             | Contracts live in `packages/contracts`, consumed by client, EPG, quant                                                                                                                         |
| Database                    | **PostgreSQL 16 + TimescaleDB**                                                                                                                  | Hypertables + native compression + retention policies (in initial migration); continuous aggregates for H1/D1                                                                                  |
| Connection pooling          | **PgBouncer** (Railway sidecar or built-in pooling)                                                                                              | Prevents connection exhaustion across services                                                                                                                                                 |
| Migrations                  | **Alembic**                                                                                                                                      | Migration-first governance (§6.1); Railway release step runs `alembic upgrade head`; `lock_timeout` set globally                                                                               |
| Events                      | **Redis Streams** fed by **transactional outbox**                                                                                                | Durable: consumer groups, acks, replay. Outbox table written in the same transaction as the state change; relay publishes. Upgrade path: NATS/Kafka only on volume evidence                    |
| Cache                       | **Redis 7** (same instance, separate logical use)                                                                                                | Railway service in prod; Docker locally                                                                                                                                                        |
| Task orchestration          | **APScheduler in a dedicated worker service** — same image as API, entrypoint `python -m app.scheduler`                                          | Never inside the API process (replica double-fire, restart kills). Upgrade path: Celery/Arq                                                                                                    |
| Trading calendar            | Custom module (or `exchange_calendars`)                                                                                                          | UTC everywhere; owns sessions, holidays, MT5 server-time DST offset                                                                                                                            |
| MT5 connectivity            | **MetaTrader5 Python package**                                                                                                                   | Runs on a Windows worker (MT5 requirement) — outside Railway, pushes into Railway DB/API over TLS                                                                                              |
| News/macro                  | Finnhub or Marketaux; **FRED** (free)                                                                                                            | Source registry table records license, rate limits, cost                                                                                                                                       |
| Deterministic analytics     | **pandas / numpy / statsmodels**; HMM via `hmmlearn` or rule-based classifier                                                                    | Numbers tier — no LLM involvement                                                                                                                                                              |
| LLM (generative tier)       | Provider-agnostic client (OpenAI/Anthropic) behind an internal interface                                                                         | Narratives + sentiment only; outputs labeled; per-article cache + daily budget cap with alerting                                                                                               |
| Observability               | **Sentry** (server + client, from Phase 0); Prometheus-style `/metrics` (from Phase 3); structured JSON logs                                     | Watchdog monitors the *data*; this monitors the *system*                                                                                                                                       |
| Human auth                  | **Clerk** (social + email login, invite-only org, roles)                                                                                         | Client sessions on Vercel; Railway verifies Clerk JWT via JWKS. Does **not** replace machine API keys                                                                                          |
| Email                       | **Resend**                                                                                                                                       | Watchdog alerts, digests, weekly scoring; optional Clerk invite mail via Resend                                                                                                                |
| Client framework            | **Next.js 16 (App Router) + TypeScript**                                                                                                         | Built in Phase 4, against the live Railway staging API; Clerk-protected routes                                                                                                                 |
| Client package manager      | **pnpm**                                                                                                                                         | Local dev `pnpm dev`; Docker option via `client/Dockerfile`                                                                                                                                    |
| UI kit                      | **shadcn/ui + Tailwind CSS**                                                                                                                     | Fast, consistent, dark-mode native                                                                                                                                                             |
| Charts                      | **TradingView Lightweight Charts** (price), **Recharts** (metrics/sentiment)                                                                     |                                                                                                                                                                                                |
| Data fetching (client)      | **TanStack Query** + generated API client from OpenAPI spec                                                                                      | Generated-client compile check runs in CI on every server PR                                                                                                                                   |
| Containerization            | **Docker** — `client/Dockerfile`, `server/Dockerfile`, root `docker-compose.yml` for local services                                              | Compose profiles: services-only, `--profile server`, `--profile worker`, `--profile client`                                                                                                    |
| Hosting (client)            | **Vercel** — project root = `client/`                                                                                                            | Preview deploys per PR from Phase 4 onward                                                                                                                                                     |
| Hosting (server + DB)       | **Railway** — API service + worker service from `server/Dockerfile` (different entrypoints); TimescaleDB via Docker-image service; Redis service | Private networking; **staging live from Week 1**, continuously deployed                                                                                                                        |
| CI/CD                       | **GitHub Actions**                                                                                                                               | Lint, tests, migration-drift check, `schemathesis` contract tests, generated-TS-client compile check, Dependabot + `pip-audit`/`pnpm audit`, image scanning, image builds; auto-deploy on main |
| Testing                     | pytest, pytest-asyncio, schemathesis (server); Playwright (client, Phase 4)                                                                      |                                                                                                                                                                                                |
| Lint/format                 | Ruff (py), ESLint + Prettier (ts)                                                                                                                |                                                                                                                                                                                                |


### 3.1 Environment matrix


| Environment               | Client                         | API service                | Worker service                          | Postgres/Timescale          | Redis          |
| ------------------------- | ------------------------------ | -------------------------- | --------------------------------------- | --------------------------- | -------------- |
| **Local (native)**        | `pnpm dev`                     | `uvicorn` via uv/venv      | `python -m app.scheduler`               | Docker Compose              | Docker Compose |
| **Local (full Docker)**   | compose `--profile client`     | compose `--profile server` | compose `--profile worker`              | Docker Compose              | Docker Compose |
| **Staging (from Week 1)** | Vercel previews (from Phase 4) | Railway (Docker deploy)    | Railway (same image, worker entrypoint) | Railway (TimescaleDB image) | Railway        |
| **Production (Week 12)**  | Vercel                         | Railway                    | Railway                                 | Railway                     | Railway        |


Both client and server read all configuration from env vars (`NEXT_PUBLIC_API_URL`, `DATABASE_URL`, `REDIS_URL`, `CLERK_*`, `RESEND_API_KEY`, …) so nothing changes between local and hosted except the env file.

---

## 3.2 Dual-auth design

```
Browser (human)
  → Clerk session (social / email)
  → client (Vercel) attaches Authorization: Bearer <Clerk JWT>
  → Railway API verifies JWT against Clerk JWKS
  → roles from Clerk public metadata / org roles (viewer | analyst | admin | ops)

EPG / Quant / workers (machine)
  → X-API-Key: <plaintext key once issued>
  → Railway API looks up hash, attaches service principal
  → no Clerk involvement
```

- Health and OpenAPI docs may stay public or IP-restricted; all data routes require one of the two schemes.
- Client never stores machine API keys; it only uses the user's Clerk session.
- Admin UI (Phase 4/5) can mint/revoke machine keys; plaintext shown once; only hashes persist.
- Audit log fields: `auth_method` (`clerk` | `api_key`), `subject_id`, `role` / `service_name`.

---

## 3.3 Environment / secrets template (uncommitted)

Committed files are `.env.example` only (placeholders). Real values live in gitignored `server/.env`, `client/.env.local`, and/or a root `secrets.env` that is **never committed**.

```env
# === LOCAL INFRA ===
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=ouroboros
DATABASE_URL=
REDIS_URL=

# === OBSERVABILITY ===
SENTRY_DSN_SERVER=
SENTRY_DSN_CLIENT=

# === MT5 (Windows worker) ===
MT5_LOGIN=
MT5_PASSWORD=
MT5_SERVER=
MT5_PATH=

# === DATA PROVIDERS ===
NEWS_PROVIDER=finnhub
NEWS_API_KEY=
FRED_API_KEY=

# === ALERTS ===
ALERT_CHANNEL=resend   # telegram | webhook | resend | multi
ALERT_TELEGRAM_BOT_TOKEN=
ALERT_TELEGRAM_CHAT_ID=
ALERT_WEBHOOK_URL=

# === AUTH (Clerk) — humans ===
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=
CLERK_JWKS_URL=
CLERK_AUTHORIZED_PARTIES=http://localhost:3000
CLERK_ALLOWED_ORG_ID=

# === EMAIL (Resend) ===
RESEND_API_KEY=
EMAIL_FROM=alerts@yourdomain.com
EMAIL_ALERT_TO=ops@yourdomain.com

# === LLM ===
LLM_PROVIDER=openai
OPENAI_API_KEY=
LLM_MODEL=
LLM_DAILY_BUDGET_USD=10

# === MACHINE API KEYS (issued by us; hashes stored in DB) ===
# Plaintext only for local bootstrap / handoff — not required in prod once minted via admin
OUROBOROS_API_KEY_CLIENT=
OUROBOROS_API_KEY_EPG=
OUROBOROS_API_KEY_QUANT=

# === CLIENT / HOSTING ===
NEXT_PUBLIC_API_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000
```

---

## 4. Folder Structure

Monorepo with a **hard client/server split**. Vercel's project root points at `client/`; Railway's at `server/` (two services, one image). Each deployable owns its Dockerfile, config, and env template. They share only `packages/contracts` and the OpenAPI spec.

```
ouroboros/
├── roadmap.md
├── concept.md
├── README.md
├── docker-compose.yml              # LOCAL DEV: postgres+timescale, redis (always);
│                                   # profiles: --profile server, --profile worker, --profile client
├── .github/
│   ├── dependabot.yml
│   └── workflows/
│       ├── ci.yml                  # lint + tests + drift check + schemathesis + TS-client
│       │                           # compile check + security scans + image builds
│       └── deploy.yml
├── packages/
│   └── contracts/                  # ★ versioned data contracts (shared source of truth)
│       ├── pyproject.toml
│       └── contracts/
│           ├── profile_v1.py       # AssetProfile schema
│           ├── state_v1.py         # MarketState schema
│           ├── sentiment_v1.py     # SentimentSnapshot schema
│           ├── insight_v1.py       # Insight/narrative schema
│           ├── events_v1.py        # stream event payloads
│           └── jsonschema/         # exported .json schemas for non-Python consumers
│
├── server/                         # ★ RAILWAY deploy root (API + worker services, one image)
│   ├── Dockerfile
│   ├── railway.toml                # build; release = alembic upgrade head; two services/entrypoints
│   ├── .env.example
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── migrations/                 # ★ Alembic — the only way schema changes
│   │   └── versions/               # initial migration includes hypertable, compression,
│   │                               # retention, continuous aggregates, outbox table
│   ├── app/
│   │   ├── main.py                 # FastAPI entrypoint (API service)
│   │   ├── scheduler.py            # worker entrypoint (python -m app.scheduler)
│   │   ├── config.py               # pydantic-settings, env-driven
│   │   ├── db/                     # engine, session (pooled), base
│   │   ├── models/                 # one model per file (incl. outbox.py)
│   │   ├── api/
│   │   │   └── v1/                 # one router per resource; dual-auth middleware
│   │   │                           # (Clerk JWT | hashed API key); problem+json;
│   │   │                           # cursor pagination; /metrics; health.py
│   │   ├── auth/                   # ★ clerk_jwt.py, api_keys.py, roles.py, dependencies.py
│   │   ├── calendar/               # ★ trading calendar: UTC, sessions, MT5 offset/DST
│   │   ├── ingestion/
│   │   │   ├── mt5/
│   │   │   ├── news/
│   │   │   ├── macro/
│   │   │   └── registry.py
│   │   ├── analytics/              # ★ deterministic tier — numbers only
│   │   │   ├── metrics.py
│   │   │   ├── regimes.py
│   │   │   └── profiles.py
│   │   ├── intelligence/           # ★ generative tier — words only
│   │   │   ├── llm_client.py       # retries, cost logging, budget cap, per-article cache
│   │   │   ├── sentiment.py
│   │   │   └── narratives.py
│   │   ├── events/                 # outbox writer + relay → Redis Streams
│   │   ├── notifications/          # ★ Resend client + alert/digest templates
│   │   ├── watchdog/
│   │   ├── scoring/
│   │   └── observability/          # Sentry init, structured logging, metrics registry
│   └── tests/
│       ├── unit/
│       ├── integration/
│       └── conftest.py
│
├── client/                         # ★ VERCEL deploy root
│   ├── Dockerfile
│   ├── vercel.json
│   ├── .env.example                # NEXT_PUBLIC_API_URL, NEXT_PUBLIC_CLERK_*, Sentry DSN
│   ├── package.json                # pnpm
│   ├── next.config.ts
│   ├── middleware.ts               # ★ Clerk middleware — protect all app routes
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx          # ClerkProvider
│   │   │   ├── sign-in/[[...sign-in]]/page.tsx
│   │   │   ├── sign-up/[[...sign-up]]/page.tsx   # invite-only; public sign-up disabled in Clerk
│   │   │   ├── page.tsx            # dashboard
│   │   │   ├── assets/[symbol]/page.tsx
│   │   │   └── system/page.tsx     # ops/admin role-gated
│   │   ├── components/             # one component per .tsx file (§6.7)
│   │   │   ├── ui/                 # shadcn primitives
│   │   │   ├── charts/             # PriceChart.tsx, SentimentGauge.tsx, RegimeTimeline.tsx
│   │   │   ├── asset/              # ProfileCard.tsx, StateBadge.tsx, InsightFeed.tsx, ...
│   │   │   ├── system/             # FeedRegistryTable.tsx, ScoringResults.tsx, ...
│   │   │   └── auth/               # UserButton, RoleGate.tsx
│   │   ├── lib/
│   │   │   ├── api/                # ★ GENERATED client from server OpenAPI spec
│   │   │   └── queries/            # one TanStack Query hook file per resource
│   │   └── styles/
│   └── public/
│
├── ops/
│   ├── railway/                    # Timescale image config, PgBouncer, backup jobs
│   └── mt5-worker/                 # Windows worker setup (connects to Railway over TLS)
└── docs/
    ├── architecture.md
    ├── adr/                        # ★ Architecture Decision Records — one per §1.3 decision
    ├── data-contracts.md
    └── runbooks/                   # feed-down, restore-from-backup, redeploy
```

**Separation rules (no refactoring later):**

- No file in `client/` imports from `server/` or vice versa — shared artifacts are `packages/contracts` and the generated OpenAPI client only.
- Each side has its **own** `.env.example`, Dockerfile, and lockfile. The root compose file only wires local services and optional app profiles.
- The client always talks to the server through `NEXT_PUBLIC_API_URL` — never a relative path — so localhost, Docker, and Vercel→Railway all work unchanged.

---

## 5. UI & Assets

### 5.1 UI plan (built Phase 4 — against the live, continuously deployed staging API)

**Design language:** dark-mode-first (market tooling convention), dense but scannable, shadcn/ui + Tailwind. Latency-honest: every panel shows `generated_at` and a stale badge when applicable — the UI never pretends data is fresher than it is. All app routes sit behind **Clerk**; unsigned users hit sign-in. Role gates hide `/system` and API-key admin from non-ops/admin users.

**Pages:**

1. **Sign-in / invite** — Clerk-hosted social + email; public sign-up disabled (invite-only org).
2. **Dashboard (`/`)** — asset grid: symbol, sparkline, current regime badge (color-coded), vol percentile, sentiment gauge, staleness indicators. Market-wide summary strip (risk-on/off, top movers, high-impact news ticker).
3. **Asset detail (`/assets/[symbol]`)** —
  - Price chart (Lightweight Charts) with regime bands overlaid as background shading.
  - Profile card: identity, hours, liquidity/vol character, event sensitivities, correlation mini-heatmap.
  - Market state panel: regime probabilities, trend strength, model version, confidence.
  - Sentiment panel: score gauge, 24h trend, top driver headlines with links.
  - Insight feed: LLM narratives, clearly labeled as AI-generated with disclaimer.
4. **System health (`/system`)** — feed registry with last-seen timestamps and cadence status, watchdog alerts history, weekly scoring results; **ops/admin only**.
5. **Admin (keys)** — mint/revoke machine API keys for EPG/quant (**admin only**); plaintext shown once.

**The "hug the backend" rule:** the client API layer is *generated* from the server's OpenAPI spec (`openapi-typescript` / `orval`) — pulled from the Railway staging URL. Requests from the browser attach the Clerk session JWT; generated client + TanStack Query hooks never embed machine API keys. CI compiles the generated client on every server PR, so drift is caught mechanically, not aspirationally.

### 5.2 Assets


| Asset               | Source/Plan                                                                                                                                        |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Logo & favicon      | Ouroboros mark (stylized loop) — commission or generate in Phase 4, SVG + PNG set in `client/public/`                                              |
| Fonts               | Inter (UI) + JetBrains Mono (numeric/tabular data) — self-hosted in `client/public/fonts/`                                                         |
| Icons               | Lucide (ships with shadcn)                                                                                                                         |
| Regime color system | trending-up `green-500`, trending-down `red-500`, ranging `zinc-400`, high-vol `amber-500` — Tailwind tokens, used consistently in API docs and UI |
| Chart themes        | Single dark theme token file shared by Lightweight Charts + Recharts                                                                               |
| OG/social images    | Deferred (internal tool)                                                                                                                           |


---

## 6. Industry Best Practices Adopted

### 6.1 Migration-first database governance ★

- **Every** schema change is an Alembic migration committed with the code that needs it. No manual DDL against any environment, including local.
- Migrations are **forward-only in shared environments**; down-revisions are for local development only.
- CI runs a **drift check**: autogenerate a migration against current models — non-empty output fails the build.
- **Expand–contract for live changes:** add new → backfill → cut over → drop old, as separate deploys. `lock_timeout` set in Alembic so a migration can never lock the prices hypertable during market hours.
- Destructive operations require explicit sign-off and a backfill/rollback plan in the PR description.
- Seed/reference data lives in versioned, idempotent data migrations — any environment reproduces from zero with `alembic upgrade head`.
- **Railway release phase runs `alembic upgrade head`** before new code takes traffic.
- **Timescale lifecycle in the initial migration:** compression policy on old M1 chunks (~90% savings) and retention/aggregation policy — not a v1.1 retrofit.
- **Backups with defined RPO/RTO (N9):** Railway Timescale is self-managed — we own backup and recovery. Nightly full `pg_dump` + hourly targeted dumps of irreplaceable tables (sentiment, forecast log, outbox, profiles); prices accept 24h RPO because they're re-backfillable from MT5 (documented assumption). **Restore drill in Week 2** and re-drilled before production cutover.

### 6.2 Contract-first integration

Schemas in `packages/contracts` are the source of truth, versioned (`profile.v1`), exported to JSON Schema for non-Python consumers. Breaking changes create `v2`, never mutate `v1`. API standards are fixed before any consumer exists: RFC 9457 `application/problem+json` errors, cursor-based pagination, `/v1/` versioning. `schemathesis` runs contract tests against the OpenAPI spec in CI.

### 6.3 Deterministic/generative separation

Numbers come from tested, reproducible code (`server/app/analytics/`); words come from LLMs (`server/app/intelligence/`) and are labeled `type: narrative`. LLM output can never enter a numeric field. Regression fixtures pin regime-classifier behavior. LLM spend is bounded: daily budget cap with alerting, per-article sentiment cache.

### 6.4 Provenance, observability, honesty

Every output: `sources[]`, `generated_at`, `model_version`, `confidence`, `stale`. Two layers of monitoring: the **staleness watchdog** monitors the *data*; **Sentry** (server + client, from Phase 0) and Prometheus-style `**/metrics`** (ingestion lag, event publish counts, LLM spend — from Phase 3) monitor the *system*. Structured JSON logs, per-service health endpoints, immutable forecast log + weekly scoring.

### 6.5 12-factor operations & supply-chain security

Env-driven config on both sides, secrets in Vercel/Railway stores + local uncommitted `.env` / `secrets.env`, stateless services. CI on every PR: lint, tests, drift check, contract tests, generated-client compile check, **Dependabot + `pip-audit`/`pnpm audit` + container image scanning** — from Week 1, not retrofitted. Dual auth ships with the first protected routers: **Clerk JWT for humans, hashed API keys for machines**. Clerk org invite-only; machine keys never shipped in the browser bundle.

### 6.5.1 Dual auth & human email ★

- **Humans → Clerk** (social + email): sessions on Vercel; Railway validates JWT via JWKS; roles `viewer` | `analyst` | `admin` | `ops`.
- **Machines → API keys**: hashed at rest; `X-API-Key` header; issued to EPG/quant/workers.
- Same FastAPI dependency resolves either scheme into a typed principal (`HumanPrincipal` | `ServicePrincipal`) for authorization and audit.
- **Resend** delivers watchdog/staleness alerts, optional digests, and weekly scoring mail; SPF/DKIM/DMARC on `EMAIL_FROM` domain. Telegram/webhook remain optional parallel channels (`ALERT_CHANNEL=multi`).

### 6.6 Backend-first delivery on a walking skeleton

A near-empty system (health endpoint + DB + migrations + Redis) deploys to Railway staging in **Week 1** and is continuously deployed from then on — every phase lands on real infrastructure the day it's built. Phases 1–3 build ingestion → analytics → API/events; the client starts in Phase 4 against the already-live staging API. UI never drives API design mid-flight; API changes flow through contracts first.

### 6.7 Modular, single-file implementation workflow ★

- **One component/module per file.** Each React component gets its own `.tsx`; each API router, analytics module, and ingestion source gets its own `.py`. No grab-bag `utils.ts` / `helpers.py`.
- **Implement one file at a time.** Each step creates or completes a single file end-to-end before moving to the next — keeps edits small and reviewable and avoids too many simultaneous tool calls or timeouts during AI-assisted building.
- **Files stay small.** Soft cap ~200 lines for components, ~300 for server modules; split when exceeded.
- **Composition over configuration.** Pages compose small components; components receive data via props from query hooks.
- The daily tables below respect this: each day lists discrete files/modules, tackled sequentially.

### 6.8 Hard deploy-boundary separation

`client/` and `server/` are independent deployables from Day 1 (own Dockerfiles in their own directories, own env templates, own lockfiles, no cross-imports). Vercel and Railway each point at their subdirectory — the Week 12 production cutover is configuration, not refactoring. Within `server/`, API and worker are separate services sharing one image (decision #13).

### 6.9 Durable eventing: transactional outbox → Redis Streams

State changes and their events are written in the **same database transaction** (outbox table); a relay publishes outbox rows to **Redis Streams**. Consumers use consumer groups with acknowledgement and can replay missed events after disconnects. No event is ever emitted for a rolled-back change, and none is lost for a committed one. Plain pub/sub is explicitly rejected (decision #1).

### 6.10 Decisions are recorded

Every significant decision (§1.3) gets a one-page **ADR** in `docs/adr/` — context, options, choice, consequences — so sibling-platform teams and future maintainers get the *why*, not just the *what*.

---

## 7. Roadmap — Phases


| Phase                              | Weeks | Theme                                                                                                                                         | Exit criteria                                                                                                                                                                     |
| ---------------------------------- | ----- | --------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **0 — Foundations**                | 1     | Repo split, contracts, DB + migration governance, Docker, CI with security scans, **walking-skeleton staging deploy**                         | Contracts v1 merged; `alembic upgrade head` builds full schema (incl. compression/retention/outbox); CI green; **health endpoint live on Railway staging with continuous deploy** |
| **1 — Ingestion**                  | 2–3   | MT5 live + historical, trading calendar0, news, macro, registry, watchdog, **restore drill**                                                  | 2+ years M1 backfilled; live bars flowing to staging; watchdog alerts on killed feed; backup restore proven                                                                       |
| **2 — Analytics (deterministic)**  | 4–5   | Metrics, regime classifier, asset profiles, forecast log, worker service                                                                      | Regimes + profiles generated daily on staging; regression fixtures passing; worker running as separate Railway service                                                            |
| **3 — API, events & intelligence** | 6–8   | REST API v1 (**dual auth from day one**), outbox → Streams, LLM sentiment + narratives, scoring, Resend digests hook, observability hardening | All F9/F10 endpoints/events live on staging; Clerk JWT *and* API-key paths verified; sentiment ≤ 5 min; `/metrics` + dashboards up; backend frozen                                |
| **4 — Client**                     | 9–11  | Clerk-protected dashboard, asset detail, system health — hugging the live staging API; Vercel previews                                        | All pages behind Clerk on Vercel preview against staging; role gates live; generated-client compile check in CI                                                                   |
| **5 — Hardening & production**     | 12    | Production cutover (Railway + Vercel), backups re-drilled, runbooks, EPG/quant pilot                                                          | Prod live on both hosts; ≥ 1 sibling platform consuming a feed; success criteria baselined                                                                                        |
| **Buffer**                         | 13–14 | **Unallocated by design (~15% slack)** — absorbs overruns from MT5 data quality, LLM prompt iteration, Railway quirks, pilot feedback         | Not scheduled against; if unused, v1.1 starts early                                                                                                                               |


> **Staffing note:** this plan is sized for ~2 engineers. For a solo build, re-baseline to ~16–18 weeks rather than compressing quality (the usual silent failure mode: D5 test/status days getting skipped).

---

## 8. Weekly/Daily Implementation Table

Backend first (Weeks 1–8), then client (Weeks 9–11), then hardening (Week 12), then buffer (13–14). Five working days per week; Day 5 always ends with tests green and a short written status note. Per §6.7, each day's work proceeds **one file/module at a time** in the order listed.

### Phase 0 — Foundations (Week 1)


| Day   | Work                                                                                                                                                                                                                                                                                                                                                                                         |
| ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W1·D1 | Init monorepo with `client/` + `server/` + `packages/contracts/` skeletons. Root `docker-compose.yml` for services (Postgres+Timescale, Redis) with named volumes. Per-side `.env.example` (incl. `CLERK_*`, `RESEND_*` placeholders) + gitignore for real secrets. `.github/dependabot.yml`. First ADRs for §1.3 decisions (incl. dual auth + Resend). Verify `docker compose up`.          |
| W1·D2 | Contracts, one schema file at a time: `profile_v1.py` → `state_v1.py` → `sentiment_v1.py` → `insight_v1.py` → `events_v1.py` → JSON Schema export script.                                                                                                                                                                                                                                    |
| W1·D3 | Contract review pass (walk EPG/quant needs through schemas); finalize v1. Server scaffold: `pyproject.toml` (uv), `app/main.py`, `config.py`, `observability/` (Sentry init + structured logging), `api/v1/health.py`. Runs natively via uvicorn against Dockerized services.                                                                                                                |
| W1·D4 | SQLAlchemy models, one file per model (assets, prices, news, sentiment, states, profiles, insights, source_registry, forecast_log, **outbox**). Alembic init (+ global `lock_timeout`) + initial migration: hypertable, **compression policy, retention policy**, H1/D1 continuous aggregates, outbox table. `server/Dockerfile`.                                                            |
| W1·D5 | Seed data migrations (asset universe, source registry). CI: Ruff, pytest, **drift check**, `pip-audit`/`pnpm audit`, image scan, image builds. **Walking-skeleton staging deploy on Railway:** TimescaleDB (Docker image) + Redis + server (release = `alembic upgrade head`), private networking, secrets; continuous deploy on main enabled. Health endpoint live. Tag `v0.1-foundations`. |


### Phase 1 — Ingestion (Weeks 2–3)


| Day   | Work                                                                                                                                                                                                                                                          |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W2·D1 | `app/calendar/` trading-calendar module first (UTC storage, sessions, MT5 server-time offset/DST). Then MT5 worker scaffold (`ops/mt5-worker/` + `ingestion/mt5/`): connectivity module → symbol-mapping module (canonical ID ↔ MT5 ticker).                  |
| W2·D2 | Historical backfill job: 2–5 yrs M1 OHLCV per symbol; idempotent, resumable; calendar-aware. Start backfill against local DB, then staging.                                                                                                                   |
| W2·D3 | Live price poller module: 1-min bars, gap detection + re-fetch; write path integration-tested; pointed at staging DB (via pooler).                                                                                                                            |
| W2·D4 | `ingestion/registry.py`: source registry with cadence expectations; heartbeats. **Backups live: nightly full `pg_dump` + hourly targeted dumps of irreplaceable tables. Restore drill executed against a scratch DB — RPO/RTO (N9) proven, runbook written.** |
| W2·D5 | Watchdog v1 (cadence checker → stale-flag propagation → log alerts). Kill-feed drill on staging. Backfill integrity gap report. Status note.                                                                                                                  |
| W3·D1 | News poller (`ingestion/news/`): API client module → dedupe module → asset-mapping module.                                                                                                                                                                    |
| W3·D2 | Economic calendar ingestion + high-impact flagging; FRED macro poller (`ingestion/macro/`).                                                                                                                                                                   |
| W3·D3 | Ingestion integration tests (recorded fixtures); shared rate-limit + retry/backoff module.                                                                                                                                                                    |
| W3·D4 | Alert channel module: **Resend client** (`notifications/`) + optional Telegram/webhook; shared send interface; watchdog alerting end-to-end on staging (email required path proven).                                                                          |
| W3·D5 | Stabilization: all feeds running 24h on staging, fix gaps, feed-down runbook. Tag `v0.2-ingestion`.                                                                                                                                                           |


### Phase 2 — Deterministic analytics (Weeks 4–5)

**Locked baseline (2026-09-12):** model tags `metrics.v1` / `regimes.rule_v1`.

| Decision | Choice |
| -------- | ------ |
| Timeframes | **M1, M15, H1, H4, D1** — add Timescale continuous aggregates for M15/H4 in W4·D1 (H1/D1 already exist) |
| Realized vol | Rolling std of log returns, **20** + **60** periods, annualized; percentile rank **30d** (profile) / **90d** (context) |
| ATR | Wilder **ATR(14)**; percentiles **30d** / **90d** |
| Rolling returns | **1 / 5 / 20** periods per timeframe |
| Correlations | Pearson on log returns, **30d** window on **H1**; all active symbols pairwise |
| Session policy | Use all bars; calendar module **excludes weekend/holiday gaps from return series** (no Friday→Sunday synthetic returns). No per-session metric variants in v1 |
| USDCHF | Stay `is_active` for ingest; **exclude from correlations + regimes** until ≥90 days M1 depth (analytics config, not DB demotion) |
| Spread / liquidity | **Defer** true bid/ask; use range proxies (typical daily range, high−low percentiles); leave `typical_spread` null with a note |
| Trend strength | **Kaufman Efficiency Ratio (20)**; signed by net-change direction; tagged `metrics.v1` |
| Regime grid v0 | **Tuned W4·D4:** vol percentile ≥**75** → `high_volatility`; else \|ER\| ≥**0.25** → trend by sign; else `ranging`. Soft probs + N=3 persistence. H1 avg ~0.86 flips/day (budget ≤2); D1 within ≤1/week |
| Flip-rate budget | Hysteresis + **N=3** bar persistence; target **≤2 flips/symbol/day on H1**, **≤1 flip/symbol/week on D1** |
| Profile refresh | Daily **00:15 UTC**; event-triggered on `regime.changed` (H4/D1) + high-impact calendar (mapped assets); debounce **≤1 refresh/hour/symbol** |
| Profile retention | Keep every version **180 days**, then prune to last-of-day |
| HMM (W5·D5) | Spike complete — **not promoted** (flip-rate slightly better, agreement ~0.49 < 0.55). Production stays `regimes.rule_v1`. See ADR-017. |
| Compute target | **Local Docker Timescale** for W4–W5 development; Railway second worker service at **W5·D4** (confirm below) |

**Confirm before / on W4·D1 (two defaults):**

1. **DB target = local Docker** — `server/.env` `DATABASE_URL` points at Compose Postgres (`localhost:5433` / project default). Sanity: `docker compose ps` shows healthy postgres; `SELECT count(*), min(ts), max(ts) FROM prices GROUP BY symbol` returns the ~10M-bar universe. If you want analytics to write to Railway staging instead, say so and we switch `DATABASE_URL` + run migrations there.
2. **MT5 server offset = EET-style UTC+2/+3** — calendar uses `infer_mt5_offset_hours()` (Europe/Bucharest DST) unless `MT5_SERVER_UTC_OFFSET_HOURS` overrides. Confirm on W4·D1: compare a known YWO bar’s MT5 terminal timestamp vs stored UTC in `prices`; if mismatch by 1h, set the env override and re-check. Session-aware gap filtering depends on this being right.

| Day   | Work                                                                                                                                                                                                                                                  |
| ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W4·D1 | Migration: Timescale caggs for **M15 + H4**. Sanity-check MT5 offset vs YWO bars. `analytics/metrics.py` part 1 (`metrics.v1`): realized vol (20/60), ATR(14)+percentiles, rolling returns on **M1/M15/H1/H4/D1**; gap-aware returns via calendar.   |
| W4·D2 | Metrics part 2 (split file if >300 lines): Kaufman ER(20) trend strength; H1 30d correlation matrix (**exclude USDCHF** until depth gate); range-based liquidity proxies (true spread deferred).                                                      |
| W4·D3 | `analytics/regimes.py` (`regimes.rule_v1`): vol percentile × ER grid → 4 regimes + soft probabilities; hysteresis + N=3 persistence; USDCHF excluded until depth gate.                                                                               |
| W4·D4 | Backtest classifier over history; tune thresholds against flip-rate budget (≤2/day H1, ≤1/week D1); measure noise.                                                                                                                                  |
| W4·D5 | Regression fixtures pinning classifier behavior; unit tests for all metrics. Status note.                                                                                                                                                             |
| W5·D1 | `analytics/profiles.py`: daily profile builder assembling `AssetProfile` per contract (30d percentiles, correlations, regime distribution).                                                                                                          |
| W5·D2 | Event-triggered profile refresh (regime.changed H4/D1 + high-impact calendar, ≤1/hour/symbol); versioning + **180d retention then last-of-day** (migration).                                                                                        |
| W5·D3 | Forecast/regime-call immutable log writer; every classification recorded with model version.                                                                                                                                                          |
| W5·D4 | `scheduler.py` as **worker entrypoint**: APScheduler (metrics cadence, daily 00:15 UTC profiles, log writes). Compose `--profile worker`. **Deploy worker as second Railway service (same image, worker entrypoint).** Full pipeline dry-run on staging. |
| W5·D5 | HMM classifier spike (`hmmlearn`, 4-state Gaussian) as v2 candidate — compare vs rule-based on flip-rate + agreement; decide & write ADR. Tag `v0.3-analytics`.                                                                                      |


### Phase 3 — API, events & intelligence (Weeks 6–8)


| Day   | Work                                                                                                                                                                                                                                                                                                                                                                                     |
| ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W6·D1 | **Dual-auth middleware first** (`auth/api_keys.py` hashed keys → `auth/clerk_jwt.py` JWKS verify → `auth/roles.py` → FastAPI dependencies) + shared **problem+json (RFC 9457) error model** + **cursor pagination** helpers. Then routers one file at a time: `assets.py` → `profiles.py` — provenance envelope on every response. Smoke: call with API key *and* with a test Clerk JWT. |
| W6·D2 | `states.py` → `metrics.py` → `news.py` routers; p95 latency check; role checks stubbed for ops-only routes.                                                                                                                                                                                                                                                                              |
| W6·D3 | `events/`: **outbox writer → relay → Redis Streams publisher**; `regime.changed` + `profile.updated` wired into analytics jobs in the same transaction as state changes. Consumer-group + replay smoke test.                                                                                                                                                                             |
| W6·D4 | OpenAPI spec polish (security schemes: `bearerAuth` Clerk + `apiKey`); CORS for known origins (incl. Clerk authorized parties); `schemathesis` contract tests wired into CI; API integration tests for both auth paths.                                                                                                                                                                  |
| W6·D5 | Consumer smoke test: minimal Python client simulating EPG (API key pull + consumer-group subscribe + replay after disconnect). Status note.                                                                                                                                                                                                                                              |
| W7·D1 | `intelligence/llm_client.py`: provider-agnostic interface, retries, cost logging, **daily budget cap with alerting**.                                                                                                                                                                                                                                                                    |
| W7·D2 | `intelligence/sentiment.py`: news → per-asset score [-1,+1], decay-weighted 24h, top drivers → `SentimentSnapshot`; **per-article score cache** (dedupe = never score the same headline twice).                                                                                                                                                                                          |
| W7·D3 | Sentiment schedule (≤ 5 min, worker service); `sentiment.spike` + `news.high_impact` events via outbox; `sentiment.py` router.                                                                                                                                                                                                                                                           |
| W7·D4 | `intelligence/narratives.py`: deterministic outputs → labeled narratives; `insights.py` router with disclaimer field.                                                                                                                                                                                                                                                                    |
| W7·D5 | Guardrail tests: narratives never alter numeric fields; label + provenance enforcement; budget-cap behavior. Status note.                                                                                                                                                                                                                                                                |
| W8·D1 | `scoring/` weekly job (worker service): regime calls vs realized outcomes; accuracy tables; **Resend weekly scoring email** to `EMAIL_ALERT_TO`.                                                                                                                                                                                                                                         |
| W8·D2 | Staleness → API integration: `stale: true` propagates to every affected endpoint response; Resend alert on prolonged staleness.                                                                                                                                                                                                                                                          |
| W8·D3 | Load test API on staging (universe-wide polling pattern); index tuning; verify PgBouncer under load.                                                                                                                                                                                                                                                                                     |
| W8·D4 | **Observability hardening:** `/metrics` endpoint (ingestion lag, event publish/ack counts, LLM spend/day, API latency, auth method counts); alert rules; Sentry release tagging; ADR catch-up (dual auth + Resend).                                                                                                                                                                      |
| W8·D5 | **Backend freeze for v1.** End-to-end soak on staging (already weeks-deployed — no big-bang risk). Tag `v0.4-api`. Staging API is now the client's stable target.                                                                                                                                                                                                                        |


### Phase 4 — Client, hugging the deployed backend (Weeks 9–11)

*Per §6.7: one `.tsx` component per step, completed and wired before starting the next.*


| Day    | Work                                                                                                                                                                                                                                                                                                                                                                      |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W9·D1  | `client/`: Next.js 16 + TS + Tailwind + shadcn via pnpm; dark theme tokens incl. regime colors; fonts; Sentry (client). **Clerk**: install SDK, `ClerkProvider` in `layout.tsx`, `middleware.ts` protecting all app routes, sign-in/sign-up catch-all pages; invite-only org configured. Finalize `client/Dockerfile`. Env: `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_CLERK_`*. |
| W9·D2  | **Generate API client from staging OpenAPI spec** (orval/openapi-typescript) into `lib/api/`; TanStack Query provider that attaches **Clerk session JWT** to requests; **generated-client compile check** in CI for every server PR. Connect Vercel project (root = `client/`) → first preview deploy with Clerk + Resend env vars.                                       |
| W9·D3  | One file at a time: `layout.tsx` shell + nav + `UserButton` → `lib/queries/assets.ts` → `AssetGrid.tsx` bound to live `GET /v1/assets` (Clerk JWT).                                                                                                                                                                                                                       |
| W9·D4  | `Sparkline.tsx` → `StateBadge.tsx` → `VolPercentile.tsx` → `StaleBadge.tsx`; compose into dashboard grid.                                                                                                                                                                                                                                                                 |
| W9·D5  | `MarketSummaryStrip.tsx` → `NewsTicker.tsx`. Vercel preview review (signed-in vs signed-out). Status note.                                                                                                                                                                                                                                                                |
| W10·D1 | Asset detail: `lib/queries/asset-detail.ts` → `PriceChart.tsx` (Lightweight Charts) → `RegimeBands.tsx` overlay from `/state` history.                                                                                                                                                                                                                                    |
| W10·D2 | `ProfileCard.tsx` → `CorrelationHeatmap.tsx` → `StatePanel.tsx` (probabilities, confidence, model version, `generated_at`).                                                                                                                                                                                                                                               |
| W10·D3 | `SentimentGauge.tsx` → `SentimentTrend.tsx` → `DriverHeadlines.tsx` from `/sentiment`.                                                                                                                                                                                                                                                                                    |
| W10·D4 | `InsightFeed.tsx` with AI-generated labeling + disclaimer; compose full asset detail page.                                                                                                                                                                                                                                                                                |
| W10·D5 | Refetch intervals honest to backend cadences; stale badges across all panels. Vercel preview review. Status note.                                                                                                                                                                                                                                                         |
| W11·D1 | System page: `FeedRegistryTable.tsx` → `WatchdogAlertsList.tsx` from health/metrics endpoints; `**RoleGate.tsx**` (ops/admin only).                                                                                                                                                                                                                                       |
| W11·D2 | `ScoringResults.tsx` (weekly regime accuracy); **Admin API-key mint/revoke UI** (admin only); logo/favicon into `client/public/`.                                                                                                                                                                                                                                         |
| W11·D3 | Responsive + a11y pass; empty/error/loading states, one page at a time; unauthenticated redirect check.                                                                                                                                                                                                                                                                   |
| W11·D4 | Playwright smoke tests (sign-in gate, 3 pages, role-denied `/system`, critical paths) in CI against preview URL.                                                                                                                                                                                                                                                          |
| W11·D5 | Polish + bugfix day; UI review against real market hours on Vercel preview. Tag `v0.5-client`.                                                                                                                                                                                                                                                                            |


### Phase 5 — Hardening & production (Week 12)


| Day    | Work                                                                                                                                                                                                                                  |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W12·D1 | **Railway production environment:** replicate staging (API + worker + TimescaleDB + Redis + PgBouncer), prod secrets, MT5 worker → prod DB; API domain. Prod backup schedule live.                                                    |
| W12·D2 | **Vercel production:** promote client, prod `NEXT_PUBLIC_API_URL`, Clerk prod instance + allowed origins, CORS locked to prod domains, Resend domain DNS verified. **Re-run restore drill against prod backups**; runbooks finalized. |
| W12·D3 | EPG/quant integration pilot: hand over contracts package + **machine API keys** (hashed at rest); support first real consumption — pull + Streams consumer group — against prod. Confirm dashboard humans use Clerk only.             |
| W12·D4 | Baseline success criteria: freshness numbers, regime accuracy baseline, adoption check. Fix what the pilot surfaces.                                                                                                                  |
| W12·D5 | Retro + v1.1 planning (HMM promotion, more assets, NATS/Kafka decision). Tag `v1.0`.                                                                                                                                                  |


### Buffer (Weeks 13–14)


| Slot    | Purpose                                                                                                                                                                                                                                          |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| W13–W14 | **Unallocated by design (~15% slack).** Absorbs overruns from MT5 backfill quality issues, LLM prompt iteration, Railway/Timescale operational surprises, and pilot feedback. Not to be scheduled against upfront; if unused, v1.1 starts early. |


---

## 9. Risks & Mitigations


| Risk                                                         | Mitigation                                                                                                                                                                      |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| MT5 Windows dependency is fragile (and can't run on Railway) | Dedicated Windows worker with auto-restart + heartbeat, pushing into Railway over TLS; watchdog catches silence within minutes                                                  |
| Big-bang deploy surprises                                    | Eliminated by design: walking skeleton on Railway from W1·D5, continuously deployed thereafter                                                                                  |
| Event loss to disconnected consumers                         | Outbox + Redis Streams (consumer groups, acks, replay) — no fire-and-forget pub/sub                                                                                             |
| Scheduled jobs double-fire or die on restart                 | Scheduler runs in a dedicated worker service, never in the API process                                                                                                          |
| Self-managed Timescale data loss                             | Defined RPO/RTO (N9); nightly full + hourly targeted dumps; restore drill in Week 2 and again before prod cutover                                                               |
| Timezone/DST corruption of bars and sessions                 | UTC everywhere + trading-calendar module built first (W2·D1), before any bar is stored                                                                                          |
| News API licensing limits redistribution                     | Source registry records license terms; derived sentiment/insights served internally only; confirm derived-data clauses before adding paid feeds                                 |
| Regime classifier noise (excessive flips)                    | Flip-rate budget: ≤2 flips/symbol/day on H1, ≤1/week on D1; hysteresis + N=3 persistence (W4·D3/D4); HMM candidate evaluated before promotion (W5·D5)                          |
| LLM hallucination reaching consumers                         | Two-tier split enforced by tests (W7·D5); narratives labeled; numeric fields untouchable by LLM code paths                                                                      |
| LLM cost blowout                                             | Daily budget cap with alerting; per-article sentiment cache; spend tracked in `/metrics`                                                                                        |
| Schedule pressure eroding quality                            | Explicit buffer (Weeks 13–14); D5 test/status discipline; solo build re-baselines to 16–18 weeks instead of compressing                                                         |
| Scope creep                                                  | Everything outside §2.1 goes to the v1.1 backlog; phase exit criteria are the gate                                                                                              |
| Silent staleness                                             | Watchdog + `stale` propagation built in Phase 1, *before* any consumer exists; Resend email path proven at W3·D4                                                                |
| Multi-file edit sprawl during AI-assisted implementation     | §6.7 single-file workflow; daily plans enumerate discrete files in sequence                                                                                                     |
| Mixing human and machine auth                                | Dual-auth design (§3.2): Clerk JWT for browsers only; API keys for EPG/quant; browser never holds machine keys                                                                  |
| Clerk or Resend outage                                       | API keys still allow machine consumers; alerts fall back to Telegram/webhook if `ALERT_CHANNEL=multi`; dashboard degrades to sign-in unavailable (acceptable for internal tool) |


---

## 10. v1.1 Backlog (explicitly deferred)

- HMM regime classifier promotion (if W5·D5 spike wins)
- Tick-level data for select instruments (only on proven consumer need)
- NATS/Kafka migration (only on event-volume evidence from Streams metrics)
- Infographic/report generation (PDF/PNG exports)
- Additional asset classes (equities, crypto, rates) and sources (bank/settlement data)
- External access tier (would trigger regulatory review first)

