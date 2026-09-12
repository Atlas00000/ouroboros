"""CLI: print source registry cadence / heartbeat snapshot."""

from __future__ import annotations

import os
import sys
from pathlib import Path

SERVER_ROOT = Path(__file__).resolve().parents[1] / "server"
sys.path.insert(0, str(SERVER_ROOT))
os.chdir(SERVER_ROOT)

from app.config import get_settings  # noqa: E402
from app.db.session import get_session_factory  # noqa: E402
from app.ingestion.registry import refresh_statuses  # noqa: E402
from app.observability.logging import configure_logging  # noqa: E402


def main() -> int:
    get_settings.cache_clear()
    settings = get_settings()
    configure_logging(settings.log_level)

    session = get_session_factory()()
    try:
        snaps = refresh_statuses(session)
        print(f"sources={len(snaps)}")
        for s in snaps:
            age = f"{s.age_seconds:.0f}s" if s.age_seconds is not None else "never"
            print(
                f"  {s.source_id:20} kind={s.kind:8} cadence={s.expected_cadence_seconds:>5}s "
                f"status={s.status:8} age={age} stale={s.stale}"
            )
    finally:
        session.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
