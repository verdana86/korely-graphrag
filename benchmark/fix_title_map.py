"""Rebuild benchmark/bench_nano/title_to_docid.json from nano-graphrag's storage.

My ingest_nano.py precomputed doc IDs via md5 of the raw file bytes, but
nano-graphrag strips/normalises content before hashing internally, so the
IDs I guessed don't match the IDs in kv_store_full_docs.json.

Rebuild the map by matching each file's content against nano's stored
doc content (nano keeps the original text under the "content" key).
"""

from __future__ import annotations

import json
from pathlib import Path


CORPUS = Path("/bench/karpathy")
NANO_DIR = Path("/bench/bench_nano")
OUT = NANO_DIR / "title_to_docid.json"


def main():
    full_docs = json.loads((NANO_DIR / "kv_store_full_docs.json").read_text())

    # nano-graphrag strips whitespace before storing. Match on stripped content.
    content_to_id: dict[str, str] = {}
    for doc_id, rec in full_docs.items():
        content = (rec.get("content") or "").strip()
        content_to_id[content] = doc_id

    files = sorted(CORPUS.glob("*.md")) + sorted(CORPUS.glob("*.markdown"))
    title_to_id: dict[str, str] = {}
    misses: list[str] = []
    for f in files:
        raw = f.read_text(encoding="utf-8", errors="replace").strip()
        doc_id = content_to_id.get(raw)
        if doc_id:
            title_to_id[f.stem] = doc_id
        else:
            misses.append(f.stem)

    OUT.write_text(json.dumps(title_to_id, indent=2, ensure_ascii=False))
    print(f"[done] {len(title_to_id)} titles mapped, {len(misses)} misses")
    if misses:
        print(f"  MISSED: {misses}")


if __name__ == "__main__":
    main()
