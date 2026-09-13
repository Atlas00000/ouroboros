# W7 status — multi-model LLM, sentiment, narratives (local)

**Date:** 2026-09-13  
**Scope:** W7·D1–D5 (local Docker)

## Delivered

### W7·D1
- `app/intelligence/llm_client.py` — ordered providers from `LLM_PROVIDERS`
- Skip missing keys; 429/errors → next provider; daily USD budget (Redis + in-process fallback)
- Providers: OpenAI, Anthropic, Gemini, Groq, **mock** (tests / no keys)
- No Ollama / local GPU

### W7·D2
- `app/intelligence/sentiment.py` — [-1,+1], 24h half-life decay, top drivers
- Migration `0009_article_scores` — per-article cache (never re-score same `external_id`)
- Batch cap per tick (`MAX_SCORE_PER_TICK`)

### W7·D3
- Scheduler jobs: `sentiment_refresh` (`SENTIMENT_INTERVAL_MINUTES`), `narratives_refresh`
- Outbox: `sentiment.spike`, `news.high_impact`
- `GET /v1/sentiment` → `sentiment.v1`

### W7·D4
- `app/intelligence/narratives.py` — labeled `type: narrative` + disclaimer
- Template path when mock / LLM fail; JSON path for cloud providers
- `GET /v1/insights` → `insight.v1`

### W7·D5
- Guardrail tests: budget cap, article cache, narrative label/disclaimer, insight writes only `InsightRow`

## Config

```
LLM_PROVIDERS=mock          # or gemini,groq / openai,anthropic,gemini
LLM_DAILY_BUDGET_USD=10
SENTIMENT_INTERVAL_MINUTES=15
SENTIMENT_SPIKE_THRESHOLD=0.25
```

## Tests / migrate

```powershell
cd server
py -3.12 -m alembic upgrade head
py -3.12 -m pytest tests/test_intelligence_w7.py tests/test_api_w7.py tests/test_scheduler.py -q
```

## Next

**W8** — observability hardening (`/metrics` Prometheus), digests hook, staging freeze prep.
