"""Markdown / text chunker.

Strategy (in order of preference):
1. If text has "Speaker N:" markers (diarized transcripts), group consecutive
   turns up to chunk_size — never cut mid-turn.
2. Otherwise split on paragraph > sentence > word boundaries.

Background reading:
- Optimal chunk size for mixed factual+contextual queries: 400-800 tokens
  (arXiv 2505.21700v2; Jina late-chunking 2409.04701)
- ~15% overlap preserves cross-boundary context without too much duplication
- Semantic boundaries beat fixed-size cuts by ~5-10% nDCG
"""

from __future__ import annotations

import logging
import re
from typing import Optional

from ..config import get_settings

logger = logging.getLogger(__name__)

_SPEAKER_TURN_RE = re.compile(r"(?m)^\s*Speaker\s+\d+\s*:\s*")


def chunk_text(
    text: str,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[str]:
    """Split text into chunks of ~chunk_size chars with overlap.

    Returns a single-element list for short documents (≤ min_chars_for_chunking).
    """
    settings = get_settings()
    chunk_size = chunk_size or settings.chunk_size_chars
    overlap = overlap if overlap is not None else settings.chunk_overlap_chars
    min_chars = settings.min_chars_for_chunking

    if not text or not text.strip():
        return []
    text = text.strip()
    if len(text) <= min_chars:
        return [text]

    if _SPEAKER_TURN_RE.search(text):
        speaker_chunks = _chunk_by_speaker_turns(text, chunk_size, overlap)
        if speaker_chunks:
            logger.info(
                "[chunker] %d chars → %d speaker-aware chunks",
                len(text),
                len(speaker_chunks),
            )
            return speaker_chunks

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        if current and len(current) + len(para) + 2 > chunk_size:
            chunks.append(current.strip())
            if overlap > 0 and len(current) > overlap:
                current = current[-overlap:] + "\n\n" + para
            else:
                current = para
        else:
            current = (current + "\n\n" + para) if current else para

        while len(current) > chunk_size * 1.5:
            split = _find_split_point(current, chunk_size)
            chunks.append(current[:split].strip())
            remainder = current[split:].strip()
            if overlap > 0:
                tail = current[max(0, split - overlap) : split]
                current = tail + " " + remainder
            else:
                current = remainder

    if current.strip():
        chunks.append(current.strip())

    # Merge stragglers (<50 chars) into the previous chunk
    merged: list[str] = []
    for c in chunks:
        if len(c) < 50 and merged:
            merged[-1] += "\n\n" + c
        else:
            merged.append(c)

    logger.info("[chunker] %d chars → %d chunks", len(text), len(merged))
    return merged


def _chunk_by_speaker_turns(text: str, chunk_size: int, overlap: int) -> list[str]:
    matches = list(_SPEAKER_TURN_RE.finditer(text))
    if not matches:
        return []

    turns: list[str] = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        turn = text[m.start() : end].strip()
        if turn:
            turns.append(turn)
    if not turns:
        return []

    chunks: list[str] = []
    current = ""
    soft_limit = int(chunk_size * 1.5)
    for turn in turns:
        if len(turn) > soft_limit:
            if current:
                chunks.append(current.strip())
                current = ""
            chunks.extend(chunk_text(turn, chunk_size=chunk_size, overlap=overlap))
            continue

        prospective = (current + "\n\n" + turn) if current else turn
        if len(prospective) > chunk_size and current:
            chunks.append(current.strip())
            # No char-slice overlap at speaker boundaries: each chunk starts
            # cleanly with a "Speaker N:" marker — better signal for the embedder.
            current = turn
        else:
            current = prospective

    if current.strip():
        chunks.append(current.strip())
    return chunks


def _find_split_point(text: str, target: int) -> int:
    for pat in ("\n\n", "\n"):
        pos = text.rfind(pat, target - 200, target + 200)
        if pos > 0:
            return pos + len(pat)
    for pat in (". ", "! ", "? ", ".\n", "!\n", "?\n"):
        pos = text.rfind(pat, target - 300, target + 100)
        if pos > 0:
            return pos + len(pat)
    pos = text.rfind(" ", target - 100, target + 100)
    if pos > 0:
        return pos + 1
    return target


def extract_section_heading(chunk: str) -> Optional[str]:
    for line in chunk.split("\n"):
        s = line.strip()
        if s.startswith("#"):
            return s.lstrip("#").strip()
    return None


def build_contextual_prefix(
    *,
    title: Optional[str] = None,
    folder: Optional[str] = None,
    chunk_index: int = 0,
    total_chunks: int = 1,
    section: Optional[str] = None,
) -> str:
    """Lightweight metadata prefix prepended to a chunk before embedding.

    Improves retrieval recall by anchoring chunks to their document context.
    """
    parts = []
    if total_chunks > 1:
        parts.append(f"This is chunk {chunk_index + 1} of {total_chunks}")
    if title:
        parts.append(f"from the note '{title}'")
    if folder:
        parts.append(f"Folder: {folder}")
    if section:
        parts.append(f"Section: {section}")
    if not parts:
        return ""
    return ". ".join(parts) + ".\n\n"
