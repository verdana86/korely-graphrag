"""Query adapters for the nano-graphrag side of the 3-way benchmark.

We bypass nano-graphrag's response-generation layer (which returns LLM
prose) and go directly to its storage to get structured doc IDs — the
thing benchmark metrics actually need. Specifically:

- `nano_search(query)`: embed the query with Gemini, query nano's
  chunks vector DB directly, dedupe chunks to doc IDs.
- `nano_related(seed_doc_id)`: nano has no `get_related(doc)` primitive,
  so we traverse its networkx graph ourselves — find entities anchored
  to chunks of the seed doc, then rank candidate docs by shared-entity
  overlap (no IDF, no hub filter — bare-bones). This is the minimum
  fair approximation of what korely-graphrag's get_related does.
"""

from __future__ import annotations

import asyncio
import json
from collections import Counter
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np

from nano_adapters import gemini_embed


class NanoSearch:
    """Lazy loader for nano-graphrag's working-dir artifacts.

    Reads once, reuses across queries in the benchmark loop. Avoids
    spinning up the full GraphRAG object (which would also pre-warm
    an LLM client we don't need for retrieval).
    """

    def __init__(self, working_dir: str | Path):
        self.working_dir = Path(working_dir)
        self._chunks: dict[str, dict] | None = None
        self._graph: nx.Graph | None = None
        self._entity_to_chunks: dict[str, list[str]] | None = None
        self._chunk_vectors: dict[str, np.ndarray] | None = None
        self._title_to_docid: dict[str, str] | None = None

    # ── storage loaders ────────────────────────────────────────────

    def _load_chunks(self) -> dict[str, dict]:
        if self._chunks is None:
            with (self.working_dir / "kv_store_text_chunks.json").open() as f:
                self._chunks = json.load(f)
        return self._chunks

    def _load_graph(self) -> nx.Graph:
        if self._graph is None:
            self._graph = nx.read_graphml(self.working_dir / "graph_chunk_entity_relation.graphml")
        return self._graph

    def _load_chunk_vectors(self) -> dict[str, np.ndarray]:
        if self._chunk_vectors is None:
            with (self.working_dir / "vdb_chunks.json").open() as f:
                blob = json.load(f)
            # nano-vectordb layout: {"embedding_dim": N, "data": [...], "matrix": base64}
            # For simplicity we recompute vectors at query time using Gemini
            # against the entity ids. But chunks_vdb.matrix is a base64 numpy
            # array of shape (N_chunks, embedding_dim).
            import base64
            dim = blob["embedding_dim"]
            matrix = np.frombuffer(base64.b64decode(blob["matrix"]), dtype=np.float32).reshape(-1, dim)
            ids = [d["__id__"] for d in blob["data"]]
            self._chunk_vectors = {cid: matrix[i] for i, cid in enumerate(ids)}
        return self._chunk_vectors

    def title_to_docid(self) -> dict[str, str]:
        if self._title_to_docid is None:
            with (self.working_dir / "title_to_docid.json").open() as f:
                self._title_to_docid = json.load(f)
        return self._title_to_docid

    def docid_to_title(self) -> dict[str, str]:
        return {v: k for k, v in self.title_to_docid().items()}

    # ── entity index ──────────────────────────────────────────────

    def _entity_index(self) -> dict[str, list[str]]:
        """entity_name -> [chunk_ids that mention it]."""
        if self._entity_to_chunks is None:
            g = self._load_graph()
            ent_map: dict[str, list[str]] = {}
            # In nano-graphrag's graphml, entity nodes have an attribute
            # 'source_id' containing comma-separated chunk ids where the
            # entity was extracted.
            for node, attrs in g.nodes(data=True):
                src = attrs.get("source_id")
                if not src:
                    continue
                chunks = [c.strip() for c in src.split("<SEP>") if c.strip()]
                if not chunks:
                    chunks = [c.strip() for c in src.split(",") if c.strip()]
                ent_map[node] = chunks
            self._entity_to_chunks = ent_map
        return self._entity_to_chunks

    # ── search ────────────────────────────────────────────────────

    async def search(self, query: str, limit: int = 10) -> list[str]:
        """Return top-N doc IDs most similar to `query` by pure vector
        similarity over nano's chunk embeddings. Mirrors nano's `naive`
        RAG mode but skips the LLM response step.
        """
        vectors = self._load_chunk_vectors()
        if not vectors:
            return []

        query_emb_arr = await gemini_embed([query])
        q = query_emb_arr[0]
        q_norm = np.linalg.norm(q) or 1.0

        # Cosine over precomputed chunk embeddings
        chunk_ids = list(vectors.keys())
        mat = np.stack([vectors[c] for c in chunk_ids])
        mat_norms = np.linalg.norm(mat, axis=1)
        mat_norms[mat_norms == 0] = 1.0
        sims = (mat @ q) / (mat_norms * q_norm)

        # Aggregate chunk hits -> doc hits, keeping the best chunk score per doc
        chunks = self._load_chunks()
        doc_score: dict[str, float] = {}
        for cid, s in zip(chunk_ids, sims):
            doc_id = chunks.get(cid, {}).get("full_doc_id")
            if not doc_id:
                continue
            if s > doc_score.get(doc_id, -1e9):
                doc_score[doc_id] = float(s)

        ranked = sorted(doc_score.items(), key=lambda kv: kv[1], reverse=True)
        return [d for d, _ in ranked[:limit]]

    # ── related (DIY, since nano has no primitive) ────────────────

    def related(self, seed_doc_id: str, limit: int = 10) -> list[str]:
        """Rank other docs by count of entities co-mentioned with the seed.

        1. Gather entities whose source_id chunks include ANY chunk of the
           seed doc.
        2. For each such entity, find OTHER docs that also mention it.
        3. Score each candidate doc by count of overlapping entities.

        No IDF, no hub filtering — that's on purpose. We're measuring
        nano-graphrag as-is, not tuning it.
        """
        chunks = self._load_chunks()
        seed_chunks = {cid for cid, data in chunks.items() if data.get("full_doc_id") == seed_doc_id}
        if not seed_chunks:
            return []

        ent_idx = self._entity_index()

        # Entities of the seed
        seed_entities = [e for e, cs in ent_idx.items() if any(c in seed_chunks for c in cs)]
        if not seed_entities:
            return []

        # Chunks of OTHER docs that mention any seed entity
        doc_overlap: Counter[str] = Counter()
        for ent in seed_entities:
            for cid in ent_idx[ent]:
                if cid in seed_chunks:
                    continue
                doc_id = chunks.get(cid, {}).get("full_doc_id")
                if doc_id and doc_id != seed_doc_id:
                    doc_overlap[doc_id] += 1

        return [d for d, _ in doc_overlap.most_common(limit)]
