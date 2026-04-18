"""Storage integration tests — require a running Postgres+pgvector.

The test fixture uses TEST_DATABASE_URL if set, otherwise the default from
config. Tests drop and recreate the schema before each session — DESTRUCTIVE,
must point to a disposable test DB.
"""

from __future__ import annotations

import os
import uuid

import pytest
from sqlalchemy import select

# Allow override before settings are imported
os.environ.setdefault(
    "DATABASE_URL",
    os.environ.get("TEST_DATABASE_URL", "postgresql+psycopg2://korely:korely@localhost:5433/korely_graphrag_test"),
)

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


@pytest.fixture(scope="session", autouse=True)
def _bootstrap_schema():
    reset_engine_for_tests()
    if not healthcheck():
        pytest.skip("Test Postgres not reachable")
    init_db(drop_first=True)
    yield


@pytest.fixture()
def clean_db():
    init_db(drop_first=True)
    yield


def test_create_item_and_chunk(clean_db):
    item_id = uuid.uuid4()
    with session_scope() as s:
        s.add(Item(
            id=item_id,
            path="/notes/foo.md",
            title="Foo",
            folder="Inbox",
            content="hello world",
            content_hash="abc",
        ))

    with session_scope() as s:
        s.add(Chunk(
            item_id=item_id,
            chunk_index=0,
            text="hello world this is the first chunk content",
        ))

    with session_scope() as s:
        item = s.execute(select(Item).where(Item.path == "/notes/foo.md")).scalar_one()
        assert item.title == "Foo"
        assert len(item.chunks) == 1
        assert item.chunks[0].chunk_index == 0


def test_unique_path_enforced(clean_db):
    with session_scope() as s:
        s.add(Item(path="/dup.md", title="A", content="x", content_hash="h1"))

    with pytest.raises(Exception):
        with session_scope() as s:
            s.add(Item(path="/dup.md", title="B", content="y", content_hash="h2"))


def test_mentions_link_chunks_to_entities(clean_db):
    item_id = uuid.uuid4()
    chunk_id = uuid.uuid4()
    with session_scope() as s:
        s.add(Item(id=item_id, path="/n.md", title="N", content="c", content_hash="h"))
        s.add(Chunk(id=chunk_id, item_id=item_id, chunk_index=0, text="PostgreSQL is a database"))
        e = Entity(name="PostgreSQL", entity_type="technology")
        s.add(e)
        s.flush()
        s.add(Mention(chunk_id=chunk_id, entity_id=e.id, importance=0.8, context="db engine"))

    with session_scope() as s:
        ent = s.execute(select(Entity).where(Entity.name == "PostgreSQL")).scalar_one()
        assert len(ent.mentions) == 1
        assert ent.mentions[0].importance == 0.8
        assert ent.mentions[0].chunk.text.startswith("PostgreSQL")


def test_cascade_delete_chunks_when_item_deleted(clean_db):
    item_id = uuid.uuid4()
    with session_scope() as s:
        s.add(Item(id=item_id, path="/x.md", title="X", content="x", content_hash="h"))
        s.add(Chunk(item_id=item_id, chunk_index=0, text="chunk text"))

    with session_scope() as s:
        item = s.get(Item, item_id)
        s.delete(item)

    with session_scope() as s:
        n = s.execute(select(Chunk).where(Chunk.item_id == item_id)).all()
        assert n == []


def test_fts_tsvector_populated(clean_db):
    """Postgres-generated tsvector column should be auto-filled on insert."""
    from sqlalchemy import func

    item_id = uuid.uuid4()
    chunk_id = uuid.uuid4()
    with session_scope() as s:
        s.add(Item(id=item_id, path="/f.md", title="F", content="c", content_hash="h"))
        s.add(Chunk(id=chunk_id, item_id=item_id, chunk_index=0, text="hybrid search retrieval"))

    with session_scope() as s:
        # match on the generated tsvector via to_tsquery
        row = s.execute(
            select(Chunk).where(Chunk.fts.op("@@")(func.to_tsquery("simple", "hybrid & retrieval")))
        ).scalar_one()
        assert row.id == chunk_id
