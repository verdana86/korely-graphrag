#!/usr/bin/env python3
"""
M0 — re-benchmark the ORACLE split against the CURRENT production get_context.

Why: the committed oracle blocks (run compare-native-20260615) were generated
with _FACTS_LIMIT=30 and ingestion-date facts. Current code caps facts at 10 and
uses event-time dates (verified live: same qid 6a1eabeb has 30 stale facts dated
2026-06-15 vs 10 fresh facts dated 2023-05-25). So the published 76.4 reflects a
config production no longer uses. This regenerates all 178 oracle blocks against
the live /v1/context, correctly waiting for the ASYNC Layer-3 fact extraction to
drain before fetching (the naive reproduce.py settle is too short — facts appear
seconds-to-minutes after ingest).

Three phases:
  1. INGEST every turn of all 178 questions (event-time timestamp per turn).
  2. POLL a sample until the fact counts stabilize (extraction drained), capped.
  3. FETCH all 178 contexts -> transcript jsonl (accuracy.py-compatible).

Then score separately:
  python3 scripts/accuracy.py --transcripts results/m0-oracle.jsonl --out results/m0
  python3 scripts/fullhist_accuracy.py   # ceiling unchanged (full history)

Cleanup after (delete the benchmark end-users from the account):
  python3 scripts/m0_run.py --cleanup
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ.get("KORELY_BASE_URL", "https://api.korely.ai")
CONTENT_TEMPLATE = "[{date}] {role}: {content}"
MAX_CONTENT_CHARS = 16000
MIN_TURN_CHARS = 12
TOKEN_BUDGET = 2000
AGENT_ID = "longmemeval-m0"
TAG = "m0"
KEY = ""
_DATE = re.compile(r"(\d{4})/(\d{2})/(\d{2}).*?(\d{2}):(\d{2})")


def korely_key() -> str:
    k = os.environ.get("KORELY_API_KEY")
    if not k:
        sys.exit("Set KORELY_API_KEY")
    return k


def _req(method, url, body=None, *, retries=8):
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(retries):
        req = urllib.request.Request(
            url, data=data, method=method,
            headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.status, json.loads(r.read() or "null")
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                ra = e.headers.get("Retry-After")
                time.sleep(float(ra) if (ra and ra.isdigit()) else min(2 ** attempt + 0.5, 30))
                continue
            if e.code == 403:
                sys.exit(f"403 (account limit): {(e.read() or b'')[:200].decode(errors='replace')}")
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:  # incl socket timeout
            if attempt < retries - 1:
                time.sleep(min(2 ** attempt + 0.5, 30))
                continue
            raise


def iso_event_time(date):
    m = _DATE.search(date or "")
    if not m:
        return None
    y, mo, d, h, mi = m.groups()
    return f"{y}-{mo}-{d}T{h}:{mi}:00"


def turns_chrono(item):
    sessions = item["haystack_sessions"]
    dates = item.get("haystack_dates") or [""] * len(sessions)
    for i in sorted(range(len(sessions)), key=lambda i: dates[i]):
        for t in sessions[i]:
            c = (t.get("content") or "").strip()
            if len(c) >= MIN_TURN_CHARS:
                yield dates[i], t.get("role", "user"), c


def load_oracle_all():
    cached = glob.glob(os.path.expanduser(
        "~/.cache/huggingface/hub/datasets--xiaowu0162--longmemeval-cleaned/"
        "snapshots/*/longmemeval_oracle.json"))
    if cached:
        data = json.load(open(cached[0]))
    else:
        from huggingface_hub import hf_hub_download
        data = json.load(open(hf_hub_download(
            "xiaowu0162", "longmemeval_oracle.json", repo_type="dataset")))
    # Restrict to the EXACT 178 qids in the committed benchmark so M0 is
    # apples-to-apples with the published 76.4 (the HF oracle file has 500).
    committed = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "data", "korely_longmemeval_oracle.jsonl")
    if os.path.exists(committed):
        keep = {json.loads(l)["qid"] for l in open(committed)}
        data = [d for d in data if d["question_id"] in keep]
        print(f"  filtered HF oracle to {len(data)} committed-benchmark qids", flush=True)
    return data


def uid_for(qid):
    return f"lme-{TAG}-{qid}"


def get_context(uid, query):
    url = f"{BASE}/v1/context?" + urllib.parse.urlencode(
        {"query": query, "user_id": uid, "token_budget": TOKEN_BUDGET})
    _st, j = _req("GET", url)
    return (j or {}).get("context") or ""


def nfacts(blk):
    m = re.search(r"## Known facts\n(.*?)(?:\n## |\Z)", blk, re.S)
    return 0 if not m else sum(1 for ln in m.group(1).splitlines() if ln.strip().startswith("- "))


def cmd_run(args):
    items = load_oracle_all()
    if args.limit:
        items = items[:args.limit]
    print(f"M0: {len(items)} oracle questions -> {args.out}", flush=True)

    # ---- Phase 1: ingest (concurrent — backend embeds inline ~3.75s/write) ----
    import concurrent.futures as cf
    meta = []
    work = []  # (uid, body)
    for item in items:
        qid = item["question_id"]
        uid = uid_for(qid)
        turns = list(turns_chrono(item))
        for date, role, content in turns:
            body = {"content": CONTENT_TEMPLATE.format(date=date, role=role, content=content)[:MAX_CONTENT_CHARS],
                    "user_id": uid, "agent_id": AGENT_ID}
            ev = iso_event_time(date)
            if ev:
                body["timestamp"] = ev
            work.append(body)
        meta.append({"qid": qid, "uid": uid, "question": item["question"],
                     "gold": item.get("answer", ""), "axis": item["question_type"],
                     "n_turns": len(turns)})
    json.dump(meta, open(args.out + ".meta.json", "w"))
    print(f"  ingesting {len(work)} writes across {len(meta)} questions, "
          f"{args.workers} workers", flush=True)

    def _write(body):
        try:
            st, _ = _req("POST", f"{BASE}/v1/memories", body)
            return int(st in (200, 201))
        except Exception as e:  # noqa: BLE001
            return 0

    t0 = time.time()
    ok_total = 0
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for n, res in enumerate(ex.map(_write, work), 1):
            ok_total += res
            if n % 200 == 0 or n == len(work):
                print(f"  ingest {n}/{len(work)} writes  ok={ok_total}  ({time.time()-t0:.0f}s)", flush=True)
    print(f"  ingest done: {ok_total}/{len(work)} writes ok ({time.time()-t0:.0f}s)", flush=True)

    # ---- Phase 2: poll until fact extraction drains (sample of knowledge-update) ----
    sample = [m for m in meta if m["axis"] == "knowledge-update"][:12]
    print(f"\nWaiting for async Layer-3 extraction (poll {len(sample)} sample qids)...", flush=True)
    prev = -1
    stable = 0
    for rnd in range(args.max_poll):  # max_poll * 45s cap
        time.sleep(45)
        total = sum(nfacts(get_context(m["uid"], m["question"])) for m in sample)
        print(f"  poll {rnd+1}: sample facts total = {total} (prev {prev})", flush=True)
        if total <= prev:
            stable += 1
            if stable >= 2:
                print("  extraction stable -> proceeding to fetch", flush=True)
                break
        else:
            stable = 0
        prev = total

    # ---- Phase 3: fetch all contexts (concurrent) ----
    print(f"\nFetching {len(meta)} contexts ({args.workers} workers)...", flush=True)

    def _fetch(m):
        ctx = get_context(m["uid"], m["question"])
        return {
            "run_id": f"m0-{TAG}", "qid": m["qid"], "system": "korely",
            "mode": "native", "question": m["question"], "gold": m["gold"],
            "retrieved_context": ctx, "n_expected": m["n_turns"],
            "use_hint": True, "seed": None, "axis": m["axis"],
            "n_facts": nfacts(ctx),
        }

    with open(args.out, "w") as fh:
        with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
            for i, row in enumerate(ex.map(_fetch, meta), 1):
                fh.write(json.dumps(row) + "\n")
                fh.flush()
                if i % 40 == 0 or i == len(meta):
                    print(f"  fetch {i}/{len(meta)}", flush=True)
    # fact-count summary
    facts = [nfacts(json.loads(l)["retrieved_context"]) for l in open(args.out)]
    with_facts = [f for f in facts if f > 0]
    print(f"\nDone -> {args.out}\n  blocks with facts: {len(with_facts)}/{len(facts)} | "
          f"avg facts (when present): {sum(with_facts)/max(1,len(with_facts)):.1f} | max: {max(facts)}")
    print(f"  Score: python3 scripts/accuracy.py --transcripts {args.out} --out results/m0")


def cmd_cleanup(args):
    meta = json.load(open(args.out + ".meta.json"))
    print(f"Deleting {len(meta)} benchmark end-users...", flush=True)
    n = 0
    for m in meta:
        url = f"{BASE}/v1/memories?" + urllib.parse.urlencode({"user_id": m["uid"]})
        try:
            st, _ = _req("DELETE", url)
            n += int(st in (200, 204))
        except Exception as e:  # noqa: BLE001
            print(f"  delete error {m['uid']}: {e}", flush=True)
    print(f"Deleted {n}/{len(meta)} end-user namespaces.", flush=True)


def main():
    global KEY
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/m0-oracle.jsonl")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=12)  # concurrent writes/fetches
    ap.add_argument("--max-poll", type=int, default=14)  # 14*45s = ~10.5 min cap
    ap.add_argument("--cleanup", action="store_true")
    args = ap.parse_args()
    KEY = korely_key()
    if args.cleanup:
        cmd_cleanup(args)
    else:
        cmd_run(args)


if __name__ == "__main__":
    main()
