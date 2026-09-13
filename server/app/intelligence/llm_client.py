"""Multi-model LLM client — OpenAI → Anthropic → Gemini → Groq (W7·D1).

No local/Ollama backend. Missing keys are skipped. On 429 / errors, try next
provider. Daily USD budget is shared across providers (Redis counter).
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Any

import httpx
import redis

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)

MODEL_VERSION = "llm.multi.v1"

# In-process spend fallback when Redis is unavailable (unit tests / offline).
_SPEND_FALLBACK: dict[str, float] = {}

# Cheap defaults for free/dev; override via LLM_MODEL / per-provider settings later.
DEFAULT_MODELS: dict[str, str] = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-5-haiku-latest",
    "gemini": "gemini-2.0-flash",
    "groq": "llama-3.1-8b-instant",
    "mock": "mock-heuristic-v1",
}

# Rough USD per 1M tokens (input/output blended) for budget accounting.
_COST_PER_1M: dict[str, float] = {
    "openai": 0.30,
    "anthropic": 0.50,
    "gemini": 0.10,
    "groq": 0.05,
    "mock": 0.0,
}


class BudgetExceededError(RuntimeError):
    pass


class LLMError(RuntimeError):
    pass


@dataclass(frozen=True)
class LLMResponse:
    text: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float


def _redis() -> redis.Redis:
    return redis.Redis.from_url(get_settings().redis_url, decode_responses=True)


def budget_key(day: date | None = None) -> str:
    d = day or datetime.now(UTC).date()
    return f"ouroboros:llm_spend:{d.isoformat()}"


def get_daily_spend_usd() -> float:
    key = budget_key()
    try:
        raw = _redis().get(key)
        return float(raw) if raw else 0.0
    except Exception:
        return float(_SPEND_FALLBACK.get(key, 0.0))


def record_spend(amount_usd: float) -> float:
    if amount_usd <= 0:
        return get_daily_spend_usd()
    key = budget_key()
    try:
        r = _redis()
        new_val = r.incrbyfloat(key, amount_usd)
        r.expire(key, 60 * 60 * 48)
        return float(new_val)
    except Exception:
        _SPEND_FALLBACK[key] = float(_SPEND_FALLBACK.get(key, 0.0)) + amount_usd
        return float(_SPEND_FALLBACK[key])


def reset_spend_fallback() -> None:
    """Test helper — clear in-process and Redis daily spend counters."""
    _SPEND_FALLBACK.clear()
    try:
        _redis().delete(budget_key())
    except Exception:
        pass


def _estimate_cost(provider: str, in_tok: int, out_tok: int) -> float:
    rate = _COST_PER_1M.get(provider, 0.5)
    return (in_tok + out_tok) / 1_000_000.0 * rate


def heuristic_sentiment_score(headline: str) -> float:
    """Deterministic fallback / mock scorer in [-1, 1]."""
    text = headline.lower()
    pos = sum(
        1
        for w in (
            "rally",
            "surge",
            "gain",
            "beat",
            "growth",
            "hawkish",
            "strong",
            "upbeat",
            "optimism",
            "record high",
        )
        if w in text
    )
    neg = sum(
        1
        for w in (
            "crash",
            "plunge",
            "fear",
            "war",
            "recession",
            "miss",
            "weak",
            "dovish",
            "selloff",
            "default",
            "cut",
        )
        if w in text
    )
    raw = (pos - neg) / max(pos + neg, 1)
    # Mild non-zero from length hash so neutrals aren't always 0
    if pos == neg == 0:
        raw = ((sum(ord(c) for c in text) % 21) - 10) / 50.0
    return float(max(-1.0, min(1.0, raw)))


def _parse_score_from_text(text: str) -> float | None:
    m = re.search(r"-?\d+(?:\.\d+)?", text)
    if not m:
        return None
    val = float(m.group(0))
    if abs(val) > 1.0 and abs(val) <= 100:
        val = val / 100.0
    return float(max(-1.0, min(1.0, val)))


class LLMClient:
    """Ordered multi-provider client."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def provider_chain(self) -> list[str]:
        raw = (self.settings.llm_providers or self.settings.llm_provider or "mock").strip()
        names = [p.strip().lower() for p in raw.split(",") if p.strip()]
        # Always allow mock last for local/tests when nothing else is configured
        configured = [p for p in names if self._has_key(p)]
        if not configured:
            return ["mock"]
        return configured

    def _has_key(self, provider: str) -> bool:
        if provider == "mock":
            return True
        s = self.settings
        return {
            "openai": bool(s.openai_api_key),
            "anthropic": bool(s.anthropic_api_key),
            "gemini": bool(s.gemini_api_key),
            "groq": bool(s.groq_api_key),
        }.get(provider, False)

    def _model_for(self, provider: str) -> str:
        if self.settings.llm_model and provider == (self.settings.llm_provider or "").lower():
            return self.settings.llm_model
        if self.settings.llm_fallback_model and provider != (self.settings.llm_provider or "").lower():
            return self.settings.llm_fallback_model
        return DEFAULT_MODELS.get(provider, "unknown")

    def complete(
        self,
        prompt: str,
        *,
        system: str | None = None,
        max_tokens: int = 256,
        temperature: float = 0.2,
    ) -> LLMResponse:
        budget = float(self.settings.llm_daily_budget_usd)
        spent = get_daily_spend_usd()
        if spent >= budget:
            raise BudgetExceededError(f"daily LLM budget ${budget:.2f} exhausted (spent ${spent:.4f})")

        errors: list[str] = []
        for provider in self.provider_chain():
            model = self._model_for(provider)
            try:
                resp = self._call_provider(
                    provider,
                    model=model,
                    prompt=prompt,
                    system=system,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                new_spend = record_spend(resp.estimated_cost_usd)
                if new_spend > budget:
                    logger.warning("llm_budget_crossed spend=%.4f budget=%.2f", new_spend, budget)
                return resp
            except BudgetExceededError:
                raise
            except Exception as exc:  # noqa: BLE001
                msg = f"{provider}: {exc}"
                errors.append(msg)
                logger.info("llm_provider_failed %s", msg)
                continue
        raise LLMError("; ".join(errors) or "no LLM providers available")

    def score_headline(self, headline: str, *, symbol: str | None = None) -> tuple[float, LLMResponse]:
        """Return sentiment in [-1,1] plus raw LLM response metadata."""
        system = (
            "You score financial news sentiment for FX/metals/indices. "
            "Reply with ONLY a number in [-1,1]. Negative=bearish, positive=bullish."
        )
        prompt = f"Symbol: {symbol or 'N/A'}\nHeadline: {headline}\nScore:"
        # Prefer mock/heuristic path when only mock is configured — still goes through complete()
        resp = self.complete(prompt, system=system, max_tokens=16, temperature=0.0)
        if resp.provider == "mock":
            return heuristic_sentiment_score(headline), resp
        parsed = _parse_score_from_text(resp.text)
        if parsed is None:
            return heuristic_sentiment_score(headline), resp
        return parsed, resp

    def _call_provider(
        self,
        provider: str,
        *,
        model: str,
        prompt: str,
        system: str | None,
        max_tokens: int,
        temperature: float,
    ) -> LLMResponse:
        if provider == "mock":
            text = str(heuristic_sentiment_score(prompt))
            return LLMResponse(
                text=text,
                provider="mock",
                model=model,
                input_tokens=len(prompt.split()),
                output_tokens=1,
                estimated_cost_usd=0.0,
            )
        if provider in ("openai", "groq"):
            return self._openai_compatible(
                provider,
                model=model,
                prompt=prompt,
                system=system,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        if provider == "anthropic":
            return self._anthropic(
                model=model,
                prompt=prompt,
                system=system,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        if provider == "gemini":
            return self._gemini(
                model=model,
                prompt=prompt,
                system=system,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        raise LLMError(f"unknown provider {provider}")

    def _openai_compatible(
        self,
        provider: str,
        *,
        model: str,
        prompt: str,
        system: str | None,
        max_tokens: int,
        temperature: float,
    ) -> LLMResponse:
        if provider == "openai":
            url = "https://api.openai.com/v1/chat/completions"
            key = self.settings.openai_api_key
        else:
            url = "https://api.groq.com/openai/v1/chat/completions"
            key = self.settings.groq_api_key
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        body = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        with httpx.Client(timeout=45.0) as client:
            r = client.post(url, headers=headers, json=body)
            if r.status_code == 429:
                raise LLMError("rate limited (429)")
            r.raise_for_status()
            data = r.json()
        text = data["choices"][0]["message"]["content"]
        usage = data.get("usage") or {}
        in_t = int(usage.get("prompt_tokens") or 0)
        out_t = int(usage.get("completion_tokens") or 0)
        return LLMResponse(
            text=str(text).strip(),
            provider=provider,
            model=model,
            input_tokens=in_t,
            output_tokens=out_t,
            estimated_cost_usd=_estimate_cost(provider, in_t, out_t),
        )

    def _anthropic(
        self,
        *,
        model: str,
        prompt: str,
        system: str | None,
        max_tokens: int,
        temperature: float,
    ) -> LLMResponse:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.settings.anthropic_api_key or "",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        body: dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            body["system"] = system
        with httpx.Client(timeout=45.0) as client:
            r = client.post(url, headers=headers, json=body)
            if r.status_code == 429:
                raise LLMError("rate limited (429)")
            r.raise_for_status()
            data = r.json()
        parts = data.get("content") or []
        text = "".join(p.get("text", "") for p in parts if isinstance(p, dict))
        usage = data.get("usage") or {}
        in_t = int(usage.get("input_tokens") or 0)
        out_t = int(usage.get("output_tokens") or 0)
        return LLMResponse(
            text=text.strip(),
            provider="anthropic",
            model=model,
            input_tokens=in_t,
            output_tokens=out_t,
            estimated_cost_usd=_estimate_cost("anthropic", in_t, out_t),
        )

    def _gemini(
        self,
        *,
        model: str,
        prompt: str,
        system: str | None,
        max_tokens: int,
        temperature: float,
    ) -> LLMResponse:
        key = self.settings.gemini_api_key
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            f"?key={key}"
        )
        full = f"{system}\n\n{prompt}" if system else prompt
        body = {
            "contents": [{"parts": [{"text": full}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
            },
        }
        with httpx.Client(timeout=45.0) as client:
            r = client.post(url, json=body)
            if r.status_code == 429:
                raise LLMError("rate limited (429)")
            r.raise_for_status()
            data = r.json()
        cands = data.get("candidates") or []
        text = ""
        if cands:
            parts = (cands[0].get("content") or {}).get("parts") or []
            text = "".join(p.get("text", "") for p in parts if isinstance(p, dict))
        # Gemini usage metadata optional
        usage = data.get("usageMetadata") or {}
        in_t = int(usage.get("promptTokenCount") or 0)
        out_t = int(usage.get("candidatesTokenCount") or 0)
        return LLMResponse(
            text=text.strip(),
            provider="gemini",
            model=model,
            input_tokens=in_t,
            output_tokens=out_t,
            estimated_cost_usd=_estimate_cost("gemini", in_t, out_t),
        )


def extract_json_object(text: str) -> dict[str, Any]:
    """Best-effort JSON object parse from model output."""
    text = text.strip()
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        raise LLMError("no JSON object in model output")
    data = json.loads(m.group(0))
    if not isinstance(data, dict):
        raise LLMError("JSON root is not an object")
    return data
