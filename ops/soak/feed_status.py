"""One-shot feed health snapshot for soak / stabilization checks."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

SERVER_ROOT = Path(__file__).resolve().parents[2] / "server"
sys.path.insert(0, str(SERVER_ROOT))
os.chdir(SERVER_ROOT)

from sqlalchemy import text  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.db.session import get_session_factory  # noqa: E402
from app.ingestion.registry import refresh_statuses  # noqa: E402
from app.observability.logging import configure_logging  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Snapshot ingestion feed health")
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Optional path to append a JSONL soak sample",
    )
    args = parser.parse_args()

    get_settings.cache_clear()
    settings = get_settings()
    configure_logging(settings.log_level)

    session = get_session_factory()()
    try:
        snaps = refresh_statuses(session)
        news_count = session.execute(text("SELECT count(*) FROM news")).scalar() or 0
        cal_count = (
            session.execute(text("SELECT count(*) FROM news WHERE is_calendar = true")).scalar()
            or 0
        )
        macro_count = (
            session.execute(text("SELECT count(*) FROM macro_observations")).scalar() or 0
        )
        price_symbols = session.execute(
            text("SELECT count(DISTINCT symbol) FROM prices")
        ).scalar() or 0
        price_bars = session.execute(text("SELECT count(*) FROM prices")).scalar() or 0

        sample = {
            "ts": datetime.now(UTC).isoformat(),
            "sources": [
                {
                    "source_id": s.source_id,
                    "status": s.status,
                    "stale": s.stale,
                    "age_seconds": s.age_seconds,
                    "cadence": s.expected_cadence_seconds,
                }
                for s in snaps
            ],
            "counts": {
                "news_rows": int(news_count),
                "calendar_rows": int(cal_count),
                "macro_rows": int(macro_count),
                "price_symbols": int(price_symbols),
                "price_bars": int(price_bars),
            },
            "stale_sources": [s.source_id for s in snaps if s.stale],
            "error_sources": [s.source_id for s in snaps if s.status == "error"],
        }

        print(f"feed_status at={sample['ts']}")
        print(
            f"  counts news={sample['counts']['news_rows']} calendar={sample['counts']['calendar_rows']} "
            f"macro={sample['counts']['macro_rows']} price_symbols={sample['counts']['price_symbols']} "
            f"price_bars={sample['counts']['price_bars']}"
        )
        for s in snaps:
            age = f"{s.age_seconds:.0f}s" if s.age_seconds is not None else "never"
            print(
                f"  {s.source_id:20} status={s.status:8} age={age} stale={s.stale}"
            )
        if sample["stale_sources"] or sample["error_sources"]:
            print(
                f"  PROBLEMS stale={sample['stale_sources']} error={sample['error_sources']}"
            )

        if args.json_out is not None:
            args.json_out.parent.mkdir(parents=True, exist_ok=True)
            with args.json_out.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(sample) + "\n")
            print(f"  appended {args.json_out}")

        return 1 if sample["stale_sources"] or sample["error_sources"] else 0
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
