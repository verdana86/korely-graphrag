"""Gemini provider — chat + embedding via google-genai SDK."""

from __future__ import annotations

import logging
import re
import time

from google import genai
from google.genai import errors as genai_errors
from google.genai import types as genai_types

from ..config import get_settings
from .base import BaseProvider, CompletionResult

logger = logging.getLogger(__name__)


def _retry_on_429(call, *, max_attempts: int = 6, base_delay: float = 4.0):
    """Retry callable on 429 RESOURCE_EXHAUSTED with exponential backoff.

    Free-tier Gemini quotas (esp. embeddings) are aggressive: 5 RPM is common.
    A simple exponential backoff (4s, 8s, 16s, 32s, 64s, 128s) makes ingestion
    succeed in the background without manual throttling.
    """
    delay = base_delay
    for attempt in range(1, max_attempts + 1):
        try:
            return call()
        except genai_errors.ClientError as e:
            status = getattr(e, "code", None) or 0
            msg = str(e)
            if status != 429 and "RESOURCE_EXHAUSTED" not in msg:
                raise
            if attempt == max_attempts:
                raise
            # If the error includes a retry hint, prefer it
            m = re.search(r"retry in\s+(\d+(?:\.\d+)?)s", msg, re.IGNORECASE)
            wait = float(m.group(1)) if m else delay
            logger.warning(
                "[gemini] 429 quota exhausted; sleeping %.1fs (attempt %d/%d)",
                wait, attempt, max_attempts,
            )
            time.sleep(wait)
            delay *= 2


class GeminiProvider(BaseProvider):
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Get a free key at https://aistudio.google.com "
                "and set it in your .env file."
            )
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._chat_model = settings.gemini_chat_model
        self._embed_model = settings.gemini_embedding_model

    def complete(
        self,
        *,
        system: str,
        user: str,
        max_tokens: int = 2048,
        temperature: float = 0.2,
        json_mode: bool = False,
    ) -> CompletionResult:
        config = genai_types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=max_tokens,
            temperature=temperature,
            response_mime_type="application/json" if json_mode else "text/plain",
        )
        resp = _retry_on_429(lambda: self._client.models.generate_content(
            model=self._chat_model,
            contents=user,
            config=config,
        ))
        usage = getattr(resp, "usage_metadata", None)
        return CompletionResult(
            text=resp.text or "",
            prompt_tokens=getattr(usage, "prompt_token_count", 0) or 0,
            completion_tokens=getattr(usage, "candidates_token_count", 0) or 0,
        )

    def embed(self, text: str) -> list[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        settings = get_settings()
        config = genai_types.EmbedContentConfig(output_dimensionality=settings.embedding_dim)
        resp = _retry_on_429(lambda: self._client.models.embed_content(
            model=self._embed_model,
            contents=texts,
            config=config,
        ))
        return [list(e.values) for e in resp.embeddings]
