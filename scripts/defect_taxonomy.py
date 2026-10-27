"""Where do benchmark defects come from, and what finds them?

    python scripts/defect_taxonomy.py

Merges three sources into one list of defects:
* cases/defect_catalogue.yaml: defects in documents, references, agent models, the checker and the generators;
* results/s1_candidates.json: every determined fact that an S1 candidate model contradicts (found by gate G4);
* results/mutation.json (if present): checker gaps, i.e. defect mutants the fact sheet accepted (completeness)
  and admissible or equivalent mutants it rejected (soundness).

Writes results/defect_taxonomy.json with the list and cross-tabulations (origin x finder, origin x type,
model defects by facet).
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bemgen import mutate  # noqa: E402

RES = ROOT / "results"
MISSING_HINT = ("win", "door", "erv", "dehum", "hpwh", "solar", "pv", "internal-mass", "entrance", "windows")
ORIGIN = {"expected": "supplied_reference", "harness": "agent_model", "direct": "agent_model"}


def model_type(fact_id: str, observed) -> str:
    empty = observed in (0, 0.0, None, False, [], {}) or (isinstance(observed, list) and not any(observed))
    if any(h in fact_id.lower() for h in MISSING_HINT) and empty:
        return "missing_component"
    return "wrong_value"


def main():
    cat = yaml.safe_load((ROOT / "cases" / "defect_catalogue.yaml").read_text(encoding="utf-8"))["defects"]
    rows = [dict(d) for d in cat]
    for r in json.loads((RES / "s1_candidates.json").read_text()):
        if not (r.get("run") or {}).get("completed", True):  # did not run: its facts were never extracted (defect A01)
            continue
        for f in r.get("failed", []):
            if f.get("kind") not in ("stated", "derived", "provided"):
                continue
            rows.append({"id": f"{r['case'][:3]}-{r['candidate']}-{f['id']}", "origin": ORIGIN[r["candidate"]],
                         "case": r["case"][:3], "candidate": r["candidate"], "facet": f["facet"],
                         "type": model_type(f["id"], f.get("observed")), "found_by": "G4", "text": f.get("text", "")})
    mpath = RES / "mutation.json"
    if mpath.is_file():
        for m in json.loads(mpath.read_text()):
            if "error" in m or m.get("C") is None:
                continue
            role = mutate.role(m["seed"], m["family"], m["op"])  # per seed, from the documents (bemgen.mutate)
            if role == "defect" and m["C"] >= 1.0:
                rows.append({"id": f"MUT-{m['seed'][:4]}-{m['op']}", "origin": "checker", "case": m["seed"][:3],
                             "facet": m.get("facet"), "type": "coverage_gap", "found_by": "mutation",
                             "text": f"defect mutant accepted by the fact sheet: {m.get('description')}"
                                     + (f" (documents: {mutate.role_source(m['seed'], m['family'], m['op'])})"
                                        if mutate.role_source(m["seed"], m["family"], m["op"]) else "")})
            if role in ("admissible", "equivalent") and m["C"] < 1.0:
                rows.append({"id": f"MUT-{m['seed'][:4]}-{m['op']}", "origin": "checker", "case": m["seed"][:3],
                             "facet": m.get("facet"), "type": "convention_mismatch", "found_by": "mutation",
                             "text": f"{role} mutant rejected: {m.get('description')}; failed "
                                     f"{[x['id'] for x in m.get('failed', [])]}"})
    by_of = defaultdict(Counter)
    by_ot = defaultdict(Counter)
    facet_models = defaultdict(Counter)
    for r in rows:
        by_of[r["origin"]][r["found_by"]] += 1
        by_ot[r["origin"]][r["type"]] += 1
        if r["origin"] in ("supplied_reference", "agent_model", "curated_reference"):
            facet_models[r["origin"]][r["facet"]] += 1
    doc = {"n": len(rows), "origin_x_finder": {k: dict(v) for k, v in by_of.items()},
           "origin_x_type": {k: dict(v) for k, v in by_ot.items()},
           "model_defects_by_facet": {k: dict(v) for k, v in facet_models.items()}, "defects": rows}
    (RES / "defect_taxonomy.json").write_text(json.dumps(doc, indent=1, default=str))
    print(json.dumps({k: v for k, v in doc.items() if k != "defects"}, indent=1))


if __name__ == "__main__":
    main()


def figure():
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    doc = json.loads((RES / "defect_taxonomy.json").read_text())
    origins = [("documents", "input documents"), ("supplied_reference", "supplied references"), ("agent_model", "agent models"),
               ("curated_reference", "curated references"), ("generator", "generators"), ("checker", "the checker")]
    finders = [("fact_sheet_writing", "writing the\nfact sheet"), ("G0", "G0\nrights"), ("G1", "G1\nschema"), ("G2", "G2\nruns"),
               ("G3", "G3\nplausibility"), ("G4", "G4\nconformance"), ("G6", "G6\nleakage"), ("pilot", "pilot\nagent"),
               ("mutation", "check\naudit"), ("inspection", "inspection\nor review")]
    M = np.zeros((len(origins), len(finders)))
    for r in doc["defects"]:
        f = "inspection" if r["found_by"] == "review" else r["found_by"]
        i = [o for o, _ in origins].index(r["origin"])
        j = [x for x, _ in finders].index(f)
        M[i, j] += 1
    cmap = LinearSegmentedColormap.from_list("b", ["#f0efec", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"])
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5})
    fig, ax = plt.subplots(figsize=(7.4, 2.7))
    ax.imshow(np.log1p(M), cmap=cmap, aspect="auto", vmin=0, vmax=np.log1p(M.max()))
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = int(M[i, j])
            ax.text(j, i, str(v) if v else "", ha="center", va="center", fontsize=7,
                    color="white" if np.log1p(v) > 0.6 * np.log1p(M.max()) else "#0b0b0b")
    ax.set_xticks(range(len(finders)))
    ax.set_xticklabels([b for _, b in finders], fontsize=6.1)
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(origins)))
    ax.set_yticklabels([f"{b}  ({int(M[i].sum())})" for i, (_, b) in enumerate(origins)], fontsize=7)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    fig.tight_layout()
    out = RES / "figures"
    fig.savefig(out / "fig_taxonomy.png", dpi=600)
    fig.savefig(out / "fig_taxonomy.pdf")
    plt.close(fig)


if __name__ == "__main__" and "--figure" in sys.argv:
    figure()
