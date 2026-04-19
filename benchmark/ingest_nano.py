"""Ingest the Karpathy corpus into nano-graphrag with Gemini.

nano-graphrag indexes the 24 markdown posts into its own file-based store
(`bench_nano/` working dir). We also write `bench_nano/title_to_docid.json`
so downstream benchmark queries can map human-readable titles to the md5
doc IDs nano-graphrag invents internally.

Runs inside the isolated `nano` compose service:
    docker compose --profile benchmark run --rm nano python ingest_nano.py
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

from nano_graphrag import GraphRAG

sys.path.insert(0, str(Path(__file__).parent))
from nano_adapters import gemini_complete, gemini_embed, repair_json


CORPUS_DIR = Path("/bench/karpathy")
WORKING_DIR = Path("/bench/bench_nano")
TITLE_MAP_PATH = WORKING_DIR / "title_to_docid.json"


def _title_from_filename(p: Path) -> str:
    """Same title convention korely-graphrag uses (strip .md / .markdown).

    Keeps the two systems comparable when ground truth is matched by title.
    """
    return p.stem


def main() -> None:
    if not CORPUS_DIR.exists():
        print(f"ERROR: corpus dir not found: {CORPUS_DIR}", file=sys.stderr)
        print("Hint: mount it at /bench/karpathy (see docker-compose.yml `nano` service).", file=sys.stderr)
        sys.exit(1)

    WORKING_DIR.mkdir(parents=True, exist_ok=True)

    graph = GraphRAG(
        working_dir=str(WORKING_DIR),
        best_model_func=gemini_complete,
        cheap_model_func=gemini_complete,
        embedding_func=gemini_embed,
        convert_response_to_json_func=repair_json,
        enable_naive_rag=True,  # for precision@1 / recall@5 vector baselines
        best_model_max_async=4,  # conservative: avoid Gemini 429s on free tier
        cheap_model_max_async=4,
        embedding_batch_num=16,
        embedding_func_max_async=4,
    )

    files = sorted(CORPUS_DIR.glob("*.md")) + sorted(CORPUS_DIR.glob("*.markdown"))
    print(f"[ingest_nano] found {len(files)} files in {CORPUS_DIR}", file=sys.stderr)

    title_to_docid: dict[str, str] = {}
    for i, f in enumerate(files, 1):
        title = _title_from_filename(f)
        raw = f.read_text(encoding="utf-8", errors="replace")
        # nano-graphrag keys docs by md5 of content. We recompute the same
        # hash so we can map title -> doc_id without relying on internals.
        doc_id = "doc-" + hashlib.md5(raw.encode("utf-8")).hexdigest()
        title_to_docid[title] = doc_id

        print(f"  [{i:>2}/{len(files)}] {title} ({len(raw)} chars)", file=sys.stderr)
        graph.insert(raw)

    TITLE_MAP_PATH.write_text(json.dumps(title_to_docid, indent=2, ensure_ascii=False))
    print(f"\n[done] ingested {len(files)} docs into {WORKING_DIR}", file=sys.stderr)
    print(f"       title map: {TITLE_MAP_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
