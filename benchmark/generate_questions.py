"""Generate a benchmark question set from the ingested Karpathy corpus.

Strategy:
1. For each post in DB → ask Gemini to produce 2 single-post ground-truth
   questions (one factual, one conceptual). Ground truth = that post's id.
2. For entities mentioned in 3-5 distinct posts → ask Gemini to produce a
   multi-post question where the answer requires those posts. Ground truth =
   the set of posts that mention the entity with high importance.
3. For each of the 3 most-connected posts (by shared-entity count) → one
   "related to X?" question. Ground truth = top-N graph neighbors.

Output: benchmark/questions.jsonl (one JSON object per line).
"""

from __future__ import annotations

import json
import os
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, "/app/src")

from sqlalchemy import bindparam, text as sql_text  # noqa: E402

from korely_graphrag.providers.base import get_provider  # noqa: E402
from korely_graphrag.search import get_related_items  # noqa: E402
from korely_graphrag.storage import (  # noqa: E402
    Entity,
    Item,
    session_scope,
)


OUT_PATH = Path("/app/benchmark/questions.jsonl")


SINGLE_POST_SYSTEM = (
    "You design retrieval benchmark questions from a blog post. "
    "The questions must be answerable ONLY by retrieving this specific post — "
    "they must be SPECIFIC enough that a reasonable RAG system would not confuse "
    "this post with a sibling post about a related topic. "
    "Return strict JSON: {\"questions\": [\"q1\", \"q2\"]}."
)

SINGLE_POST_USER_TEMPLATE = """Post title: {title}
Post content (first 3000 chars):
\"\"\"{content}\"\"\"

Generate 2 questions:
1. A FACTUAL question about a specific claim, number, anecdote, code snippet, or named item
   unique to this post. The question must NOT mention the post's title or obvious keywords
   from the title. Example shape: "Which post argues that..." / "Which post describes..."
2. A CONCEPTUAL question about the central argument or recommendation of the post.
   Same rules: no title keywords.

Rules:
- Each question 10-25 words.
- Do NOT use generic phrasing that would match many posts ("Which post talks about neural networks?" is BAD).
- The questions must uniquely identify this post if the retriever is decent.
- Respond with ONLY the JSON object."""


MULTI_POST_SYSTEM = (
    "You design retrieval benchmark questions that test cross-post recall. "
    "Given an entity shared by several posts, write ONE question whose best answers "
    "are exactly those posts. "
    "Return strict JSON: {\"question\": \"...\", \"rationale\": \"...\"}."
)

MULTI_POST_USER_TEMPLATE = """Entity: {entity_name} ({entity_type})
Posts that mention this entity:
{post_summaries}

Write ONE question whose ideal answer is the union of these posts.
Example: if all posts mention "gradient descent", question could be "Which posts discuss optimization convergence issues?"

Rules:
- Question 10-25 words.
- Do NOT name the entity directly (that would be too easy).
- The question should require connecting the shared theme across posts.
- Respond with ONLY the JSON object."""


def _extract_json(raw: str) -> dict:
    """Robust JSON extraction: strips fences, repairs truncation, finds first {..}."""
    from korely_graphrag.ingest.entity_extractor import (
        _repair_truncated_json,
        _sanitize_json_string,
        _strip_code_fence,
    )
    raw = _strip_code_fence((raw or "").strip())
    raw = _sanitize_json_string(raw)
    # Find first '{' and last '}'
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


def generate_single_post_questions(provider, item) -> list[str]:
    content = (item.content or "")[:3000]
    user = SINGLE_POST_USER_TEMPLATE.format(title=item.title, content=content)
    try:
        result = provider.complete(
            system=SINGLE_POST_SYSTEM, user=user,
            max_tokens=1024, temperature=0.5, json_mode=True,
        )
        raw = result.text or ""
        try:
            data = _extract_json(raw)
        except Exception:
            print(f"  ! raw (first 300c) for {item.title[:40]}: {raw[:300]!r}", file=sys.stderr)
            return []
        return [q.strip() for q in (data.get("questions") or []) if q and q.strip()][:2]
    except Exception as e:
        print(f"  ! failed for {item.title}: {e}", file=sys.stderr)
        return []


def generate_multi_post_question(provider, entity_name, entity_type, posts) -> str | None:
    summaries = "\n".join(
        f"- [{p.id}] {p.title}: {(p.content or '')[:200]}..." for p in posts
    )
    user = MULTI_POST_USER_TEMPLATE.format(
        entity_name=entity_name, entity_type=entity_type, post_summaries=summaries,
    )
    try:
        result = provider.complete(
            system=MULTI_POST_SYSTEM, user=user,
            max_tokens=800, temperature=0.5, json_mode=True,
        )
        raw = result.text or ""
        try:
            data = _extract_json(raw)
        except Exception:
            print(f"  ! multi-post raw (first 200c) for {entity_name}: {raw[:200]!r}", file=sys.stderr)
            return None
        q = (data.get("question") or "").strip()
        return q if q else None
    except Exception as e:
        print(f"  ! multi-post gen failed for {entity_name}: {e}", file=sys.stderr)
        return None


