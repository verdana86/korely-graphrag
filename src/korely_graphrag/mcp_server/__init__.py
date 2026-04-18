"""MCP server module — exposes 5 read tools over SSE transport.

The `server` submodule depends on the optional `fastmcp` package; importing it
eagerly at package load time would break tools-only consumers (and tests) that
don't need to spin up the server. Import lazily via `from .server import mcp`.
"""

from . import tools

__all__ = ["tools"]
