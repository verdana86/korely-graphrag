from korely_graphrag.ingest.chunker import (
    chunk_text,
    extract_section_heading,
    build_contextual_prefix,
)


def test_short_text_returns_single_chunk():
    text = "Hello world.\n\nA second paragraph."
    assert chunk_text(text) == [text]


def test_empty_returns_empty_list():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_long_text_splits_on_paragraphs():
    para = ("Lorem ipsum dolor sit amet. " * 40).strip()
    text = "\n\n".join([para] * 6)
    chunks = chunk_text(text, chunk_size=2800, overlap=420)
    assert len(chunks) > 1
    assert all(len(c) > 50 for c in chunks)


def test_speaker_turns_grouped_not_split():
    turn = "Speaker 1: " + ("This is a turn. " * 80) + "\n\n"
    text = turn * 6
    chunks = chunk_text(text, chunk_size=2800, overlap=0)
    assert len(chunks) >= 2
    for c in chunks:
        assert c.lstrip().startswith("Speaker")


def test_section_heading():
    assert extract_section_heading("# My Title\nbody") == "My Title"
    assert extract_section_heading("## Sub\n\ntext") == "Sub"
    assert extract_section_heading("no heading here") is None


def test_contextual_prefix_metadata():
    p = build_contextual_prefix(
        title="Note A", folder="Inbox", chunk_index=0, total_chunks=3, section="Intro"
    )
    assert "chunk 1 of 3" in p
    assert "Note A" in p
    assert "Inbox" in p
    assert "Intro" in p


def test_contextual_prefix_empty_when_no_data():
    assert build_contextual_prefix() == ""
