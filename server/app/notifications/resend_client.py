"""Resend email notifier."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import Settings, get_settings
from app.ingestion.httputil import RateLimiter, request_with_retry
from app.notifications.base import AlertMessage, SendResult

logger = logging.getLogger(__name__)

RESEND_EMAILS_URL = "https://api.resend.com/emails"
_RESEND_LIMITER = RateLimiter(min_interval_seconds=0.3)


class ResendNotifier:
    name = "resend"

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
        key = self._settings.resend_api_key
        from_addr = self._settings.email_from
        to_addr = self._settings.email_alert_to
        if not key or not from_addr or not to_addr:
            detail = "RESEND_API_KEY / EMAIL_FROM / EMAIL_ALERT_TO not fully configured"
            logger.error("resend skip: %s", detail)
            return SendResult(channel=self.name, ok=False, detail=detail)

        payload: dict[str, Any] = {
            "from": from_addr,
            "to": [to_addr],
            "subject": f"[Ouroboros] {message.subject}",
            "text": message.body,
            "html": message.html_body,
        }
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        try:
            resp = request_with_retry(
                "POST",
                RESEND_EMAILS_URL,
                timeout=self._timeout,
                headers=headers,
                json=payload,
                rate_limiter=_RESEND_LIMITER,
                transport=self._transport,
                retries=2,
            )
            data = resp.json() if resp.content else {}
            provider_id = data.get("id") if isinstance(data, dict) else None
            logger.info("resend sent id=%s subject=%s", provider_id, message.subject)
            return SendResult(
                channel=self.name,
                ok=True,
                detail="sent",
                provider_id=str(provider_id) if provider_id else None,
            )
        except httpx.HTTPStatusError as exc:
            body = (exc.response.text or "")[:400]
            detail = f"HTTP {exc.response.status_code}: {body}"
            logger.error("resend send failed %s", detail)
            return SendResult(channel=self.name, ok=False, detail=detail)
        except Exception as exc:  # noqa: BLE001 — surface as soft failure to MultiNotifier
            logger.exception("resend send failed")
            return SendResult(channel=self.name, ok=False, detail=str(exc))
