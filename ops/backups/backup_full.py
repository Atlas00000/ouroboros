#!/usr/bin/env python3
"""Nightly full database dump (custom format). RPO for prices ≤ 24h (N9)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import DEFAULT_CONTAINER, DEFAULT_DB, DEFAULT_USER, ensure_backup_dir, pg_dump_custom, stamp


def main() -> int:
    parser = argparse.ArgumentParser(description="Full pg_dump of Ouroboros DB")
    parser.add_argument("--db", default=DEFAULT_DB)
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--container", default=DEFAULT_CONTAINER)
    args = parser.parse_args()

    out = ensure_backup_dir("full") / f"ouroboros_full_{stamp()}.dump"
    path = pg_dump_custom(
        outfile=out,
        db=args.db,
        user=args.user,
        container=args.container,
    )
    size = path.stat().st_size
    print(f"full backup ok path={path} bytes={size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
