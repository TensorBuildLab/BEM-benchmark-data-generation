"""Derived results quoted in the paper that are not written by the case-study drivers.

    python scripts/extra_results.py

Writes, under results/:
  s1_outputs.json     annual results of every S1 candidate and the output differences between candidates
  s3_parity.json      agreement of the S3 references with their analytic fact sheets
  sensitivity.json    conformance of the S1 candidates under other severity weights and tolerances
  weather_measured.json  the measured-weather EPW built for P06
  summary.json        means and counts quoted in the text
"""
from __future__ import annotations

import copy
import json
import re
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bemgen.generators.harvest import load_case, spec_from_case  # noqa: E402
from bemgen.spec import STRICT, evaluate_check  # noqa: E402

RES = ROOT / "results"
RUNS = ROOT / "work" / "s1" / "runs"
METRICS = ("heating_gj", "cooling_gj", "site_energy_gj", "internal_gains_gj", "unmet_occupied_heating_h",
           "unmet_occupied_cooling_h")


def load(p):
    return json.loads(Path(p).read_text())


def s1_outputs():
    out = {}
    for d in sorted(RUNS.iterdir()):
        f = d / "reference" / "facts.json"
        if not f.is_file():
            continue
        r = load(f).get("results") or {}
        out[d.name] = {m: r.get(m) for m in METRICS}
    diffs = {}
    for name, v in out.items():
        cid, cand = name.split("@")
        ref = out.get(f"{cid}@expected")
        if cand == "expected" or not ref:
            continue
        diffs[name] = {m: ((v[m] - ref[m]) / ref[m] if v.get(m) is not None and ref.get(m) else None)
                       for m in ("heating_gj", "cooling_gj", "site_energy_gj", "internal_gains_gj")}
    # the mode each BESTEST case specifies: heating only (Colorado Springs), cooling only (Las Vegas)
    mode = {"P08-bestest-l100a-cos": "heating_gj", "P09-bestest-l100a-lv": "cooling_gj"}
    specified = {}
    for cid, m in mode.items():
        h, e = out.get(f"{cid}@harness", {}).get(m), out.get(f"{cid}@expected", {}).get(m)
        if h and e:
            specified[cid] = {"metric": m, "harness": h, "expected": e, "difference": (h - e) / e}
    doc = {"annual": out, "vs_expected": diffs, "specified_mode": specified}
    (RES / "s1_outputs.json").write_text(json.dumps(doc, indent=1))
    return doc


def s3_parity():
    R = load(RES / "s3_items.json")
    pts = []
    for r in R:
        g = load(ROOT / "work" / "s3" / "runs" / r["item"] / "reference" / "grade.json")
        for f in g["results"]:
            c = f["check"]
            if c.get("op") != "approx" or not isinstance(f["observed"], (int, float)):
                continue
            exp = float(c["value"])
            if exp == 0:
                continue
            pts.append({"item": r["item"], "fact": f["id"], "facet": f["facet"], "expected": exp,
                        "observed": float(f["observed"]), "rel_error": abs(float(f["observed"]) - exp) / abs(exp),
                        "pass": f["pass"] is True})
    worst = max(pts, key=lambda p: p["rel_error"])
    by_facet = defaultdict(int)
    for p in pts:
        by_facet[p["facet"]] += 1
    doc = {"n_numeric_facts": len(pts), "n_pass": sum(p["pass"] for p in pts),
           "max_rel_error": worst["rel_error"], "worst": worst,
           "median_rel_error": float(np.median([p["rel_error"] for p in pts])), "by_facet": dict(by_facet)}
    (RES / "s3_parity.json").write_text(json.dumps(doc, indent=1))
    return doc


def scale_tol(check, k):
    c = copy.deepcopy(check)
    for key in ("any_of", "all_of"):
        if key in c:
            c[key] = [scale_tol(s, k) for s in c[key]]
            return c
    if c.get("op", "approx") == "approx":
        if c.get("tol") is None and c.get("rtol") is None:
            c["rtol"] = 0.02
        if c.get("tol") is not None:
            c["tol"] = float(c["tol"]) * k
        if c.get("rtol") is not None:
            c["rtol"] = float(c["rtol"]) * k
    return c


def conformance(results, w):
    sel = [r for r in results if r["kind"] in STRICT]
    tot = sum(w[r["severity"]] for r in sel)
    return sum(w[r["severity"]] for r in sel if r["pass"] is True) / tot if tot else None


def spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    return float(np.corrcoef(ra, rb)[0, 1])


def sensitivity():
    weights = {"3-2-1 (default)": {"critical": 3, "major": 2, "minor": 1},
               "1-1-1 (equal)": {"critical": 1, "major": 1, "minor": 1},
               "9-3-1 (steep)": {"critical": 9, "major": 3, "minor": 1}}
    tols = [0.5, 1.0, 2.0]
    rows = []
    for cp in sorted((ROOT / "cases" / "practice").glob("P*.yaml")):
        case = load_case(cp)
        sp = spec_from_case(case)
        for cand in case.get("candidates", {}):
            f = RUNS / f"{case['id']}@{cand}" / "reference" / "facts.json"
            if not f.is_file():
                continue
            facts = load(f)
            row = {"case": case["id"], "candidate": cand, "C": {}, "flips": {}}
            base = None
            for k in tols:
                res = []
                for fa in sp.facts:
                    try:
                        r = evaluate_check(scale_tol(fa.check, k), facts)
                    except Exception:
                        r = {"pass": None}
                    res.append({"kind": fa.kind, "severity": fa.severity, "pass": r["pass"], "id": fa.id})
                if k == 1.0:
                    base = res
                for wn, w in weights.items():
                    row["C"][f"{wn} | tol x{k:g}"] = conformance(res, w)
                row.setdefault("_res", {})[k] = res
            for k in tols:
                row["flips"][f"tol x{k:g}"] = [a["id"] for a, b in zip(row["_res"][k], base)
                                              if a["kind"] in STRICT and (a["pass"] is True) != (b["pass"] is True)]
            del row["_res"]
            rows.append(row)
    keys = list(rows[0]["C"])
    dk = "3-2-1 (default) | tol x1"
    base = [r["C"][dk] for r in rows]
    summ = {}
    for k in keys:
        v = [r["C"][k] for r in rows]
        # order of candidates within each case with more than one candidate
        flips = 0
        pairs = 0
        bycase = defaultdict(list)
        for r, x, b in zip(rows, v, base):
            bycase[r["case"]].append((x, b))
        for c, lst in bycase.items():
            for (x1, b1), (x2, b2) in combinations(lst, 2):
                if b1 == b2:
                    continue
                pairs += 1
                flips += (x1 - x2) * (b1 - b2) < 0
        summ[k] = {"max_abs_change": max(abs(x - b) for x, b in zip(v, base)),
                   "mean_abs_change": float(np.mean([abs(x - b) for x, b in zip(v, base)])),
                   "spearman_vs_default": spearman(v, base), "within_case_order_flips": f"{flips} of {pairs}"}
    doc = {"candidates": rows, "summary": summ}
    (RES / "sensitivity.json").write_text(json.dumps(doc, indent=1))
    return doc


def weather_measured():
    p = ROOT / "work" / "weather" / "iUnit_measured_2021-01-01_2021-04-25.epw"
    hdr = p.read_text(errors="replace").splitlines()[5]
    n = int(re.search(r"Measured hours \((\d+)\)", hdr).group(1))
    doc = {"file": p.name, "measured_hours": n, "comment": hdr}
    (RES / "weather_measured.json").write_text(json.dumps(doc, indent=1))
    return doc


def summary():
    C = load(RES / "s1_candidates.json")
    by = defaultdict(list)
    for r in C:
        if r.get("conformance") is not None:
            by[r["candidate"]].append(r["conformance"])
    doc = {"s1_mean_conformance": {k: {"mean": float(np.mean(v)), "n": len(v)} for k, v in by.items()},
           "s1_candidates": len(C),
           "s1_completed_simulation": sum(1 for v in load(RES / "s1_outputs.json")["annual"].values()
                                          if v.get("site_energy_gj") is not None)}
    (RES / "summary.json").write_text(json.dumps(doc, indent=1))
    return doc


if __name__ == "__main__":
    for fn in (s1_outputs, s3_parity, sensitivity, weather_measured, summary):
        d = fn()
        print(f"== {fn.__name__}")
        if fn is sensitivity:
            print(json.dumps(d["summary"], indent=1))
        elif fn is s1_outputs:
            print(json.dumps(d["specified_mode"], indent=1)); print(json.dumps(d["vs_expected"], indent=1)[:1500])
        else:
            print(json.dumps(d, indent=1)[:1200])
