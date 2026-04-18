"""MCP tool implementations — pure data provider (no server-side LLM at query time).

The 5 read tools form the public interface to the knowledge base. Each returns
JSON-serializable dicts that an MCP client (Claude Code, Cursor, ...) can
consume and synthesize with its own LLM.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from ..search import get_related_items, hybrid_search
from ..storage import Chunk, Item, session_scope


def search(query: str, *, limit: int = 10) -> dict[str, Any]:
    """Hybrid search (FTS + vector) over all ingested items."""
    with session_scope() as s:
        hits = hybrid_search(query, session=s, limit=limit)
    return {
        "query": query,
        "count": len(hits),
        "results": [h.to_dict() for h in hits],
    }


def read_item(item_id: str) -> dict[str, Any]:
    """Return full content + metadata for a single item by id."""
    with session_scope() as s:
        item = s.get(Item, item_id)
        if item is None:
            return {"error": f"item {item_id} not found"}
        return {
            "id": str(item.id),
            "path": item.path,
            "title": item.title,
            "folder": item.folder,
            "content": item.content,
            "created_at": item.created_at.isoformat(),
            "updated_at": item.updated_at.isoformat(),
        }


def get_related(item_id: str, *, limit: int = 10) -> dict[str, Any]:
    """Return items related to `item_id` via shared entities (graph traversal)."""
    with session_scope() as s:
        # Verify item exists for a clearer error
        if s.get(Item, item_id) is None:
            return {"error": f"item {item_id} not found", "results": []}
        related = get_related_items(item_id, session=s, limit=limit)
    return {
        "item_id": item_id,
        "count": len(related),
        "results": [r.to_dict() for r in related],
    }


def list_notes(
    *,
    folder: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    """List ingested items, paginated, optionally filtered by folder."""
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    with session_scope() as s:
        stmt = select(Item.id, Item.title, Item.folder, Item.path, Item.updated_at)
        if folder:
            stmt = stmt.where(Item.folder == folder)
        stmt = stmt.order_by(Item.updated_at.desc()).limit(limit).offset(offset)
        rows = s.execute(stmt).all()
        total_stmt = select(func.count(Item.id))
        if folder:
            total_stmt = total_stmt.where(Item.folder == folder)
        total = s.execute(total_stmt).scalar_one()
    return {
        "count": len(rows),
        "total": int(total),
        "limit": limit,
        "offset": offset,
        "folder": folder,
        "items": [
            {
                "id": str(r.id),
                "title": r.title,
                "folder": r.folder,
                "path": r.path,
                "updated_at": r.updated_at.isoformat(),
            }
            for r in rows
        ],
    }


def list_folders() -> dict[str, Any]:
    """Return the distinct folder values currently in the knowledge base."""
    with session_scope() as s:
        rows = s.execute(
            select(Item.folder, func.count(Item.id))
            .where(Item.folder.is_not(None))
            .group_by(Item.folder)
            .order_by(Item.folder)
        ).all()
    return {
        "count": len(rows),
        "folders": [{"name": r[0], "item_count": int(r[1])} for r in rows],
    }
