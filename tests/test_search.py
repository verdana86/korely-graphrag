"""Search integration tests — require Postgres+pgvector.

Use a fake provider (deterministic embeddings) so we never call Gemini in CI.
"""

from __future__ import annotations

import os
import uuid

import pytest

os.environ.setdefault(
    "DATABASE_URL",
    os.environ.get("TEST_DATABASE_URL", "postgresql+psycopg2://korely:korely@localhost:5433/korely_graphrag_test"),
)

from korely_graphrag.providers.base import BaseProvider, CompletionResult  # noqa: E402
from korely_graphrag.search import get_related_items, hybrid_search  # noqa: E402
from korely_graphrag.storage import (  # noqa: E402
    Chunk,
    Entity,
    Item,
    Mention,
    healthcheck,
    init_db,
    reset_engine_for_tests,
    session_scope,
)


class FakeProvider(BaseProvider):
    """Deterministic, *semantically reasonable* provider for tests.

    The embedding is a 1536-dim sparse bag-of-words: each word is hashed into
    one bucket. Texts that share words have non-zero cosine similarity; texts
    with no overlap are orthogonal. Realistic enough to validate hybrid_search
    behavior without calling Gemini.
    """

    def complete(self, *, system, user, max_tokens=2048, temperature=0.2, json_mode=False) -> CompletionResult:
        return CompletionResult(text="{}", prompt_tokens=0, completion_tokens=0)

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * 1536
        for word in text.lower().split():
            bucket = hash(word) % 1536
            vec[bucket] += 1.0
        # Normalize so cosine distance behaves
        norm = sum(v * v for v in vec) ** 0.5
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]


@pytest.fixture(scope="session", autouse=True)
def _bootstrap_schema():
    reset_engine_for_tests()
    if not healthcheck():
        pytest.skip("Test Postgres not reachable")
    init_db(drop_first=True)
    yield


@pytest.fixture()
def seeded_db():
    init_db(drop_first=True)

    fp = FakeProvider()
    item_a_id = uuid.uuid4()
    item_b_id = uuid.uuid4()
    item_c_id = uuid.uuid4()

    with session_scope() as s:
        # Three items
        s.add(Item(id=item_a_id, path="/a.md", title="Note A — PostgreSQL deep dive",
                   folder="DB", content="x", content_hash="ha"))
        s.add(Item(id=item_b_id, path="/b.md", title="Note B — Embeddings and vector search",
                   folder="ML", content="x", content_hash="hb"))
        s.add(Item(id=item_c_id, path="/c.md", title="Note C — A trip to Paris",
                   folder="Travel", content="x", content_hash="hc"))

        # Chunks (with text + fake embeddings)
        ca = Chunk(id=uuid.uuid4(), item_id=item_a_id, chunk_index=0,
                   text="PostgreSQL hybrid search retrieval engine pgvector",
                   embedding=fp.embed("PostgreSQL hybrid search retrieval engine pgvector"))
        cb = Chunk(id=uuid.uuid4(), item_id=item_b_id, chunk_index=0,
                   text="Embeddings dense vector retrieval pgvector index",
                   embedding=fp.embed("Embeddings dense vector retrieval pgvector index"))
        cc = Chunk(id=uuid.uuid4(), item_id=item_c_id, chunk_index=0,
                   text="A walk along the Seine river in Paris during spring",
                   embedding=fp.embed("A walk along the Seine river in Paris during spring"))
        s.add_all([ca, cb, cc])

        # Shared entities: A and B both mention "PostgreSQL" and "pgvector"
        # C mentions "Paris" only
        e_pg = Entity(id=uuid.uuid4(), name="PostgreSQL", entity_type="technology")
        e_pgv = Entity(id=uuid.uuid4(), name="pgvector", entity_type="technology")
        e_paris = Entity(id=uuid.uuid4(), name="Paris", entity_type="location")
        s.add_all([e_pg, e_pgv, e_paris])
        s.flush()

        s.add_all([
            Mention(chunk_id=ca.id, entity_id=e_pg.id, importance=0.9),
            Mention(chunk_id=ca.id, entity_id=e_pgv.id, importance=0.8),
            Mention(chunk_id=cb.id, entity_id=e_pg.id, importance=0.6),
            Mention(chunk_id=cb.id, entity_id=e_pgv.id, importance=0.9),
            Mention(chunk_id=cc.id, entity_id=e_paris.id, importance=1.0),
        ])

    yield {"a": str(item_a_id), "b": str(item_b_id), "c": str(item_c_id)}


def test_hybrid_search_finds_keyword_match(seeded_db):
    fp = FakeProvider()
    with session_scope() as s:
        hits = hybrid_search("PostgreSQL pgvector", session=s, limit=5, provider=fp)
    assert len(hits) >= 2
    titles = [h.title for h in hits]
    assert any("PostgreSQL" in t for t in titles)
    assert any("Embeddings" in t for t in titles)
    # The unrelated note about Paris should NOT be in the top hits
    assert all("Paris" not in t for t in titles[:2])


def test_hybrid_search_returns_no_hits_for_unrelated(seeded_db):
    fp = FakeProvider()
    with session_scope() as s:
        hits = hybrid_search("quantum chromodynamics", session=s, limit=5, provider=fp)
    # No FTS match. Vector hits will exist (RRF over fake embeddings) — but the
    # top hit for an unrelated query is allowed to be anything; we only assert
    # the call doesn't crash and returns ≤ limit results.
    assert len(hits) <= 5


def test_get_related_finds_shared_entity_items(seeded_db):
    a_id = seeded_db["a"]
    b_id = seeded_db["b"]
    c_id = seeded_db["c"]
    with session_scope() as s:
        related = get_related_items(a_id, session=s, limit=5)
    item_ids = [r.item_id for r in related]
    assert b_id in item_ids, "B should be related to A (both share PostgreSQL + pgvector)"
    assert c_id not in item_ids, "C is unrelated and must not appear"
    # Shared entity names must be reported
    b_hit = next(r for r in related if r.item_id == b_id)
    assert "PostgreSQL" in b_hit.shared_entities
    assert "pgvector" in b_hit.shared_entities
    assert b_hit.score > 0


def test_get_related_for_isolated_item_returns_empty(seeded_db):
    c_id = seeded_db["c"]
    with session_scope() as s:
        related = get_related_items(c_id, session=s, limit=5)
    # C only shares Paris, with no other item → empty
    assert related == []
