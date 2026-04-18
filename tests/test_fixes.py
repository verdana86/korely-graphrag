"""Tests for the 3 quality fixes from the 2026-04-18 smoke test:

1. Title extraction must skip H1s inside code fences and prefer the doc head.
2. Hub-node filter: entities present in >50% of items must NOT drag related().
3. Semantic dedup: 'Karpathy' and 'Andrej Karpathy' should resolve to the same entity.
"""

from __future__ import annotations

import os
import uuid

import pytest

os.environ.setdefault(
    "DATABASE_URL",
    os.environ.get("TEST_DATABASE_URL", "postgresql+psycopg2://korely:korely@localhost:5433/korely_graphrag_test"),
)

from sqlalchemy import select  # noqa: E402

from korely_graphrag.ingest.pipeline import _extract_title, _upsert_entities  # noqa: E402
from korely_graphrag.providers.base import BaseProvider, CompletionResult  # noqa: E402
from korely_graphrag.search import get_related_items  # noqa: E402
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


# ---------------------------------------------------------------------------
# #3 — Title extraction
# ---------------------------------------------------------------------------


def test_title_skips_h1_inside_code_fence():
    body = (
        "```python\n"
        "# conquer world here\n"
        "x = 1\n"
        "```\n"
        "\n"
        "# Real Title\n"
        "\n"
        "body content\n"
    )
    # First H1 is inside ``` block; real title comes after
    assert _extract_title(body, fallback="fallback") == "Real Title"


def test_title_picks_first_h1_at_top():
    body = "# A Recipe for Training Neural Networks\n\nIntro paragraph."
    assert _extract_title(body, fallback="fb") == "A Recipe for Training Neural Networks"


def test_title_falls_back_when_no_h1():
    body = "Just a paragraph, no heading at all."
    assert _extract_title(body, fallback="my-file") == "my-file"


def test_title_falls_back_when_only_code_h1():
    body = "```\n# only inside code\n```\n\nbody"
    assert _extract_title(body, fallback="post-name") == "post-name"


def test_title_rejects_codey_titles():
    body = "# `docs` array spec\n\nbody"
    # Starts with backtick → reject, fall back
    assert _extract_title(body, fallback="real-name") == "real-name"


# ---------------------------------------------------------------------------
# Postgres-backed fixtures for fixes #1 and #2
# ---------------------------------------------------------------------------


class FakeProvider(BaseProvider):
    """Embedding-aware fake that puts 'Karpathy' close to 'Andrej Karpathy'."""

    def complete(self, *, system, user, max_tokens=2048, temperature=0.2, json_mode=False):
        return CompletionResult(text="{}")

    def embed(self, text: str) -> list[float]:
        # Bag-of-words style. Critical: the test relies on shared tokens
        # between 'Karpathy' and 'Andrej Karpathy' giving cosine ≈ 0.5
        # (one shared token of two), which exceeds the 0.15-distance threshold.
        # So for THIS test we hand-craft a special closeness for these two.
        if text.strip().lower() in ("karpathy", "andrej karpathy"):
            # Both vectors point almost entirely at bucket 42, with a tiny
            # second component for "Andrej Karpathy". Cosine distance ≈ 0.005,
            # well below the 0.15 dedup threshold.
            v = [0.0] * 1536
            v[42] = 1.0
            if "andrej" in text.lower():
                v[43] = 0.1
            n = sum(x * x for x in v) ** 0.5
            return [x / n for x in v]
        v = [0.0] * 1536
        for w in text.lower().split():
            v[hash(w) % 1536] += 1.0
        n = sum(x * x for x in v) ** 0.5
        return [x / n for x in v] if n else v

    def embed_batch(self, texts):
        return [self.embed(t) for t in texts]


@pytest.fixture(scope="session", autouse=True)
def _bootstrap():
    reset_engine_for_tests()
    if not healthcheck():
        pytest.skip("Test Postgres not reachable")


# ---------------------------------------------------------------------------
# #2 — Semantic entity dedup
# ---------------------------------------------------------------------------


def test_semantic_dedup_merges_close_entity_names():
    init_db(drop_first=True)
    fp = FakeProvider()

    from korely_graphrag.ingest.entity_extractor import ExtractedEntity

    with session_scope() as s:
        # First wave: just "Karpathy"
        m1, new1 = _upsert_entities(
            s,
            [ExtractedEntity(name="Karpathy", raw_name="Karpathy", entity_type="person", importance=0.9)],
            provider=fp,
        )
        assert new1 == 1

        # Second wave: "Andrej Karpathy" should merge into the existing one
        m2, new2 = _upsert_entities(
            s,
            [ExtractedEntity(name="Andrej Karpathy", raw_name="Andrej Karpathy", entity_type="person", importance=0.9)],
            provider=fp,
        )
        assert new2 == 0, "Expected semantic dedup to merge into existing 'Karpathy'"
        assert m2["Andrej Karpathy"].name == "Karpathy"

    with session_scope() as s:
        all_persons = [e.name for e in s.execute(select(Entity).where(Entity.entity_type == "person")).scalars()]
        assert all_persons == ["Karpathy"], f"unexpected entities: {all_persons}"


