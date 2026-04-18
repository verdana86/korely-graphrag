"""Ingest module — chunking, embedding, entity extraction, and the pipeline."""

from .chunker import build_contextual_prefix, chunk_text, extract_section_heading
from .embedder import embed_many, embed_one
from .entity_extractor import (
    ExtractedEntity,
    extract_entities_from_text,
    is_valid_entity_name,
    normalize_entity_name,
    should_index_content,
)
from .pipeline import IngestStats, ingest_directory

__all__ = [
    "chunk_text",
    "extract_section_heading",
    "build_contextual_prefix",
    "embed_one",
    "embed_many",
    "ExtractedEntity",
    "extract_entities_from_text",
    "normalize_entity_name",
    "is_valid_entity_name",
    "should_index_content",
    "IngestStats",
    "ingest_directory",
]
