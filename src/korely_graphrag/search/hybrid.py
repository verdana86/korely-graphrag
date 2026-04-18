"""Hybrid search: FTS + pgvector cosine, merged with Reciprocal Rank Fusion.

Returns a ranked list of `SearchHit` dicts at the *item* level (not chunk).
Per-item score is the best score across that item's chunks.

RRF reference:
    Cormack et al. 2009. "Reciprocal rank fusion outperforms Condorcet and
    individual rank learning methods." SIGIR.
    score_RRF(d) = sum over systems s of 1 / (k + rank_s(d))
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import bindparam, func, select, text
from sqlalchemy.orm import Session

from ..ingest.embedder import embed_one
from ..providers.base import BaseProvider
from ..storage.models import Chunk, Item

logger = logging.getLogger(__name__)

RRF_K = 60


@dataclass
class SearchHit:
    item_id: str
    title: str
    folder: str | None
    snippet: str
    score: float

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "title": self.title,
            "folder": self.folder,
            "snippet": self.snippet,
            "score": round(self.score, 6),
        }


def _fts_chunk_ranking(session: Session, query: str, limit: int) -> list[tuple[str, str, int]]:
    """Return [(chunk_id, item_id, rank)] from FTS, best rank first."""
    if not query.strip():
        return []
    # Build a tsquery: split on whitespace, AND-join with prefix matching.
    # 'simple' config matches our generated column.
    terms = [w for w in query.split() if w.strip()]
    if not terms:
        return []
    tsquery = " & ".join(f"{w}:*" for w in terms)
    rows = session.execute(
        text(
            "SELECT id::text, item_id::text "
            "FROM chunks "
            "WHERE fts @@ to_tsquery('simple', :q) "
            "ORDER BY ts_rank(fts, to_tsquery('simple', :q)) DESC "
            "LIMIT :lim"
        ).bindparams(bindparam("q", value=tsquery), bindparam("lim", value=limit * 3)),
    ).all()
    return [(r[0], r[1], idx + 1) for idx, r in enumerate(rows)]


def _vector_chunk_ranking(
    session: Session, query_embedding: list[float], limit: int
) -> list[tuple[str, str, int]]:
    """Return [(chunk_id, item_id, rank)] from cosine vector search, best first."""
    rows = session.execute(
        text(
            "SELECT id::text, item_id::text "
            "FROM chunks "
            "WHERE embedding IS NOT NULL "
            "ORDER BY embedding <=> CAST(:emb AS vector) "
            "LIMIT :lim"
        ).bindparams(bindparam("emb", value=str(query_embedding)), bindparam("lim", value=limit * 3)),
    ).all()
    return [(r[0], r[1], idx + 1) for idx, r in enumerate(rows)]


def _rrf_merge(rankings: Iterable[list[tuple[str, str, int]]]) -> dict[str, tuple[str, float]]:
    """Reciprocal Rank Fusion at the item level.

    Returns: {item_id: (best_chunk_id, rrf_score)}.
    For each item, we keep only the chunk with the highest RRF contribution.
    """
    # First, accumulate RRF score per chunk
    chunk_score: dict[str, float] = {}
    chunk_to_item: dict[str, str] = {}
    for ranking in rankings:
        for chunk_id, item_id, rank in ranking:
            chunk_score[chunk_id] = chunk_score.get(chunk_id, 0.0) + 1.0 / (RRF_K + rank)
            chunk_to_item[chunk_id] = item_id

    # Then collapse to item level: keep the best chunk per item
    item_best: dict[str, tuple[str, float]] = {}
    for chunk_id, score in chunk_score.items():
        item_id = chunk_to_item[chunk_id]
        existing = item_best.get(item_id)
        if existing is None or score > existing[1]:
            item_best[item_id] = (chunk_id, score)
    return item_best


def hybrid_search(
    query: str,
    *,
    session: Session,
    limit: int = 10,
    provider: BaseProvider | None = None,
) -> list[SearchHit]:
    """Run FTS + vector search and merge with RRF. Return top `limit` items."""
    if not query or not query.strip():
        return []

    query = query.strip()
    fts_ranking = _fts_chunk_ranking(session, query, limit)

    try:
        query_emb = embed_one(query, provider=provider)
        vec_ranking = _vector_chunk_ranking(session, query_emb, limit)
    except Exception as e:
        logger.warning("[hybrid_search] vector path failed (%s); falling back to FTS only", e)
        vec_ranking = []

    if not fts_ranking and not vec_ranking:
        return []

    item_best = _rrf_merge([fts_ranking, vec_ranking])
    if not item_best:
        return []

    # Sort by RRF score desc, take top N
    sorted_items = sorted(item_best.items(), key=lambda kv: kv[1][1], reverse=True)[:limit]
    item_ids = [iid for iid, _ in sorted_items]
    chunk_ids = [chunk_id for _, (chunk_id, _) in sorted_items]

    # Fetch items + the snippet chunk in two queries
    items_rows = session.execute(
        select(Item.id, Item.title, Item.folder).where(Item.id.in_(item_ids))
    ).all()
    items_map = {str(r.id): (r.title, r.folder) for r in items_rows}
    chunks_rows = session.execute(select(Chunk.id, Chunk.text).where(Chunk.id.in_(chunk_ids))).all()
    chunks_map = {str(r.id): r.text for r in chunks_rows}

    hits: list[SearchHit] = []
    for item_id, (chunk_id, score) in sorted_items:
        title, folder = items_map.get(item_id, ("(unknown)", None))
        snippet = (chunks_map.get(chunk_id) or "")[:240]
        hits.append(SearchHit(item_id=item_id, title=title, folder=folder, snippet=snippet, score=score))
    return hits
