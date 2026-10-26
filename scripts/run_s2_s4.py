"""S2 and S4 case studies.

S2  derive variants of the curated HERS BESTEST L100A item (relocations, a wall retrofit,
    a glazing retrofit, a rotation) and QA each derived reference.
S4  repair tasks from quarantined practice models; modality variants of virtual items;
    a round trip of the DOE small-office reference building; metamorphic relations
    checked on the reference pairs.

Usage: python scripts/run_s2_s4.py --weather work/weather --workers 6
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bemgen.generators import derive as D  # noqa: E402
from bemgen.generators import other as O  # noqa: E402
from bemgen.generators.s3 import PROBE_PLAN, sample_program  # noqa: E402
from bemgen.generators.harvest import public_copy  # noqa: E402
from bemgen.energyplus import run_model  # noqa: E402
from bemgen.facts import extract  # noqa: E402
from bemgen.idf import IDF  # noqa: E402
from bemgen.item import Item  # noqa: E402
from bemgen.qa import run_qa  # noqa: E402
from bemgen.schema import get_schema  # noqa: E402


def qa_summary(it: Item, runs: Path, W):
    d = run_qa(Item.load(it.root), runs, W).to_dict()
    c = d.get("conformance") or {}
    return {"item": it.id, "source": it.card.get("source_type"), "tier": d["tier"], "gates": d["gates"],
            "conformance": c.get("conformance"), "n_facts": c.get("n_facts"), "n_pass": c.get("n_pass"),
            "failed": [f["id"] for f in c.get("failed", [])], "unverified": [f["id"] for f in c.get("unverified", [])],
            "n_findings": d["n_findings"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weather", default=str(ROOT / "work" / "weather"))
    ap.add_argument("--work", default=str(ROOT / "work"))
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()
    W = Path(args.weather)
    work = Path(args.work)
    out_items = ROOT / "benchmark" / "items"
    results = {"S2": [], "S4": [], "metamorphic": []}

    # ------------------------------------------------------------------ S2
    seed = Item.load(work / "s1" / "curated" / "P08-bestest-l100a-cos")
    seed_facts = json.loads((work / "s1" / "curated_runs" / "P08-bestest-l100a-cos" / "reference" / "facts.json").read_text())
    m = IDF.load(seed.root / "reference" / "model.idf")
    from bemgen.ops import exterior_walls
    wall_cons = sorted({w.get(2) for w in exterior_walls(m)
                        if "ATTIC" not in w.get(3).upper() and "GABLE" not in w.name.upper()})
    variants = [
        D.relocate_variant("Miami", "FL", "USA_FL_Miami.Intl.AP.722020_TMY3.epw", "USA_FL_Miami.Intl.AP.722020_TMY3.ddy", W, "decrease"),
        D.relocate_variant("Seattle", "WA", "USA_WA_Seattle-Tacoma.Intl.AP.727930_TMY3.epw", "USA_WA_Seattle-Tacoma.Intl.AP.727930_TMY3.ddy", W, "decrease"),
        D.relocate_variant("Chicago", "IL", "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw", "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.ddy", W, "increase"),
        D.relocate_variant("Fairbanks", "AK", "USA_AK_Fairbanks.Intl.AP.702610_TMY3.epw", "USA_AK_Fairbanks.Intl.AP.702610_TMY3.ddy", W, "increase"),
        D.insulation_variant(wall_cons[0]),
        D.glazing_variant(),
        D.rotate_variant(90),
    ]
    s2_items = [D.derive(seed, v, out_items / "S2", seed_facts, W, "D01-l100a") for v in variants]
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        results["S2"] = list(ex.map(lambda it: qa_summary(it, work / "s2" / "runs", [W]), s2_items))
    for v, it in zip(variants, s2_items):
        vf = json.loads((work / "s2" / "runs" / it.id / "reference" / "facts.json").read_text())
        ok = O.check_relation(seed_facts, vf, v.relation)
        results["metamorphic"].append({"base": seed.id, "variant": it.id, "relation": v.relation, "holds_on_references": ok,
                                       "base_value": seed_facts["results"].get(v.relation["metric"]),
                                       "variant_value": vf["results"].get(v.relation["metric"])})

    # ------------------------------------------------------------------ S4 repair
    rep_specs = [("P06-iunit@direct", "agent output (documents straight to IDF)", "R01-iunit-direct"),
                 ("P08-bestest-l100a-cos@expected", "ASHRAE 140 EnergyPlus file converted to 23.1", "R02-l100a-cos-std140"),
                 ("P10-nist-nzertf@harness", "agent harness output", "R03-nzertf-harness"),
                 ("P04-office-narrative@harness", "agent harness output", "R04-office-narrative-harness")]
    cand = {(r["case"], r["candidate"]): r for r in json.loads((ROOT / "results" / "s1_candidates.json").read_text())}
    rep_items = []
    for src, label, rid in rep_specs:
        case, c = src.split("@")
        failing = [f["id"] for f in cand[(case, c)]["failed"]]
        rep_items.append(O.repair_item(Item.load(work / "s1" / "items" / src), work / "s4_private", label, failing, rid))
    # ------------------------------------------------------------------ S4 modality
    mod_items = []
    for idx in (1, 8, 16, 20):     # V02 office (IP spec), V09 retail (IP spec), V17 house (IP narrative), V21 rowhouse (SI narrative)
        arch, cname, probes, units, style, omitted = PROBE_PLAN[idx]
        p = sample_program(idx, arch, cname, probes, units, style, omitted, W)
        flip_u = "SI" if units == "IP" else "IP"
        flip_s = "spec" if style == "narrative" else "narrative"
        mod_items.append(O.modality_variant(p, out_items / "S4", W, flip_u, style, f"M-{flip_u.lower()}"))
        mod_items.append(O.modality_variant(p, out_items / "S4", W, units, flip_s, f"M-{flip_s}"))
    # ------------------------------------------------------------------ S4 round trip
    raw = IDF.load(work / "seeds" / "RefBldgSmallOfficeNew2004_Chicago.idf")
    sc = raw.first("SimulationControl")      # the test file runs design days only; the item needs the annual run
    sc.fields[3], sc.fields[4] = "No", "Yes"
    sc.comment = "! source: seed preparation (annual run instead of design days only)"
    src = work / "seeds" / "RefBldgSmallOfficeNew2004_Chicago_annual.idf"
    raw.save(src)
    epw = "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw"
    rr = run_model(IDF.load(src), W / epw, work / "seeds" / "run_smalloffice")
    S = get_schema()
    sf = extract(IDF.load(src), rr.run_dir, S, IDF.load(rr.expanded_idf) if rr.expanded_idf else None)
    rt = O.roundtrip_item(src, "DOE commercial reference building: small office, new construction, 90.1-2004 (EnergyPlus 23.1 test file)",
                          sf, epw, W, out_items / "S4", "T01-doe-small-office-chicago", "Chicago, IL",
                          "EnergyPlus test file, BSD-3-Clause-like EnergyPlus licence")
    s4 = rep_items + mod_items + [rt]
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        results["S4"] = list(ex.map(lambda it: qa_summary(it, work / "s4" / "runs", [W]), s4))
    # repair items are released without withheld files
    for it in rep_items:
        public_copy(Item.load(it.root), out_items / "S4")
    # invariance check on modality variants: identical reference -> identical facts
    (ROOT / "results" / "s2_s4.json").write_text(json.dumps(results, indent=1, default=str))
    for k, v in results.items():
        for r in v:
            print(k, json.dumps(r, default=str)[:300], flush=True)


if __name__ == "__main__":
    main()
