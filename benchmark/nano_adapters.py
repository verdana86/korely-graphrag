"""Gemini adapters for nano-graphrag.

nano-graphrag ships with OpenAI / Azure / Bedrock LLM hooks but no Gemini
support. This module provides async `complete` and `embed` functions in
the shape nano-graphrag expects, so we can benchmark it apples-to-apples
against korely-graphrag (which also uses Gemini).

Shared by ingest_nano.py and the run_benchmark.py extension.
"""

from __future__ import annotations

import asyncio
import os
from typing import Any

import json_repair
import numpy as np
from google import genai
from google.genai import types as genai_types
from nano_graphrag._utils import wrap_embedding_func_with_attrs


GEMINI_MODEL = os.environ.get("NANO_GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_EMBED_MODEL = os.environ.get("NANO_GEMINI_EMBED_MODEL", "gemini-embedding-001")
EMBED_DIM = 1536

# Single shared client (google-genai is thread-safe and async-friendly)
_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


async def gemini_complete(
    prompt: str,
    system_prompt: str | None = None,
    history_messages: list[dict[str, str]] | None = None,
    **kwargs: Any,
) -> str:
    """Async LLM function nano-graphrag plugs into `best_model_func` /
    `cheap_model_func`. Returns a plain string; JSON parsing (when the
    caller passes response_format) is delegated to nano-graphrag's
    `convert_response_to_json_func` which we wire to json_repair.
    """
    # nano-graphrag sometimes passes `hashing_kv` and `response_format`
    # that Gemini doesn't understand — swallow them.
    kwargs.pop("hashing_kv", None)
    kwargs.pop("response_format", None)

    contents: list[genai_types.Content] = []
    for msg in history_messages or []:
        role = "user" if msg.get("role") == "user" else "model"
        contents.append(
            genai_types.Content(role=role, parts=[genai_types.Part(text=msg.get("content", ""))])
        )
    contents.append(genai_types.Content(role="user", parts=[genai_types.Part(text=prompt)]))

    config = genai_types.GenerateContentConfig(
        system_instruction=system_prompt or None,
        max_output_tokens=kwargs.get("max_tokens", 4096),
        temperature=kwargs.get("temperature", 0.2),
    )

    # google-genai is sync-only in its generate_content; run in thread
    def _call() -> str:
        resp = _client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=config,
        )
        return resp.text or ""

    return await asyncio.to_thread(_call)


def repair_json(raw: str) -> dict | list | None:
    """Tolerant JSON loader for Gemini outputs.

    nano-graphrag hands the raw LLM output to `convert_response_to_json_func`
    after stripping code fences. Gemini occasionally emits trailing commas /
    unclosed objects under pressure; json_repair fixes the common cases.
    """
    try:
        return json_repair.loads(raw)
    except Exception:
        return {}


@wrap_embedding_func_with_attrs(embedding_dim=EMBED_DIM, max_token_size=2048)
async def gemini_embed(texts: list[str]) -> np.ndarray:
    """Batch embedding via Gemini. Returns (N, 1536) numpy array.

    gemini-embedding-001 is 1536d by default, matching nano-graphrag's
    default vector dimension — no projection needed.
    """
    def _call() -> np.ndarray:
        resp = _client.models.embed_content(
            model=GEMINI_EMBED_MODEL,
            contents=texts,
            config=genai_types.EmbedContentConfig(output_dimensionality=EMBED_DIM),
        )
        arr = np.array([e.values for e in resp.embeddings], dtype=np.float32)
        return arr

    return await asyncio.to_thread(_call)
