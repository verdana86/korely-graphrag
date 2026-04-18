"""Provider abstraction for LLM + embedding calls.

OSS scope: only Gemini is implemented day-1. Ollama is on the roadmap.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class CompletionResult:
    text: str
    prompt_tokens: int = 0
    completion_tokens: int = 0


class BaseProvider(ABC):
    @abstractmethod
    def complete(
        self,
        *,
        system: str,
        user: str,
        max_tokens: int = 2048,
        temperature: float = 0.2,
        json_mode: bool = False,
    ) -> CompletionResult: ...

    @abstractmethod
    def embed(self, text: str) -> list[float]: ...

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]: ...


def get_provider() -> BaseProvider:
    """Factory: instantiate the provider configured in settings."""
    from ..config import get_settings

    settings = get_settings()
    if settings.llm_provider == "gemini":
        from .gemini import GeminiProvider

        return GeminiProvider()
    raise ValueError(
        f"Unsupported LLM_PROVIDER='{settings.llm_provider}'. "
        f"Day-1 supports only 'gemini'. Ollama is on the roadmap."
    )
