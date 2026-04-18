"""End-to-end ingest pipeline: markdown directory → DB.

For each .md file:
1. Read + hash the content
2. Extract title (first H1) and folder (parent dir relative to root)
3. Chunk the body
4. Embed each chunk (batched)
5. Extract entities (single LLM call per document)
6. Upsert item; replace its chunks; upsert entities; insert mentions

Idempotent at the file level: re-running on the same path is a no-op when the
content hash matches the stored row.
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from ..providers.base import BaseProvider, get_provider
from ..storage import (
    Chunk,
    Entity,
    Item,
    Mention,
    init_db,
    session_scope,
)
from .chunker import build_contextual_prefix, chunk_text, extract_section_heading
from .embedder import embed_many, embed_one
from .entity_extractor import (
    ExtractedEntity,
    extract_entities_from_text,
    should_index_content,
)

logger = logging.getLogger(__name__)


@dataclass
class IngestStats:
    files_seen: int = 0
    files_skipped_unchanged: int = 0
    files_indexed: int = 0
    chunks_created: int = 0
    entities_created: int = 0
    mentions_created: int = 0
    errors: int = 0

    def as_dict(self) -> dict:
        return self.__dict__.copy()


_H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
_CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_TITLE_LOOKAHEAD_CHARS = 1500


def _extract_title(content: str, fallback: str) -> str:
    """Pick the first H1 in the document head, ignoring H1s inside code fences.

    Karpathy-style posts had inline `# something` *inside* code blocks (Python
    comments rendered as headings); that previously yielded titles like
    "conquer world here" or "Let there be an input dataset `docs`...". The fix
    is to strip code fences first and only look in the first ~1.5 KB of text
    (real titles always sit at the top).
    """
    head = content[:_TITLE_LOOKAHEAD_CHARS]
    head_no_code = _CODE_FENCE_RE.sub("", head)
    m = _H1_RE.search(head_no_code)
    if m:
        candidate = m.group(1).strip()
        # Reject titles that look like code (backticks, leading punctuation)
        if candidate and not candidate.startswith(("`", "*", "-", "+")):
            return candidate[:512]
    return fallback


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _folder_for(path: Path, root: Path) -> str | None:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return None
    parent = rel.parent
    if str(parent) in (".", ""):
        return None
    return str(parent)


# Cosine distance threshold for semantic entity dedup. Calibrated on
# gemini-embedding-001 at 1536 dim: <0.22 catches "ML" vs "Machine Learning",
# "GPT-4" vs "GPT 4", "ImageNet" vs "Imagenet" without over-merging
# (e.g. "PostgreSQL" vs "MySQL" stay distinct at ~0.35).
SEMANTIC_DEDUP_DISTANCE = 0.22

# Entity types where a shorter name is commonly the informal/short version of
# a longer one (e.g. "Karpathy" for "Andrej Karpathy", "IBM" for "International
# Business Machines"). For these, a token-subset match merges without an embed
# call and without the 0.22 threshold miss.
_SUBSTRING_DEDUP_TYPES = frozenset({"person", "organization"})


def _tokenset(name: str) -> frozenset[str]:
    return frozenset(t for t in name.lower().split() if t)


def _find_substring_match(
    session, name: str, entity_type: str
) -> Entity | None:
    """Token-subset heuristic: if `name`'s tokens are a strict subset of some
    existing entity's tokens (or vice versa), and the type is person/org,
    treat them as the same entity. Handles "Karpathy" ⊂ "Andrej Karpathy".
    """
    if entity_type not in _SUBSTRING_DEDUP_TYPES:
        return None
    tokens = _tokenset(name)
    if not tokens or len(tokens) > 5:
        return None
    existing = session.execute(
        select(Entity).where(Entity.entity_type == entity_type)
    ).scalars().all()
    for ent in existing:
        ent_tokens = _tokenset(ent.name)
        if not ent_tokens:
            continue
        # Require at least one token overlap AND one is a strict subset
        if tokens < ent_tokens or ent_tokens < tokens:
            return ent
    return None


def _find_semantic_match(session, name_embedding: list[float]) -> Entity | None:
    """Return an existing entity whose embedding is within SEMANTIC_DEDUP_DISTANCE
    cosine of `name_embedding`, or None if no close match.
    """
    from sqlalchemy import bindparam, text as _text

    row = session.execute(
        _text(
            "SELECT id, embedding <=> CAST(:emb AS vector) AS dist "
            "FROM entities WHERE embedding IS NOT NULL "
            "ORDER BY dist ASC LIMIT 1"
        ).bindparams(bindparam("emb", value=str(name_embedding))),
    ).first()
    if row is None or row.dist is None:
        return None
    if float(row.dist) > SEMANTIC_DEDUP_DISTANCE:
        return None
    return session.get(Entity, row.id)


def _upsert_entities(
    session,
    raw_entities: list[ExtractedEntity],
    *,
    provider: BaseProvider,
) -> tuple[dict[str, Entity], int]:
    """Return {entity_raw_name: Entity}, deduping via name AND embedding.

    Two-stage dedup:
    1. Exact match on normalized name (handles "the BBC" → "BBC", articles).
    2. Semantic match via embedding cosine (handles "Karpathy" vs "Andrej
       Karpathy", acronyms, spelling variants). Cost: 1 embedding per *new*
       entity name.
    """
    if not raw_entities:
        return {}, 0

    name_to_ent: dict[str, Entity] = {}
    created_count = 0

    # Stage 1: exact name match
    distinct_names = list({e.name for e in raw_entities})
    existing = {
        e.name: e
        for e in session.execute(select(Entity).where(Entity.name.in_(distinct_names))).scalars()
    }

    # Stage 2a: substring-based dedup for person/organization (zero-cost,
    # catches informal/short names like "Karpathy" ⊂ "Andrej Karpathy").
    name_to_type = {r.name: r.entity_type for r in raw_entities}
    after_substring: list[str] = []
    for name in distinct_names:
        if name in existing:
            continue
        ent_type = name_to_type.get(name, "concept")
        sub_match = _find_substring_match(session, name, ent_type)
        if sub_match is not None:
            logger.info("[ingest] substring dedup: '%s' → '%s'", name, sub_match.name)
            existing[name] = sub_match
        else:
            after_substring.append(name)

    # Stage 2b: for remaining names, embed + semantic search
    needs_embed = after_substring
    if needs_embed:
        try:
            embeddings = provider.embed_batch(needs_embed)
        except Exception as e:
            logger.warning("[ingest] semantic dedup embed failed (%s); falling back to name-only", e)
            embeddings = [None] * len(needs_embed)

        for name, emb in zip(needs_embed, embeddings, strict=True):
            ent_type = name_to_type.get(name, "concept")
            if emb is None:
                ent = Entity(name=name, entity_type=ent_type)
                session.add(ent)
                existing[name] = ent
                created_count += 1
                continue
            match = _find_semantic_match(session, emb)
            if match is not None:
                logger.info("[ingest] semantic dedup: '%s' → '%s'", name, match.name)
                existing[name] = match
            else:
                ent = Entity(name=name, entity_type=ent_type, embedding=emb)
                session.add(ent)
                existing[name] = ent
                created_count += 1
        session.flush()

    for raw in raw_entities:
        name_to_ent[raw.name] = existing[raw.name]
    return name_to_ent, created_count


def _ingest_one_file(
    *,
    path: Path,
    root: Path,
    provider: BaseProvider,
    stats: IngestStats,
) -> None:
    raw = path.read_text(encoding="utf-8", errors="replace").strip()
    if not raw:
        return
    folder = _folder_for(path, root)
    title = _extract_title(raw, fallback=path.stem)
    h = _content_hash(raw)
    path_key = str(path.resolve())

    with session_scope() as s:
        existing = s.execute(select(Item).where(Item.path == path_key)).scalar_one_or_none()
        if existing and existing.content_hash == h:
            stats.files_skipped_unchanged += 1
            return

        # Chunk + embed
        chunks_text = chunk_text(raw)
        if not chunks_text:
            return

        # Build prefixed texts for embedding (better retrieval anchoring)
        prefixed = []
        for i, c in enumerate(chunks_text):
            prefix = build_contextual_prefix(
                title=title, folder=folder, chunk_index=i, total_chunks=len(chunks_text),
                section=extract_section_heading(c),
            )
            prefixed.append(prefix + c)

        chunk_embeddings = embed_many(prefixed, provider=provider)
        item_embedding = embed_one(raw[:8000], provider=provider)

        if existing:
            # Replace: delete chunks (cascade kills mentions). Keep entities.
            s.delete(existing)
            s.flush()

        item = Item(
            path=path_key,
            title=title,
            folder=folder,
            content=raw,
            content_hash=h,
            embedding=item_embedding,
        )
        s.add(item)
        s.flush()

        chunk_objs = []
        for i, (c_text, c_emb) in enumerate(zip(chunks_text, chunk_embeddings, strict=True)):
            ch = Chunk(item_id=item.id, chunk_index=i, text=c_text, embedding=c_emb)
            s.add(ch)
            chunk_objs.append(ch)
        s.flush()
        stats.chunks_created += len(chunk_objs)

        # Entities (single call per doc, gated by content quality)
        if not should_index_content(raw):
            stats.files_indexed += 1
            return

        entities = extract_entities_from_text(raw, provider=provider)
        if not entities:
            stats.files_indexed += 1
            return
        ent_map, num_new = _upsert_entities(s, entities, provider=provider)
        stats.entities_created += num_new

        # Distribute mentions across chunks: heuristic — attach each entity to
        # the chunk whose text contains its name, falling back to chunk 0.
        mention_count = 0
        for raw_ent in entities:
            ent = ent_map[raw_ent.name]
            target_chunk = chunk_objs[0]
            for ch in chunk_objs:
                if raw_ent.name.lower() in ch.text.lower():
                    target_chunk = ch
                    break
            try:
                s.add(Mention(
                    chunk_id=target_chunk.id,
                    entity_id=ent.id,
                    importance=raw_ent.importance,
                    context=raw_ent.context[:256] if raw_ent.context else None,
                ))
                mention_count += 1
            except IntegrityError:
                # Duplicate (chunk, entity) pair — composite PK collision. Safe to ignore.
                s.rollback()
                continue
        stats.mentions_created += mention_count
        stats.files_indexed += 1


def ingest_directory(
    path: str | Path,
    *,
    reset: bool = False,
    provider: BaseProvider | None = None,
) -> IngestStats:
    """Walk a directory of markdown files and ingest them.

    Idempotent: re-running on unchanged files is a no-op.
    """
    root = Path(path).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")

    init_db(drop_first=reset)
    provider = provider or get_provider()

    stats = IngestStats()
    files = sorted(root.rglob("*.md"))
    logger.info("[ingest] discovered %d markdown files under %s", len(files), root)

    for f in files:
        stats.files_seen += 1
        try:
            _ingest_one_file(path=f, root=root, provider=provider, stats=stats)
        except Exception as e:
            stats.errors += 1
            logger.exception("[ingest] failed on %s: %s", f, e)

    return stats
