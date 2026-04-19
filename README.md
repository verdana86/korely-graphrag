# korely-graphrag

> A second brain for your markdown notes — with an entity graph that finds the connections you didn't write down.

**Status:** early preview · single-user · CLI-first · Apache 2.0

---

## What it is

`korely-graphrag` is the open-source extraction of the retrieval engine that powers [Korely](https://korely.com): an MCP-compatible second brain that goes beyond vanilla RAG by automatically extracting and indexing entities (people, organizations, technologies, concepts) from your notes, then surfacing related items through a knowledge graph.

Plug it into Claude Code, Cursor, Claude Desktop, or any MCP client and ask questions about your notes — including questions like *"what else mentions X?"* that flat-file memory and chunk-based RAG can't answer well.

## Why another RAG tool?

There are a lot of "second brain with LLM" projects right now. Most of them stop at: chunk markdown → embed → cosine search → return top-k. That's fine for "find me the note about X", but it falls apart when you want to *discover* connections.

`korely-graphrag` adds a layer most don't:

| Layer | Vanilla RAG | Claude Code memory | korely-graphrag |
|---|---|---|---|
| Keyword + vector search | yes | partial | yes |
| Auto entity extraction | no | no | **yes** |
| Graph traversal across notes | no | no | **yes** |
| MCP-native (any client) | varies | n/a | **yes** |

Inspired in spirit by [Karpathy's LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), but built around an automatic entity graph instead of a hand-curated wiki.

See [BENCHMARK.md](BENCHMARK.md) for honest numbers vs alternatives.

## Quickstart

```bash
git clone https://github.com/verdana86/korely-graphrag
cd korely-graphrag

cp .env.example .env
# edit .env: set GEMINI_API_KEY (free tier works — get one at aistudio.google.com)

# Tell docker-compose where your markdown notes live.
# Either copy them into ./notes, or point HOST_NOTES_PATH at your real vault:
export HOST_NOTES_PATH=~/my-notes    # or any absolute path to a directory of *.md

docker compose up -d                  # Postgres + pgvector + app container

# Ingest. Inside the container your notes are mounted at /notes (read-only).
docker compose exec app korely-graphrag ingest /notes

# Check what got indexed
docker compose exec app korely-graphrag stats

# See the graph visually (Mermaid — paste anywhere that renders it)
docker compose exec app korely-graphrag export -o /app/graph.md
# Sample output on the benchmark corpus: benchmark/graph.md

# Start MCP server
docker compose exec app korely-graphrag serve
# MCP available at http://localhost:8080/sse
```

Then point your MCP client (Claude Code, Cursor, etc.) at `http://localhost:8080/sse` and ask questions about your notes.

## Architecture

```mermaid
flowchart LR
    MD[Markdown files] -->|chunk + embed<br/>+ entity extract| DB[(Postgres<br/>+ pgvector)]
    DB --> S[search]
    DB --> R[read_item]
    DB --> GR[get_related<br/>via entity graph]
    DB --> LN[list_notes]
    DB --> LF[list_folders]
    S & R & GR & LN & LF --> MCP{{MCP server<br/>SSE}}
    MCP --> CC[Claude Code]
    MCP --> CU[Cursor]
    MCP --> CD[Claude Desktop]
    MCP --> N8N[n8n / ChatGPT]

    style GR fill:#d6ffdd,stroke:#2b8a3e,stroke-width:2px
    style MCP fill:#eef6ff,stroke:#1c7ed6
```

The killer feature is `get_related` — given a note, it surfaces other notes
that share *entities* (people, technologies, concepts) rather than keywords.
Everything else is standard hybrid RAG served through MCP.

Full details in [ARCHITECTURE.md](ARCHITECTURE.md) — 3 more diagrams inside
covering ingest, query, and graph-traversal pipelines.

## Requirements

- Docker + Docker Compose (recommended path)
- A Gemini API key — get one free at [aistudio.google.com](https://aistudio.google.com)

Or, if you prefer manual setup:
- Python 3.11+
- PostgreSQL 15+ with `pgvector` extension

## Roadmap

- [x] Apache 2.0 release
- [x] Gemini provider
- [x] 5 MCP read tools
- [x] CLI ingest / serve / stats
- [ ] **Ollama provider — 100% local mode** (planned)
- [ ] Incremental re-ingest (only changed files)
- [ ] Web UI for browsing the graph
- [ ] Obsidian plugin

## Contributing

This is an early preview. Issues and PRs welcome, but no SLA — this is a side project. Please open an issue before starting any large change.

## Relationship to Korely

`korely-graphrag` is a self-contained extraction of the retrieval core used by Korely (the commercial product). The full Korely product adds: web UI, meeting recording + transcription, multi-user collaboration, billing, and a richer chat pipeline. If you want all that, see [korely.com](https://korely.com). If you just want a strong MCP-backed second brain on your own machine, this repo is for you.

## License

[Apache 2.0](LICENSE) — do what you want, including commercial use. See LICENSE for the full text.
