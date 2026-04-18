"""Pipeline integration test — full ingest with a fake provider, no Gemini call."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault(
    "DATABASE_URL",
    os.environ.get("TEST_DATABASE_URL", "postgresql+psycopg2://korely:korely@localhost:5433/korely_graphrag_test"),
)

from sqlalchemy import select  # noqa: E402

from korely_graphrag.ingest import ingest_directory  # noqa: E402
from korely_graphrag.providers.base import BaseProvider, CompletionResult  # noqa: E402
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
    """Fake provider that returns a fixed entity-extraction JSON for any input."""

    def complete(self, *, system, user, max_tokens=2048, temperature=0.2, json_mode=False):
        # Return entities consistent with the test corpus content
        body = (
            '{"entities": ['
            '{"name": "PostgreSQL", "type": "technology", "context": "db engine", "importance": 0.9},'
            '{"name": "pgvector", "type": "technology", "context": "vector ext", "importance": 0.8}'
            ']}'
        )
        return CompletionResult(text=body, prompt_tokens=10, completion_tokens=20)

    def embed(self, text):
        vec = [0.0] * 1536
        for word in text.lower().split():
            vec[hash(word) % 1536] += 1.0
        norm = sum(v * v for v in vec) ** 0.5
        return [v / norm for v in vec] if norm else vec

    def embed_batch(self, texts):
        return [self.embed(t) for t in texts]


@pytest.fixture(scope="session", autouse=True)
def _bootstrap():
    reset_engine_for_tests()
    if not healthcheck():
        pytest.skip("Test Postgres not reachable")


@pytest.fixture()
def corpus(tmp_path: Path) -> Path:
    init_db(drop_first=True)
    (tmp_path / "DB").mkdir()
    (tmp_path / "ML").mkdir()
    # Each file long enough to clear should_index_content (≥30 unique words)
    (tmp_path / "DB" / "postgres.md").write_text(
        "# PostgreSQL deep dive\n\n"
        "PostgreSQL is a powerful open source relational database management system "
        "with strong support for advanced indexing, full text search via tsvector, "
        "JSON columns, partitioning, materialized views, and the pgvector extension "
        "for high dimensional embeddings used in semantic retrieval pipelines.\n",
        encoding="utf-8",
    )
    (tmp_path / "ML" / "embeddings.md").write_text(
        "# Embeddings primer\n\n"
        "Embedding models map text into dense vectors that capture semantic meaning. "
        "These vectors live in PostgreSQL via pgvector and enable cosine similarity "
        "search across millions of documents using approximate nearest neighbor indexes "
        "such as IVFFlat or HNSW for very fast retrieval.\n",
        encoding="utf-8",
    )
    return tmp_path


def test_ingest_creates_items_chunks_entities_mentions(corpus):
    fp = FakeProvider()
    stats = ingest_directory(corpus, reset=True, provider=fp)

    assert stats.files_seen == 2
    assert stats.files_indexed == 2
    assert stats.chunks_created >= 2
    assert stats.entities_created >= 2
    assert stats.mentions_created >= 2

    with session_scope() as s:
        items = s.execute(select(Item)).scalars().all()
        assert len(items) == 2
        titles = {i.title for i in items}
        assert "PostgreSQL deep dive" in titles
        assert "Embeddings primer" in titles

        # Folder derived from parent dir
        folders = {i.folder for i in items}
        assert folders == {"DB", "ML"}

        # Entities created and shared between docs.
        # Note: normalize_entity_name capitalizes "pgvector" → "Pgvector"
        # (no internal caps, not an acronym). Intentional canonicalization.
        ents = {e.name for e in s.execute(select(Entity)).scalars()}
        assert "PostgreSQL" in ents
        assert "Pgvector" in ents

        # Mentions populated
        n_mentions = s.execute(select(Mention)).all()
        assert len(n_mentions) >= 2


def test_re_ingest_unchanged_is_noop(corpus):
    fp = FakeProvider()
    ingest_directory(corpus, reset=True, provider=fp)

    stats2 = ingest_directory(corpus, reset=False, provider=fp)
    assert stats2.files_seen == 2
    assert stats2.files_skipped_unchanged == 2
    assert stats2.files_indexed == 0


def test_modified_file_is_re_indexed(corpus):
    fp = FakeProvider()
    ingest_directory(corpus, reset=True, provider=fp)

    target = corpus / "DB" / "postgres.md"
    new_body = target.read_text() + "\n\nA new paragraph added later in the day."
    target.write_text(new_body)

    stats = ingest_directory(corpus, reset=False, provider=fp)
    assert stats.files_indexed == 1
    assert stats.files_skipped_unchanged == 1
