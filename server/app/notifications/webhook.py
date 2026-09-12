"""Optional generic webhook notifier (Slack-compatible JSON body)."""

from __future__ import annotations

import logging

import httpx

from app.config import Settings, get_settings
from app.ingestion.httputil import request_with_retry
from app.notifications.base import AlertMessage, SendResult

logger = logging.getLogger(__name__)


class WebhookNotifier:
    name = "webhook"

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._timeout = timeout
        self._transport = transport

    def send(self, message: AlertMessage) -> SendResult:
        url = self._settings.alert_webhook_url
        if not url:
            detail = "ALERT_WEBHOOK_URL not configured"
            logger.warning("webhook skip: %s", detail)
            return SendResult(channel=self.name, ok=False, detail=detail)

        payload = {
            "text": f"{message.subject}\n{message.body}",
            "subject": message.subject,
            "severity": message.severity,
            "tags": list(message.tags),
            "created_at": message.created_at.isoformat(),
        }
        try:
            request_with_retry(
                "POST",
                url,
                timeout=self._timeout,
                json=payload,
                transport=self._transport,
                retries=2,
            )
            return SendResult(channel=self.name, ok=True, detail="sent")
        except Exception as exc:  # noqa: BLE001
            logger.exception("webhook send failed")
            return SendResult(channel=self.name, ok=False, detail=str(exc))
