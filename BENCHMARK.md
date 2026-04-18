# Benchmark

> **Status:** placeholder — to be filled in Phase 3.

## Methodology

- **Corpus:** TBD (candidates: Karpathy public writings, top 500 HN 2024 posts, 200 arXiv interpretability papers)
- **Questions:** 50 hand-curated questions with ground truth (which document(s) actually contain the answer)
- **Systems compared:**
  1. Claude Code memory (file flat, no RAG)
  2. Vanilla RAG (LangChain default, single embedding + cosine)
  3. korely-graphrag (this repo)
- **Metrics:** precision@5, recall@5, latency p50/p95, USD per query, "related discovery" (non-obvious links surfaced)

## Honesty contract

Numbers will be published as-is, including those where korely-graphrag loses. The setup script and question set are committed in `benchmark/` so anyone can reproduce.

## Results

(to be filled in)
