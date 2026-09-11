# Ouroboros API server (Railway deploy root)

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
