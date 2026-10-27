"""Conceptual figure: admissible models, the fact sheet that approximates them, and the output band.

    python scripts/fig_concept.py   ->  results/figures/fig_concept.{png,pdf}
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyArrowPatch, Rectangle

OUT = Path(__file__).resolve().parents[1] / "results" / "figures"
INK, QUIET, ACCENT, BAD, WARN, GOOD = "#222222", "#6b6b6b", "#1f5fa8", "#c8513f", "#d08a1e", "#4d9a5b"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})


def main():
    fig = plt.figure(figsize=(7.2, 3.2))
    a = fig.add_axes([0.005, 0.02, 0.58, 0.96])
    b = fig.add_axes([0.64, 0.22, 0.345, 0.56])
    a.set_xlim(0, 10)
    a.set_ylim(0, 7)
    a.axis("off")
    a.add_patch(Rectangle((0.1, 0.1), 9.8, 6.8, fc="#fafafa", ec="#999999", lw=0.8))
    a.text(0.75, 6.65, "Runnable EnergyPlus models of the building", va="top", fontsize=7.6, color=QUIET)
    a.add_patch(Ellipse((4.9, 3.5), 6.9, 4.4, fc="none", ec=INK, lw=1.0, ls=(0, (4, 3))))
    a.text(7.95, 5.75, "$A_F$: passes\nthe fact sheet", fontsize=7.2, color=INK, ha="left", va="center")
    a.add_patch(Ellipse((4.7, 3.45), 5.0, 2.9, fc="#e8f0fa", ec=ACCENT, lw=1.4))
    a.text(4.7, 4.5, "$A(D)$: admissible models", ha="center", fontsize=8.2, weight="bold", color=ACCENT)
    a.text(4.7, 4.12, "consistent with the documents D", ha="center", fontsize=7.0, color=ACCENT)
    pts = [(3.0, 3.25, "*", ACCENT, 11, "r  reference", (0.22, 0.0), "left"),
           (3.4, 2.65, "o", ACCENT, 5.5, "rewrite of r", (0.2, 0.0), "left"),
           (6.0, 3.2, "o", GOOD, 7, "m1  valid model", (0.0, -0.42), "center"),
           (7.55, 1.95, "x", WARN, 7, "m3  defect the sheet misses", (0.0, -0.45), "center"),
           (9.3, 0.95, "x", BAD, 7, "m2  defect", (-0.22, 0.0), "right"),
           (0.7, 6.0, "x", BAD, 7, "r*  supplied reference that contradicts D", (0.22, 0.0), "left")]
    for x, y, mk, c, s, lab, (dx, dy), ha in pts:
        a.plot([x], [y], marker=mk, ms=s, color=c, mew=1.6, ls="none")
        a.text(x + dx, y + dy, lab, fontsize=7.0, color=c if c != ACCENT else INK, va="center", ha=ha)
    a.text(0.3, 0.42, "Completeness: defects fall outside $A_F$.   Soundness: all of $A(D)$ lies inside $A_F$.",
           ha="left", fontsize=6.9, color=QUIET)
    # output space
    b.set_xlim(0, 10)
    b.set_ylim(0, 3)
    b.set_yticks([])
    b.set_xticks([])
    for s in ("left", "right", "top"):
        b.spines[s].set_visible(False)
    b.set_xlabel("annual site energy  y(m)", fontsize=7.8)
    b.add_patch(Rectangle((2.0, 0.85), 5.2, 1.3, fc="#e8f0fa", ec=ACCENT, lw=1.2))
    b.text(4.6, 2.4, "band  $B(D) = y(A(D))$", ha="center", fontsize=8, color=ACCENT, weight="bold")
    for x, mk, c, lab in [(3.1, "*", ACCENT, "r"), (4.0, "x", BAD, "m2"), (6.4, "o", GOOD, "m1"), (8.8, "x", BAD, "r*")]:
        b.plot([x], [1.55], marker=mk, ms=9 if mk == "*" else 7, color=c, mew=1.6, ls="none")
        b.text(x, 1.18, lab, ha="center", va="top", fontsize=7.2, color=c if c != ACCENT else INK)
    fig.add_artist(FancyArrowPatch((0.588, 0.52), (0.635, 0.52), transform=fig.transFigure, arrowstyle="-|>",
                                   mutation_scale=10, color=QUIET, lw=1.0))
    fig.text(0.612, 0.57, "simulate", ha="center", fontsize=7, color=QUIET)
    fig.text(0.012, 0.955, "(a)", fontsize=8.5, weight="bold", color=INK)
    fig.text(0.64, 0.955, "(b)", fontsize=8.5, weight="bold", color=INK)
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "fig_concept.png", dpi=600)
    fig.savefig(OUT / "fig_concept.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
