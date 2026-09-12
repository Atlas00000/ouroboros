"""Fan-out notifier + factory from settings."""

from __future__ import annotations

import logging

from app.config import Settings, get_settings
from app.notifications.base import AlertMessage, Notifier, SendResult
from app.notifications.log import LogNotifier
from app.notifications.resend_client import ResendNotifier
from app.notifications.telegram import TelegramNotifier
from app.notifications.webhook import WebhookNotifier

logger = logging.getLogger(__name__)


class MultiNotifier:
    """Send to every configured child; ok if any child succeeds."""

    name = "multi"

    def __init__(self, channels: list[Notifier]) -> None:
        self._channels = channels

    def send(self, message: AlertMessage) -> SendResult:
        results: list[SendResult] = []
        for channel in self._channels:
            results.append(channel.send(message))
        ok_any = any(r.ok for r in results)
        detail = "; ".join(f"{r.channel}={'ok' if r.ok else 'fail'}:{r.detail}" for r in results)
        provider_ids = [r.provider_id for r in results if r.provider_id]
        return SendResult(
            channel=self.name,
            ok=ok_any,
            detail=detail,
            provider_id=",".join(provider_ids) if provider_ids else None,
        )


def build_notifier(settings: Settings | None = None) -> Notifier:
    """
    Build notifier from ALERT_CHANNEL.

    Values: `resend` | `telegram` | `webhook` | `log` | `multi`
    `multi` fans out to every channel that has credentials configured (+ always logs).
    """
    cfg = settings or get_settings()
    channel = (cfg.alert_channel or "resend").strip().lower()

    if channel == "log":
        return LogNotifier()
    if channel == "resend":
        return ResendNotifier(cfg)
    if channel == "telegram":
        return TelegramNotifier(cfg)
    if channel == "webhook":
        return WebhookNotifier(cfg)
    if channel == "multi":
        channels: list[Notifier] = [LogNotifier()]
        if cfg.resend_api_key and cfg.email_from and cfg.email_alert_to:
            channels.append(ResendNotifier(cfg))
        if cfg.alert_telegram_bot_token and cfg.alert_telegram_chat_id:
            channels.append(TelegramNotifier(cfg))
        if cfg.alert_webhook_url:
            channels.append(WebhookNotifier(cfg))
        return MultiNotifier(channels)

    logger.warning("unknown ALERT_CHANNEL=%s — using log", channel)
    return LogNotifier()
