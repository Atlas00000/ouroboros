#!/usr/bin/env python3
"""
Restore drill against a scratch database (W2·D4 / N9).

Creates ouroboros_restore_drill, restores the latest full dump (or a path you
pass), verifies seeded row counts, then optionally drops the scratch DB.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (
    BACKUP_ROOT,
    DEFAULT_CONTAINER,
    DEFAULT_USER,
    docker_available,
    drop_database,
    ensure_database,
    pg_restore_custom,
    run,
)

SCRATCH_DB = "ouroboros_restore_drill"


def latest_full_dump() -> Path | None:
    full_dir = BACKUP_ROOT / "full"
    if not full_dir.exists():
        return None
    dumps = sorted(full_dir.glob("ouroboros_full_*.dump"), key=lambda p: p.stat().st_mtime)
    return dumps[-1] if dumps else None


def verify_scratch(*, user: str, container: str) -> dict[str, int]:
    checks = {
        "assets": "SELECT count(*) FROM assets",
        "source_registry": "SELECT count(*) FROM source_registry",
        "prices": "SELECT count(*) FROM prices",
    }
    out: dict[str, int] = {}
    for name, sql in checks.items():
        r = run(
            [
                "docker",
                "exec",
                container,
                "psql",
                "-U",
                user,
                "-d",
                SCRATCH_DB,
                "-tAc",
                sql,
            ]
        )
        out[name] = int(r.stdout.strip() or "0")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Restore drill into scratch DB")
    parser.add_argument("--dump", type=Path, default=None, help="Path to -Fc dump")
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--container", default=DEFAULT_CONTAINER)
    parser.add_argument(
        "--keep",
        action="store_true",
        help="Keep scratch DB after verification (default: drop)",
    )
    args = parser.parse_args()

    if not docker_available(args.container):
        print(f"FAILED: container {args.container} not running", file=sys.stderr)
        return 1

    dump = args.dump or latest_full_dump()
    if dump is None or not dump.exists():
        print("FAILED: no dump found — run backup_full.py first", file=sys.stderr)
        return 1

    print(f"restore drill dump={dump}")
    drop_database(SCRATCH_DB, user=args.user, container=args.container)
    ensure_database(SCRATCH_DB, user=args.user, container=args.container)

    # Timescale extension required before restore of hypertables.
    run(
        [
            "docker",
            "exec",
            args.container,
            "psql",
            "-U",
            args.user,
            "-d",
            SCRATCH_DB,
            "-c",
            "CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;",
        ]
    )

    # Timescale: disable background jobs during restore (avoids partial catalog issues).
    run(
        [
            "docker",
            "exec",
            args.container,
            "psql",
            "-U",
            args.user,
            "-d",
            SCRATCH_DB,
            "-c",
            "SELECT timescaledb_pre_restore();",
        ],
        check=False,
    )

    pg_restore_custom(
        dump_path=dump,
        db=SCRATCH_DB,
        user=args.user,
        container=args.container,
        clean=False,
    )

    run(
        [
            "docker",
            "exec",
            args.container,
            "psql",
            "-U",
            args.user,
            "-d",
            SCRATCH_DB,
            "-c",
            "SELECT timescaledb_post_restore();",
        ],
        check=False,
    )

    counts = verify_scratch(user=args.user, container=args.container)
    print(f"verify counts={counts}")
    if counts.get("assets", 0) < 1 or counts.get("source_registry", 0) < 1:
        print("FAILED: expected seeded assets/source_registry rows", file=sys.stderr)
        return 1
    if counts.get("prices", 0) < 1:
        print(
            "WARN: prices empty after restore — acceptable if dump had no bars; "
            "re-backfill from MT5 covers prices RPO",
            file=sys.stderr,
        )

    if not args.keep:
        drop_database(SCRATCH_DB, user=args.user, container=args.container)
        print(f"scratch db {SCRATCH_DB} dropped")
    else:
        print(f"scratch db kept: {SCRATCH_DB}")

    print("restore drill PASSED")
    print(
        "RPO assumptions: prices <= 24h (re-backfill MT5); "
        "irreplaceable <= 1h (targeted dumps)"
    )
    print("RTO target: <= 4h (restore dump + alembic verify + resume workers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
