# Architecture

This document explains how `korely-graphrag` works internally. It is the source of truth for contributors and for anyone curious about why retrieval quality differs from vanilla RAG.

> **Note:** placeholder — to be filled in during Phase 2 (after extraction).

## Pipelines

### Ingest pipeline
1. Walk a directory for `*.md` files
2. For each file:
   - Read content
   - Chunk into ~700-token segments at semantic boundaries (paragraphs)
   - Generate 1536-dim embedding per chunk via Gemini
   - Run a single Gemini call per document for entity extraction (JSON-mode)
   - Persist chunks, entities, mentions to Postgres

### Query pipeline (`search` MCP tool)
1. Receive query string
2. (Optional) query rewrite via Gemini Flash Lite if query > 4 words
3. Run FTS query (Postgres TSVECTOR) and pgvector cosine query in parallel
4. Merge with Reciprocal Rank Fusion
5. Return top-N items

### Related pipeline (`get_related` MCP tool)
1. Given an item_id, fetch all entities mentioned by that item
2. Find all *other* items that mention any of those entities
3. Score by entity overlap × entity importance
4. Return top-N items

## Data model

- `items` — top-level documents (one per markdown file)
- `chunks` — text chunks with embedding
- `entities` — extracted named entities (person, org, technology, concept, ...)
- `mentions` — many-to-many edge between chunks and entities

(Full schema in `src/korely_graphrag/storage/models.py`.)

## Provider abstraction

LLM calls go through `providers/`. Day-1 supports Gemini only. Ollama planned.

## Why no full LLM at query time?

Pure data provider pattern: the MCP server returns structured data. The MCP client (Claude Code, Cursor) does the synthesis with its own LLM. This means:
- Zero LLM cost on the server side at query time
- Scales linearly with disk + Postgres
- No vendor lock-in for the consumer LLM
