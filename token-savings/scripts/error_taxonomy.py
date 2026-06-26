#!/usr/bin/env python3
"""
M1 — Error taxonomy of Korely's WRONG answers on LongMemEval (oracle split).

The 76.4% is the headline; the 42 WRONG rows are what caps it. Before paying for
ANY algorithm we ask one question per wrong row: *whose fault is it?*

  RETRIEVAL_MISS   the gold evidence is NOT in Korely's block        -> fixable by retrieval/selection (HippoRAG, reranker, _s work)
  ABSTENTION_MISS  evidence IS present but the reader said "I don't know" -> fixable by reader/prompt (anti-abstention, M4)
  READER_MISS      evidence present, reader committed, still wrong    -> fixable by reader/prompt (Chain-of-Note, M3)
  JUDGE_SUSPECT    the answer literally contains the gold yet graded wrong -> likely a JUDGE error => a FREE point on re-grade
  ABSTENTION_FAIL  an _abs question where the reader hallucinated instead of abstaining -> reader/calibration (the OPPOSITE of over-abstention)

The deterministic classification needs NO API key and NO model ($0). The optional
--rejudge pass re-grades only the JUDGE_SUSPECT rows with a second model (gpt-4o)
to turn "suspect" into a measured confidence interval on the 76.4 (each flip to
CORRECT is a real recovered point). That tiny pass is the ONLY thing that costs.

  python3 scripts/error_taxonomy.py                # $0 deterministic table
  python3 scripts/error_taxonomy.py --rejudge      # + re-grade suspects (~$0.05, gpt-4o)

Honest caveats (printed in the report too):
- evidence_present is computed by the harness via a 48-char gold signature match
  (analyze.gold_signatures). It can FALSE-NEGATIVE on paraphrased gold, so
  RETRIEVAL_MISS is an UPPER BOUND — confirm a sample by eye before trusting it.
- JUDGE_SUSPECT is a *candidate* list for re-grading, not a verdict; short numeric
  golds (e.g. "5") match loosely, so they are flagged 'weak'.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import norm  # noqa: E402  (reuse the harness's exact normalizer)

ABSTAIN_RE_WORDS = (
    "i don't know", "i dont know", "i do not know", "don't know", "dont know",
    "no record", "not available", "not in the context", "not provided",
    "no information", "cannot determine", "can't determine", "unable to",
    "non lo so",
)

AXES = [
    "knowledge-update", "multi-session", "single-session-user",
    "single-session-preference", "temporal-reasoning", "single-session-assistant",
]
BUCKETS = [
    "RETRIEVAL_MISS", "ABSTENTION_MISS", "READER_MISS",
    "ABSTENTION_FAIL", "JUDGE_SUSPECT",
]


def _is_abstain_answer(ans: str) -> bool:
    a = norm(ans)
    return any(w in a for w in ABSTAIN_RE_WORDS)


def _token_overlap(gold: str, ans: str) -> float:
    g = set(norm(str(gold)).split())
    if not g:
        return 0.0
    a = set(norm(str(ans)).split())
    return len(g & a) / len(g)


def _numbers(text: str) -> set[str]:
    """Distinctive numeric tokens (digits) in a string — '25:50', '27', '2023'."""
    import re as _re
    return set(_re.findall(r"\d+", norm(str(text))))


def _gold_in_answer(gold: str, ans: str) -> tuple[bool, bool]:
    """(is_suspect, is_weak). Suspect = gold appears in the answer; weak = the
    gold is so short (<=1 token / numeric) that a loose match is unreliable.
    NB: gold can be a raw int/number in the dataset, so coerce to str.

    Principled guard: if BOTH gold and answer carry numbers and those numbers
    DIFFER, it is a genuine value error (READER_MISS), never a judge artifact —
    the shared prose ('minutes and seconds') must not fake a suspect."""
    g, a = norm(str(gold)), norm(str(ans))
    if not g or not a:
        return False, False
    gnums, anums = _numbers(gold), _numbers(ans)
    if gnums and anums and not (gnums & anums):
        return False, (len(g.split()) <= 1 or g.isdigit())  # different numbers => real miss
    substring = g in a
    overlap = _token_overlap(gold, ans)
    suspect = substring or overlap >= 0.6
    weak = len(g.split()) <= 1 or g.isdigit()
    return suspect, weak


def classify(row: dict, pq: dict) -> str:
    """Classify one Korely-WRONG row. row from accuracy.jsonl, pq the per_question
    record for the same qid."""
    ans = row.get("korely_answer", "") or ""
    gold = row.get("gold", "") or ""
    is_abs = bool(row.get("is_abstention"))
    ev_present = bool(pq.get("evidence_present"))

    # _abs questions: the only correct behavior is to abstain. Wrong => the reader
    # gave a concrete answer instead. evidence_present is meaningless here (no gold
    # answer exists by design), so branch first.
    if is_abs:
        return "ABSTENTION_FAIL"

    # JUDGE_SUSPECT takes priority: if the answer literally carries the gold yet was
    # graded wrong, the grade is the prime suspect (a free point on re-judge).
    suspect, _weak = _gold_in_answer(gold, ans)
    if suspect:
        return "JUDGE_SUSPECT"

    if not ev_present:
        return "RETRIEVAL_MISS"            # gold evidence not in the block (upper bound)
    if _is_abstain_answer(ans):
        return "ABSTENTION_MISS"           # evidence present, reader over-abstained
    return "READER_MISS"                   # evidence present, committed, still wrong


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--acc", default="results/accuracy.jsonl")
    ap.add_argument("--pq", default="results/per_question.jsonl")
    ap.add_argument("--out", default="results/error_taxonomy.json")
    ap.add_argument("--rejudge", action="store_true",
                    help="re-grade JUDGE_SUSPECT rows with a 2nd model (gpt-4o, ~$0.05)")
    ap.add_argument("--rejudge-model", default="gpt-4o")
    args = ap.parse_args()

    acc = [json.loads(l) for l in open(args.acc)]
    pq = {json.loads(l)["qid"]: json.loads(l) for l in open(args.pq)}

    # sanity: reconstruct the headline so we know we're reading the right files
    n = len(acc)
    k = sum(r["korely_correct"] for r in acc)
    w = sum(r["window_correct"] for r in acc)
    missing = [r["qid"] for r in acc if r["qid"] not in pq]
    if missing:
        print(f"WARN: {len(missing)} qids in accuracy have no per_question row "
              f"(evidence_present defaults to False -> may inflate RETRIEVAL_MISS): {missing[:5]}")

    wrong = [r for r in acc if not r["korely_correct"]]
    # cell[bucket][axis] = [qid,...]
    cell = defaultdict(lambda: defaultdict(list))
    rows_out = []
    both_wrong = 0
    for r in wrong:
        b = classify(r, pq.get(r["qid"], {}))
        cell[b][r["axis"]].append(r["qid"])
        bw = not r["window_correct"]
        both_wrong += int(bw)
        rows_out.append({
            "qid": r["qid"], "axis": r["axis"], "bucket": b,
            "is_abstention": bool(r.get("is_abstention")),
            "evidence_present": bool(pq.get(r["qid"], {}).get("evidence_present")),
            "evidence_retention_pct": pq.get(r["qid"], {}).get("evidence_retention_pct"),
            "gold": r.get("gold", ""), "korely_answer": r.get("korely_answer", ""),
            "also_window_wrong": bw,
        })

    # ---- report ----
    print(f"\nLongMemEval oracle · Korely {k}/{n} = {100*k/n:.1f}% correct · "
          f"{len(wrong)} WRONG rows ({both_wrong} also window-wrong)\n")
    colw = 18
    header = f"{'bucket':<16}" + "".join(f"{a[:colw]:>{colw+2}}" for a in AXES) + f"{'TOT':>6}"
    print(header)
    print("-" * len(header))
    bucket_tot = {}
    for b in BUCKETS:
        tot = sum(len(cell[b][a]) for a in AXES)
        bucket_tot[b] = tot
        line = f"{b:<16}" + "".join(f"{len(cell[b][a]):>{colw+2}}" for a in AXES) + f"{tot:>6}"
        print(line)
    print("-" * len(header))
    axis_tot = {a: sum(len(cell[b][a]) for b in BUCKETS) for a in AXES}
    print(f"{'TOT WRONG':<16}" + "".join(f"{axis_tot[a]:>{colw+2}}" for a in AXES)
          + f"{len(wrong):>6}")

    # ---- fixability rollup ----
    retrieval = bucket_tot["RETRIEVAL_MISS"]
    reader = bucket_tot["READER_MISS"] + bucket_tot["ABSTENTION_MISS"] + bucket_tot["ABSTENTION_FAIL"]
    judge = bucket_tot["JUDGE_SUSPECT"]
    print(f"\nFIXABILITY ROLLUP (of {len(wrong)} wrong):")
    print(f"  retrieval-bound (RETRIEVAL_MISS)            = {retrieval:>2}  -> WAVE 3 / _s selection")
    print(f"  reader-bound   (READER+ABSTENTION_MISS+FAIL)= {reader:>2}  -> WAVE 1 (Chain-of-Note, anti-abstention)")
    print(f"  judge-suspect  (likely free points)         = {judge:>2}  -> re-grade with --rejudge")

    # ---- suspects detail ----
    suspects = [r for r in rows_out if r["bucket"] == "JUDGE_SUSPECT"]
    if suspects:
        print(f"\nJUDGE_SUSPECT detail ({len(suspects)}) — each flip on re-grade is a free point:")
        for s in suspects:
            _, weak = _gold_in_answer(s["gold"], s["korely_answer"])
            tag = " [weak: short/numeric gold]" if weak else ""
            print(f"  {s['qid']} ({s['axis']}){tag}\n"
                  f"      gold:   {s['gold'][:90]!r}\n"
                  f"      answer: {s['korely_answer'][:90]!r}")

    # ---- per-axis sub-ceiling flag (dead headroom) ----
    print("\nDEAD-HEADROOM CHECK (axes where retrieval/reader work can't help):")
    print("  single-session-preference: Korely 40% == full-history ceiling 40% -> dataset/judge bound, do NOT target.")

    out = {
        "n": n, "korely_correct": k, "korely_acc": round(100*k/n, 1),
        "wrong": len(wrong), "both_wrong": both_wrong,
        "bucket_totals": bucket_tot,
        "fixability": {"retrieval": retrieval, "reader": reader, "judge_suspect": judge},
        "rows": rows_out,
    }

    # ---- optional re-judge of suspects ----
    if args.rejudge and suspects:
        print(f"\nRe-grading {len(suspects)} suspects with {args.rejudge_model} ...")
        import accuracy as A  # reuse the exact judge prompt/parse
        from analyze import load_dataset
        by_qid = load_dataset(None)  # real question text per qid (judge needs it)
        A.configure_provider(args.rejudge_model)
        model = A.make_model(args.rejudge_model)
        flips = 0
        for s in suspects:
            qtype = s["axis"]
            q = (by_qid.get(s["qid"], {}) or {}).get("question", "")
            verdict = A.judge(model, q, s["gold"], s["korely_answer"], qtype, False)
            s["rejudge_correct"] = bool(verdict)
            flips += int(verdict)
            print(f"  {s['qid']}: {'FLIP->CORRECT (free point)' if verdict else 'stays wrong'}")
        recovered_acc = round(100*(k+flips)/n, 1)
        print(f"\n{flips}/{len(suspects)} suspects flip to CORRECT on re-grade with "
              f"{args.rejudge_model}.")
        print(f"  => Korely accuracy {out['korely_acc']}%  ->  {recovered_acc}% "
              f"(a {args.rejudge_model}-grader recovers {flips} judge-lost points).")
        out["rejudge"] = {"model": args.rejudge_model, "flips": flips,
                          "recovered_acc": recovered_acc}

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
