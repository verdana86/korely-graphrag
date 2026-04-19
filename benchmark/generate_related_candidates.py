"""Generate human-reviewable 'related' ground-truth candidates.

Fix for circular benchmark: current questions.jsonl builds ground truth for
'related' questions by calling get_related_items() — i.e. the system under
test. This script breaks the circle: ground truth is proposed by Gemini
given only titles + abstracts (no entity graph, no retrieval), and then
human-reviewed by the user.

Output: benchmark/related_review.md (markdown checklist for the user).
After the user edits it, run build_related_questions.py to patch
questions.jsonl.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, "/app/src")

from sqlalchemy import text as sql_text  # noqa: E402

from korely_graphrag.providers.base import get_provider  # noqa: E402
from korely_graphrag.storage import session_scope  # noqa: E402


OUT_PATH = Path("/app/benchmark/related_review.md")
SEEDS_JSON_PATH = Path("/app/benchmark/related_seeds.json")
TARGET_N_SEEDS = 20
ABSTRACT_CHARS = 500


RELATED_SYSTEM = (
    "You are judging thematic relatedness between blog posts for a retrieval "
    "benchmark ground-truth. You MUST reason only from the titles and abstracts "
    "shown to you. Do NOT invent connections; only mark a post as related if the "
    "abstracts make the thematic link evident. Return strict JSON: "
    '{"related": [{"item_id": "...", "reason": "..."}], '
    '"rejected": [{"item_id": "...", "reason": "..."}]}.'
)

RELATED_USER_TEMPLATE = """SEED POST
id: {seed_id}
title: {seed_title}
abstract:
\"\"\"{seed_abstract}\"\"\"

CANDIDATE POSTS (rate each)
{candidates}

Task: for each candidate, decide if it is THEMATICALLY RELATED to the seed.
'Related' means: same topic family, same technique applied in a different
domain, continuation of the same argument, or sharing a non-trivial named
entity (technology, concept, person) that is central to BOTH posts.

STRICT rules:
- Same author mentioned in both abstracts is NOT sufficient (authors are
  structurally ubiquitous on a single-author blog).
- Same broad field (e.g. 'neural networks') is NOT sufficient; the link
  must be specific.
- It is perfectly valid to reject all candidates if none truly fit.
- Prefer precision over recall; better to miss a marginal link than to
  invent one.

Return the JSON with two arrays:
- "related": candidates you accept as thematically linked (with 1-sentence reason)
- "rejected": the rest (with 1-sentence reason why not)