def main():
    provider = get_provider()

    all_questions = []
    q_id = 0

    # ---------------------------------------------------------------------
    # Phase 1: single-post questions (up to 2 per post × 24 posts = 48)
    # We'll use only ~1 per post (random pick of factual OR conceptual) to
    # keep total around 30.
    # ---------------------------------------------------------------------
    with session_scope() as s:
        items = s.execute(sql_text("SELECT id, title, content FROM items ORDER BY updated_at DESC")).all()

    print(f"[phase 1] generating single-post questions for {len(items)} posts...", file=sys.stderr)
    for i, item in enumerate(items, 1):
        with session_scope() as s:
            item_obj = s.get(Item, item.id)
            questions = generate_single_post_questions(provider, item_obj)
        for q in questions:
            q_id += 1
            all_questions.append({
                "id": q_id,
                "type": "precision@1",
                "question": q,
                "ground_truth": [str(item.id)],
                "ground_truth_titles": [item.title],
            })
        print(f"  [{i}/{len(items)}] {item.title[:50]}: {len(questions)} q", file=sys.stderr)
        time.sleep(0.5)  # gentle on quota

    # ---------------------------------------------------------------------
    # Phase 2: multi-post questions (entities in 3-5 posts)
    # ---------------------------------------------------------------------
    print("\n[phase 2] picking entities shared by 3-5 posts...", file=sys.stderr)
    with session_scope() as s:
        shared_entity_rows = s.execute(sql_text("""
            SELECT e.name, e.entity_type,
                   COUNT(DISTINCT c.item_id) AS doc_count,
                   ARRAY_AGG(DISTINCT c.item_id::text) AS item_ids
            FROM entities e
            JOIN mentions m ON m.entity_id = e.id
            JOIN chunks c ON c.id = m.chunk_id
            WHERE e.entity_type IN ('technology', 'concept', 'topic', 'location')
            GROUP BY e.id, e.name, e.entity_type
            HAVING COUNT(DISTINCT c.item_id) BETWEEN 2 AND 4
            ORDER BY doc_count DESC, RANDOM()
            LIMIT 20
        """)).all()

    # Generate up to 15 multi-post questions
    target_multi = 15
    random.seed(42)
    random.shuffle(list(shared_entity_rows))
    multi_generated = 0
    for row in shared_entity_rows:
        if multi_generated >= target_multi:
            break
        item_ids = row.item_ids
        with session_scope() as s:
            posts = [s.get(Item, iid) for iid in item_ids]
        q = generate_multi_post_question(provider, row.name, row.entity_type, posts)
        if not q:
            continue
        q_id += 1
        all_questions.append({
            "id": q_id,
            "type": "recall@5",
            "question": q,
            "ground_truth": [str(iid) for iid in item_ids],
            "ground_truth_titles": [p.title for p in posts],
            "seed_entity": row.name,
        })
        multi_generated += 1
        print(f"  multi {multi_generated}/{target_multi}: [{row.name}] {q[:60]}", file=sys.stderr)
        time.sleep(0.5)

    # ---------------------------------------------------------------------
    # Phase 3: related-to questions (5 posts with richest graph neighborhood)
    # ---------------------------------------------------------------------
    print("\n[phase 3] generating related-to questions...", file=sys.stderr)
    with session_scope() as s:
        # Pick 5 items with most mentions (likely richest graph neighborhoods)
        rich_rows = s.execute(sql_text("""
            SELECT i.id::text AS id, i.title
            FROM items i
            JOIN chunks c ON c.item_id = i.id
            JOIN mentions m ON m.chunk_id = c.id
            GROUP BY i.id, i.title
            ORDER BY COUNT(m.*) DESC
            LIMIT 5
        """)).all()

        for row in rich_rows:
            related = get_related_items(row.id, session=s, limit=5)
            if len(related) < 2:
                continue  # not enough graph neighbors to be meaningful
            q_id += 1
            all_questions.append({
                "id": q_id,
                "type": "related",
                "question": f"Which posts are thematically related to \"{row.title}\"?",
                "ground_truth": [r.item_id for r in related],
                "ground_truth_titles": [r.title for r in related],
                "seed_item_id": row.id,
                "seed_item_title": row.title,
            })
            print(f"  related for '{row.title[:40]}': {len(related)} neighbors", file=sys.stderr)

    # ---------------------------------------------------------------------
    # Save
    # ---------------------------------------------------------------------
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        for q in all_questions:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")

    print(f"\n[done] wrote {len(all_questions)} questions to {OUT_PATH}", file=sys.stderr)
    by_type = {}
    for q in all_questions:
        by_type[q["type"]] = by_type.get(q["type"], 0) + 1
    print(f"       by type: {by_type}", file=sys.stderr)


if __name__ == "__main__":
    main()
