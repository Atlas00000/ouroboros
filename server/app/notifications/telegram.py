"""Optional Telegram Bot API notifier."""

from __future__ import annotations

import logging

import httpx

from app.config import Settings, get_settings
from app.ingestion.httputil import request_with_retry
from app.notifications.base import AlertMessage, SendResult

logger = logging.getLogger(__name__)


class TelegramNotifier:
    name = "telegram"

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
        token = self._settings.alert_telegram_bot_token
        chat_id = self._settings.alert_telegram_chat_id
        if not token or not chat_id:
            detail = "ALERT_TELEGRAM_BOT_TOKEN / ALERT_TELEGRAM_CHAT_ID not configured"
            logger.warning("telegram skip: %s", detail)
            return SendResult(channel=self.name, ok=False, detail=detail)

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        text = f"*{message.subject}*\n{message.body}"
        try:
            resp = request_with_retry(
                "POST",
                url,
                timeout=self._timeout,
                json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
                transport=self._transport,
                retries=2,
            )
            data = resp.json() if resp.content else {}
            mid = None
            if isinstance(data, dict):
                result = data.get("result") or {}
                if isinstance(result, dict):
                    mid = result.get("message_id")
            return SendResult(
                channel=self.name,
                ok=True,
                detail="sent",
                provider_id=str(mid) if mid is not None else None,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("telegram send failed")
            return SendResult(channel=self.name, ok=False, detail=str(exc))
