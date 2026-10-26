"""Render the documents of a virtual building (source S3) from its :class:`Program`.

Documents are what a modeller receives: a brief (narrative prose or a spec
sheet), optional tables (CSV), a dimensioned floor-plan drawing (PNG), and
optional addenda. Probes change *how* a fact is written, never the fact:
the same program rendered with ``units`` reads in feet, Btu and degrees F.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Dict, List

from .virtual import Program, MATERIALS, ASSEMBLIES, assembly_r, expected_eflh

FT = 0.3048
W_FT2_PER_W_M2 = 1 / 10.7639
U_IP = 1 / 5.678263          # W/m2K -> Btu/h-ft2-F

HVAC_WORDS = {
    "ideal": ("Load calculation only: represent each conditioned zone with an ideal system of unlimited capacity "
              "that holds the thermostat setpoints exactly."),
    "ptac": ("Each conditioned zone has a through-the-wall packaged terminal air conditioner with an electric "
             "resistance heating coil."),
    "pthp": ("Each conditioned zone has a through-the-wall packaged terminal heat pump with electric "
             "supplemental heat."),
    "psz_hp": ("Each conditioned zone is served by its own packaged single-zone rooftop heat pump (ducted, constant "
               "volume, electric backup, no economizer)."),
    "none": "The building has no mechanical heating or cooling; it is naturally ventilated and free-running.",
}
FACADE_NAMES = {"N": "north", "E": "east", "S": "south", "W": "west"}
SHEET_NAMES = {"N": "top", "E": "right-hand", "S": "bottom", "W": "left-hand"}


def fname(p, f: str) -> str:
    """Name of a facade as drawn: compass words on a north-up plan, sheet positions otherwise."""
    return FACADE_NAMES[f] if round(p.north_axis) % 360 == 0 else SHEET_NAMES[f]


TYPE_NAMES = {"office": "office building", "retail": "retail store", "school": "school classroom building",
              "house": "single-family house", "apartment": "apartment building"}


def ft_in(m: float) -> str:
    tot = m / FT
    f = int(tot)
    i = round((tot - f) * 12)
    if i == 12:
        f, i = f + 1, 0
    return f"{f}'-{i}\""


def length(m: float, p: Program) -> str:
    return ft_in(m) if p.units == "IP" else f"{m:.2f} m"


def area(m2: float, p: Program) -> str:
    return f"{m2 / FT ** 2:,.0f} sq ft" if p.units == "IP" else f"{m2:,.1f} m2"


def temp(c: float, p: Program) -> str:
    return f"{c * 1.8 + 32:.0f} F" if p.units == "IP" else f"{c:.1f} C"


def u_value(u: float, p: Program) -> str:
    return f"U-{u * U_IP:.3f} Btu/h-ft2-F" if p.units == "IP" else f"U = {u:.2f} W/m2K"


def power_density(w: float, p: Program) -> str:
    return f"{w * W_FT2_PER_W_M2:.2f} W/sq ft" if p.units == "IP" else f"{w:.1f} W/m2"


def _hours(h):
    if not h:
        return "closed"
    def t(x):
        return "noon" if x == 12 else (f"{x % 12 or 12} {'a.m.' if x < 12 else 'p.m.'}")
    return f"{t(h[0])} to {t(h[1])}"


def layer_table(asm: str, p: Program) -> List[List[str]]:
    rows = [["Layer (outside to inside)", "Thickness", "Conductivity", "Density", "Specific heat"]]
    for m in ASSEMBLIES[asm]:
        nm, t, k, rho, cp = MATERIALS[m]
        if p.units == "IP":
            rows.append([nm.split(" ")[0] + " " + " ".join(nm.split(" ")[1:-1]), f"{t / 0.0254:.2f} in",
                         f"{k * 6.93347:.3f} Btu-in/h-ft2-F", f"{rho * 0.062428:.1f} lb/ft3", f"{cp / 4186.8:.3f} Btu/lb-F"])
        else:
            rows.append([nm, f"{t * 1000:.1f} mm", f"{k:.3f} W/m-K", f"{rho:.0f} kg/m3", f"{cp:.0f} J/kg-K"])
    return rows


def render(p: Program, out_dir: Path) -> Dict[str, str]:
    """Write the documents; return {file name: kind}."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    files: Dict[str, str] = {}
    pr = set(p.probes)
    om = set(p.omitted)
    f2f_doc = p.f2f + (0.3 if "precedence" in pr else 0.0)     # the narrative's (overridden) value
    L = []
    title = f"{p.notes.get('name', p.id)}: {TYPE_NAMES[p.btype]}"
    L.append(f"# {title}")
    L.append("")
    if p.style == "narrative":
        loc = f"The {TYPE_NAMES[p.btype]} stands in {p.city.name}, {p.city.state}"
        if "orientation" in pr:
            entrance = p.doors[0] if p.doors else "S"
            L.append(f"{loc}. Its main entrance is on the facade that faces {FACADE_NAMES[p.true_facade(entrance)]}"
                     f" (true {p.facade_azimuth(entrance):.0f} deg). The drawing is drawn with the entrance facade at "
                     "the bottom of the sheet; its north arrow gives true north.")
        else:
            L.append(f"{loc}. Plan north is true north.")
        L.append("")
        dims = f"{length(p.length, p)} by {length(p.width, p)}"
        if p.shape == "L":
            dims += (f", with a wing of {length(p.wing_length, p)} by {length(p.wing_width, p)} extending from the west "
                     "end of the north facade (see the drawing)")
        L.append(f"It has {p.n_floors} {'storey' if p.n_floors == 1 else 'storeys'} on a {dims} footprint, "
                 f"{length(f2f_doc, p)} floor to floor, with a flat roof and a slab on grade.")
        if p.zoning == "core_perimeter":
            L.append(f"Model each floor with four perimeter zones {length(p.perimeter_depth, p)} deep and one core zone.")
        else:
            L.append("Model each floor as one thermal zone.")
        if p.party_walls:
            L.append(" ".join(f"The {fname(p, f)} wall (as drawn) is a party wall shared with a heated neighbouring "
                              "building of the same use; treat it as adiabatic, with no windows." for f in p.party_walls))
        if p.garage:
            L.append(f"An unheated, uncooled single-storey garage {length(p.garage['depth'], p)} deep and "
                     f"{length(p.f2f, p)} high is attached along the full {fname(p, p.garage['side'])} wall (as drawn); "
                     "it is not part of the conditioned floor area" +
                     (", and the upper floor of that wall is an exterior wall above the garage roof." if p.n_floors > 1 else "."))
        L.append("")
    else:
        L.append("## Project data")
        L.append("")
        L.append(f"- Building type: {TYPE_NAMES[p.btype]}")
        L.append(f"- Location: {p.city.name}, {p.city.state}")
        L.append(f"- Storeys: {p.n_floors}; floor-to-floor height {length(f2f_doc, p)}; flat roof; slab on grade")
        L.append(f"- Footprint: {length(p.length, p)} x {length(p.width, p)}" +
                 (f" plus a wing {length(p.wing_length, p)} x {length(p.wing_width, p)} (see drawing)" if p.shape == "L" else ""))
        if "orientation" in pr:
            entrance = p.doors[0] if p.doors else "S"
            L.append(f"- Orientation: entrance facade faces {FACADE_NAMES[p.true_facade(entrance)]} "
                     f"(true azimuth {p.facade_azimuth(entrance):.0f} deg); see the north arrow on the drawing")
        else:
            L.append("- Orientation: plan north = true north")
        L.append("- Zoning: " + (f"core and four perimeter zones per floor, perimeter depth {length(p.perimeter_depth, p)}"
                                 if p.zoning == "core_perimeter" else "one zone per floor"))
        for f in p.party_walls:
            L.append(f"- {fname(p, f).capitalize()} wall (as drawn): party wall, adiabatic, no windows")
        if p.garage:
            L.append(f"- Attached garage on the {fname(p, p.garage['side'])} side (as drawn): single storey, "
                     f"{length(p.garage['depth'], p)} deep, {length(p.f2f, p)} high, unconditioned")
        L.append("")
    # envelope
    L.append("## Envelope")
    L.append("")
    if "layers" in pr:
        L.append("Exterior walls and the roof are built up as listed in `envelope_layers.csv` (outside to inside).")
        rows = [["Assembly"] + layer_table(p.wall, p)[0]]
        rows += [["Exterior wall"] + r for r in layer_table(p.wall, p)[1:]]
        rows += [["Roof"] + r for r in layer_table(p.roof, p)[1:]]
        with open(out_dir / "envelope_layers.csv", "w", newline="", encoding="utf-8") as fh:
            csv.writer(fh).writerows(rows)
        files["envelope_layers.csv"] = "table"
    else:
        uw = 1 / assembly_r(p.wall, "wall", False)
        ur = 1 / assembly_r(p.roof, "roof", False)
        L.append(f"- Exterior walls: {u_value(uw, p)} (layers only, without surface films)")
        L.append(f"- Roof: {u_value(ur, p)} (layers only, without surface films)")
    L.append(f"- Windows: {u_value(p.win_u, p)} (whole window), SHGC {p.win_shgc:.2f}, visible transmittance {p.win_vt:.2f}")
    if "window_dims" in pr:
        L.append("- Window sizes per facade are listed in `windows.csv`.")
        rows = [["Facade (as drawn)", "Floor", "Count", "Width", "Height", "Sill height"]]
        for fac in ("S", "E", "N", "W"):
            if p.wwr.get(fac, 0) <= 0 or fac in p.party_walls:
                continue
            fp = p.footprint()
            from .virtual import _edge_facade
            seg = sum(math.hypot(fp[(i + 1) % len(fp)][0] - fp[i][0], fp[(i + 1) % len(fp)][1] - fp[i][1])
                      for i in range(len(fp)) if _edge_facade(fp[i], fp[(i + 1) % len(fp)]) == fac)
            a = p.wwr[fac] * seg * p.f2f
            h = 1.5 if p.f2f >= 3.0 else 1.2
            n = max(1, round(a / (h * 1.8)))
            w = a / (n * h)
            for k in range(p.n_floors):
                if p.garage and fac == p.garage["side"] and k == 0:
                    continue                   # that wall adjoins the garage on the ground floor
                rows.append([fname(p, fac), str(k + 1), str(n), length(w, p), length(h, p), length(p.sill, p)])
        with open(out_dir / "windows.csv", "w", newline="", encoding="utf-8") as fh:
            csv.writer(fh).writerows(rows)
        files["windows.csv"] = "table"
    else:
        parts = []
        for f in ("S", "E", "N", "W"):
            if f in p.party_walls:
                continue
            if p.garage and f == p.garage["side"]:
                if p.n_floors > 1:
                    parts.append(f"{fname(p, f)} {p.wwr.get(f, 0) * 100:.0f} % (upper floor only, above the garage)")
                continue
            parts.append(f"{fname(p, f)} {p.wwr.get(f, 0) * 100:.0f} %")
        L.append("- Window-to-wall ratio by facade (as drawn): " + ", ".join(parts) + f"; sill height {length(p.sill, p)}")
    if p.doors:
        L.append("- Doors: one " + ", one ".join(f"{fname(p, d)}" for d in p.doors) + " facade door (as drawn), "
                 + f"{length(0.91, p)} x {length(2.13, p)}, insulated panel")
    L.append("")
    # internal loads and schedules
    L.append("## Internal loads and schedules")
    L.append("")
    if "loads" not in om:
        if "code_lookup" in pr:
            L.append("- Lighting: installed at the ASHRAE Standard 90.1-2019 building area method allowance for an office.")
        else:
            L.append(f"- Lighting: {power_density(p.lpd, p)}")
        L.append(f"- Plug and process loads: {power_density(p.epd, p)}")
        if p.btype in ("house", "apartment"):
            L.append(f"- Occupants: {p.total_people():g} people")
        else:
            dens = p.occ_density
            if p.units == "IP":
                L.append(f"- Occupant density: {dens / 100 * 1000 * FT ** 2:.2f} people per 1,000 sq ft")
            else:
                L.append(f"- Occupant density: {dens:.1f} people per 100 m2 of floor area")
    if "schedules" not in om:
        if p.btype in ("house", "apartment"):
            L.append("- Schedules: typical residential profiles (see `schedules.csv`, hourly fractions).")
            from .virtual import schedule_profile
            prof = schedule_profile(p)
            rows = [["Hour ending", "Occupancy weekday", "Occupancy weekend", "Lighting weekday", "Lighting weekend",
                     "Equipment weekday", "Equipment weekend"]]
            for h in range(24):
                rows.append([str(h + 1)] + [f"{prof[d][w][h]:g}" for w in (0, 1, 2) for d in ("weekday", "saturday")])
            with open(out_dir / "schedules.csv", "w", newline="", encoding="utf-8") as fh:
                csv.writer(fh).writerows(rows)
            files["schedules.csv"] = "table"
        else:
            hh = p.hours
            L.append(f"- Hours of operation: weekdays {_hours(hh.get('weekday'))}, Saturdays {_hours(hh.get('saturday'))}, "
                     f"Sundays {_hours(hh.get('sunday'))}; no holidays.")
            L.append("- During operating hours occupancy is 95 %, lighting 90 % and plug loads 90 % of design; outside "
                     "them occupancy is zero, lighting 5 % and plug loads 30 %.")
    L.append("")
    L.append("## Air leakage")
    L.append("")
    if "infiltration" not in om:
        L.append(f"- Infiltration: {p.infiltration_ach:.2f} air changes per hour, constant"
                 + ("; the garage leaks 1.0 air change per hour." if p.garage else "."))
    else:
        L.append("- Not measured.")
    L.append("")
    L.append("## Systems and controls")
    L.append("")
    if "hvac" not in om:
        L.append("- " + HVAC_WORDS[p.hvac])
        if p.hvac in ("ptac", "pthp", "psz_hp"):
            if p.units == "IP":
                L.append(f"- Cooling efficiency: EER {p.cop_cool * 3.412:.1f} (gross, rated)")
            else:
                L.append(f"- Cooling efficiency: COP {p.cop_cool:.2f} (gross, rated)")
            if p.hvac in ("pthp", "psz_hp"):
                L.append(f"- Heat pump heating COP {p.cop_heat:.2f} (gross, rated)")
    if "setpoints" not in om and p.hvac != "none":
        s = f"- Thermostat: heating {temp(p.heat_sp, p)}, cooling {temp(p.cool_sp, p)}"
        if p.heat_setback is not None:
            s += (f"; outside operating hours setback to {temp(p.heat_setback, p)} heating and setup to "
                  f"{temp(p.cool_setup, p)} cooling, with recovery starting two hours before opening")
        L.append(s + ".")
    L.append("")
    if "distractor" in pr:
        L.append("## Site notes")
        L.append("")
        L.append("- The neighbouring building across the street has a 60 % glazed curtain wall.")
        L.append("- The parking lot has 42 spaces and LED pole lights (outside the scope of this model).")
        L.append("- The owner's 25 kW server room is in a separate building and is not part of this model.")
        L.append("")
    if "precedence" in pr:
        L.append("Where this brief and the drawing differ, the drawing governs.")
        L.append("")
    (out_dir / "brief.md").write_text("\n".join(L), encoding="utf-8")
    files["brief.md"] = "text"
    draw_plan(p, out_dir / "floorplan.png")
    files["floorplan.png"] = "drawing"
    return files


