"""SQLAlchemy models for the korely-graphrag knowledge base.

Schema (V1, intentionally minimal):

    items        — one row per ingested file (markdown document)
    chunks       — text segments of an item, with vector embeddings
    entities     — named entities extracted from items (people, orgs, ...)
    mentions     — many-to-many edge (chunk, entity) with per-mention metadata

Notes
-----
- pgvector dimension is configurable but the column type is fixed at module
  import time; use `EMBEDDING_DIM` from `config` to keep schema and runtime
  in sync. Changing the dim later requires a migration.
- Full-text search lives on `chunks.text` via a generated tsvector column.
- No `users` table: V1 is single-user. Multi-user is a non-goal for OSS.
"""

from __future__ import annotations

import datetime as dt
import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Column,
    Computed,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from ..config import get_settings

EMBEDDING_DIM = get_settings().embedding_dim


def _utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    path: Mapped[str] = mapped_column(String(2048), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    folder: Mapped[str | None] = mapped_column(String(512), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    embedding = Column(Vector(EMBEDDING_DIM), nullable=True)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False)

    chunks: Mapped[list["Chunk"]] = relationship(back_populates="item", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_items_folder", "folder"),
        Index("ix_items_updated_at", "updated_at"),
    )


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("items.id", ondelete="CASCADE"), nullable=False
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding = Column(Vector(EMBEDDING_DIM), nullable=True)

    # Generated tsvector for FTS — auto-updated by Postgres on insert/update
    fts = Column(
        TSVECTOR,
        Computed("to_tsvector('simple', text)", persisted=True),
    )

    item: Mapped[Item] = relationship(back_populates="chunks")
    mentions: Mapped[list["Mention"]] = relationship(back_populates="chunk", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("item_id", "chunk_index", name="uq_chunks_item_index"),
        Index("ix_chunks_item_id", "item_id"),
        Index("ix_chunks_fts", "fts", postgresql_using="gin"),
    )


class Entity(Base):
    __tablename__ = "entities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    embedding = Column(Vector(EMBEDDING_DIM), nullable=True)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)

    mentions: Mapped[list["Mention"]] = relationship(back_populates="entity", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_entities_type", "entity_type"),
    )


class Mention(Base):
    """Edge (chunk → entity). One row per occurrence of an entity in a chunk."""

    __tablename__ = "mentions"

    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chunks.id", ondelete="CASCADE"), primary_key=True
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE"), primary_key=True
    )
    importance: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    context: Mapped[str | None] = mapped_column(String(256), nullable=True)

    chunk: Mapped[Chunk] = relationship(back_populates="mentions")
    entity: Mapped[Entity] = relationship(back_populates="mentions")

    __table_args__ = (
        Index("ix_mentions_entity_id", "entity_id"),
    )


def create_extensions(connection) -> None:
    """Enable required Postgres extensions. Call once before create_all()."""
    connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
