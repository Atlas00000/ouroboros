"""W6·D5: quant-platform consumer smoke — API pull + Streams subscribe/ack/replay."""

from __future__ import annotations

import os
import sys
from uuid import uuid4

os.chdir(os.path.dirname(__file__))
sys.path.insert(0, os.getcwd())

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.auth.api_keys import BootstrapKey, upsert_bootstrap_keys
from app.config import get_settings
from app.db.session import get_session_factory
from app.events.relay import (
    CONSUMER_GROUP,
    STREAM_KEY,
    ack,
    get_redis,
    read_group,
    relay_unpublished,
)
from app.main import app
from app.models.outbox import OutboxMessage


def main() -> int:
    os.environ.setdefault("OUROBOROS_API_KEY_QUANT", "smoke-quant-key")
    os.environ["CLERK_JWKS_URL"] = ""
    get_settings.cache_clear()
    settings = get_settings()
    raw = settings.ouroboros_api_key_quant or "smoke-quant-key"

    session = get_session_factory()()
    try:
        upsert_bootstrap_keys(
            session,
            [BootstrapKey(name="quant", service_name="quant", raw_key=raw, role="viewer")],
        )
        event_id = str(uuid4())
        session.add(
            OutboxMessage(
                event_id=event_id,
                event="regime.changed",
                payload_json=(
                    '{"schema_id":"events.v1","event":"regime.changed","event_id":"%s"}'
                    % event_id
                ),
            )
        )
        session.commit()
        published = relay_unpublished(session)
        session.commit()
        print(f"relay published={published.published} failed={published.failed}")
    finally:
        session.close()

    client = TestClient(app)
    headers = {"X-API-Key": raw}
    for path in (
        "/v1/assets",
        "/v1/metrics?symbol=EURUSD&timeframe=H1",
        "/v1/state?symbol=EURUSD&timeframe=H1",
        "/v1/news?limit=5",
    ):
        res = client.get(path, headers=headers)
        print(f"GET {path.split('?')[0]} -> {res.status_code}")

    r = get_redis()
    # First read
    msgs = read_group(consumer="quant-smoke", count=20, block_ms=500, client=r)
    print(f"stream read count={len(msgs)} group={CONSUMER_GROUP} key={STREAM_KEY}")
    ids = [m[0] for m in msgs]
    if ids:
        n = ack(ids, client=r)
        print(f"acked={n}")
    # Replay check: pending should be empty for this consumer after ack;
    # new '>' read returns only newer — simulate disconnect by reading again
    again = read_group(consumer="quant-smoke", count=5, block_ms=200, client=r)
    print(f"after-ack new messages={len(again)} (expect 0 unless more published)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
