"""Run nano-graphrag predictions for every question, dump to JSONL.

Runs inside the isolated `nano` docker service (see docker-compose.yml).
Produces `nano_predictions.jsonl` with one record per question:

    {"id": 60, "type": "related", "predicted": ["doc-...", ...], "latency_s": 0.041}

The main `run_benchmark.py` (app container) reads this file and joins it
in as a third system column next to vanilla and graphrag — keeps the
nano-graphrag dep chain out of the main app image.
"""

from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, "/bench")
from nano_search import NanoSearch


QUESTIONS = Path("/bench/questions.jsonl")
OUT = Path("/bench/nano_predictions.jsonl")
WORKING_DIR = Path("/bench/bench_nano")


def _resolve_seed_docid(ns: NanoSearch, q: dict) -> str | None:
    """Map a `related` question's seed to a nano doc ID.

    Our `questions.jsonl` carries `seed_item_id` (a korely-graphrag UUID)
    and `seed_item_title` (filename stem). nano-graphrag indexes by md5
    of content — so the title is the only bridge we have.
    """
    title = q.get("seed_item_title")
    if not title:
        return None
    return ns.title_to_docid().get(title)


def _resolve_truth_titles_to_docids(ns: NanoSearch, q: dict) -> set[str]:
    """Convert ground-truth titles (present on every question) to nano IDs."""
    t2d = ns.title_to_docid()
    titles = q.get("ground_truth_titles") or []
    if titles:
        return {t2d[t] for t in titles if t in t2d}
    # For related questions the GT is in `ground_truth` (korely UUIDs).
    # We don't have a direct UUID->title bridge on the nano side, so the
    # caller should only use this set when titles are present.
    return set()


async def main() -> None:
    if not QUESTIONS.exists():
        print(f"ERROR: {QUESTIONS} not found (copy from app container).", file=sys.stderr)
        sys.exit(1)

    if not WORKING_DIR.exists():
        print(f"ERROR: {WORKING_DIR} not found. Run ingest_nano.py first.", file=sys.stderr)
        sys.exit(1)

    ns = NanoSearch(WORKING_DIR)
    questions = [json.loads(l) for l in QUESTIONS.read_text().splitlines() if l.strip()]
    print(f"[run_nano] {len(questions)} questions", file=sys.stderr)

    records: list[dict] = []
    for q in questions:
        t0 = time.perf_counter()
        try:
            if q["type"] == "related":
                seed_id = _resolve_seed_docid(ns, q)
                predicted = ns.related(seed_id, limit=10) if seed_id else []
            else:
                predicted = await ns.search(q["question"], limit=10)
        except Exception as e:
            print(f"  ! Q{q['id']} failed: {e}", file=sys.stderr)
            predicted = []

        latency = time.perf_counter() - t0
        records.append({
            "id": q["id"],
            "type": q["type"],
            "predicted": predicted[:10],
            "latency_s": round(latency, 3),
        })
        # Minimal progress logging — ranking is what matters, not the prose
        print(f"  Q{q['id']:>3} ({q['type']:11s}) n={len(predicted):>2} t={latency*1000:>4.0f}ms", file=sys.stderr)

    OUT.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n")
    print(f"\n[done] wrote {len(records)} predictions to {OUT}", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
