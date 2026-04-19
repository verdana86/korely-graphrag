"""Graph traversal: find items related to a given item via shared entities.

This is the killer feature vs vanilla RAG — it surfaces *non-keyword*
connections (two notes that mention the same people/concepts/technologies
but never share a search term).
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session


@dataclass
class RelatedHit:
    item_id: str
    title: str
    folder: str | None
    score: float
    shared_entities: list[str]
    source: str = "graph"  # "graph" (entity-overlap) or "semantic" (embedding fallback)

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "title": self.title,
            "folder": self.folder,
            "score": round(self.score, 6),
            "shared_entities": self.shared_entities,
            "source": self.source,
        }


_RELATED_SQL = text("""
WITH total AS (
    SELECT GREATEST(COUNT(*), 1)::float AS n FROM items
),
entity_doc_freq AS (
    SELECT m.entity_id,
           COUNT(DISTINCT c.item_id)::float AS doc_count
    FROM mentions m
    JOIN chunks c ON c.id = m.chunk_id
    GROUP BY m.entity_id
),
useful_entities AS (
    -- Defense-in-depth hard filter. Truly ubiquitous entities (in >threshold of
    -- items — e.g. filter tools mentioned in every doc) get dropped outright.
    -- Semi-ubiquitous entities are handled by the IDF weighting below.
    SELECT edf.entity_id
    FROM entity_doc_freq edf, total t
    WHERE edf.doc_count <= GREATEST(2.0, :ubiquity_threshold * t.n)
),
source_entities AS (
    SELECT DISTINCT m.entity_id, MAX(m.importance) AS src_imp
    FROM mentions m
    JOIN chunks c ON c.id = m.chunk_id
    JOIN useful_entities ue ON ue.entity_id = m.entity_id
    WHERE c.item_id = :item_id
    GROUP BY m.entity_id
),
candidate_chunks AS (
    SELECT c.item_id,
           m.entity_id,
           m.importance AS cand_imp,
           se.src_imp
    FROM chunks c
    JOIN mentions m ON m.chunk_id = c.id
    JOIN source_entities se ON se.entity_id = m.entity_id
    WHERE c.item_id <> :item_id
),
scored AS (
    -- IDF-weighted scoring: shared entities present in many docs contribute
    -- proportionally less. IDF = ln(N / df), clamped at [0.1, 5.0] to avoid
    -- blow-ups on tiny corpora. A hub-like entity in 6/24 docs gets weight
    -- ln(4)=1.39 vs a rare entity in 1/24 getting ln(24)=3.18.
    SELECT cc.item_id,
           SUM(cc.src_imp * cc.cand_imp *
               GREATEST(0.1, LEAST(5.0, LN(t.n / GREATEST(1.0, edf.doc_count))))
           ) AS score,
           ARRAY_AGG(DISTINCT e.name ORDER BY e.name) AS shared_names
    FROM candidate_chunks cc
    JOIN entities e ON e.id = cc.entity_id
    JOIN entity_doc_freq edf ON edf.entity_id = cc.entity_id
    CROSS JOIN total t
    GROUP BY cc.item_id
)
SELECT s.item_id::text,
       i.title,
       i.folder,
       s.score,
       s.shared_names
FROM scored s
JOIN items i ON i.id = s.item_id
ORDER BY s.score DESC
LIMIT :lim
""")

# An entity is "ubiquitous" if it appears in >50% of all items. The floor of
# 2 docs ensures we don't filter everything in tiny corpora (e.g. 4 items).
DEFAULT_UBIQUITY_THRESHOLD = 0.5


_SEMANTIC_FALLBACK_SQL = text("""
    SELECT i.id::text, i.title, i.folder,
           1.0 - (i.embedding <=> CAST(:seed_emb AS vector)) AS cosine_sim
    FROM items i
    WHERE i.id <> :seed_id
      AND i.embedding IS NOT NULL
      AND i.id NOT IN :excluded_ids
    ORDER BY i.embedding <=> CAST(:seed_emb AS vector)
    LIMIT :lim
""")


def _semantic_fallback(
    seed_id: str,
    excluded_ids: set[str],
    *,
    session: Session,
    limit: int,
) -> list[RelatedHit]:
    """Fill remaining slots using pgvector similarity on item embeddings.

    Used when the entity graph returns fewer items than requested — typical
    for 'island' documents (short narratives with unique named entities that
    don't overlap with the rest of the corpus). Items are tagged `source='semantic'`
    so callers can distinguish graph-derived from embedding-derived links.
    """
    seed_emb_row = session.execute(
        text("SELECT embedding FROM items WHERE id = :id"),
        {"id": seed_id},
    ).first()
    if not seed_emb_row or seed_emb_row[0] is None:
        return []
    # psycopg2 returns pgvector as string "[...]" or list; ensure str
    seed_emb = seed_emb_row[0]
    if not isinstance(seed_emb, str):
        seed_emb = str(list(seed_emb))

    # Need at least one value for IN-clause — sentinel UUID when set is empty
    excluded_list = list(excluded_ids) or ["00000000-0000-0000-0000-000000000000"]

    rows = session.execute(
        _SEMANTIC_FALLBACK_SQL.bindparams(
            bindparam("seed_emb", value=seed_emb),
            bindparam("seed_id", value=seed_id),
            bindparam("excluded_ids", value=tuple(excluded_list), expanding=True),
            bindparam("lim", value=limit),
        )
    ).all()
    return [
        RelatedHit(
            item_id=r[0],
            title=r[1],
            folder=r[2],
            score=float(r[3]),
            shared_entities=[],
            source="semantic",
        )
        for r in rows
    ]


def get_related_items(
    item_id: str,
    *,
    session: Session,
    limit: int = 10,
    ubiquity_threshold: float = DEFAULT_UBIQUITY_THRESHOLD,
    semantic_fallback: bool = True,
) -> list[RelatedHit]:
    """Return items sharing entities with `item_id`, ranked by importance overlap.

    Entities present in more than `ubiquity_threshold` of items are treated as
    structurally ubiquitous (e.g. the blog author across all posts) and
    excluded from the traversal — they create hairball connections.

    When `semantic_fallback=True` and the graph returns fewer items than
    `limit`, the remaining slots are filled by pgvector cosine similarity on
    item embeddings. Fallback items are tagged `source='semantic'`.
    """
    rows = session.execute(
        _RELATED_SQL.bindparams(
            bindparam("item_id", value=item_id),
            bindparam("lim", value=limit),
            bindparam("ubiquity_threshold", value=float(ubiquity_threshold)),
        )
    ).all()
    graph_hits = [
        RelatedHit(
            item_id=r[0],
            title=r[1],
            folder=r[2],
            score=float(r[3]),
            shared_entities=list(r[4]) if r[4] else [],
            source="graph",
        )
        for r in rows
    ]

    if not semantic_fallback or len(graph_hits) >= limit:
        return graph_hits

    excluded = {item_id, *(h.item_id for h in graph_hits)}
    remaining = limit - len(graph_hits)
    fallback_hits = _semantic_fallback(
        item_id, excluded, session=session, limit=remaining
    )
    return graph_hits + fallback_hits
