"""MCP tools integration tests — exercise the 5 read tools end-to-end against Postgres."""

from __future__ import annotations

import os
import uuid

import pytest

os.environ.setdefault(
    "DATABASE_URL",
    os.environ.get("TEST_DATABASE_URL", "postgresql+psycopg2://korely:korely@localhost:5433/korely_graphrag_test"),
)

from korely_graphrag.mcp_server import tools as mcp_tools  # noqa: E402
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
    def complete(self, *, system, user, max_tokens=2048, temperature=0.2, json_mode=False):
        return CompletionResult(text="{}", prompt_tokens=0, completion_tokens=0)

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
    init_db(drop_first=True)
    yield


@pytest.fixture()
def populated_db(monkeypatch):
    init_db(drop_first=True)
    fp = FakeProvider()
    # Patch get_provider so hybrid_search uses the fake one
    from korely_graphrag.providers import base as base_mod

    monkeypatch.setattr(base_mod, "get_provider", lambda: fp)

    item_a = uuid.uuid4()
    item_b = uuid.uuid4()
    with session_scope() as s:
        s.add(Item(id=item_a, path="/a.md", title="PostgreSQL deep dive",
                   folder="DB", content="A: PostgreSQL pgvector hybrid search.", content_hash="ha"))
        s.add(Item(id=item_b, path="/b.md", title="Embeddings explained",
                   folder="ML", content="B: Embeddings dense vector retrieval pgvector.", content_hash="hb"))
        ca = Chunk(id=uuid.uuid4(), item_id=item_a, chunk_index=0,
                   text="PostgreSQL pgvector hybrid search engine retrieval",
                   embedding=fp.embed("PostgreSQL pgvector hybrid search engine retrieval"))
        cb = Chunk(id=uuid.uuid4(), item_id=item_b, chunk_index=0,
                   text="Embeddings dense vector retrieval pgvector index",
                   embedding=fp.embed("Embeddings dense vector retrieval pgvector index"))
        s.add_all([ca, cb])
        e_pg = Entity(id=uuid.uuid4(), name="PostgreSQL", entity_type="technology")
        e_pgv = Entity(id=uuid.uuid4(), name="pgvector", entity_type="technology")
        s.add_all([e_pg, e_pgv])
        s.flush()
        s.add_all([
            Mention(chunk_id=ca.id, entity_id=e_pg.id, importance=0.9),
            Mention(chunk_id=ca.id, entity_id=e_pgv.id, importance=0.8),
            Mention(chunk_id=cb.id, entity_id=e_pgv.id, importance=0.9),
        ])
    yield {"a": str(item_a), "b": str(item_b)}


def test_search_returns_results_with_snippet(populated_db):
    out = mcp_tools.search("pgvector", limit=5)
    assert out["query"] == "pgvector"
    assert out["count"] >= 2
    titles = [r["title"] for r in out["results"]]
    assert any("PostgreSQL" in t for t in titles)
    assert any("Embeddings" in t for t in titles)
    assert all("snippet" in r and r["score"] > 0 for r in out["results"])


def test_read_item_returns_full_content(populated_db):
    out = mcp_tools.read_item(populated_db["a"])
    assert out["title"] == "PostgreSQL deep dive"
    assert out["folder"] == "DB"
    assert "PostgreSQL" in out["content"]
    assert "created_at" in out


def test_read_item_missing_returns_error(populated_db):
    out = mcp_tools.read_item(str(uuid.uuid4()))
    assert "error" in out


def test_get_related_finds_b_from_a(populated_db):
    out = mcp_tools.get_related(populated_db["a"], limit=5)
    assert out["item_id"] == populated_db["a"]
    assert out["count"] >= 1
    ids = [r["item_id"] for r in out["results"]]
    assert populated_db["b"] in ids


def test_get_related_unknown_item_returns_error(populated_db):
    out = mcp_tools.get_related(str(uuid.uuid4()))
    assert "error" in out
    assert out["results"] == []


def test_list_notes_paginated(populated_db):
    out = mcp_tools.list_notes(limit=10)
    assert out["total"] == 2
    assert out["count"] == 2
    assert {i["title"] for i in out["items"]} == {"PostgreSQL deep dive", "Embeddings explained"}


def test_list_notes_filtered_by_folder(populated_db):
    out = mcp_tools.list_notes(folder="DB", limit=10)
    assert out["total"] == 1
    assert out["items"][0]["title"] == "PostgreSQL deep dive"


def test_list_folders_groups_with_counts(populated_db):
    out = mcp_tools.list_folders()
    names = {f["name"]: f["item_count"] for f in out["folders"]}
    assert names == {"DB": 1, "ML": 1}


def test_search_empty_query_returns_no_results(populated_db):
    out = mcp_tools.search("   ", limit=5)
    assert out["count"] == 0
    assert out["results"] == []
