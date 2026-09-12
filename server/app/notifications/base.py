"""Shared notification types and Notifier protocol."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class AlertMessage:
    """Channel-agnostic alert payload."""

    subject: str
    body: str
    severity: str = "warning"  # info|warning|error|critical
    tags: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def html_body(self) -> str:
        escaped = (
            self.body.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br/>\n")
        )
        return (
            f"<h2>{self.subject}</h2>"
            f"<p><strong>severity:</strong> {self.severity}</p>"
            f"<p>{escaped}</p>"
            f"<p><small>{self.created_at.isoformat()}</small></p>"
        )


@dataclass(frozen=True)
class SendResult:
    channel: str
    ok: bool
    detail: str
    provider_id: str | None = None


@runtime_checkable
class Notifier(Protocol):
    name: str

    def send(self, message: AlertMessage) -> SendResult:
        """Deliver one alert. Implementations should not raise for soft failures."""
        ...
