"""Log-only notifier (always available)."""

from __future__ import annotations

import logging

from app.notifications.base import AlertMessage, SendResult

logger = logging.getLogger(__name__)


class LogNotifier:
    name = "log"

    def send(self, message: AlertMessage) -> SendResult:
        level = {
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
        }.get(message.severity, logging.WARNING)
        logger.log(level, "alert subject=%s body=%s", message.subject, message.body)
        return SendResult(channel=self.name, ok=True, detail="logged")
