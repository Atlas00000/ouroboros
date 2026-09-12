#!/usr/bin/env python3
"""Hourly targeted dump of irreplaceable tables (N9 RPO ≤ 1h)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (
    DEFAULT_CONTAINER,
    DEFAULT_DB,
    DEFAULT_USER,
    IRREPLACEABLE_TABLES,
    ensure_backup_dir,
    pg_dump_custom,
    stamp,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Targeted dump of irreplaceable tables")
    parser.add_argument("--db", default=DEFAULT_DB)
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--container", default=DEFAULT_CONTAINER)
    args = parser.parse_args()

    out = ensure_backup_dir("targeted") / f"ouroboros_targeted_{stamp()}.dump"
    path = pg_dump_custom(
        outfile=out,
        db=args.db,
        user=args.user,
        container=args.container,
        tables=IRREPLACEABLE_TABLES,
    )
    size = path.stat().st_size
    print(f"targeted backup ok path={path} bytes={size} tables={len(IRREPLACEABLE_TABLES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