def draw_plan(p: Program, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 6), dpi=130)
    fp = p.footprint()
    xs = [a for a, _ in fp] + [fp[0][0]]
    ys = [b for _, b in fp] + [fp[0][1]]
    ax.fill(xs, ys, color="#f2f2f2", zorder=1)
    ax.plot(xs, ys, color="black", lw=2.2, zorder=3)
    if p.zoning == "core_perimeter" and p.shape == "rect":
        d, Lx, Wy = p.perimeter_depth, p.length, p.width
        for (x1, y1, x2, y2) in [(0, 0, d, d), (Lx, 0, Lx - d, d), (Lx, Wy, Lx - d, Wy - d), (0, Wy, d, Wy - d)]:
            ax.plot([x1, x2], [y1, y2], color="0.5", lw=0.8, ls="--", zorder=2)
        ax.plot([d, Lx - d, Lx - d, d, d], [d, d, Wy - d, Wy - d, d], color="0.5", lw=0.8, ls="--", zorder=2)
        ax.text(Lx / 2, Wy / 2, "CORE", ha="center", va="center", fontsize=8, color="0.3")
    if p.garage:
        g = p.garage
        gx0 = -g["depth"] if g["side"] == "W" else p.length
        ax.add_patch(plt.Rectangle((gx0, 0), g["depth"], p.width, fill=False, hatch="//", ec="0.4", lw=1.2))
        ax.text(gx0 + g["depth"] / 2, p.width / 2, "GARAGE\n(unconditioned,\nsingle storey)" +
                ("\nupper-floor windows\nabove it" if p.n_floors > 1 and p.wwr.get(g["side"], 0) > 0 else ""),
                ha="center", va="center", fontsize=7)
    # windows (as thick blue ticks) and doors
    for i in range(len(fp)):
        a, b = fp[i], fp[(i + 1) % len(fp)]
        from .virtual import _edge_facade
        fac = _edge_facade(a, b)
        if fac in p.party_walls:
            ax.plot([a[0], b[0]], [a[1], b[1]], color="#b04020", lw=5, alpha=0.5, zorder=4)
            ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, "PARTY WALL", fontsize=7, color="#b04020",
                    rotation=90 if a[0] == b[0] else 0, ha="center", va="center")
            continue
        if p.garage and fac == p.garage["side"]:
            continue
        frac = p.wwr.get(fac, 0)
        if frac > 0:
            m = 0.5 * (1 - min(0.95, frac / 0.6))
            ax.plot([a[0] + (b[0] - a[0]) * m, b[0] - (b[0] - a[0]) * m], [a[1] + (b[1] - a[1]) * m, b[1] - (b[1] - a[1]) * m],
                    color="#2060c0", lw=4, zorder=4)
    for dfac in p.doors:
        for i in range(len(fp)):
            a, b = fp[i], fp[(i + 1) % len(fp)]
            if _edge_facade(a, b) == dfac:
                seg = math.hypot(b[0] - a[0], b[1] - a[1])
                ux, uy = (b[0] - a[0]) / seg, (b[1] - a[1]) / seg
                ax.plot([a[0] + ux * 0.5, a[0] + ux * 1.41], [a[1] + uy * 0.5, a[1] + uy * 1.41], color="#d08000", lw=6, zorder=5)
                ax.text(a[0] + ux * 1.0 - uy * 1.2, a[1] + uy * 1.0 + ux * 1.2, "ENTRY", fontsize=7, color="#d08000", ha="center")
                break
    # dimensions
    off = -0.12 * max(p.length, p.width)
    ax.annotate("", (0, off), (p.length, off), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(p.length / 2, off * 1.25, length(p.length, p), ha="center", va="top", fontsize=9)
    ax.annotate("", (p.length - off, 0), (p.length - off, p.width), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(p.length - off * 1.15, p.width / 2, length(p.width, p), rotation=90, va="center", fontsize=9)
    if p.shape == "L":
        ax.text(p.wing_length / 2, p.width + p.wing_width / 2, f"WING\n{length(p.wing_length, p)} x {length(p.wing_width, p)}",
                ha="center", va="center", fontsize=8)
    # north arrow: true north is rotated counterclockwise by the north axis on the plan
    th = math.radians(p.north_axis)
    cx = p.length + 0.25 * max(p.length, p.width)
    cy = max(p.width + (p.wing_width if p.shape == "L" else 0), 6) * 0.85
    r = 0.07 * max(p.length, p.width) + 1
    ax.annotate("", (cx - r * math.sin(th), cy + r * math.cos(th)), (cx, cy), arrowprops=dict(arrowstyle="-|>", lw=1.5))
    ax.text(cx - 1.35 * r * math.sin(th), cy + 1.35 * r * math.cos(th), "N", ha="center", va="center", fontsize=11, weight="bold")
    f2f_draw = p.f2f
    ax.set_title(f"{p.notes.get('name', p.id)} - typical floor plan ({p.n_floors} storey{'s' if p.n_floors > 1 else ''}, "
                 f"floor to floor {length(f2f_draw, p)})", fontsize=9)
    ax.text(0.0, -0.06, "Window and door marks are schematic and not to scale; sizes and ratios are given in the brief.",
            transform=ax.transAxes, fontsize=7, color="0.3", ha="left", va="top")
    ax.set_aspect("equal")
    ax.axis("off")
    xmin = min(xs + ([-p.garage["depth"]] if p.garage and p.garage["side"] == "W" else [])) - 3
    xmax = max(xs + ([p.length + p.garage["depth"]] if p.garage and p.garage["side"] == "E" else [])) + 0.4 * max(p.length, p.width)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(off * 1.8, max(ys) + 4)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
