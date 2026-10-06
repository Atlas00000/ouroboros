# Ouroboros API server (Railway)

FastAPI API + APScheduler worker (same Docker image, different start commands).

**Deploy:** Railway — Root Directory = **repository root**, Dockerfile `server/Dockerfile`.  
Full steps: [`../DEPLOYMENT.md`](../DEPLOYMENT.md) · walking skeleton: [`../ops/railway/STAGING.md`](../ops/railway/STAGING.md).

| Service | Config | Start |
| --- | --- | --- |
| API | [`railway.toml`](./railway.toml) | `uvicorn … --port $PORT` · release `alembic upgrade head` |
| Worker | [`railway.worker.toml`](./railway.worker.toml) | `python -m app.scheduler` |

## Local run

```bash
# From repo root — services must be up
docker-compose up -d

cd server
python -m pip install -e ".[dev]"
python -m alembic upgrade head
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health: [http://localhost:8000/v1/health](http://localhost:8000/v1/health)

Copy `.env.example` → `.env` before first run (gitignored).
