# Benchmark — korely-graphrag vs vanilla RAG

**Corpus:** 24 public blog posts from Andrej Karpathy's github.io
(reproducible: `git clone https://github.com/karpathy/karpathy.github.io`).

**Questions:** 60 — ground-truth generated with Gemini,
human-reviewed, drops ambiguous cases. Mix of 3 types:
- **precision@1**: specific question that should uniquely identify one post
- **recall@5**: cross-post question whose best answers are multiple posts
- **related**: "what posts are thematically linked to X?" — graph-specific

**Systems under test:**
- `vanilla`: FTS + pgvector + RRF over the *same* chunks and embeddings,
  with **no entity graph** and no IDF weighting. This is the default you get
  from LangChain / LlamaIndex with a pgvector store.
- `graphrag`: korely-graphrag full stack (FTS + pgvector + RRF **plus**
  entity-graph traversal with IDF weighting for `related`).

Both systems use identical Gemini models: `gemini-embedding-001` (1536d)
for embeddings, `gemini-2.5-flash` for entity extraction (only graphrag uses it).

## Overall results

| metric | vanilla (mean) | graphrag (mean) | Δ |
|---|---:|---:|---:|
| p@1 | 0.800 | 0.867 | +0.067 |
| p@5 | 0.227 | 0.260 | +0.033 |
| r@5 | 0.937 | 0.978 | +0.041 |
| hit@5 | 0.983 | 1.000 | +0.017 |
| latency_s | 0.391 | 0.342 | -0.049 |

## Breakdown by question type

### precision@1 (48 questions)

| metric | vanilla | graphrag | Δ |
|---|---:|---:|---:|
| p@1 | 0.896 | 0.896 | +0.000 |
| p@5 | 0.200 | 0.200 | +0.000 |
| r@5 | 1.000 | 1.000 | +0.000 |
| hit@5 | 1.000 | 1.000 | +0.000 |
| latency_s | 0.390 | 0.365 | -0.025 |

### recall@5 (8 questions)

| metric | vanilla | graphrag | Δ |
|---|---:|---:|---:|
| p@1 | 0.625 | 0.625 | +0.000 |
| p@5 | 0.375 | 0.375 | +0.000 |
| r@5 | 0.833 | 0.833 | +0.000 |
| hit@5 | 1.000 | 1.000 | +0.000 |
| latency_s | 0.366 | 0.372 | +0.006 |

### related (4 questions)

| metric | vanilla | graphrag | Δ |
|---|---:|---:|---:|
| p@1 | 0.000 | 1.000 | +1.000 |
| p@5 | 0.250 | 0.750 | +0.500 |
| r@5 | 0.392 | 1.000 | +0.608 |
| hit@5 | 0.750 | 1.000 | +0.250 |
| latency_s | 0.454 | 0.007 | -0.447 |

## Takeaways (honest interpretation)

**Where the systems are identical — and we say so upfront.**
On pure search (48 *precision@1* questions and 8 *recall@5* questions), the two
systems return the same top-K in the same order. This is **by design**: both
use the same hybrid search (FTS + pgvector + RRF) over the same chunks. We are
not claiming graphrag is a better keyword/vector retriever — it isn't. The
underlying retrieval stack is shared.

**Where graphrag wins — decisively.**
On 4 *related* questions (the graph's whole reason to exist), graphrag:
- Finds the expected neighbors **every time** (p@1 0.00 → 1.00, r@5 0.39 → 1.00)
- Is **65× faster** (7 ms vs 454 ms), because it runs a single SQL CTE over the
  entity graph instead of doing another embedding call + vector scan.

The vanilla baseline tries to answer *"what is related to post X?"* by
searching on post X's title — a naive fallback that LangChain / LlamaIndex
users would reach for without an entity graph. It misses non-keyword
connections entirely.

**Why this matters.**
If you only ever ask *"which document mentions X?"*, any RAG is fine; you
don't need the entity graph. But if you want the system to **surface
connections** — posts that share a thread of thought, people, or
technologies without repeating the same words — that's where the graph
earns its keep. The benchmark quantifies that: +0.608 r@5 and +0.500 p@5
on exactly the workload the graph is built for.

**What's not in the benchmark.** Cost per query is essentially identical
(both systems do one embedding call per search). Ingestion cost is higher
for graphrag (one additional Gemini entity-extraction call per document),
but amortizes immediately because it's a one-time cost per document.

## Notable cases

Where graphrag beat vanilla (top 5):

- **Q61** (related): "Which posts are thematically related to "2026-02-12-microgpt"?"
  - vanilla hit@5=0, graphrag hit@5=1

Where vanilla beat graphrag (top 5):


## Reproducibility

```bash
git clone https://github.com/verdana86/korely-graphrag
cd korely-graphrag
cp .env.example .env  # set GEMINI_API_KEY
docker compose up -d db
# fetch Karpathy corpus
git clone --depth 1 https://github.com/karpathy/karpathy.github.io /tmp/kb
mkdir -p benchmark/karpathy && cp /tmp/kb/_posts/*.markdown benchmark/karpathy/
# ingest + benchmark
docker compose run --rm app korely-graphrag ingest --reset /app/benchmark/karpathy
docker compose run --rm app python /app/benchmark/run_benchmark.py
```