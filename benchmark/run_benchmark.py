"""Run the benchmark: vanilla RAG vs korely-graphrag on the same corpus.

- **Vanilla RAG** (`vanilla`): FTS + pgvector + RRF, NO entity graph, NO
  get_related. Same chunks and embeddings as korely-graphrag — the only
  difference is the ranking is pure cosine/FTS without IDF-weighted entity
  traversal. For "related" questions: fall back to search on title.
- **korely-graphrag** (`graphrag`): full stack.

Output:
- benchmark/results.jsonl (per-question per-system)
- benchmark/BENCHMARK.md (aggregated, human-readable)
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from statistics import mean, median

sys.path.insert(0, "/app/src")

from sqlalchemy import bindparam, text as sql_text  # noqa: E402

from korely_graphrag.ingest.embedder import embed_one  # noqa: E402
from korely_graphrag.mcp_server import tools  # noqa: E402
from korely_graphrag.search import get_related_items  # noqa: E402
from korely_graphrag.search.hybrid import _sanitize_tsquery_terms  # noqa: E402
from korely_graphrag.storage import Item, session_scope  # noqa: E402


QUESTIONS_PATH = Path("/app/benchmark/questions.jsonl")
RESULTS_PATH = Path("/app/benchmark/results.jsonl")
REPORT_PATH = Path("/app/BENCHMARK.md")


# ---------------------------------------------------------------------------
# Systems under test
# ---------------------------------------------------------------------------


def _vanilla_rag_search(query: str, limit: int = 10) -> list[str]:
    """FTS + pgvector with RRF but NO entity graph, NO IDF. The simplest
    possible RAG baseline, as any LangChain-default setup would produce.
    """
    with session_scope() as s:
        # Identical to korely-graphrag's hybrid_search without the graph path.
        try:
            q_emb = embed_one(query)
        except Exception:
            q_emb = None

        # FTS (sanitized tokens only)
        terms = _sanitize_tsquery_terms(query)
        tsquery = " & ".join(f"{w}:*" for w in terms) if terms else ""
        fts_rows = []
        if tsquery:
            fts_rows = s.execute(
                sql_text(
                    "SELECT item_id::text, ROW_NUMBER() OVER (ORDER BY ts_rank(fts, to_tsquery('simple', :q)) DESC) AS rank "
                    "FROM chunks WHERE fts @@ to_tsquery('simple', :q) "
                    "ORDER BY rank LIMIT :lim"
                ).bindparams(bindparam("q", value=tsquery), bindparam("lim", value=limit * 3))
            ).all()

        vec_rows = []
        if q_emb:
            vec_rows = s.execute(
                sql_text(
                    "SELECT item_id::text, ROW_NUMBER() OVER (ORDER BY embedding <=> CAST(:emb AS vector)) AS rank "
                    "FROM chunks WHERE embedding IS NOT NULL ORDER BY rank LIMIT :lim"
                ).bindparams(bindparam("emb", value=str(q_emb)), bindparam("lim", value=limit * 3))
            ).all()

        # RRF at item level
        item_score: dict[str, float] = {}
        for rows in (fts_rows, vec_rows):
            seen_items: set[str] = set()
            for r in rows:
                if r.item_id in seen_items:
                    continue
                seen_items.add(r.item_id)
                item_score[r.item_id] = item_score.get(r.item_id, 0.0) + 1.0 / (60 + r.rank)
        ranked = sorted(item_score.items(), key=lambda kv: kv[1], reverse=True)[:limit]
        return [iid for iid, _ in ranked]


def _vanilla_rag_related(item_id: str, limit: int = 10) -> list[str]:
    """No graph → use the item's title as a search query."""
    with session_scope() as s:
        item = s.get(Item, item_id)
        if not item:
            return []
        return _vanilla_rag_search(item.title, limit=limit)[:limit]


def query_vanilla(q: dict) -> tuple[list[str], float]:
    t0 = time.perf_counter()
    if q["type"] == "related":
        ids = _vanilla_rag_related(q["seed_item_id"], limit=10)
    else:
        ids = _vanilla_rag_search(q["question"], limit=10)
    return ids, time.perf_counter() - t0


def query_graphrag(q: dict) -> tuple[list[str], float]:
    t0 = time.perf_counter()
    if q["type"] == "related":
        out = tools.get_related(q["seed_item_id"], limit=10)
        ids = [r["item_id"] for r in out.get("results", [])]
    else:
        out = tools.search(q["question"], limit=10)
        ids = [r["item_id"] for r in out.get("results", [])]
    return ids, time.perf_counter() - t0


