"""CLI: send a test alert through the configured notification channel."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

SERVER_ROOT = Path(__file__).resolve().parents[2] / "server"
sys.path.insert(0, str(SERVER_ROOT))
os.chdir(SERVER_ROOT)

from app.config import get_settings  # noqa: E402
from app.notifications import AlertMessage, build_notifier  # noqa: E402
from app.observability.logging import configure_logging  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Send a test Ouroboros alert")
    parser.add_argument(
        "--subject",
        default="W3·D4 notification smoke test",
        help="Alert subject",
    )
    parser.add_argument(
        "--body",
        default="If you received this, the Resend (or configured) alert path works.",
        help="Alert body",
    )
    parser.add_argument(
        "--channel",
        default="",
        help="Override ALERT_CHANNEL for this send (resend|telegram|webhook|log|multi)",
    )
    args = parser.parse_args()

    get_settings.cache_clear()
    settings = get_settings()
    if args.channel:
        settings = settings.model_copy(update={"alert_channel": args.channel})
    configure_logging(settings.log_level)

    notifier = build_notifier(settings)
    result = notifier.send(
        AlertMessage(subject=args.subject, body=args.body, severity="info", tags=("smoke",))
    )
    print(f"notify channel={result.channel} ok={result.ok} detail={result.detail} id={result.provider_id}")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
