"""Admissible-model ensembles: how much do an item's documents determine its annual results?

    python scripts/ensembles.py --n 30 --workers 6

For each item, the inputs its documents leave open are sampled by Latin hypercube within plausible
ranges and applied to a copy of the reference (outdoor air, fan pressure and efficiency, slab
insulation, exterior solar absorptance, furniture mass, sizing factors, ground temperature, door
insulation; for P04 also window ratios, glazing and setpoints, which its documents do not fix).
Each member is simulated and graded against the item's fact sheet: only members that satisfy
every determined fact are admissible. The spread of their annual results is the item's
document-induced output band. The pilot runs of results/pilot.json are placed in the bands.

Writes results/ensembles.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bemgen import mutate, ops  # noqa: E402
from bemgen.energyplus import prune_run_dir  # noqa: E402
from bemgen.idf import IDF  # noqa: E402
from bemgen.item import Item  # noqa: E402
from bemgen.scoring import score  # noqa: E402

W = ROOT / "work" / "weather"
OUT = ROOT / "work" / "ensembles"
ITEMS = ["S3/V02-small-office-chicago", "S3/V03-small-office-seattle", "S3/V08-medium-office-rochester",
         "S3/V09-retail-las-vegas", "S3/V17-house-denver", "S3/V21-rowhouse-chicago",
         "S1/P02-lupton-heat-pump", "S1/P04-office-narrative"]
# parameter: (low, high); every item samples these unless excluded below
GENERIC = {"oa_L_s_person": (0.0, 7.5), "fan_factor": (0.5, 2.0), "fan_eff": (0.5, 0.75), "slab_xps_m": (0.0, 0.10),
           "absorptance": (0.3, 0.9), "furniture_ratio": (0.0, 1.5), "sizing": (1.0, 1.4), "ground_dT": (-3.0, 3.0),
           "door_insulated": (0.0, 1.0)}
EXTRA = {"P04-office-narrative": {"wwr_S": (0.15, 0.45), "wwr_E": (0.15, 0.45), "wwr_N": (0.15, 0.45), "wwr_W": (0.15, 0.45),
                                  "glass_u": (1.6, 3.5), "glass_shgc": (0.25, 0.60), "heat_dT": (-3.0, 1.9), "cool_dT": (-0.8, 3.0)}}
# inputs the documents of an item DO state (bemgen.mutate.STATED_INPUTS): not sampled there
PARAM_INPUT = {"oa_L_s_person": "outdoor_air", "fan_factor": "fans", "fan_eff": "fans", "slab_xps_m": "slab",
               "absorptance": "absorptance", "furniture_ratio": "internal_mass", "sizing": "sizing", "ground_dT": "ground",
               "door_insulated": "doors"}
EXCLUDE = {item: {p for p, inp in PARAM_INPUT.items() if inp in stated} for item, stated in mutate.STATED_INPUTS.items()}


def lhs(n, ranges, seed):
    rng = np.random.default_rng(seed)
    keys = list(ranges)
    u = np.empty((n, len(keys)))
    for j in range(len(keys)):
        u[:, j] = (rng.permutation(n) + rng.random(n)) / n
    return [{k: float(ranges[k][0] + u[i, j] * (ranges[k][1] - ranges[k][0])) for j, k in enumerate(keys)} for i in range(n)]


def ref_run_dir(item_id):
    for base in (ROOT / "work" / "s3" / "runs", ROOT / "work" / "s1" / "curated_runs"):
        d = base / item_id / "reference"
        if (d / "facts.json").is_file():
            return d
    raise FileNotFoundError(item_id)


def build_member(ref_path, p, cond):
    m = IDF.load(ref_path)
    ctx = {"conditioned_zones": cond}
    applied = []
    if "oa_L_s_person" in p:
        applied.append(mutate.a_outdoor_air(m, ctx, p["oa_L_s_person"] / 1000.0))
    if "fan_factor" in p:
        applied.append(mutate.a_fan(m, ctx, p["fan_factor"], p.get("fan_eff")))
    if "slab_xps_m" in p and p["slab_xps_m"] > 0.005:
        applied.append(mutate.a_slab_insulation(m, ctx, round(p["slab_xps_m"], 3)))
    if "absorptance" in p:
        applied.append(mutate.a_exterior_absorptance(m, ctx, round(p["absorptance"], 3)))
    if "furniture_ratio" in p and p["furniture_ratio"] > 0.05:
        applied.append(mutate.a_internal_mass(m, ctx, round(p["furniture_ratio"], 3)))
    if "sizing" in p:
        applied.append(mutate.a_sizing(m, ctx, p["sizing"], p["sizing"]))
    if "ground_dT" in p:
        applied.append(mutate.a_ground_temperature(m, ctx, p["ground_dT"]))
    if p.get("door_insulated", 0) >= 0.5:
        applied.append(mutate.a_door_insulated(m, ctx))
    if "wwr_S" in p:
        for w in mutate.windows(m):
            m.remove(w)
        vt = min(0.8, p["glass_shgc"] + 0.15)
        applied.append(ops.add_windows_by_wwr(m, {f: round(float(p[f"wwr_{f}"]), 3) for f in "NESW"}, round(p["glass_u"], 3),
                                              round(p["glass_shgc"], 3), round(vt, 3), glazing_name="Ensemble Glazing").description)
    if "heat_dT" in p:
        for n in mutate.setpoint_schedules(m, "heating"):
            mutate.schedule_shift(m, n, round(p["heat_dT"], 2))
        for n in mutate.setpoint_schedules(m, "cooling"):
            mutate.schedule_shift(m, n, round(p["cool_dT"], 2))
        applied.append(f"setpoints shifted {p['heat_dT']:+.1f} K heating, {p['cool_dT']:+.1f} K cooling")
    return m, [a for a in applied if a]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--items", nargs="*")
    ap.add_argument("--prune", action="store_true", help="delete bulky run outputs once a member is scored")
    a = ap.parse_args()
    jobs = []
    for k, sid in enumerate(a.items or ITEMS):
        item_dir = ROOT / "benchmark" / "items" / sid
        it = Item.load(item_dir)
        rdir = ref_run_dir(it.id)
        ref = json.loads((rdir / "facts.json").read_text())
        cond = {z.upper() for z, v in ref["geometry"]["zones"].items() if v.get("conditioned")}
        ranges = {kk: v for kk, v in GENERIC.items() if kk not in EXCLUDE.get(it.id, set())} | EXTRA.get(it.id, {})
        for i, p in enumerate(lhs(a.n, ranges, seed=1000 + k)):
            m, applied = build_member(it.reference_path(), p, cond)
            d = OUT / it.id / f"m{i:02d}"
            d.mkdir(parents=True, exist_ok=True)
            m.save(d / "model.idf")
            jobs.append({"item": it.id, "member": i, "params": p, "applied": applied, "model": d / "model.idf",
                         "item_dir": item_dir, "ref": ref})
    print(len(jobs), "members", flush=True)

    def run(j):
        it = Item.load(j["item_dir"])
        s = score(it, Path(j["model"]), Path(j["model"]).parent / "run", [W], reference_facts=j["ref"])
        f = json.loads((Path(j["model"]).parent / "run" / "facts.json").read_text())
        if a.prune:
            prune_run_dir(Path(j["model"]).parent / "run")
        r = f.get("results") or {}
        return {"item": j["item"], "member": j["member"], "params": j["params"], "applied": j["applied"],
                "C": s.get("L2_conformance"), "C_e": s.get("L2_conformance_evaluable"), "L1": s.get("L1_runs"),
                "failed": [x["id"] for x in s.get("failed", []) if x.get("kind") in ("stated", "derived", "provided")],
                "site_energy_gj": r.get("site_energy_gj"), "heating_gj": r.get("heating_gj"), "cooling_gj": r.get("cooling_gj"),
                "eui_mj_m2": r.get("eui_mj_m2"), "unmet_occupied_heating_h": r.get("unmet_occupied_heating_h"),
                "unmet_occupied_cooling_h": r.get("unmet_occupied_cooling_h")}
    rows = []
    with ThreadPoolExecutor(a.workers) as ex:
        futs = [ex.submit(run, j) for j in jobs]
        for f in as_completed(futs):
            try:
                rows.append(f.result())
            except Exception as e:
                rows.append({"error": f"{type(e).__name__}: {e}"})
            r = rows[-1]
            print(f"{len(rows):4d}/{len(jobs)} {r.get('item', '?')[:4]} m{r.get('member')} C={r.get('C')} site={r.get('site_energy_gj')}", flush=True)
    res = ROOT / "results" / "ensembles.json"
    old = json.loads(res.read_text()) if (res.is_file() and a.items) else {"members": []}
    keep = [r for r in old.get("members", []) if r.get("item") not in {x.get("item") for x in rows}]
    members = keep + sorted([r for r in rows if "item" in r], key=lambda r: (r["item"], r["member"]))
    res.write_text(json.dumps({"ranges": GENERIC, "extra": EXTRA, "exclude": {k: sorted(v) for k, v in EXCLUDE.items()},
                               "members": members, "errors": [r for r in rows if "error" in r]}, indent=1, default=str))


if __name__ == "__main__":
    main()
