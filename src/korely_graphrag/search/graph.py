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

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "title": self.title,
            "folder": self.folder,
            "score": round(self.score, 6),
            "shared_entities": self.shared_entities,
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


def get_related_items(
    item_id: str,
    *,
    session: Session,
    limit: int = 10,
    ubiquity_threshold: float = DEFAULT_UBIQUITY_THRESHOLD,
) -> list[RelatedHit]:
    """Return items sharing entities with `item_id`, ranked by importance overlap.

    Entities present in more than `ubiquity_threshold` of items are treated as
    structurally ubiquitous (e.g. the blog author across all posts) and
    excluded from the traversal — they create hairball connections.
    """
    rows = session.execute(
        _RELATED_SQL.bindparams(
            bindparam("item_id", value=item_id),
            bindparam("lim", value=limit),
            bindparam("ubiquity_threshold", value=float(ubiquity_threshold)),
        )
    ).all()
    return [
        RelatedHit(
            item_id=r[0],
            title=r[1],
            folder=r[2],
            score=float(r[3]),
            shared_entities=list(r[4]) if r[4] else [],
        )
        for r in rows
    ]
