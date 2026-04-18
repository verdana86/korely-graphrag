"""Embedding generation — thin wrapper around the configured provider."""

from __future__ import annotations

import logging

from ..providers.base import BaseProvider, get_provider

logger = logging.getLogger(__name__)


def embed_one(text: str, provider: BaseProvider | None = None) -> list[float]:
    provider = provider or get_provider()
    return provider.embed(text)


def embed_many(texts: list[str], provider: BaseProvider | None = None, batch_size: int = 32) -> list[list[float]]:
    """Embed in batches to respect provider limits.

    Gemini accepts up to ~100 inputs per call; we default to 32 to stay safe
    and to surface partial-failure modes earlier.
    """
    if not texts:
        return []
    provider = provider or get_provider()
    out: list[list[float]] = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        out.extend(provider.embed_batch(batch))
        logger.info("[embedder] embedded %d/%d", min(start + batch_size, len(texts)), len(texts))
    return out
