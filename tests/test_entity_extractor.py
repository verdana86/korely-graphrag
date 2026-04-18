from korely_graphrag.ingest.entity_extractor import (
    is_valid_entity_name,
    normalize_entity_name,
    should_index_content,
)


def test_valid_entity_names():
    assert is_valid_entity_name("PostgreSQL")
    assert is_valid_entity_name("AI")
    assert is_valid_entity_name("Machine Learning")
    assert is_valid_entity_name("USA")


def test_gibberish_rejected():
    assert not is_valid_entity_name("asdasd")
    assert not is_valid_entity_name("a")
    assert not is_valid_entity_name("xxxx")
    assert not is_valid_entity_name("ababab")
    assert not is_valid_entity_name("bcdfg")  # no vowels


def test_normalize_strips_articles():
    assert normalize_entity_name("The Beatles") == "Beatles"
    assert normalize_entity_name("Il Piemonte") == "Piemonte"
    assert normalize_entity_name("L'Italia") == "Italia"
    # Don't strip "Il" inside a word
    assert normalize_entity_name("Illinois") == "Illinois"


def test_normalize_preserves_acronyms():
    assert normalize_entity_name("JWT") == "JWT"
    assert normalize_entity_name("USA") == "USA"


def test_normalize_preserves_internal_caps():
    assert normalize_entity_name("PostgreSQL") == "PostgreSQL"
    assert normalize_entity_name("GraphQL") == "GraphQL"


def test_should_index_skips_short_or_repetitive():
    assert not should_index_content("")
    assert not should_index_content("just a few words here")
    long_repetitive = "the the the " * 100
    assert not should_index_content(long_repetitive)
    long_real = (
        "PostgreSQL is a relational database system that supports advanced "
        "indexing, full-text search, JSON columns, and the pgvector extension "
        "for storing high-dimensional embeddings. Many production systems "
        "leverage these features to combine traditional queries with semantic "
        "retrieval over neural embeddings produced by language models."
    )
    assert should_index_content(long_real)
