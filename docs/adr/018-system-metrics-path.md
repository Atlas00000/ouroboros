# ADR-018: System `/metrics` vs asset `/v1/metrics`

- **Status:** Accepted
- **Date:** 2026-09-13
- **Roadmap ref:** Phase 3 W8·D4 / N6

## Context

Roadmap F9 exposes asset analytics at `GET /v1/metrics` (`metrics.v1`). Observability also needs a Prometheus scrape endpoint for ingestion lag, outbox depth, LLM spend, API latency, and auth-method counts. Colliding those on one path would break OpenAPI clients and Prometheus alike.

## Options

1. Put Prometheus series under `GET /v1/metrics` (break or overload asset contract)
2. Put Prometheus at `GET /metrics` (root, public scrape) and keep asset metrics at `/v1/metrics`
3. Put Prometheus at `/v1/ops/metrics` (ops-auth only)

## Decision

Option 2. System metrics live at **`GET /metrics`** (text/plain OpenMetrics-style, no auth in local/staging — protect at the edge in production). Asset analytics remain **`GET /v1/metrics`**.

ADR-015 (dual auth) and ADR-016 (Resend) already cover W8·D4 catch-up items.

## Consequences

- Client OpenAPI generation must ignore `/metrics` (not in v1 schema)
- Scrapers must not treat `/v1/metrics` as Prometheus
- Alert rules should watch `ouroboros_ingestion_lag_seconds`, `ouroboros_outbox_unpublished`, `ouroboros_llm_spend_usd_day`
