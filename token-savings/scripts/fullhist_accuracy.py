#!/usr/bin/env python3
"""Third condition: accuracy when you send the FULL history (every turn).

Completes the cost x quality picture:
  Korely block       ~1,900 tok   (measured in accuracy.py)
  recency window     ~1,900 tok   (measured in accuracy.py)
  full history       ~5,500 tok   (this script)
So we can answer: does Korely's 66%-smaller block KEEP the accuracy of sending
everything? Reuses accuracy.py's reader + judge.
"""
from __future__ import annotations
import glob, json, os, sys, warnings
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import full_history, load_dataset
import accuracy as A
import google.generativeai as genai

genai.configure(api_key=A._load_key())
by_qid = load_dataset(None)

work, seen = [], set()
for f in sorted(glob.glob("data/*.jsonl")):
    for line in open(f):
        r = json.loads(line)
        if r.get("system") != "korely" or not r.get("use_hint"):
            continue
        qid = r["qid"]
        if qid in seen:
            continue
        it = by_qid.get(qid)
        if it is None or not (r.get("retrieved_context") or "").strip():
            continue
        seen.add(qid)
        work.append(dict(it, _qid=qid, _gold=r.get("gold")))


def proc(it):
    m = genai.GenerativeModel("gemini-2.5-flash")
    q, gold, qt = it["question"], it["_gold"], it["question_type"]
    is_abs = str(it["_qid"]).endswith("_abs")
    ans = A.reader(m, full_history(it), q)
    return {"axis": qt, "correct": A.judge(m, q, gold, ans, qt, is_abs)}


rows = []
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = [ex.submit(proc, it) for it in work]
    for n, fut in enumerate(as_completed(futs), 1):
        rows.append(fut.result())
        if n % 30 == 0:
            print(f"  {n}/{len(work)}", flush=True)

per = defaultdict(lambda: [0, 0])
for r in rows:
    per[r["axis"]][0] += int(r["correct"])
    per[r["axis"]][1] += 1
tot = [sum(int(r["correct"]) for r in rows), len(rows)]
print("\nFULL-HISTORY accuracy (send everything, ~5,500 tok):")
for ax in sorted(per):
    print(f"  {ax:28} {100*per[ax][0]/per[ax][1]:5.1f}%  (n={per[ax][1]})")
print(f"  {'ALL':28} {100*tot[0]/tot[1]:5.1f}%  (n={tot[1]})")
