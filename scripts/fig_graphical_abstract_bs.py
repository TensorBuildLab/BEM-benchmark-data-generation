"""Graphical abstract for Building Simulation: 8 cm x 5 cm, 600 dpi, numbers read from the study summaries.

    python scripts/fig_graphical_abstract_bs.py  ->  results/figures/graphical_abstract_bs.{png,pdf}
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
INK, QUIET, ACCENT, BAD, GOOD = "#0b0b0b", "#52514e", "#2a78d6", "#c8513f", "#1baf7a"
plt.rcParams.update({"font.family": "DejaVu Sans"})


def main():
    ms = json.loads((RES / "mutation_summary.json").read_text())
    es = json.loads((RES / "ensemble_summary.json").read_text())
    spreads = [v["site_energy_gj"]["spread_p05_p95"] for v in es.values() if "site_energy_gj" in v]
    W, H = 8 / 2.54, 5 / 2.54
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 5)
    ax.axis("off")
    ax.text(0.15, 4.78, "Grading AI-built energy models by the set of\nmodels the documents allow", va="top", fontsize=6.8,
            weight="bold", color=INK, linespacing=1.1)
    # concept
    ax.add_patch(Ellipse((1.75, 2.15), 3.1, 2.3, fc="none", ec=INK, lw=0.7, ls=(0, (3, 2))))
    ax.add_patch(Ellipse((1.65, 2.15), 2.3, 1.55, fc="#e8f0fa", ec=ACCENT, lw=1.0))
    ax.text(1.65, 2.62, "admissible\nmodels A(D)", ha="center", va="center", fontsize=5.4, color=ACCENT, weight="bold", linespacing=1.0)
    ax.plot([1.2], [1.85], marker="*", ms=6, color=ACCENT, ls="none")
    ax.text(1.32, 1.85, "reference", fontsize=4.9, va="center", color=INK)
    ax.plot([2.05], [2.25], marker="o", ms=3.5, color=GOOD, ls="none")
    ax.text(2.15, 2.25, "valid", fontsize=4.9, va="center", color=GOOD)
    ax.plot([3.15], [0.85], marker="x", ms=4.5, mew=1.1, color=BAD, ls="none")
    ax.text(3.05, 0.62, "defect", fontsize=4.9, ha="right", color=BAD)
    ax.text(0.15, 0.62, "dashed: passes\nthe fact sheet", fontsize=4.6, color=QUIET, va="center", linespacing=1.0)
    # findings
    x0 = 3.75
    items = [("4 of 4", "supplied reference models contradicted\ntheir own documents"),
             (f"{ms['kappa_fact_sheet'] * 100:.0f} % vs {ms['kappa_output_5pct'] * 100:.0f} %",
              "seeded defects caught by the fact sheet\nvs by a ±5 % site-energy check"),
             (f"{np.median(spreads) * 100:.0f} points", "median band of annual site energy across\nvalid models (5th–95th percentile)")]
    for i, (big, small) in enumerate(items):
        y = 3.75 - i * 1.15
        ax.add_patch(FancyBboxPatch((x0, y - 0.82), 4.1, 0.95, boxstyle="round,pad=0.02,rounding_size=0.08", fc="white",
                                    ec="#c3c2b7", lw=0.6))
        ax.text(x0 + 0.12, y - 0.06, big, fontsize=7.6, weight="bold", color=ACCENT, va="top")
        ax.text(x0 + 0.12, y - 0.42, small, fontsize=4.9, color=INK, va="top", linespacing=1.05)
    ax.text(7.85, 0.12, "52 open items, code and QA records", fontsize=4.8, color=QUIET, ha="right")
    out = RES / "figures"
    fig.savefig(out / "graphical_abstract_bs.png", dpi=600)
    fig.savefig(out / "graphical_abstract_bs.pdf")
    plt.close(fig)
    print("graphical abstract:", items)


if __name__ == "__main__":
    main()
