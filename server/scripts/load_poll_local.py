#!/usr/bin/env python3
"""Local load poll — universe-wide GET pattern (W8·D3).

Usage (API must be running, API key set):

  set OUROBOROS_API_KEY_QUANT=...
  py -3.12 scripts/load_poll_local.py --base http://127.0.0.1:8000 --rounds 3

Verifies pooling under concurrent-ish sequential polling of /v1/assets +
per-symbol /state and /metrics. Prints latency summary; exit 1 if error rate high.
"""

from __future__ import annotations

import argparse
import os
import statistics
import sys
import time

import httpx


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Local API load poll")
    p.add_argument("--base", default="http://127.0.0.1:8000")
    p.add_argument("--rounds", type=int, default=2)
    p.add_argument("--key", default=os.environ.get("OUROBOROS_API_KEY_QUANT") or os.environ.get("OUROBOROS_API_KEY_EPG"))
    args = p.parse_args(argv)
    if not args.key:
        print("Provide --key or OUROBOROS_API_KEY_QUANT", file=sys.stderr)
        return 2

    headers = {"X-API-Key": args.key}
    latencies: list[float] = []
    errors = 0
    calls = 0

    with httpx.Client(base_url=args.base.rstrip("/"), timeout=30.0, headers=headers) as client:
        for _ in range(args.rounds):
            t0 = time.perf_counter()
            r = client.get("/v1/assets", params={"limit": 50})
            latencies.append(time.perf_counter() - t0)
            calls += 1
            if r.status_code != 200:
                errors += 1
                continue
            symbols = [i["symbol"] for i in r.json().get("items", [])][:12]
            for sym in symbols:
                for path, params in (
                    ("/v1/state", {"symbol": sym, "timeframe": "H1"}),
                    ("/v1/metrics", {"symbol": sym, "timeframe": "H1"}),
                ):
                    t0 = time.perf_counter()
                    rr = client.get(path, params=params)
                    latencies.append(time.perf_counter() - t0)
                    calls += 1
                    if rr.status_code not in (200, 404):
                        errors += 1

            t0 = time.perf_counter()
            m = client.get("/metrics")
            latencies.append(time.perf_counter() - t0)
            calls += 1
            if m.status_code != 200:
                errors += 1

    if not latencies:
        print("no samples")
        return 1
    p95 = sorted(latencies)[max(0, int(len(latencies) * 0.95) - 1)]
    print(
        f"calls={calls} errors={errors} "
        f"mean_ms={statistics.mean(latencies)*1000:.1f} "
        f"p95_ms={p95*1000:.1f} max_ms={max(latencies)*1000:.1f}"
    )
    err_rate = errors / calls if calls else 1.0
    return 1 if err_rate > 0.1 else 0


if __name__ == "__main__":
    sys.exit(main())
