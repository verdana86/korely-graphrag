"""Validate the 3 fixes in-place on a populated knowledge base."""

import sys
sys.path.insert(0, "/app/src")

from korely_graphrag.mcp_server import tools  # noqa: E402


def main() -> None:
    # FIX #3 — titles
    print("### FIX #3 — titles (should be real article titles, not inline-code H1s):")
    notes = tools.list_notes(limit=30)["items"]
    for n in notes:
        fname = n["path"].split("/")[-1]
        print(f"  {fname:60s} -> {n['title']}")

    # FIX #1 — get_related should NOT be dominated by hub-nodes
    rnn = next(n for n in notes if "rnn" in n["path"].lower() or "recurrent" in n["title"].lower())
    print(f"\n### FIX #1 — get_related({rnn['title']}):")
    rel = tools.get_related(rnn["id"], limit=8)
    if not rel["results"]:
        print("  (no related — means everything was filtered as hub-node)")
    for r in rel["results"]:
        shared = ", ".join(r["shared_entities"])
        print(f"  score={r['score']:.2f}  shared=[{shared}]  -> {r['title'][:70]}")

    # FIX #2 — dedup: list person entities and look for Karpathy
    print("\n### FIX #2 — person entities (should NOT have both 'Karpathy' and 'Andrej Karpathy'):")
    from sqlalchemy import select
    from korely_graphrag.storage import Entity, session_scope

    with session_scope() as s:
        rows = s.execute(
            select(Entity.name).where(Entity.entity_type == "person").order_by(Entity.name)
        ).all()
    persons = [r[0] for r in rows]
    print(f"  {persons}")

    # Search still works
    print("\n### search sanity checks:")
    for q in ["recurrent neural networks", "reinforcement learning Pong", "training tricks"]:
        out = tools.search(q, limit=3)
        print(f"\n  query={q!r}")
        for r in out["results"]:
            print(f"    {r['score']:.3f}  -> {r['title'][:60]}")


if __name__ == "__main__":
    main()
