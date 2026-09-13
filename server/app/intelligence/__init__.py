"""Intelligence package — generative tier (sentiment + narratives)."""

from app.intelligence.llm_client import MODEL_VERSION as LLM_MODEL_VERSION
from app.intelligence.llm_client import LLMClient

__all__ = ["LLMClient", "LLM_MODEL_VERSION"]
