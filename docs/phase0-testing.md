# Phase 0 test automation

## One command

```bash
python scripts/test_phase0.py --quick
```

Full (includes Docker image builds):

```bash
python scripts/test_phase0.py
```

## What it covers

| Step | Checks |
|------|--------|
| structure | client/server/contracts/CI/Railway/Dockerfiles exist |
| compose | Timescale + Redis up |
| migrate | `alembic upgrade head` |
| ruff | server lint |
| alembic_check | model ↔ migration drift |
| jsonschema_export | contract JSON Schema export |
| pytest_contracts | 6 contract schema tests |
| pytest_server | health, OpenAPI, seeds, hypertables, caggs |
| docker_builds | server + client images (unless `--quick`) |

## Individual suites

```bash
# Contracts only
cd packages/contracts && python -m pytest -q

# Server only (Docker services required)
cd server && python -m pytest -q
```
