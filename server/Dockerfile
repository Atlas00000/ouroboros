# syntax=docker/dockerfile:1
# Build context must be the monorepo root (not server/):
#   docker build -f server/Dockerfile .
#   docker-compose --profile worker up -d
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Shared contracts (profile.v1, events.v1, …)
COPY packages/contracts /tmp/contracts
RUN pip install --upgrade pip && pip install /tmp/contracts && rm -rf /tmp/contracts

COPY server/pyproject.toml server/README.md ./
COPY server/app ./app
COPY server/migrations ./migrations
COPY server/alembic.ini ./

RUN pip install .

# Default: API. Worker overrides command to: python -m app.scheduler
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
