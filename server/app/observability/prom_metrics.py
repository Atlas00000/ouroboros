"""In-process + Redis-backed Prometheus-style metrics (W8·D4).

Exposed at ``GET /metrics`` (not ``/v1/metrics``, which is asset metrics.v1).
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable

_lock = threading.Lock()


@dataclass
class _Counter:
    values: dict[tuple[tuple[str, str], ...], float] = field(default_factory=lambda: defaultdict(float))

    def inc(self, labels: dict[str, str], amount: float = 1.0) -> None:
        key = tuple(sorted(labels.items()))
        self.values[key] += amount


@dataclass
class _Gauge:
    values: dict[tuple[tuple[str, str], ...], float] = field(default_factory=dict)

    def set(self, labels: dict[str, str], value: float) -> None:
        key = tuple(sorted(labels.items()))
        self.values[key] = value


# HTTP
HTTP_REQUESTS = _Counter()
HTTP_LATENCY_SUM = _Counter()
HTTP_LATENCY_COUNT = _Counter()
AUTH_METHOD = _Counter()

# Latency buckets (seconds)
LATENCY_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
HTTP_LATENCY_BUCKET = _Counter()


def observe_request(
    *,
    method: str,
    path: str,
    status: int,
    duration_sec: float,
    auth_method: str | None = None,
) -> None:
    # Collapse high-cardinality paths: keep first 3 segments
    parts = [p for p in path.split("/") if p]
    route = "/" + "/".join(parts[:3]) if parts else path
    labels = {
        "method": method.upper(),
        "path": route,
        "status": str(status),
    }
    with _lock:
        HTTP_REQUESTS.inc(labels)
        HTTP_LATENCY_SUM.inc(labels, duration_sec)
        HTTP_LATENCY_COUNT.inc(labels, 1.0)
        for b in LATENCY_BUCKETS:
            if duration_sec <= b:
                HTTP_LATENCY_BUCKET.inc({**labels, "le": str(b)})
        HTTP_LATENCY_BUCKET.inc({**labels, "le": "+Inf"})
        if auth_method:
            AUTH_METHOD.inc({"method": auth_method})


def reset_http_metrics() -> None:
    """Test helper."""
    with _lock:
        HTTP_REQUESTS.values.clear()
        HTTP_LATENCY_SUM.values.clear()
        HTTP_LATENCY_COUNT.values.clear()
        HTTP_LATENCY_BUCKET.values.clear()
        AUTH_METHOD.values.clear()


def _fmt_labels(labels: Iterable[tuple[str, str]]) -> str:
    if not labels:
        return ""
    inner = ",".join(f'{k}="{v}"' for k, v in labels)
    return "{" + inner + "}"


def _render_counter(name: str, help_text: str, counter: _Counter) -> list[str]:
    lines = [f"# HELP {name} {help_text}", f"# TYPE {name} counter"]
    with _lock:
        items = list(counter.values.items())
    if not items:
        lines.append(f"{name} 0")
        return lines
    for key, val in sorted(items):
        lines.append(f"{name}{_fmt_labels(key)} {val}")
    return lines


def render_prometheus_text(
    *,
    extra_gauges: dict[str, tuple[str, dict[tuple[tuple[str, str], ...], float]]] | None = None,
) -> str:
    """
    Render OpenMetrics-ish text.

    ``extra_gauges``: name → (help, {(labels): value})
    """
    lines: list[str] = []
    lines.extend(
        _render_counter(
            "ouroboros_http_requests_total",
            "HTTP requests processed",
            HTTP_REQUESTS,
        )
    )
    lines.extend(
        _render_counter(
            "ouroboros_http_request_duration_seconds_sum",
            "Sum of HTTP request durations",
            HTTP_LATENCY_SUM,
        )
    )
    lines.extend(
        _render_counter(
            "ouroboros_http_request_duration_seconds_count",
            "Count of HTTP request durations",
            HTTP_LATENCY_COUNT,
        )
    )
    lines.extend(
        _render_counter(
            "ouroboros_http_request_duration_seconds_bucket",
            "HTTP request duration histogram buckets",
            HTTP_LATENCY_BUCKET,
        )
    )
    lines.extend(
        _render_counter(
            "ouroboros_auth_method_total",
            "Authenticated requests by auth method",
            AUTH_METHOD,
        )
    )

    if extra_gauges:
        for name, (help_text, values) in sorted(extra_gauges.items()):
            lines.append(f"# HELP {name} {help_text}")
            lines.append(f"# TYPE {name} gauge")
            if not values:
                lines.append(f"{name} 0")
            else:
                for key, val in sorted(values.items()):
                    lines.append(f"{name}{_fmt_labels(key)} {val}")

    lines.append("")
    return "\n".join(lines)


class Timer:
    def __init__(self) -> None:
        self._start = time.perf_counter()

    def seconds(self) -> float:
        return time.perf_counter() - self._start
