"""Mutation analysis: how well do an item's checks separate wrong models from valid ones?

    python scripts/mutation_analysis.py --workers 6

For each seed reference, every operator in ``bemgen.mutate`` (defects, admissible variants of unstated
inputs, equivalent rewrites) is applied to a copy, the copy is simulated and scored against the item,
and three checks are recorded:

* the fact sheet (L2: does any determined fact fail? evaluable facts only are reported too);
* the plausibility rules of gate G3 (does any rule fail?);
* output agreement with the reference (relative difference in annual site energy, heating, cooling).

Writes results/mutation.json. Simulations are cached, so a rerun only simulates new mutants.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bemgen import mutate  # noqa: E402
from bemgen.energyplus import prune_run_dir  # noqa: E402
from bemgen.idf import IDF  # noqa: E402
from bemgen.item import Item  # noqa: E402
from bemgen.qa import plausibility  # noqa: E402
from bemgen.scoring import score  # noqa: E402
from bemgen.spec import STRICT  # noqa: E402

W = ROOT / "work" / "weather"
OUT = ROOT / "work" / "mutation"
SEEDS = ["S3/V01-small-office-phoenix", "S3/V02-small-office-chicago", "S3/V09-retail-las-vegas", "S3/V13-school-el-paso",
         "S3/V17-house-denver", "S3/V21-rowhouse-chicago", "S3/V24-rowhouse-houston",
         "S1/P02-lupton-heat-pump", "S1/P04-office-narrative", "S1/P08-bestest-l100a-cos"]


def ref_run_dir(item_id: str) -> Path:
    for base in (ROOT / "work" / "s3" / "runs", ROOT / "work" / "s1" / "curated_runs"):
        d = base / item_id / "reference"
        if (d / "facts.json").is_file():
            return d
    raise FileNotFoundError(item_id)


def jobs_for(seed: str):
    item_dir = ROOT / "benchmark" / "items" / seed
    it = Item.load(item_dir)
    rdir = ref_run_dir(it.id)
    ref_facts = json.loads((rdir / "facts.json").read_text())
    cond = {k.upper() for k, z in ref_facts["geometry"]["zones"].items() if z.get("conditioned")}
    ctx = {"conditioned_zones": cond}
    out = []
    for fam, ops in mutate.FAMILIES.items():
        for name in ops:
            m = IDF.load(it.reference_path())
            try:
                desc = mutate.apply(m, fam, name, ctx)
            except Exception as e:  # an operator bug must not stop the study; it is recorded
                out.append({"seed": it.id, "family": fam, "op": name, "error": f"{type(e).__name__}: {e}"})
                continue
            if desc is None:
                continue
            d = OUT / it.id / f"{fam}__{name}"
            d.mkdir(parents=True, exist_ok=True)
            m.save(d / "model.idf")
            src = mutate.role_source(it.id, fam, name)
            out.append({"seed": it.id, "family": fam, "role": mutate.role(it.id, fam, name), "op": name,
                        "facet": ops[name][1], "description": desc, **({"role_source": src} if src else {}),
                        "model": d / "model.idf", "item_dir": item_dir, "ref_facts": ref_facts})
    exp = rdir / "out" / "eplusout.expidf"
    if exp.is_file():
        d = OUT / it.id / "equivalent__expand_templates"
        d.mkdir(parents=True, exist_ok=True)
        shutil.copy2(exp, d / "model.idf")
        out.append({"seed": it.id, "family": "equivalent", "role": "equivalent", "op": "expand_templates", "facet": "hvac",
                    "description": "HVAC templates replaced by the objects EnergyPlus expands them into",
                    "model": d / "model.idf", "item_dir": item_dir, "ref_facts": ref_facts})
    return out


def run_job(j, prune=False):
    if "error" in j:
        return j
    it = Item.load(j["item_dir"])
    run_dir = Path(j["model"]).parent / "run"
    s = score(it, Path(j["model"]), run_dir, [W], reference_facts=j["ref_facts"])
    facts = json.loads((run_dir / "facts.json").read_text()) if (run_dir / "facts.json").is_file() else {}
    if prune:
        prune_run_dir(run_dir)
    pl = [r for r in plausibility(facts)] if facts else []
    fails = [{"id": r["id"], "severity": r.get("severity", "minor")} for r in pl if r["pass"] is False]
    ref_pl = {r["id"] for r in plausibility(j["ref_facts"]) if r["pass"] is False}
    new_fails = [f for f in fails if f["id"] not in ref_pl]
    strict_failed = [f for f in s.get("failed", []) if f.get("kind") in STRICT]
    return {k: v for k, v in j.items() if k not in ("model", "item_dir", "ref_facts")} | {
        "L0": s.get("L0_valid"), "L1": s.get("L1_runs"), "C": s.get("L2_conformance"),
        "C_e": s.get("L2_conformance_evaluable"), "n_strict_unevaluable": s.get("n_strict_unevaluable"),
        "failed": [{"id": f["id"], "facet": f["facet"], "observed": f["observed"], "evaluated": f["evaluated"]}
                   for f in strict_failed],
        "other_failed": [{"id": f["id"], "kind": f["kind"]} for f in s.get("failed", []) if f.get("kind") not in STRICT],
        "L3": s.get("L3_constrained"), "L4": s.get("L4_plausibility"),
        "g3_new_failures": new_fails, "output": s.get("L5_output_error") or {}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--seeds", nargs="*")
    ap.add_argument("--prune", action="store_true", help="delete bulky run outputs once a mutant is scored")
    a = ap.parse_args()
    jobs = []
    for sd in (a.seeds or SEEDS):
        jobs += jobs_for(sd)
    print(len(jobs), "mutants", flush=True)
    rows = []
    with ThreadPoolExecutor(a.workers) as ex:
        futs = {ex.submit(run_job, j, a.prune): j for j in jobs}
        for f in as_completed(futs):
            j = futs[f]
            try:
                r = f.result()
            except Exception as e:
                r = {"seed": j["seed"], "family": j["family"], "op": j["op"], "error": f"{type(e).__name__}: {e}",
                     "trace": traceback.format_exc()[-800:]}
            rows.append(r)
            print(f"{len(rows):4d}/{len(jobs)} {r['seed'][:4]} {r['family'][:4]} {r['op']:22s} C={r.get('C')} "
                  f"site={round((r.get('output') or {}).get('site_energy_gj', 0) * 100, 1) if r.get('output') else None}",
                  flush=True)
    res = ROOT / "results" / "mutation.json"
    old = json.loads(res.read_text()) if (res.is_file() and a.seeds) else []
    keep = [r for r in old if r["seed"] not in {x["seed"] for x in rows}]
    for r in keep + rows:  # the role of each mutant on its seed, from the documents (bemgen.mutate)
        r["role"] = mutate.role(r["seed"], r["family"], r["op"])
        r.pop("stated_in", None)
        src = mutate.role_source(r["seed"], r["family"], r["op"])
        if src:
            r["role_source"] = src
    res.write_text(json.dumps(keep + sorted(rows, key=lambda r: (r["seed"], r["family"], r["op"])), indent=1, default=str))


if __name__ == "__main__":
    main()
