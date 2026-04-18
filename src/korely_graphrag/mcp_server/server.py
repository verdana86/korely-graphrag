"""FastMCP server exposing the 5 read tools.

Run via `korely-graphrag serve`. Uses SSE transport, suitable for Claude Code,
Cursor, Claude Desktop, and any other MCP client.
"""

from __future__ import annotations

from fastmcp import FastMCP

from . import tools

mcp = FastMCP("korely-graphrag")


_INSTRUCTIONS = """\
This MCP server is your interface to a personal knowledge base of markdown notes.

WORKFLOW:
1. SEARCH first with `search(query)` for any question about the user's notes.
2. READ details with `read_item(item_id)` for items that look relevant.
3. EXPAND with `get_related(item_id)` to surface non-obvious connections via the entity graph.
4. SYNTHESIZE the answer yourself — this server returns data, not narrative.

The killer feature is `get_related`: it surfaces notes connected via shared entities
(people, technologies, organizations, concepts), even when those notes share zero keywords.
Use it whenever a search hit deserves more context.
"""


@mcp.tool(description="Hybrid keyword + semantic search across all ingested notes.")
def search(query: str, limit: int = 10) -> dict:
    return tools.search(query, limit=limit)


@mcp.tool(description="Return full content + metadata for a single note by id.")
def read_item(item_id: str) -> dict:
    return tools.read_item(item_id)


@mcp.tool(
    description=(
        "Return notes related to a given note via shared entities (graph traversal). "
        "Surfaces non-keyword connections — the killer feature vs vanilla RAG."
    )
)
def get_related(item_id: str, limit: int = 10) -> dict:
    return tools.get_related(item_id, limit=limit)


@mcp.tool(description="List ingested notes, paginated, optionally filtered by folder.")
def list_notes(folder: str | None = None, limit: int = 20, offset: int = 0) -> dict:
    return tools.list_notes(folder=folder, limit=limit, offset=offset)


@mcp.tool(description="List distinct folders in the knowledge base with item counts.")
def list_folders() -> dict:
    return tools.list_folders()


def run(host: str = "0.0.0.0", port: int = 8080) -> None:
    """Start the MCP server over SSE."""
    mcp.run(transport="sse", host=host, port=port)


__all__ = ["mcp", "run"]
