"""Refresh continuous aggregates used by analytics (full history).

Must run outside a transaction (Timescale requirement).
"""

from __future__ import annotations

import os
import sys

os.chdir(os.path.dirname(__file__))
sys.path.insert(0, os.getcwd())

import psycopg

from app.config import get_settings

VIEWS = ("prices_m15", "prices_h4", "prices_h1", "prices_d1")


def _dsn() -> str:
    get_settings.cache_clear()
    url = get_settings().database_url
    return url.replace("postgresql+psycopg://", "postgresql://", 1)


def main() -> int:
    views = [a for a in sys.argv[1:] if not a.startswith("-")] or list(VIEWS)
    with psycopg.connect(_dsn(), autocommit=True) as conn:
        with conn.cursor() as cur:
            for name in views:
                print(f"refresh {name} ...", flush=True)
                cur.execute(f"CALL refresh_continuous_aggregate('{name}', NULL, NULL)")
                cur.execute(f"SELECT count(*) FROM {name}")
                n = cur.fetchone()[0]
                print(f"  count={n}", flush=True)
            print("done", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
