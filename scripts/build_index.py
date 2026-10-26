"""Build the benchmark index and the release-status table from the released items.

    python scripts/build_index.py

Writes benchmark/index.json, benchmark/README.md and results/release_status.json.

For every item it records the tier, the open findings, the files withheld for rights, whether the
item can be used without the originals, and its *family*: the root case it descends from. Items of
one family share ground truth (a repair task's answer is its parent's reference, a derived variant
inherits its seed's facts), so a benchmark split must keep a family together.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bemgen.item import Item  # noqa: E402

B = ROOT / "benchmark"


def family(card: dict, cards: dict) -> str:
    seen = set()
    iid = card["id"]
    while True:
        parents = [p.split("@")[0] for p in (cards.get(iid, {}).get("parents") or [])]
        if not parents or iid in seen:
            return iid
        seen.add(iid)
        iid = parents[0]


def withheld(card: dict) -> list:
    out = [r["path"] for r in card.get("inputs", []) if r.get("withheld")]
    ref = card.get("reference") or {}
    if ref.get("withheld") and ref.get("path"):
        out.append(ref["path"])
    for a in card.get("alternate_references") or []:
        if a.get("withheld"):
            out.append(a["path"])
    return out


def main():
    dirs = sorted(p.parent for p in (B / "items").glob("*/*/item.yaml"))
    cards = {d.name: yaml.safe_load((d / "item.yaml").read_text(encoding="utf-8")) for d in dirs}
    rows = []
    for d in dirs:
        c = cards[d.name]
        it = Item.load(d)
        sp = it.spec()
        rep = json.loads((d / "qa" / "report.json").read_text()) if (d / "qa" / "report.json").is_file() else {}
        open_major = [f"{f['gate']}: {f['message']}" for f in rep.get("findings", [])
                      if f.get("severity") == "major" and f.get("open")]
        wh = withheld(c)
        task_type = c.get("task_type", "build")
        ref = c.get("reference") or {}
        has_ref = bool(ref.get("path")) and not ref.get("withheld") and (d / ref["path"]).is_file()
        draft = (c.get("draft") or {}).get("path")
        inputs_ok = not [r for r in c.get("inputs", []) if r.get("withheld")]
        if task_type == "repair":
            usable = inputs_ok and bool(draft) and (d / draft).is_file()
        elif c.get("invariance"):
            usable = True          # shares the parent's reference and fact sheet
        else:
            usable = inputs_ok and has_ref
        bk = sp.by_kind()
        rows.append({"id": d.name, "path": str(d.relative_to(B)).replace("\\", "/"), "source_type": c.get("source_type"),
                     "task_type": task_type, "title": c.get("title"), "facts": len(sp.facts), "by_kind": bk,
                     "tier": rep.get("tier", "Bronze"), "open_major": open_major, "probes": (c.get("tags") or {}).get("probes") or [],
                     "weather": (c.get("weather") or {}).get("file"), "withheld_files": wh,
                     "usable_without_originals": usable, "family": family(c, cards),
                     "public_reference": bool(c.get("public_reference"))})
    fams = {}
    for r in rows:
        fams.setdefault(r["family"], []).append(r["id"])
    for r in rows:
        r["family_members"] = [x for x in fams[r["family"]] if x != r["id"]]
    (B / "index.json").write_text(json.dumps(rows, indent=1))
    (ROOT / "results" / "release_status.json").write_text(json.dumps(rows, indent=1))

    n = len(rows)
    tiers = sorted({r["tier"] for r in rows})
    L = ["# Released benchmark items", "",
         f"{n} items. Every item passed the automated QA gates that apply to it; none has an expert sign-off yet "
         f"(gate G7), so all are **{'/'.join(tiers)}**. Review packets are in each item's `qa/review_packet.md`.", "",
         "**Splits.** Items of one *family* share ground truth: a repair task's answer is its parent's reference, and "
         "derived and modality variants inherit their parent's facts. Keep a family in one split (all in development "
         "or all in test).", "",
         "**Withheld files.** Files whose redistribution rights are not cleared are replaced by their SHA-256 hash and "
         "source; items marked *needs originals* cannot be used until those files are obtained.", "",
         "| Item | Source | Facts | Probes | Open major findings | Withheld files | Usable as released | Family |",
         "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        L.append(f"| [{r['id']}]({r['path']}) | {r['source_type']} | {r['facts']} | {', '.join(r['probes'])} | "
                 f"{len(r['open_major']) or ''} | {len(r['withheld_files']) or ''} | "
                 f"{'yes' if r['usable_without_originals'] else 'needs originals'} | {r['family']} |")
    (B / "README.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{n} items; families {len(fams)}; not usable as released: "
          f"{[r['id'] for r in rows if not r['usable_without_originals']]}; with open majors: "
          f"{[(r['id'], len(r['open_major'])) for r in rows if r['open_major']]}")


if __name__ == "__main__":
    main()
