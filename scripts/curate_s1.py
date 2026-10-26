"""S1 case study, step 2: curate the practice cases into benchmark items.

For each case the curator picks the candidate reference that needs the fewest
repairs *and* does not come from a system the item will be used to evaluate
(lineage), applies documented repairs, fixes document defects, records
clarifications, and re-runs QA. Cases whose defects cannot be repaired from
the documents alone stay in Quarantine. Every repair is written to
``CHANGES.md`` in the item.

Usage: python scripts/curate_s1.py --package work/package --weather work/weather
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bemgen import ops  # noqa: E402
from bemgen.generators.harvest import load_case, build_item, public_copy  # noqa: E402
from bemgen.idf import IDF  # noqa: E402
from bemgen.item import Item, sha256  # noqa: E402
from bemgen.qa import run_qa  # noqa: E402

WOOD_PANEL = [("Wood side panel 9in", 0.2286, 0.12, 510, 1380)]


def zone_areas(run_dir: Path) -> dict:
    f = json.loads((run_dir / "facts.json").read_text())
    return {k.upper(): v["floor_area"] for k, v in f["geometry"]["zones"].items()}


PLAN = {
    "P01-lupton-free-floating": {"candidate": "harness", "lineage": "agent harness (gbXML route)",
        "repairs": lambda m, ctx: [ops.add_internal_mass(m, m.by_class("Zone")[0].name, 14.86, WOOD_PANEL)]},
    "P02-lupton-heat-pump": {"candidate": "harness", "lineage": "agent harness (gbXML route)",
        "repairs": lambda m, ctx: [ops.add_internal_mass(m, m.by_class("Zone")[0].name, 14.86, WOOD_PANEL)],
        "doc_fixes": {"input2.txt": [(r"\(passive, unconditioned\)", "(with a heat pump)",
                                      "title said 'passive, unconditioned' although the house has a heat pump"),
                                     (r"\n- The nine DX performance curves.*?hr/yr\.", "",
                                      "removed development history (feat-008, feat-009 and an unmet-hours result)")]}},
    "P03-office-minimal": {"candidate": "harness", "lineage": "agent harness (gbXML route)",
        "repairs": lambda m, ctx: [ops.add_windows_by_wwr(m, {"N": 0.3, "E": 0.3, "S": 0.3, "W": 0.3}, 2.4, 0.35, 0.5),
                                   ops.add_sizing_factors(m)],
        "clarification_file": "Location: ZIP 85730 (Tucson, AZ). Given by the requester when asked; not in the original description.\n",
        "assumptions": {"windows": "WWR 0.30 on every facade, U 2.4, SHGC 0.35 (none described; an office has windows)",
                        "sizing": "heating 1.25, cooling 1.15 sizing factors to keep unmet hours plausible"}},
    "P04-office-narrative": {"candidate": "harness", "lineage": "agent harness (gbXML route)",
        "repairs": lambda m, ctx: [ops.add_windows_by_wwr(m, {"N": 0.25, "E": 0.25, "S": 0.3, "W": 0.25}, 2.4, 0.35, 0.5),
                                   ops.add_door(m, "S"), ops.add_door(m, "E", name="Service Door"), ops.add_sizing_factors(m)],
        "assumptions": {"windows": "located but not dimensioned: WWR 0.30 south, 0.25 elsewhere; double pane U 2.4, SHGC 0.35",
                        "doors": "0.91 x 2.13 m main entrance (south) and service door (east)"}},
    "P06-iunit": {"candidate": "expected", "lineage": "course reference model (instructor), repaired",
        "repairs": lambda m, ctx: [ops.set_people_total(m, 2.0),
                                   ops.set_equipment_total(m, 149.0, ctx["zone_areas"]),
                                   ops.thermostat_single(m, "*BATHROOM*", "heating", 23.3333),
                                   ops.set_surface_construction(m, "Face 8", "Floor construction layers"),
                                   ops.set_surface_construction(m, "Face 1", "Roof construction layers"),
                                   ops.set_surface_construction(m, "Face 26", "Roof construction layers")],
        "note": "Infiltration design flow 'I = 1' has no unit in the assignment; the reference uses 0.001133 m3/s per m2 of "
                "exterior surface. Coefficients A and B are graded; the design flow is left to the author to confirm."},
    "P07-ce-building-72": {"candidate": "harness", "lineage": "agent harness (gbXML route)",
        "repairs": lambda m, ctx: [ops.add_windows_by_wwr(m, {"N": 0.25, "E": 0.25, "S": 0.25, "W": 0.25}, 5.0, 0.6, 0.7)],
        "assumptions": {"windows": "WWR 0.25 single-pane-era glazing U 5.0, SHGC 0.6 (a 1964 building; plans show no window sizes)"}},
    "P08-bestest-l100a-cos": {"candidate": "harness", "lineage": "agent harness (gbXML route); the repaired ASHRAE 140 file is kept as an alternate",
        "repairs": lambda m, ctx: [],
        "alternate": {"candidate": "expected", "repairs": lambda m, ctx: [ops.thermostat_single(m, "*", "heating", 20.0)]}},
    "P09-bestest-l100a-lv": {"candidate": "harness", "lineage": "agent harness (gbXML route); the repaired ASHRAE 140 file is kept as an alternate",
        "repairs": lambda m, ctx: [],
        "alternate": {"candidate": "expected", "repairs": lambda m, ctx: [ops.thermostat_single(m, "*", "cooling", 25.5556)]}},
}
QUARANTINE = {
    "P05-tract-house-plan": "the two floor plans in the inputs show different layouts and areas (1,815 vs 1,958 sq ft) and no "
                            "precedence rule is given; scan images show the interior of a private home; the builder plan is "
                            "third-party material. Needs the requester to say which source governs, and cleared images.",
    "P10-nist-nzertf": "every candidate contradicts the input sheet on several facets (the third-party reference: location, "
                       "timestep, PV, setpoints, floor area, occupants; both agent models: ERV, dehumidifier, heat-pump water "
                       "heater, solar thermal, glazing ratio). A conforming reference needs an expert rebuild. Released as "
                       "repair tasks (S4) instead.",
}


def apply_doc_fixes(item_root: Path, fixes: dict) -> list:
    log = []
    for fname, subs in fixes.items():
        p = item_root / "inputs" / fname
        txt = p.read_text(encoding="utf-8")
        for pat, rep, why in subs:
            new = re.sub(pat, rep, txt, flags=re.S)
            if new != txt:
                log.append(f"- `{fname}`: {why}")
                txt = new
        p.write_text(txt, encoding="utf-8")
    return log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--package", required=True)
    ap.add_argument("--weather", required=True)
    ap.add_argument("--work", default=str(ROOT / "work" / "s1"))
    ap.add_argument("--public", default=str(ROOT / "benchmark" / "items" / "S1"))
    ap.add_argument("--only", nargs="*")
    args = ap.parse_args()
    W = [Path(args.weather)]
    work = Path(args.work)
    out = []
    for cp in sorted((ROOT / "cases" / "practice").glob("P*.yaml")):
        case = load_case(cp)
        cid = case["id"]
        if args.only and cid not in args.only:
            continue
        if cid in QUARANTINE:
            out.append({"case": cid, "status": "quarantined", "reason": QUARANTINE[cid]})
            continue
        plan = PLAN[cid]
        cand = plan["candidate"]
        src_run = work / "runs" / f"{cid}@{cand}" / "reference"
        ctx = {"zone_areas": zone_areas(src_run)} if (src_run / "facts.json").is_file() else {}
        model = IDF.load(Path(args.package) / case["candidates"][cand]["path"])
        changes = plan["repairs"](model, ctx)
        tmp = work / "curated_models"
        tmp.mkdir(parents=True, exist_ok=True)
        mpath = tmp / f"{cid}.idf"
        model.save(mpath)
        sides = [Path(args.package) / s for s in case["candidates"][cand].get("side_files", [])]
        extra = {"curation": {"from_candidate": cand, "lineage": plan["lineage"],
                              "repairs": [c.to_dict() for c in changes], "note": plan.get("note", "")},
                 "assumptions": plan.get("assumptions")}
        if case.get("candidates", {}).get(cand, {}).get("redistributable") is not None:
            pass
        it = build_item(case, args.package, work / "curated", cand, W, item_id=cid, reference_override=mpath,
                        side_override=sides, extra_card=extra)
        it.card["reference"]["redistributable"] = case["candidates"][cand].get("redistributable")
        doc_log = apply_doc_fixes(it.root, plan.get("doc_fixes", {}))
        if plan.get("clarification_file"):
            (it.root / "inputs" / "clarifications.md").write_text(plan["clarification_file"], encoding="utf-8")
            it.card["inputs"].append({"path": "inputs/clarifications.md", "kind": "text", "redistributable": True,
                                      "rights": "curator record of a clarification", "sha256": sha256(it.root / "inputs" / "clarifications.md")})
        for rec in it.card["inputs"]:
            p = it.root / rec["path"]
            if p.is_file():
                rec["sha256"] = sha256(p)
        # alternate reference (kept privately when rights are not cleared)
        if plan.get("alternate"):
            alt = plan["alternate"]
            am = IDF.load(Path(args.package) / case["candidates"][alt["candidate"]]["path"])
            ach = alt["repairs"](am, ctx)
            am.save(it.root / "reference" / "alternate_model.idf")
            it.card["alternate_references"] = [{"path": "reference/alternate_model.idf", "from_candidate": alt["candidate"],
                                                "origin": case["candidates"][alt["candidate"]].get("origin"),
                                                "redistributable": case["candidates"][alt["candidate"]].get("redistributable"),
                                                "repairs": [c.to_dict() for c in ach]}]
        it.save()
        L = [f"# Curation log: {cid}", "", f"Reference taken from candidate `{cand}` ({plan['lineage']}).", ""]
        if changes:
            L += ["## Model repairs", ""] + [f"- {c.op} ({c.facet}): {c.description}" for c in changes] + [""]
        if doc_log:
            L += ["## Document fixes", ""] + doc_log + [""]
        if plan.get("clarification_file"):
            L += ["## Clarifications recorded", "", "- `clarifications.md` added (" + plan["clarification_file"].strip() + ")", ""]
        if plan.get("assumptions"):
            L += ["## Assumptions in the reference", ""] + [f"- {k}: {v}" for k, v in plan["assumptions"].items()] + [""]
        if plan.get("note"):
            L += ["## Open question for the author", "", plan["note"], ""]
        (it.root / "CHANGES.md").write_text("\n".join(L), encoding="utf-8")
        rep = run_qa(Item.load(it.root), work / "curated_runs", W)
        d = rep.to_dict()
        alt_res = None
        if (it.root / "reference" / "alternate_model.idf").is_file():
            alt_item_root = work / "curated_alt" / cid
            if alt_item_root.exists():
                shutil.rmtree(alt_item_root)
            shutil.copytree(it.root, alt_item_root)
            shutil.copy2(alt_item_root / "reference" / "alternate_model.idf", alt_item_root / "reference" / "model.idf")
            ar = run_qa(Item.load(alt_item_root), work / "curated_alt_runs", W).to_dict()
            alt_res = {"tier": ar["tier"], "conformance": (ar.get("conformance") or {}).get("conformance"),
                       "failed": [f["id"] for f in (ar.get("conformance") or {}).get("failed", [])]}
        c = d.get("conformance") or {}
        out.append({"case": cid, "status": "curated", "tier": d["tier"], "gates": d["gates"], "n_findings": d["n_findings"],
                    "conformance": c.get("conformance"), "n_facts": c.get("n_facts"), "n_pass": c.get("n_pass"),
                    "failed": [f["id"] for f in c.get("failed", [])], "unverified": [f["id"] for f in c.get("unverified", [])],
                    "open_major": [f["message"] for f in d["findings"] if f["severity"] == "major" and f["open"]],
                    "repairs": len(changes), "doc_fixes": len(doc_log), "alternate": alt_res,
                    "spec_profile": d.get("spec_profile")})
        pc = public_copy(Item.load(it.root), args.public)
        print(f"{cid:28s} tier={d['tier']:10s} conf={c.get('conformance')} failed={out[-1]['failed']} alt={alt_res} -> {pc}", flush=True)
    res = ROOT / "results" / "s1_curated.json"
    old = json.loads(res.read_text()) if (res.is_file() and args.only) else []
    keep = [r for r in old if r["case"] not in {o["case"] for o in out}]
    res.write_text(json.dumps(keep + out, indent=1, default=str))


if __name__ == "__main__":
    main()