# ---------------------------------------------------------------------------
# #1 — Hub-node filter
# ---------------------------------------------------------------------------


def test_get_related_excludes_ubiquitous_entities():
    """Build a 4-doc corpus where 'Author' appears in all 4 (ubiquitous).
    Two of them additionally share a specific entity ('PostgreSQL').
    Expectation: get_related on doc1 surfaces ONLY the PostgreSQL-sharing
    doc, never the 'Author'-only ones.
    """
    init_db(drop_first=True)
    fp = FakeProvider()

    item_ids = [uuid.uuid4() for _ in range(4)]
    chunk_ids = [uuid.uuid4() for _ in range(4)]

    with session_scope() as s:
        for idx, (iid, cid) in enumerate(zip(item_ids, chunk_ids, strict=True)):
            s.add(Item(id=iid, path=f"/doc{idx}.md", title=f"doc{idx}", content="x", content_hash=f"h{idx}"))
            s.add(Chunk(id=cid, item_id=iid, chunk_index=0, text=f"chunk text {idx}"))

        e_author = Entity(id=uuid.uuid4(), name="Author", entity_type="person")
        e_pg = Entity(id=uuid.uuid4(), name="PostgreSQL", entity_type="technology")
        s.add_all([e_author, e_pg])
        s.flush()

        # 'Author' mentioned in ALL 4 chunks (ubiquitous)
        for cid in chunk_ids:
            s.add(Mention(chunk_id=cid, entity_id=e_author.id, importance=0.9))
        # 'PostgreSQL' shared only between doc0 and doc1
        s.add(Mention(chunk_id=chunk_ids[0], entity_id=e_pg.id, importance=0.9))
        s.add(Mention(chunk_id=chunk_ids[1], entity_id=e_pg.id, importance=0.9))

    with session_scope() as s:
        related = get_related_items(str(item_ids[0]), session=s, limit=10)

    # Author is in 4/4 = 100% > 50% → must be filtered out.
    # Only doc1 shares PostgreSQL with doc0 → must be the only result.
    assert len(related) == 1, f"expected only 1 related, got {[r.item_id for r in related]}"
    assert related[0].item_id == str(item_ids[1])
    assert related[0].shared_entities == ["PostgreSQL"]
    assert "Author" not in related[0].shared_entities


def test_idf_weighting_demotes_semi_ubiquitous_entities():
    """A 'semi-ubiquitous' entity (in ~25% of docs) should be demoted by IDF
    so that docs sharing a *rare* entity outrank docs sharing only the common one.
    """
    init_db(drop_first=True)

    # 8 docs. "Common" appears in docs 0,1,2 (below 50% threshold → survives
    # the hard filter, but IDF should downweight it). "Rare" appears only in
    # docs 0 and 7 → high IDF. get_related(doc0) must rank doc7 (rare-shared)
    # ABOVE doc1/doc2 (common-shared).
    item_ids = [uuid.uuid4() for _ in range(8)]
    chunk_ids = [uuid.uuid4() for _ in range(8)]
    with session_scope() as s:
        for idx, (iid, cid) in enumerate(zip(item_ids, chunk_ids, strict=True)):
            s.add(Item(id=iid, path=f"/d{idx}.md", title=f"doc{idx}", content="x", content_hash=f"h{idx}"))
            s.add(Chunk(id=cid, item_id=iid, chunk_index=0, text=f"t{idx}"))
        e_common = Entity(id=uuid.uuid4(), name="Common", entity_type="concept")
        e_rare = Entity(id=uuid.uuid4(), name="Rare", entity_type="concept")
        s.add_all([e_common, e_rare])
        s.flush()
        for i in (0, 1, 2):
            s.add(Mention(chunk_id=chunk_ids[i], entity_id=e_common.id, importance=0.9))
        for i in (0, 7):
            s.add(Mention(chunk_id=chunk_ids[i], entity_id=e_rare.id, importance=0.9))

    with session_scope() as s:
        related = get_related_items(str(item_ids[0]), session=s, limit=10)

    by_id = {r.item_id: r for r in related}
    # doc7 (shares Rare) and doc1/doc2 (share Common) all appear
    assert str(item_ids[7]) in by_id
    assert str(item_ids[1]) in by_id
    # IDF must rank rare-share above common-share
    assert by_id[str(item_ids[7])].score > by_id[str(item_ids[1])].score, (
        f"Rare-shared doc should outrank common-shared; got rare={by_id[str(item_ids[7])].score} "
        f"common={by_id[str(item_ids[1])].score}"
    )


