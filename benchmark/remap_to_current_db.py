"""Remap questions.jsonl + related_ground_truth.json to match current DB UUIDs.

After a re-ingest, item UUIDs change but titles stay stable. This script:
1. Builds old_uuid -> title map from benchmark/related_review.md (which was
   generated when the corpus was first ingested and contains every UUID+title).
2. Reads the current DB and builds title -> new_uuid map.
3. For each question in questions.jsonl, rewrites ground_truth UUIDs via
   title lookup. Drops questions whose titles are no longer in the DB.
4. For related_ground_truth.json, converts the `related` UUID list via the
   same path and saves a `related_titles` field for future-proofing.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, "/app/src")

from sqlalchemy import text as sql_text  # noqa: E402
from korely_graphrag.storage import session_scope  # noqa: E402


BENCH = Path("/app/benchmark")
REVIEW_MD = BENCH / "related_review.md"
QUESTIONS = BENCH / "questions.jsonl"
GROUND_TRUTH = BENCH / "related_ground_truth.json"

UUID_TITLE_LINE = re.compile(r"`([0-9a-f-]{36})` — \*\*([^*]+)\*\*")


def build_old_uuid_to_title() -> dict[str, str]:
    mp: dict[str, str] = {}
    for line in REVIEW_MD.read_text().splitlines():
        m = UUID_TITLE_LINE.search(line)
        if m:
            mp[m.group(1)] = m.group(2).strip()
    # Also catch seed IDs from "## Seed N/20: <title>" + following "_id: `<uuid>`"
    lines = REVIEW_MD.read_text().splitlines()
    for i, ln in enumerate(lines):
        m_seed = re.match(r"## Seed \d+/\d+: (.+)", ln)
        if m_seed and i + 1 < len(lines):
            title = m_seed.group(1).strip()
            m_id = re.search(r"`([0-9a-f-]{36})`", lines[i + 1])
            if m_id:
                mp[m_id.group(1)] = title
    return mp


def build_title_to_new_uuid() -> dict[str, str]:
    with session_scope() as s:
        rows = s.execute(sql_text("SELECT id::text, title FROM items")).all()
    return {r.title: r.id for r in rows}


def main():
    old_uuid_to_title = build_old_uuid_to_title()
    title_to_new = build_title_to_new_uuid()
    print(f"[maps] old_uuid_to_title: {len(old_uuid_to_title)} entries", file=sys.stderr)
    print(f"[maps] title_to_new_uuid: {len(title_to_new)} entries", file=sys.stderr)

    def remap_uuid(old_uuid: str) -> str | None:
        title = old_uuid_to_title.get(old_uuid)
        if not title:
            return None
        return title_to_new.get(title)

    # ---- questions.jsonl ----
    qs = [json.loads(l) for l in QUESTIONS.read_text().splitlines() if l.strip()]
    new_qs = []
    dropped = 0
    for q in qs:
        old_gt = q.get("ground_truth") or []
        # Prefer ground_truth_titles if present (precision@1/recall@5 path).
        gt_titles = q.get("ground_truth_titles")
        if gt_titles:
            new_gt = [title_to_new[t] for t in gt_titles if t in title_to_new]
        else:
            # Related path: map each UUID via title
            new_gt = []
            for u in old_gt:
                new_u = remap_uuid(u)
                if new_u:
                    new_gt.append(new_u)
                else:
                    # Try: if the old UUID already matches a new DB item (no-op remap)
                    pass
        if not new_gt:
            print(f"  [drop q{q['id']}] no mappable ground truth", file=sys.stderr)
            dropped += 1
            continue
        q["ground_truth"] = new_gt
        # Also remap seed_item_id for related questions
        if q["type"] == "related" and "seed_item_id" in q:
            new_seed = remap_uuid(q["seed_item_id"])
            if not new_seed and q.get("seed_item_title"):
                new_seed = title_to_new.get(q["seed_item_title"])
            if new_seed:
                q["seed_item_id"] = new_seed
            else:
                print(f"  [drop q{q['id']}] seed item not remappable", file=sys.stderr)
                dropped += 1
                continue
        new_qs.append(q)

    QUESTIONS.write_text("\n".join(json.dumps(q, ensure_ascii=False) for q in new_qs) + "\n")
    print(f"\n[questions.jsonl] rewrote {len(new_qs)} questions, dropped {dropped}", file=sys.stderr)

    # ---- related_ground_truth.json ----
    gt = json.loads(GROUND_TRUTH.read_text())
    for seed in gt["seeds"]:
        new_seed_id = remap_uuid(seed["seed_id"]) or title_to_new.get(seed["seed_title"])
        if not new_seed_id:
            print(f"  [seed skip] '{seed['seed_title']}' not in current DB", file=sys.stderr)
            continue
        seed["seed_id"] = new_seed_id
        new_related_ids = []
        new_related_titles = []
        for u in seed.get("related", []):
            title = old_uuid_to_title.get(u)
            if title and title in title_to_new:
                new_related_ids.append(title_to_new[title])
                new_related_titles.append(title)
        seed["related"] = new_related_ids
        seed["related_titles"] = new_related_titles
    GROUND_TRUTH.write_text(json.dumps(gt, indent=2, ensure_ascii=False))
    print(f"[related_ground_truth.json] refreshed UUIDs + stored titles for future re-ingest", file=sys.stderr)


if __name__ == "__main__":
    main()
