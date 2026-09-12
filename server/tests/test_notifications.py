"""Notification channel unit tests (no live Resend required)."""

from __future__ import annotations

import json

import httpx

from app.config import Settings
from app.notifications import AlertMessage, LogNotifier, MultiNotifier, build_notifier
from app.notifications.resend_client import ResendNotifier
from app.notifications.webhook import WebhookNotifier
from app.watchdog.checker import WatchdogAlert
from app.watchdog.notify import alerts_to_message


def _settings(**kwargs: object) -> Settings:
    base = {
        "ALERT_CHANNEL": "resend",
        "RESEND_API_KEY": "re_test",
        "EMAIL_FROM": "alerts@example.com",
        "EMAIL_ALERT_TO": "ops@example.com",
    }
    base.update(kwargs)
    return Settings(**base)  # type: ignore[arg-type]


def test_log_notifier() -> None:
    result = LogNotifier().send(AlertMessage(subject="t", body="b", severity="info"))
    assert result.ok is True


def test_resend_notifier_mock_transport() -> None:
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["auth"] = request.headers.get("Authorization", "")[:12]
        captured["body"] = json.loads(request.content.decode())
        return httpx.Response(200, json={"id": "email_123"}, request=request)

    notifier = ResendNotifier(settings=_settings(), transport=httpx.MockTransport(handler))
    result = notifier.send(AlertMessage(subject="Stale feed", body="finnhub.news is stale"))
    assert result.ok is True
    assert result.provider_id == "email_123"
    assert captured["url"] == "https://api.resend.com/emails"
    assert captured["auth"].startswith("Bearer re_")
    assert "re_test" not in str(captured.get("body"))  # key only in header
    body = captured["body"]
    assert isinstance(body, dict)
    assert body["to"] == ["ops@example.com"]
    assert "[Ouroboros]" in body["subject"]


def test_webhook_notifier_mock() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ok": True}, request=request)

    settings = _settings(ALERT_CHANNEL="webhook", ALERT_WEBHOOK_URL="https://hooks.example/x")
    result = WebhookNotifier(settings=settings, transport=httpx.MockTransport(handler)).send(
        AlertMessage(subject="x", body="y")
    )
    assert result.ok is True


def test_multi_and_factory() -> None:
    settings = _settings(ALERT_CHANNEL="multi")
    notifier = build_notifier(settings)
    assert isinstance(notifier, MultiNotifier)
    result = notifier.send(AlertMessage(subject="m", body="n", severity="warning"))
    # Log channel always ok; Resend may fail without transport — multi ok if any ok
    assert result.ok is True


def test_alerts_to_message() -> None:
    msg = alerts_to_message(
        [
            WatchdogAlert("finnhub.news", "stale", 120.0, "FEED STALE source_id=finnhub.news"),
        ],
        checked_at="2026-09-12T00:00:00+00:00",
    )
    assert "finnhub.news" in msg.subject
    assert "FEED STALE" in msg.body
