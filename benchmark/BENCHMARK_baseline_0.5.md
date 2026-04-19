# Benchmark — korely-graphrag vs vanilla RAG

**Corpus:** 24 public blog posts from Andrej Karpathy's github.io
(reproducible: `git clone https://github.com/karpathy/karpathy.github.io`).

**Questions:** 75 — ground-truth generated with Gemini,
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
| p@1 | 0.640 | 0.747 | +0.107 |
| p@5 | 0.264 | 0.240 | -0.024 |
| r@5 | 0.858 | 0.802 | -0.056 |
| hit@5 | 0.960 | 0.920 | -0.040 |
| latency_s | 0.392 | 0.328 | -0.064 |

## Breakdown by question type

### precision@1 (48 questions)

| metric | vanilla | graphrag | Δ |
|---|---:|---:|---:|
| p@1 | 0.896 | 0.896 | +0.000 |
| p@5 | 0.200 | 0.200 | +0.000 |
| r@5 | 1.000 | 1.000 | +0.000 |
| hit@5 | 1.000 | 1.000 | +0.000 |
| latency_s | 0.382 | 0.454 | +0.072 |

### recall@5 (8 questions)

| metric | vanilla | graphrag | Δ |
|---|---:|---:|---:|
| p@1 | 0.625 | 0.625 | +0.000 |
| p@5 | 0.375 | 0.375 | +0.000 |
| r@5 | 0.833 | 0.833 | +0.000 |
| hit@5 | 1.000 | 1.000 | +0.000 |
| latency_s | 0.439 | 0.342 | -0.097 |

### related (19 questions)

| metric | vanilla | graphrag | Δ |
|---|---:|---:|---:|
| p@1 | 0.000 | 0.421 | +0.421 |
| p@5 | 0.379 | 0.284 | -0.095 |
| r@5 | 0.509 | 0.288 | -0.221 |
| hit@5 | 0.842 | 0.684 | -0.158 |
| latency_s | 0.398 | 0.006 | -0.392 |

## Notable cases

Where graphrag beat vanilla (top 5):

- **Q76** (related): "Which posts are thematically related to "2015-05-21-rnn-effectiveness"?"
  - vanilla hit@5=0, graphrag hit@5=1

Where vanilla beat graphrag (top 5):

- **Q69** (related): "Which posts are thematically related to "2013-11-23-chrome-extension-programming"?"
  - vanilla hit@5=1, graphrag hit@5=0
- **Q70** (related): "Which posts are thematically related to "2021-03-27-forward-pass"?"
  - vanilla hit@5=1, graphrag hit@5=0
- **Q73** (related): "Which posts are thematically related to "2014-08-03-quantifying-productivity"?"
  - vanilla hit@5=1, graphrag hit@5=0
- **Q77** (related): "Which posts are thematically related to "2014-07-01-switching-to-jekyll"?"
  - vanilla hit@5=1, graphrag hit@5=0

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