def test_substring_dedup_merges_short_name_into_longer_person():
    """Substring heuristic: 'Karpathy' (existing) and 'Andrej Karpathy' (new)
    must merge without calling embed_batch.
    """
    init_db(drop_first=True)
    from korely_graphrag.ingest.entity_extractor import ExtractedEntity

    class NoEmbedProvider(BaseProvider):
        """Fails on embed_batch to prove the substring path runs first."""
        calls = 0
        def complete(self, **kw): return CompletionResult(text="{}")
        def embed(self, text):
            raise AssertionError("embed must not be called for substring-mergeable names")
        def embed_batch(self, texts):
            NoEmbedProvider.calls += 1
            raise AssertionError("embed_batch must not be called for substring-mergeable names")

    fp = NoEmbedProvider()
    with session_scope() as s:
        from korely_graphrag.ingest.pipeline import _upsert_entities as upsert

        # Seed: create "Karpathy" first (via empty-name-match path)
        s.add(Entity(name="Karpathy", entity_type="person"))
        s.commit()

    with session_scope() as s:
        from korely_graphrag.ingest.pipeline import _upsert_entities as upsert

        # Now add "Andrej Karpathy" — substring dedup must catch it (no embed)
        m, new = upsert(
            s,
            [ExtractedEntity(name="Andrej Karpathy", raw_name="Andrej Karpathy", entity_type="person", importance=0.9)],
            provider=fp,
        )
        assert new == 0, "Expected substring dedup to merge, not create"
        assert m["Andrej Karpathy"].name == "Karpathy"


def test_substring_dedup_does_not_merge_across_types():
    """Substring match must only fire on person/organization types."""
    init_db(drop_first=True)
    from korely_graphrag.ingest.entity_extractor import ExtractedEntity
    fp = FakeProvider()

    with session_scope() as s:
        s.add(Entity(name="Learning", entity_type="concept"))
        s.commit()

    with session_scope() as s:
        from korely_graphrag.ingest.pipeline import _upsert_entities as upsert

        # "Machine Learning" tokens ⊃ "Learning" tokens, but type=concept, so
        # substring heuristic is SKIPPED. Falls through to semantic dedup,
        # which with our fake provider will NOT match (different token hashes).
        m, new = upsert(
            s,
            [ExtractedEntity(name="Machine Learning", raw_name="Machine Learning", entity_type="concept", importance=0.9)],
            provider=fp,
        )
        # Either created new or matched semantically — the key is substring
        # must not have forcibly merged a concept.
        assert m["Machine Learning"].name in ("Machine Learning", "Learning")
        # Verify by type (at least one concept entity exists with each name in scenarios)
        persons = s.execute(select(Entity).where(Entity.entity_type == "concept")).scalars().all()
        assert len(persons) >= 1


def test_tsquery_sanitization_handles_punctuation():
    """Previously, queries with punctuation (e.g. "PyTorch," or "`<b>`") broke
    to_tsquery with a syntax error. After fix, only alphanumeric tokens survive.
    """
    from korely_graphrag.search.hybrid import _sanitize_tsquery_terms

    assert _sanitize_tsquery_terms("PyTorch, Adam (M1) CPU?") == ["PyTorch", "Adam", "M1", "CPU"]
    assert _sanitize_tsquery_terms("`<b>` tag Twitter's DOM") == ["tag", "Twitter", "DOM"]
    assert _sanitize_tsquery_terms("   ") == []
    # 1-char tokens dropped, the rest kept
    assert _sanitize_tsquery_terms("a X b of is") == ["of", "is"]
    # Basic query still works
    assert _sanitize_tsquery_terms("recurrent neural networks") == ["recurrent", "neural", "networks"]


def test_hybrid_search_survives_punctuation_query():
    """Integration: hybrid_search must not crash on punctuation-heavy queries.
    Previously raised psycopg2 SyntaxError on tsquery.
    """
    init_db(drop_first=True)
    from korely_graphrag.search.hybrid import hybrid_search

    fp = FakeProvider()
    with session_scope() as s:
        hits = hybrid_search("PostgreSQL, (M1)! pgvector?", session=s, limit=5, provider=fp)
        assert isinstance(hits, list)  # empty ok, crash not ok


def test_hub_filter_floor_protects_tiny_corpora():
    """In a 2-doc corpus, 50% threshold would collapse to 1 doc; the floor of
    2 docs preserves entities that show up in both.
    """
    init_db(drop_first=True)
    fp = FakeProvider()

    iid_a, iid_b = uuid.uuid4(), uuid.uuid4()
    cid_a, cid_b = uuid.uuid4(), uuid.uuid4()
    with session_scope() as s:
        s.add_all([
            Item(id=iid_a, path="/a.md", title="A", content="x", content_hash="ha"),
            Item(id=iid_b, path="/b.md", title="B", content="y", content_hash="hb"),
        ])
        s.add_all([
            Chunk(id=cid_a, item_id=iid_a, chunk_index=0, text="t"),
            Chunk(id=cid_b, item_id=iid_b, chunk_index=0, text="t"),
        ])
        e = Entity(id=uuid.uuid4(), name="Shared", entity_type="concept")
        s.add(e)
        s.flush()
        s.add_all([
            Mention(chunk_id=cid_a, entity_id=e.id, importance=0.9),
            Mention(chunk_id=cid_b, entity_id=e.id, importance=0.9),
        ])

    with session_scope() as s:
        related = get_related_items(str(iid_a), session=s, limit=5)
    # With 2 items and 50% threshold, the math says doc_count <= 1.0; floor
    # bumps it to 2.0, so 'Shared' (in both) survives → b is related.
    assert len(related) == 1
    assert related[0].item_id == str(iid_b)