SYSTEMS = {
    "vanilla": query_vanilla,
    "graphrag": query_graphrag,
}


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def precision_at_k(predicted: list[str], truth: set[str], k: int) -> float:
    top = predicted[:k]
    if not top:
        return 0.0
    return sum(1 for p in top if p in truth) / k


def recall_at_k(predicted: list[str], truth: set[str], k: int) -> float:
    if not truth:
        return 0.0
    return sum(1 for p in predicted[:k] if p in truth) / len(truth)


def hit_at_k(predicted: list[str], truth: set[str], k: int) -> int:
    return 1 if any(p in truth for p in predicted[:k]) else 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    questions = [json.loads(l) for l in QUESTIONS_PATH.read_text().splitlines()]
    results = []

    for q in questions:
        truth = set(q["ground_truth"])
        row: dict = {"id": q["id"], "type": q["type"], "question": q["question"]}
        for sys_name, fn in SYSTEMS.items():
            try:
                predicted, latency = fn(q)
            except Exception as e:
                print(f"  ! {sys_name} failed on Q{q['id']}: {e}", file=sys.stderr)
                predicted, latency = [], 0.0
            row[f"{sys_name}_predicted"] = predicted[:10]
            row[f"{sys_name}_latency_s"] = round(latency, 3)
            row[f"{sys_name}_p@1"] = precision_at_k(predicted, truth, 1)
            row[f"{sys_name}_p@5"] = precision_at_k(predicted, truth, 5)
            row[f"{sys_name}_r@5"] = recall_at_k(predicted, truth, 5)
            row[f"{sys_name}_hit@5"] = hit_at_k(predicted, truth, 5)
        results.append(row)
        print(
            f"Q{q['id']:3d} ({q['type']:12s}): "
            f"vanilla p@1={row['vanilla_p@1']:.0f} hit@5={row['vanilla_hit@5']} | "
            f"graphrag p@1={row['graphrag_p@1']:.0f} hit@5={row['graphrag_hit@5']}",
            file=sys.stderr,
        )

    RESULTS_PATH.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in results) + "\n")

    # Aggregate
    agg = _aggregate(results)
    _write_report(agg, results)

    print("\n" + "=" * 70, file=sys.stderr)
    print(f"Saved: {RESULTS_PATH}", file=sys.stderr)
    print(f"Saved: {REPORT_PATH}", file=sys.stderr)


def _aggregate(results: list[dict]) -> dict:
    by_type = {}
    for r in results:
        t = r["type"]
        by_type.setdefault(t, []).append(r)

    def _agg(rows, key):
        vals = [r[key] for r in rows]
        return {"mean": round(mean(vals), 3), "median": round(median(vals), 3), "n": len(vals)}

    agg = {"overall": {}, "by_type": {}}
    for sys_name in SYSTEMS.keys():
        agg["overall"][sys_name] = {
            "p@1": _agg(results, f"{sys_name}_p@1"),
            "p@5": _agg(results, f"{sys_name}_p@5"),
            "r@5": _agg(results, f"{sys_name}_r@5"),
            "hit@5": _agg(results, f"{sys_name}_hit@5"),
            "latency_s": _agg(results, f"{sys_name}_latency_s"),
        }
    for t, rows in by_type.items():
        agg["by_type"][t] = {}
        for sys_name in SYSTEMS.keys():
            agg["by_type"][t][sys_name] = {
                "p@1": _agg(rows, f"{sys_name}_p@1"),
                "p@5": _agg(rows, f"{sys_name}_p@5"),
                "r@5": _agg(rows, f"{sys_name}_r@5"),
                "hit@5": _agg(rows, f"{sys_name}_hit@5"),
                "latency_s": _agg(rows, f"{sys_name}_latency_s"),
            }
    return agg


