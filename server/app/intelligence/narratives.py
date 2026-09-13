"""Deterministic inputs → labeled narrative insights (W7·D4).

Generative tier only — never writes metrics, regimes, prices, or other numeric
analytics tables. Output is always ``type: narrative`` with disclaimer.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal

from contracts.common_v1 import Disclaimer, Provenance
from contracts.insight_v1 import Insight
from contracts.sentiment_v1 import SentimentSnapshot
from contracts.state_v1 import MarketState
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.calendar.timebase import ensure_utc
from app.intelligence.llm_client import (
    LLMClient,
    MODEL_VERSION as LLM_MODEL_VERSION,
    extract_json_object,
)
from app.intelligence.sentiment import latest_sentiment_row, sentiment_from_row
from app.models.insight import InsightRow
from app.models.state import MarketStateRow

logger = logging.getLogger(__name__)

NARRATIVE_MODEL_VERSION = "insight.narrative.v1"
DISCLAIMER = Disclaimer()


@dataclass
class NarrativeTickReport:
    generated: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


def _template_narrative(
    symbol: str,
    *,
    regime: str | None,
    vol_pct: float | None,
    sentiment_score: float | None,
) -> tuple[str, str, list[str]]:
    regime_txt = regime or "unknown"
    vol_txt = f"{vol_pct:.0f}th pct" if vol_pct is not None else "n/a"
    sent_txt = f"{sentiment_score:+.2f}" if sentiment_score is not None else "n/a"
    title = f"{symbol}: {regime_txt.replace('_', ' ')} context"
    body = (
        f"{symbol} is currently classified as {regime_txt.replace('_', ' ')} "
        f"with realized volatility near the {vol_txt} of its recent window. "
        f"News sentiment over the last 24h is {sent_txt} on a [-1, +1] scale. "
        "This narrative summarizes deterministic analytics only and is not a trade signal."
    )
    tags = ["narrative", "auto", regime_txt]
    return title, body, tags


def build_narrative_insight(
    symbol: str,
    *,
    state: MarketState | None,
    sentiment: SentimentSnapshot | None,
    client: LLMClient | None = None,
    now: datetime | None = None,
) -> Insight:
    """Produce a labeled Insight. Never mutates numeric analytics state."""
    now = ensure_utc(now or datetime.now(UTC))
    client = client or LLMClient()
    regime = state.regime if state else None
    vol = state.volatility_percentile if state else None
    sent = sentiment.score if sentiment else None
    refs: list[str] = []
    if state:
        refs.append(f"state:{state.symbol}:{state.timeframe}:{state.provenance.model_version}")
    if sentiment:
        refs.append(f"sentiment:{sentiment.symbol}:{sentiment.provenance.model_version}")

    title, body, tags = _template_narrative(
        symbol.upper(),
        regime=regime,
        vol_pct=vol,
        sentiment_score=sent,
    )
    provider = "mock"
    model = "template"

    # Prefer LLM when a non-mock provider is configured; fall back to template.
    chain = client.provider_chain()
    if chain and chain[0] != "mock":
        system = (
            "You write concise market research narratives for an internal intelligence "
            "platform. Reply with JSON only: {\"title\": str, \"body\": str, \"tags\": [str]}. "
            "Do not invent numbers; use only the facts provided. Not investment advice."
        )
        prompt = (
            f"Symbol: {symbol.upper()}\n"
            f"Regime: {regime}\n"
            f"Volatility percentile: {vol}\n"
            f"Sentiment score: {sent}\n"
            f"Sentiment drivers: "
            f"{[d.title for d in (sentiment.top_drivers if sentiment else [])][:3]}\n"
        )
        try:
            resp = client.complete(prompt, system=system, max_tokens=400, temperature=0.3)
            data = extract_json_object(resp.text)
            title = str(data.get("title") or title)[:256]
            body = str(data.get("body") or body)
            raw_tags = data.get("tags")
            if isinstance(raw_tags, list) and raw_tags:
                tags = [str(t) for t in raw_tags][:12]
            provider = resp.provider
            model = resp.model
        except Exception as exc:  # noqa: BLE001
            logger.info("narrative_llm_fallback symbol=%s err=%s", symbol, exc)

    return Insight(
        type="narrative",
        symbol=symbol.upper(),
        title=title,
        body=body,
        tags=tags,
        related_refs=refs,
        as_of=now,
        provenance=Provenance(
            sources=["analytics.state", "sentiment.v1", f"llm:{provider}:{model}"],
            generated_at=now,
            model_version=NARRATIVE_MODEL_VERSION,
            confidence=0.6 if provider != "mock" else 0.5,
            stale=False,
        ),
        disclaimer=DISCLAIMER,
    )


def persist_insight(session: Session, insight: Insight) -> InsightRow:
    """Write InsightRow only — never touches numeric analytics tables."""
    row = InsightRow(
        symbol=insight.symbol,
        insight_type=insight.type,
        title=insight.title,
        body=insight.body,
        tags_json=json.dumps(insight.tags),
        related_refs_json=json.dumps(insight.related_refs),
        as_of=ensure_utc(insight.as_of),
        model_version=insight.provenance.model_version,
        confidence=Decimal(str(round(insight.provenance.confidence, 4))),
        stale=bool(insight.provenance.stale),
        sources_json=json.dumps(insight.provenance.sources),
    )
    session.add(row)
    session.flush()
    return row


def insight_from_row(row: InsightRow) -> Insight:
    return Insight(
        type="narrative",  # type: ignore[arg-type]
        symbol=row.symbol,
        title=row.title,
        body=row.body,
        tags=json.loads(row.tags_json) if row.tags_json else [],
        related_refs=json.loads(row.related_refs_json) if row.related_refs_json else [],
        as_of=ensure_utc(row.as_of),
        provenance=Provenance(
            sources=json.loads(row.sources_json) if row.sources_json else [row.model_version],
            generated_at=ensure_utc(row.created_at),
            model_version=row.model_version,
            confidence=float(row.confidence),
            stale=bool(row.stale),
        ),
        disclaimer=DISCLAIMER,
    )


def latest_insight_row(session: Session, symbol: str) -> InsightRow | None:
    sym = symbol.upper()
    return session.scalar(
        select(InsightRow)
        .where(InsightRow.symbol == sym, InsightRow.insight_type == "narrative")
        .order_by(InsightRow.as_of.desc(), InsightRow.id.desc())
        .limit(1)
    )


def run_narrative_tick(
    session: Session,
    symbols: list[str],
    *,
    client: LLMClient | None = None,
    commit: bool = True,
    timeframe: str = "H1",
) -> NarrativeTickReport:
    """Generate narratives for symbols that have a recent state row."""
    report = NarrativeTickReport()
    client = client or LLMClient()
    try:
        for sym in symbols:
            state_row = session.scalar(
                select(MarketStateRow)
                .where(MarketStateRow.symbol == sym.upper(), MarketStateRow.timeframe == timeframe)
                .order_by(MarketStateRow.as_of.desc(), MarketStateRow.id.desc())
                .limit(1)
            )
            if state_row is None:
                report.skipped += 1
                continue
            from app.analytics.state_store import market_state_from_row

            state = market_state_from_row(state_row)
            sent_row = latest_sentiment_row(session, sym)
            sentiment = sentiment_from_row(sent_row) if sent_row else None
            insight = build_narrative_insight(
                sym, state=state, sentiment=sentiment, client=client
            )
            # Guardrail: type must remain narrative
            if insight.type != "narrative":
                raise RuntimeError("narrative guardrail: type must be 'narrative'")
            persist_insight(session, insight)
            report.generated += 1
        if commit:
            session.commit()
        else:
            session.flush()
    except Exception as exc:  # noqa: BLE001
        report.errors.append(str(exc))
        if commit:
            session.rollback()
        logger.exception("narrative_tick_failed")
        raise
    return report