Respond with ONLY the JSON object."""


def _extract_json(raw: str) -> dict:
    from korely_graphrag.ingest.entity_extractor import (
        _repair_truncated_json,
        _sanitize_json_string,
        _strip_code_fence,
    )
    raw = _strip_code_fence((raw or "").strip())
    raw = _sanitize_json_string(raw)
    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end > start:
        raw = raw[start : end + 1]
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        repaired = _repair_truncated_json(raw)
        if repaired:
            return json.loads(repaired)
        raise


def main():
    provider = get_provider()

    with session_scope() as s:
        rows = s.execute(sql_text("""
            SELECT i.id::text AS id, i.title, i.content,
                   COALESCE((
                       SELECT COUNT(*)
                       FROM mentions m
                       JOIN chunks c ON c.id = m.chunk_id
                       WHERE c.item_id = i.id
                   ), 0) AS mention_count
            FROM items i
            ORDER BY mention_count DESC, i.updated_at DESC
        """)).all()

    items = [{
        "id": r.id,
        "title": r.title,
        "abstract": (r.content or "")[:ABSTRACT_CHARS].replace("\n", " ").strip(),
        "mention_count": r.mention_count,
    } for r in rows]

    # Pick seeds: top N by mention count that have at least 2 mentions.
    # This gives a realistic stress-test: seeds with SOMETHING to relate to.
    candidate_seeds = [it for it in items if it["mention_count"] >= 2]
    seeds = candidate_seeds[:TARGET_N_SEEDS]
    print(f"[seeds] picked {len(seeds)}/{len(candidate_seeds)} eligible seeds", file=sys.stderr)

    # For each seed, ask Gemini over ALL other items (titles+abstracts).
    output_sections: list[str] = []
    seed_records: list[dict] = []

    for idx, seed in enumerate(seeds, 1):
        others = [it for it in items if it["id"] != seed["id"]]
        candidates_block = "\n".join(
            f"- id: {o['id']}\n  title: {o['title']}\n  abstract: \"{o['abstract']}\""
            for o in others
        )
        user_msg = RELATED_USER_TEMPLATE.format(
            seed_id=seed["id"],
            seed_title=seed["title"],
            seed_abstract=seed["abstract"],
            candidates=candidates_block,
        )

        print(f"[{idx}/{len(seeds)}] {seed['title'][:60]}...", file=sys.stderr)
        try:
            result = provider.complete(
                system=RELATED_SYSTEM,
                user=user_msg,
                max_tokens=4096,
                temperature=0.2,
                json_mode=True,
            )
            data = _extract_json(result.text or "")
        except Exception as e:
            print(f"  ! failed: {e}", file=sys.stderr)
            data = {"related": [], "rejected": []}

        related = data.get("related") or []
        rejected = data.get("rejected") or []

        # Build lookup for titles by id
        title_by_id = {it["id"]: it["title"] for it in items}

        sec: list[str] = []
        sec.append(f"## Seed {idx}/{len(seeds)}: {seed['title']}")
        sec.append(f"_id: `{seed['id']}` · mentions in graph: {seed['mention_count']}_")
        sec.append("")
        sec.append(f"> {seed['abstract'][:300]}...")
        sec.append("")
        sec.append("**Gemini proposes these as RELATED** — tick [x] to KEEP, clear [ ] to DROP:")
        sec.append("")
        if not related:
            sec.append("_(Gemini found no related posts — leave empty, or add manually at bottom)_")
            sec.append("")
        for r in related:
            rid = r.get("item_id") or ""
            reason = (r.get("reason") or "").strip()
            title = title_by_id.get(rid, "(unknown id)")
            sec.append(f"- [x] `{rid}` — **{title}**")
            sec.append(f"  - _reason: {reason}_")
        sec.append("")
        sec.append("**Rejected by Gemini — tick [x] to ADD (override)**:")
        sec.append("")
        for r in rejected[:10]:  # top 10 rejected to keep the doc short
            rid = r.get("item_id") or ""
            reason = (r.get("reason") or "").strip()
            title = title_by_id.get(rid, "(unknown id)")
            sec.append(f"- [ ] `{rid}` — **{title}**")
            sec.append(f"  - _rejected because: {reason}_")
        sec.append("")
        sec.append("---")
        sec.append("")

        output_sections.append("\n".join(sec))

        seed_records.append({
            "seed_id": seed["id"],
            "seed_title": seed["title"],
            "proposed_related": [r.get("item_id") for r in related if r.get("item_id")],
            "proposed_rejected": [r.get("item_id") for r in rejected if r.get("item_id")],
        })

        time.sleep(0.6)  # rate limit

    # Write review markdown
    header = [
        "# Related-questions ground truth — human review",
        "",
        f"**Generated:** Gemini proposals over {len(seeds)} seed posts. You review the checkboxes.",
        "",
        "**How to use:**",
        "1. For each seed, read the abstract and the proposed links.",
        "2. Keep `[x]` only the truly related posts. Untick `[ ]` anything weak.",
        "3. In the 'Rejected' section, tick `[x]` any post Gemini wrongly rejected that you think IS related.",
        "4. Save the file. Then run `build_related_questions.py` to patch the benchmark.",
        "",
        "**Discipline:** precision over recall. Marginal links hurt the ground truth.",
        "",
        "---",
        "",
    ]
    OUT_PATH.write_text("\n".join(header) + "\n".join(output_sections))

    SEEDS_JSON_PATH.write_text(json.dumps(seed_records, indent=2, ensure_ascii=False))

    print(f"\n[done] {len(seeds)} seeds written to {OUT_PATH}", file=sys.stderr)
    print(f"       raw seed records: {SEEDS_JSON_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
