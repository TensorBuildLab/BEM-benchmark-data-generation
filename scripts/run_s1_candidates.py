"""S1 case study, step 1: put every candidate reference of every practice case through QA.

Usage:
    python scripts/run_s1_candidates.py --package work/package --weather work/weather --work work/s1 --workers 6

``--package`` is the unzipped test-case package (test1 ... test10). Results go to
``results/s1_candidates.json`` (one record per case x candidate).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bemgen.generators.harvest import load_case, build_item  # noqa: E402
from bemgen.qa import run_qa  # noqa: E402


def one(case_path, cand, args):
    case = load_case(case_path)
    item = build_item(case, args.package, Path(args.work) / "items", cand, [Path(args.weather)])
    t0 = time.time()
    rep = run_qa(item, Path(args.work) / "runs", [Path(args.weather)])
    d = rep.to_dict()
    return {"case": case["id"], "candidate": cand, "origin": case["candidates"][cand].get("origin"),
            "tier": d["tier"], "gates": d["gates"], "n_findings": d["n_findings"],
            "conformance": (d.get("conformance") or {}).get("conformance"),
            "n_facts": (d.get("conformance") or {}).get("n_facts"),
            "n_pass": (d.get("conformance") or {}).get("n_pass"),
            "by_facet": (d.get("conformance") or {}).get("by_facet"),
            "failed": [{k: r[k] for k in ("id", "facet", "kind", "severity", "text", "observed")}
                       for r in (d.get("conformance") or {}).get("failed", [])],
            "findings": [{k: f[k] for k in ("gate", "id", "severity", "message", "evidence")} for f in d["findings"]],
            "run": {k: (d.get("run") or {}).get(k) for k in ("completed", "severe", "warnings", "elapsed_s")},
            "spec_profile": d.get("spec_profile"), "wall_s": round(time.time() - t0, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--package", required=True)
    ap.add_argument("--weather", required=True)
    ap.add_argument("--work", default=str(ROOT / "work" / "s1"))
    ap.add_argument("--cases", default=str(ROOT / "cases" / "practice"))
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--out", default=str(ROOT / "results" / "s1_candidates.json"))
    args = ap.parse_args()
    jobs = []
    for cp in sorted(Path(args.cases).glob("P*.yaml")):
        case = load_case(cp)
        if args.only and case["id"] not in args.only:
            continue
        for cand in case.get("candidates", {}):
            jobs.append((cp, cand))
    print(f"{len(jobs)} candidate references", flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        res = list(ex.map(lambda j: one(j[0], j[1], args), jobs))
    out = Path(args.out)
    old = json.loads(out.read_text()) if out.is_file() and args.only else []
    keep = [r for r in old if (r["case"], r["candidate"]) not in {(x["case"], x["candidate"]) for x in res}]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(keep + res, indent=1, default=str))
    for r in res:
        print(f"{r['case']:28s} {r['candidate']:9s} tier={r['tier']:10s} conf={r['conformance'] if r['conformance'] is None else round(r['conformance'], 3)} "
              f"gates={r['gates']} findings={r['n_findings']}", flush=True)


if __name__ == "__main__":
    main()
