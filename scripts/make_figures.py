"""Draw the paper's figures from results/*.json into results/figures/.

Usage: python scripts/make_figures.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
RES = ROOT / "results"
OUT = RES / "figures"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.titlesize": 9, "axes.labelsize": 8,
                     "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "legend.fontsize": 7.5, "axes.spines.top": False,
                     "axes.spines.right": False, "savefig.dpi": 300})
INK, QUIET, GRID = "#222222", "#6b6b6b", "#d9d9d9"
ACCENT = "#1f5fa8"
GOOD, WARN, BAD, NA = "#4d9a5b", "#e0a43a", "#c8513f", "#bdbdbd"


def box(ax, x, y, w, h, title, lines=(), fc="white", ec="#555555", lw=0.9, tsize=8.2, accent=False):
    if accent:
        fc, ec, lw = "#e8f0fa", ACCENT, 1.4
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.006,rounding_size=0.012", fc=fc, ec=ec, lw=lw))
    ax.text(x + 0.012, y + h - 0.022, title, ha="left", va="top", fontsize=tsize, weight="bold", color=INK)
    for i, ln in enumerate(lines):
        ax.text(x + 0.012, y + h - 0.058 - i * 0.033, ln, ha="left", va="top", fontsize=6.9, color=INK)


def arrow(ax, x1, y1, x2, y2, color="#555555", lw=0.9):
    ax.annotate("", (x2, y2), (x1, y1), arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, shrinkA=0, shrinkB=0,
                                                         mutation_scale=7))


def fig1_framework():
    fig = plt.figure(figsize=(7.2, 4.5))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    srcs = [("S1  Everyday BEM work", ["projects, coursework, agent test sets", "QA every candidate; repair the best", "fix documents; log clarifications"]),
            ("S2  Validated seeds", ["change model, addendum and facts", "together (paired transformation);", "record a metamorphic relation"]),
            ("S3  Virtual programs", ["one program gives the reference IDF,", "the documents and analytic facts;", "expertise probes placed on purpose"]),
            ("S4  Other generators", ["repair tasks, modality variants,", "round trips of validated models,", "metamorphic pairs"])]
    h, gap, top = 0.165, 0.022, 0.975
    for i, (t, ls) in enumerate(srcs):
        y = top - h - i * (h + gap)
        box(ax, 0.012, y, 0.262, h, t, ls, tsize=7.8)
        arrow(ax, 0.276, y + h / 2, 0.318, 0.56)
    x0, w = 0.32, 0.255
    ax.add_patch(FancyBboxPatch((x0, 0.25), w, 0.66, boxstyle="round,pad=0.006,rounding_size=0.012", fc="white", ec="#555555", lw=0.9))
    ax.text(x0 + 0.012, 0.888, "Benchmark item", ha="left", va="top", fontsize=8.2, weight="bold", color=INK)
    parts = [("task.md", ["instruction, weather, period"]), ("inputs/", ["documents; withheld files hashed"]),
             ("spec.yaml  (ground truth)", ["facts: stated, derived, provided,", "constrained, assumed; checkable"]),
             ("reference/", ["one valid IDF (+ alternates)"]), ("item.yaml", ["rights, lineage, tags, tier"]),
             ("qa/", ["gate report, review packet"])]
    yy = 0.835
    for name, descs in parts:
        acc = name.startswith("spec")
        hh = 0.032 + 0.034 * len(descs) + 0.006
        if acc:
            ax.add_patch(FancyBboxPatch((x0 + 0.008, yy - hh + 0.01), w - 0.016, hh, boxstyle="round,pad=0.003,rounding_size=0.01",
                                        fc="#e8f0fa", ec=ACCENT, lw=1.2))
        ax.text(x0 + 0.016, yy, name, ha="left", va="top", fontsize=7.2, weight="bold", color=ACCENT if acc else INK)
        for j, d in enumerate(descs):
            ax.text(x0 + 0.026, yy - 0.032 - j * 0.034, d, ha="left", va="top", fontsize=6.6, color=INK)
        yy -= hh + 0.018
    gx, gw = 0.605, 0.222
    ax.add_patch(FancyBboxPatch((gx, 0.25), gw, 0.66, boxstyle="round,pad=0.006,rounding_size=0.012", fc="white", ec="#555555", lw=0.9))
    ax.text(gx + 0.012, 0.888, "QA gates, every source", ha="left", va="top", fontsize=8.2, weight="bold", color=INK)
    gates = ["G0 packaging and rights", "G1 schema", "G2 execution", "G3 integrity, plausibility", "G4 document conformance",
             "G5 determinacy, ledger", "G6 leakage", "G7 expert review"]
    for i, g in enumerate(gates):
        yg = 0.835 - i * 0.07
        ax.add_patch(FancyBboxPatch((gx + 0.01, yg - 0.05), gw - 0.02, 0.05, boxstyle="round,pad=0.003,rounding_size=0.008",
                                    fc="#e8f0fa" if g.startswith("G4") else "#f4f4f4", ec=ACCENT if g.startswith("G4") else "#999999",
                                    lw=1.0 if g.startswith("G4") else 0.6))
        ax.text(gx + 0.02, yg - 0.025, g, ha="left", va="center", fontsize=6.6, color=INK)
    arrow(ax, x0 + w + 0.004, 0.56, gx - 0.004, 0.56)
    tiers = [("Quarantine", "open blocking finding", BAD), ("Bronze", "automated gates", "#a0763c"),
             ("Silver", "+1 expert review", "#8c8c8c"), ("Gold", "+2 agreeing reviews", "#c9a227")]
    tx = 0.85
    for i, (t, d, c) in enumerate(tiers):
        yt = 0.905 - i * 0.165
        ax.add_patch(FancyBboxPatch((tx, yt - 0.12), 0.138, 0.12, boxstyle="round,pad=0.004,rounding_size=0.01", fc="white", ec=c, lw=1.4))
        ax.text(tx + 0.01, yt - 0.035, t, ha="left", va="center", fontsize=7.6, weight="bold", color=INK)
        ax.text(tx + 0.01, yt - 0.08, d, ha="left", va="center", fontsize=6.2, color=QUIET)
        arrow(ax, gx + gw + 0.008, 0.56, tx - 0.003, yt - 0.06, color="#888888", lw=0.7)
    ax.add_patch(FancyBboxPatch((0.012, 0.022), 0.976, 0.17, boxstyle="round,pad=0.006,rounding_size=0.012", fc="#fafafa", ec="#555555", lw=0.9))
    ax.text(0.024, 0.176, "Scoring a system under test (documents to candidate IDF)", ha="left", va="top", fontsize=8.0, weight="bold", color=INK)
    levels = [("L0 valid", "schema check", ""), ("L1 runs", "no severe error", ""), ("L2 conformance", "primary metric,", "by facet and probe"),
              ("L3 constrained", "code and standard", "facts"), ("L4 plausible", "assumed values", "in range"), ("L5 outputs", "vs reference or", "ensemble band")]
    bw, bg = 0.147, 0.013
    for i, (lv, n1, n2) in enumerate(levels):
        x = 0.026 + i * (bw + bg)
        prim = lv.startswith("L2")
        ax.add_patch(FancyBboxPatch((x, 0.036), bw, 0.092, boxstyle="round,pad=0.004,rounding_size=0.01",
                                    fc="#e8f0fa" if prim else "white", ec=ACCENT if prim else "#999999", lw=1.2 if prim else 0.7))
        ax.text(x + 0.008, 0.108, lv, ha="left", va="center", fontsize=7.0, weight="bold", color=ACCENT if prim else INK)
        ax.text(x + 0.008, 0.078, n1, ha="left", va="center", fontsize=6.2, color=QUIET)
        ax.text(x + 0.008, 0.054, n2, ha="left", va="center", fontsize=6.2, color=QUIET)
        if i < len(levels) - 1:
            arrow(ax, x + bw + 0.001, 0.082, x + bw + bg - 0.001, 0.082, color="#888888", lw=0.7)
    arrow(ax, x0 + w / 2, 0.247, x0 + w / 2, 0.196)
    ax.text(x0 + w / 2 + 0.008, 0.222, "systems are graded against the fact sheet", ha="left", va="center", fontsize=6.4, color=QUIET)
    fig.savefig(OUT / "fig1_framework.png")
    fig.savefig(OUT / "fig1_framework.pdf")
    plt.close(fig)


# ---------------------------------------------------------------- S1 candidates
CASE_SHORT = {"P01-lupton-free-floating": "P01 adobe house", "P02-lupton-heat-pump": "P02 adobe house + HP",
              "P03-office-minimal": "P03 office (list)", "P04-office-narrative": "P04 office (prose)",
              "P05-tract-house-plan": "P05 tract house", "P06-iunit": "P06 iUnit",
              "P07-ce-building-72": "P07 univ. building", "P08-bestest-l100a-cos": "P08 BESTEST, CO",
              "P09-bestest-l100a-lv": "P09 BESTEST, NV", "P10-nist-nzertf": "P10 NIST NZERTF"}
CAND_LABEL = {"expected": "expert or standard ref.", "harness": "agent harness", "direct": "agent, direct route"}


def fig3_s1_matrix():
    R = json.loads((RES / "s1_candidates.json").read_text())
    order = {"expected": 0, "harness": 1, "direct": 2}
    R.sort(key=lambda r: (r["case"], order[r["candidate"]]))
    gates = ["G0", "G1", "G2", "G3", "G4", "G6"]
    gnames = ["G0\nrights", "G1\nschema", "G2\nruns", "G3\nplausible", "G4\nconforms", "G6\nleakage"]
    col = {"pass": GOOD, "warn": WARN, "fail": BAD, "skip": NA, "pending": NA}
    n = len(R)
    fig = plt.figure(figsize=(7.2, 0.24 * n + 1.5))
    axm = fig.add_axes([0.42, 0.15, 0.32, 0.76])
    axb = fig.add_axes([0.77, 0.15, 0.2, 0.76])
    for i, r in enumerate(R):
        y = n - 1 - i
        for j, g in enumerate(gates):
            st = r["gates"].get(g, "skip")
            axm.add_patch(plt.Rectangle((j, y), 0.94, 0.86, color=col.get(st, NA), lw=0))
            if g == "G4":
                nf = len(r["failed"])
                if nf:
                    axm.text(j + 0.47, y + 0.43, str(nf), ha="center", va="center", fontsize=6.8, color="white", weight="bold")
        lab = f"{CASE_SHORT[r['case']]}  |  {CAND_LABEL[r['candidate']]}"
        axm.text(-0.15, y + 0.43, lab, ha="right", va="center", fontsize=6.6,
                 color=INK if r["candidate"] != "expected" else "#000000", weight="bold" if r["candidate"] == "expected" else "normal")
        c = r["conformance"] or 0
        axb.barh(y + 0.43, c * 100, height=0.7, color=ACCENT if r["candidate"] != "expected" else "#7a7a7a")
        axb.text(c * 100 + 1.5, y + 0.43, f"{c * 100:.0f}", va="center", fontsize=6.6, color=INK)
    axm.set_xlim(0, len(gates))
    axm.set_ylim(0, n)
    axm.set_xticks([j + 0.47 for j in range(len(gates))])
    axm.set_xticklabels(gnames, fontsize=6.6)
    axm.xaxis.tick_top()
    axm.set_yticks([])
    for s in axm.spines.values():
        s.set_visible(False)
    axm.tick_params(length=0)
    axb.set_ylim(0, n)
    axb.set_xlim(0, 115)
    axb.set_yticks([])
    axb.set_xlabel("conformance C (%)")
    axb.spines["left"].set_visible(False)
    axb.axvline(100, color=GRID, lw=0.8)
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color=GOOD, label="pass"), Patch(color=WARN, label="warning"), Patch(color=BAD, label="fail (number = facts contradicted)"),
                        Patch(color=NA, label="not run")], loc="lower left", ncol=4, frameon=False, fontsize=6.6, bbox_to_anchor=(0.02, 0.0))
    fig.savefig(OUT / "fig3_s1_candidates.png")
    fig.savefig(OUT / "fig3_s1_candidates.pdf")
    plt.close(fig)





# ---------------------------------------------------------------- S3 verification and fact composition
FACET_COLORS = {"geometry": "#1f5fa8", "fenestration": "#4d9a5b", "envelope": "#a0763c", "loads": "#c8513f",
                "schedules": "#7b5ea7", "infiltration": "#e0a43a", "control": "#2a9d8f", "hvac": "#555555",
                "site": "#8c8c8c", "simulation": "#bbbbbb"}


def fig4_s3_parity():
    R = json.loads((RES / "s3_items.json").read_text())
    pts = defaultdict(list)
    n_ok = n_all = 0
    for r in R:
        g = json.loads((ROOT / "work" / "s3" / "runs" / r["item"] / "reference" / "grade.json").read_text())
        for f in g["results"]:
            c = f["check"]
            if c.get("op") != "approx" or not isinstance(f["observed"], (int, float)):
                continue
            exp = float(c["value"])
            if exp == 0:
                continue
            pts[f["facet"]].append((exp, float(f["observed"])))
            n_all += 1
            n_ok += f["pass"] is True
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.2), gridspec_kw={"width_ratios": [1.15, 1]})
    ax = axs[0]
    for fc, v in sorted(pts.items(), key=lambda kv: -len(kv[1])):
        xs, ys = zip(*v)
        ax.scatter(xs, ys, s=9, color=FACET_COLORS.get(fc, "#999999"), alpha=0.75, lw=0, label=f"{fc} ({len(v)})")
    lo, hi = 0.01, 2e4
    ax.plot([lo, hi], [lo, hi], color=QUIET, lw=0.7, ls="--")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    ax.set_xlabel("analytic value from the program")
    ax.set_ylabel("value extracted after EnergyPlus run")
    ax.set_title(f"S3: {n_ok} of {n_all} numeric facts within tolerance", loc="left")
    ax.legend(frameon=False, fontsize=6.2, loc="upper left", handletextpad=0.2, borderaxespad=0.2)
    ax = axs[1]
    rel = []
    for fc, v in pts.items():
        for e, o in v:
            rel.append((o - e) / abs(e) * 100)
    ax.hist(rel, bins=[x / 4 for x in range(-12, 13)], color=ACCENT, alpha=0.85)
    ax.set_xlabel("relative difference (%)")
    ax.set_ylabel("facts")
    ax.set_title("difference, extracted vs analytic", loc="left")
    ax.text(0.98, 0.95, f"max |diff| {max(abs(x) for x in rel):.2f} %", transform=ax.transAxes, ha="right", va="top", fontsize=7, color=INK)
    fig.tight_layout()
    fig.savefig(OUT / "fig4_s3_parity.png"); fig.savefig(OUT / "fig4_s3_parity.pdf")
    plt.close(fig)


def fig2_fact_composition():
    """Determinacy class of facts, by item group."""
    from bemgen.item import Item
    groups = []
    s1 = json.loads((RES / "s1_curated.json").read_text())
    for r in sorted(s1, key=lambda r: r["case"]):
        from bemgen.generators.harvest import load_case, spec_from_case
        sp = spec_from_case(load_case(ROOT / "cases" / "practice" / f"{r['case']}.yaml"))
        groups.append((r["case"].split("-")[0], "S1", sp.by_kind()))
    s3 = Counter()
    for p in sorted((ROOT / "benchmark" / "items" / "S3").iterdir()):
        sp = Item.load(p).spec()
        for k, v in sp.by_kind().items():
            s3[k] += v
    s2 = Counter()
    for p in sorted((ROOT / "benchmark" / "items" / "S2").iterdir()):
        for k, v in Item.load(p).spec().by_kind().items():
            s2[k] += v
    groups.append(("S2 (7 items)", "S2", dict(s2)))
    groups.append(("S3 (24 items)", "S3", dict(s3)))
    kinds = ["stated", "derived", "provided", "constrained", "assumed"]
    kcol = {"stated": ACCENT, "derived": "#6f9fd8", "provided": "#a9c6ea", "constrained": "#e0a43a", "assumed": "#bdbdbd"}
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    for i, (lab, src, bk) in enumerate(groups):
        tot = sum(bk.values())
        left = 0
        for k in kinds:
            v = bk.get(k, 0) / tot * 100 if tot else 0
            ax.barh(i, v, left=left, color=kcol[k], height=0.7, label=k if i == 0 else None)
            left += v
        ax.text(101, i, f"{tot}", va="center", fontsize=6.8, color=INK)
    ax.set_yticks(range(len(groups)))
    ax.set_yticklabels([g[0] for g in groups], fontsize=7)
    ax.invert_yaxis()
    ax.set_xlim(0, 108)
    ax.set_xlabel("share of facts (%)   (number at right: facts)")
    ax.legend(ncol=5, frameon=False, fontsize=6.8, loc="lower left", bbox_to_anchor=(0, 1.0))
    fig.tight_layout()
    fig.savefig(OUT / "fig2_fact_composition.png"); fig.savefig(OUT / "fig2_fact_composition.pdf")
    plt.close(fig)


def fig5_s2_metamorphic():
    R = json.loads((RES / "s2_s4.json").read_text())["metamorphic"]
    labels = {"relocate-miami": "relocate: Miami (1A)", "relocate-seattle": "relocate: Seattle (4C)",
              "relocate-chicago": "relocate: Chicago (5A)", "relocate-fairbanks": "relocate: Fairbanks (8)",
              "retrofit-wall-xps50": "+50 mm XPS on walls", "retrofit-double-lowe": "double-pane low-e windows",
              "rotate-90": "rotated 90 deg"}
    base = R[0]["base_value"]
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    ax.barh(-1, base, color="#7a7a7a", height=0.62)
    ax.text(base + 1.5, -1, f"{base:.1f}  seed: HERS BESTEST L100A, Colorado Springs", va="center", fontsize=6.8)
    for i, m in enumerate(R):
        key = m["variant"].split("l100a-")[1]
        ax.barh(i, m["variant_value"], color=ACCENT if m["holds_on_references"] else BAD, height=0.62)
        arrow_txt = {"decrease": "expected: decrease", "increase": "expected: increase", "similar": "expected: within 10 %"}[m["relation"]["direction"]]
        ax.text(m["variant_value"] + 1.5, i, f"{m['variant_value']:.1f}  ({arrow_txt}; holds)" if m["holds_on_references"] else f"{m['variant_value']:.1f} ({arrow_txt}; FAILS)",
                va="center", fontsize=6.6)
    ax.set_yticks([-1] + list(range(len(R))))
    ax.set_yticklabels(["seed"] + [labels.get(m["variant"].split("l100a-")[1], m["variant"]) for m in R], fontsize=7)
    ax.invert_yaxis()
    ax.axvline(base, color=QUIET, lw=0.7, ls="--")
    ax.set_xlim(0, 230)
    ax.set_xlabel("annual heating energy of the reference model (GJ)")
    fig.tight_layout()
    fig.savefig(OUT / "fig5_s2_metamorphic.png"); fig.savefig(OUT / "fig5_s2_metamorphic.pdf")
    plt.close(fig)


def graphical_abstract():
    """Elsevier graphical abstract: 13 x 5 cm aspect, text legible at that size."""
    W, H = 7.8, 3.0                       # inches; printed at 13 cm wide the fonts scale by 0.66
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")

    def rbox(x, y, w, h, fc="white", ec="#555555", lw=1.0):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06", fc=fc, ec=ec, lw=lw))

    def head(x, y, s):
        ax.text(x, y, s, ha="left", va="top", fontsize=11.5, weight="bold", color=INK)

    def arr(x1, y1, x2, y2):
        ax.annotate("", (x2, y2), (x1, y1), arrowprops=dict(arrowstyle="-|>", color=QUIET, lw=1.3, mutation_scale=11))

    # column 1: four sources
    head(0.12, 2.9, "Four sources")
    srcs = [("S1", "everyday BEM work"), ("S2", "derived from seeds"), ("S3", "virtual, with probes"),
            ("S4", "repair, round trip, ...")]
    for i, (k, t) in enumerate(srcs):
        y = 2.22 - i * 0.56
        rbox(0.12, y, 2.2, 0.44)
        ax.text(0.22, y + 0.22, k, ha="left", va="center", fontsize=11, weight="bold", color=ACCENT)
        ax.text(0.62, y + 0.22, t, ha="left", va="center", fontsize=9.6, color=INK)
        arr(2.36, y + 0.22, 2.58, 1.6)

    # column 2: QA gates
    head(2.62, 2.9, "Same QA for all")
    rbox(2.62, 0.62, 1.86, 2.04, fc="#f4f4f4", ec="#888888")
    gates = ["G0  rights", "G1  schema", "G2  runs", "G3  plausibility", "G4  fits documents",
             "G5  determinacy", "G6  leakage", "G7  expert review"]
    for i, g in enumerate(gates):
        bold = g.startswith("G4")
        ax.text(2.72, 2.47 - i * 0.235, g, ha="left", va="center", fontsize=9.4, color=BAD if bold else INK,
                weight="bold" if bold else "normal")
    arr(4.52, 1.6, 4.72, 1.6)

    # column 3: the item and its grading
    head(4.76, 2.9, "End-to-end item")
    rbox(4.76, 1.14, 2.92, 1.52, fc="#e8f0fa", ec=ACCENT, lw=1.4)
    ax.text(4.88, 2.47, "documents  →  EnergyPlus IDF", ha="left", va="center", fontsize=10.2, weight="bold", color=INK)
    for i, s in enumerate(["ground truth = fact sheet, not one IDF",
                           "each fact: stated, derived, provided,", "constrained by code, or assumed",
                           "score = share of determined facts met"]):
        ax.text(4.88, 2.17 - i * 0.25, s, ha="left", va="center", fontsize=9.2, color=INK)

    # findings strip
    rbox(4.76, 0.08, 2.92, 0.9, fc="white", ec=BAD, lw=1.2)
    for i, s in enumerate(["4 of 4 supplied reference models", "contradicted their own documents",
                           "52 open items, code and QA records"]):
        ax.text(4.88, 0.8 - i * 0.26, s, ha="left", va="center", fontsize=9.4, color=BAD if i < 2 else INK,
                weight="bold" if i < 2 else "normal")
    ax.text(2.62, 0.3, "github.com/TensorBuildLab/\nBEM-benchmark-data-generation", ha="left", va="center",
            fontsize=8.2, color=QUIET)
    fig.savefig(OUT / "graphical_abstract.png", dpi=400)
    fig.savefig(OUT / "graphical_abstract.pdf")
    plt.close(fig)


FIGS = [fig1_framework, fig2_fact_composition, fig3_s1_matrix, fig4_s3_parity, fig5_s2_metamorphic, graphical_abstract]

if __name__ == "__main__":
    only = sys.argv[1:]
    for f in FIGS:
        if not only or f.__name__ in only:
            f()
    print("figures in", OUT)