def _write_report(agg: dict, results: list[dict]):
    lines = []
    lines.append("# Benchmark — korely-graphrag vs vanilla RAG")
    lines.append("")
    lines.append("**Corpus:** 24 public blog posts from Andrej Karpathy's github.io")
    lines.append(f"(reproducible: `git clone https://github.com/karpathy/karpathy.github.io`).")
    lines.append("")
    lines.append(f"**Questions:** {len(results)} — ground-truth generated with Gemini,")
    lines.append("human-reviewed, drops ambiguous cases. Mix of 3 types:")
    lines.append("- **precision@1**: specific question that should uniquely identify one post")
    lines.append("- **recall@5**: cross-post question whose best answers are multiple posts")
    lines.append("- **related**: \"what posts are thematically linked to X?\" — graph-specific")
    lines.append("")
    lines.append("**Systems under test:**")
    lines.append("- `vanilla`: FTS + pgvector + RRF over the *same* chunks and embeddings,")
    lines.append("  with **no entity graph** and no IDF weighting. This is the default you get")
    lines.append("  from LangChain / LlamaIndex with a pgvector store.")
    lines.append("- `graphrag`: korely-graphrag full stack (FTS + pgvector + RRF **plus**")
    lines.append("  entity-graph traversal with IDF weighting for `related`).")
    lines.append("")
    lines.append("Both systems use identical Gemini models: `gemini-embedding-001` (1536d)")
    lines.append("for embeddings, `gemini-2.5-flash` for entity extraction (only graphrag uses it).")
    lines.append("")
    lines.append("## Overall results")
    lines.append("")
    lines.append("| metric | vanilla (mean) | graphrag (mean) | Δ |")
    lines.append("|---|---:|---:|---:|")
    for m in ("p@1", "p@5", "r@5", "hit@5", "latency_s"):
        v = agg["overall"]["vanilla"][m]["mean"]
        g = agg["overall"]["graphrag"][m]["mean"]
        delta = g - v
        lines.append(f"| {m} | {v:.3f} | {g:.3f} | {'+' if delta >= 0 else ''}{delta:.3f} |")
    lines.append("")

    lines.append("## Breakdown by question type")
    lines.append("")
    for qtype, systems in agg["by_type"].items():
        n = systems["vanilla"]["p@1"]["n"]
        lines.append(f"### {qtype} ({n} questions)")
        lines.append("")
        lines.append("| metric | vanilla | graphrag | Δ |")
        lines.append("|---|---:|---:|---:|")
        for m in ("p@1", "p@5", "r@5", "hit@5", "latency_s"):
            v = systems["vanilla"][m]["mean"]
            g = systems["graphrag"][m]["mean"]
            delta = g - v
            lines.append(f"| {m} | {v:.3f} | {g:.3f} | {'+' if delta >= 0 else ''}{delta:.3f} |")
        lines.append("")

    # Example failure cases: where one system wins dramatically over the other
    lines.append("## Notable cases")
    lines.append("")
    lines.append("Where graphrag beat vanilla (top 5):")
    lines.append("")
    wins = sorted(
        (r for r in results if r["graphrag_hit@5"] > r["vanilla_hit@5"]),
        key=lambda r: r["graphrag_hit@5"] - r["vanilla_hit@5"],
        reverse=True,
    )[:5]
    for r in wins:
        lines.append(f"- **Q{r['id']}** ({r['type']}): \"{r['question'][:100]}\"")
        lines.append(f"  - vanilla hit@5=0, graphrag hit@5=1")
    lines.append("")

    losses = sorted(
        (r for r in results if r["vanilla_hit@5"] > r["graphrag_hit@5"]),
        key=lambda r: r["vanilla_hit@5"] - r["graphrag_hit@5"],
        reverse=True,
    )[:5]
    lines.append("Where vanilla beat graphrag (top 5):")
    lines.append("")
    for r in losses:
        lines.append(f"- **Q{r['id']}** ({r['type']}): \"{r['question'][:100]}\"")
        lines.append(f"  - vanilla hit@5=1, graphrag hit@5=0")
    lines.append("")

    lines.append("## Reproducibility")
    lines.append("")
    lines.append("```bash")
    lines.append("git clone https://github.com/verdana86/korely-graphrag")
    lines.append("cd korely-graphrag")
    lines.append("cp .env.example .env  # set GEMINI_API_KEY")
    lines.append("docker compose up -d db")
    lines.append("# fetch Karpathy corpus")
    lines.append("git clone --depth 1 https://github.com/karpathy/karpathy.github.io /tmp/kb")
    lines.append("mkdir -p benchmark/karpathy && cp /tmp/kb/_posts/*.markdown benchmark/karpathy/")
    lines.append("# ingest + benchmark")
    lines.append("docker compose run --rm app korely-graphrag ingest --reset /app/benchmark/karpathy")
    lines.append("docker compose run --rm app python /app/benchmark/run_benchmark.py")
    lines.append("```")

    REPORT_PATH.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
