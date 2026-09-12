"""Bridge watchdog alerts → notification channels."""

from __future__ import annotations

import logging

from app.notifications.base import AlertMessage, Notifier, SendResult
from app.notifications.factory import build_notifier
from app.watchdog.checker import WatchdogAlert, WatchdogReport

logger = logging.getLogger(__name__)


def alerts_to_message(alerts: list[WatchdogAlert], *, checked_at: str | None = None) -> AlertMessage:
    lines = [a.message for a in alerts]
    if checked_at:
        lines.append(f"checked_at={checked_at}")
    sources = ", ".join(sorted({a.source_id for a in alerts}))
    return AlertMessage(
        subject=f"Watchdog: {len(alerts)} stale feed(s) — {sources}",
        body="\n".join(lines),
        severity="error",
        tags=("watchdog", "stale"),
    )


def notify_watchdog_report(
    report: WatchdogReport,
    *,
    notifier: Notifier | None = None,
) -> SendResult | None:
    """Send a digest when the report has alerts. Returns None if nothing to send."""
    if not report.alerts:
        return None
    channel = notifier or build_notifier()
    message = alerts_to_message(
        report.alerts,
        checked_at=report.checked_at.isoformat(),
    )
    result = channel.send(message)
    logger.info(
        "watchdog notify channel=%s ok=%s detail=%s",
        result.channel,
        result.ok,
        result.detail,
    )
    return result
