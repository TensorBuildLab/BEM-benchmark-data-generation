"""Model mutations for testing a benchmark item's checks, and admissible variants for ensembles.

Three families, each applied to a copy of a validated reference model:

``defect``      a change that makes the model contradict its documents (a construction on the wrong
                surface, a missing facade of windows, a W/ft2 value read as W/m2 ...). A complete
                fact sheet should reject it.
``admissible``  a change to an input the documents leave open (outdoor air, fan pressure, slab
                insulation, exterior colour, furniture mass, sizing factors ...). The changed model
                is still a correct answer, so a sound fact sheet must accept it, although its
                annual results may move.
``equivalent``  a rewrite that keeps the building and its physics (renamed zones, split windows,
                occupants as a count instead of a density, expanded HVAC templates). A sound fact
                sheet must accept it, and its results should not move.

Every operator takes an IDF (modified in place) and a context dictionary, and returns a short
description, or ``None`` when it does not apply to that model.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from .idf import IDF, IDFObject
from .ops import VERTEX_START, _f, _verts, facade_of, wall_azimuth, rotate
from .schema import get_schema

_S = None


def S():
    global _S
    if _S is None:
        _S = get_schema("23.1")
    return _S


def fidx(o: IDFObject, name: str) -> Optional[int]:
    fields = S()._layout(o.cls)[1]
    return fields.index(name) if name in fields else None


def fget(o: IDFObject, name: str, default: str = "") -> str:
    i = fidx(o, name)
    return o.get(i, default) if i is not None else default


def fset(o: IDFObject, name: str, value) -> bool:
    i = fidx(o, name)
    if i is None:
        return False
    while len(o.fields) <= i:
        o.fields.append("")
    o.fields[i] = str(value)
    return True


def _num(x, d=None):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


def surfaces(idf, kind=None, boundary=None):
    out = []
    for o in idf.by_class("BuildingSurface:Detailed"):
        if kind and fget(o, "surface_type").upper() != kind:
            continue
        if boundary and fget(o, "outside_boundary_condition").upper() not in boundary:
            continue
        out.append(o)
    return out


def windows(idf):
    return [o for o in idf.by_class("FenestrationSurface:Detailed") if fget(o, "surface_type").upper() in ("WINDOW", "GLASSDOOR")]


def doors(idf):
    return [o for o in idf.by_class("FenestrationSurface:Detailed") if fget(o, "surface_type").upper() == "DOOR"]


def poly_area(pts):
    if len(pts) < 3:
        return 0.0
    nx = ny = nz = 0.0
    for i in range(len(pts)):
        x1, y1, z1 = pts[i]
        x2, y2, z2 = pts[(i + 1) % len(pts)]
        nx += y1 * z2 - z1 * y2
        ny += z1 * x2 - x1 * z2
        nz += x1 * y2 - y1 * x2
    return 0.5 * math.sqrt(nx * nx + ny * ny + nz * nz)


def zone_floor_areas(idf) -> Dict[str, float]:
    a: Dict[str, float] = {}
    for o in surfaces(idf, "FLOOR"):
        z = fget(o, "zone_name").upper()
        a[z] = a.get(z, 0.0) + poly_area(_verts(o))
    return a


def schedule_shift(idf, name: str, delta: float) -> bool:
    o = idf.get("Schedule:Compact", name)
    if not o:
        return False
    for i in range(2, len(o.fields)):
        v = o.fields[i].strip()
        if re.match(r"^(through|for|until|interpolate)", v, re.I):
            continue
        n = _num(v)
        if n is not None:
            o.fields[i] = f"{n + delta:g}"
    return True


def setpoint_schedules(idf, which: str) -> List[str]:
    names = []
    for o in idf.by_class("HVACTemplate:Thermostat"):
        n = fget(o, f"{which}_setpoint_schedule_name")
        if n:
            names.append(n)
    for o in idf.by_class("ThermostatSetpoint:DualSetpoint"):
        n = fget(o, f"{which}_setpoint_temperature_schedule_name")
        if n:
            names.append(n)
    cls = "ThermostatSetpoint:SingleHeating" if which == "heating" else "ThermostatSetpoint:SingleCooling"
    for o in idf.by_class(cls):
        n = fget(o, "setpoint_temperature_schedule_name")
        if n:
            names.append(n)
    return sorted(set(names))


def _hvac_templates(idf):
    return idf.by_class("HVACTemplate:Zone:*")


def _rename(idf, old: str, new: str):
    ou = old.upper()
    for o in idf:
        o.fields = [new if str(v).strip().upper() == ou else v for v in o.fields]


def _scale_vertices(idf, sx=1.0, sy=1.0, sz=1.0):
    for o in idf:
        start = VERTEX_START.get(o.key)
        if start is None:
            if o.key == "ZONE":
                for i, s in ((2, sx), (3, sy), (4, sz)):
                    v = _num(o.get(i))
                    if v is not None:
                        o.fields[i] = f"{v * s:.4f}"
            continue
        f = o.fields
        for i in range(start, len(f) - 2, 3):
            x, y, z = _num(f[i]), _num(f[i + 1]), _num(f[i + 2])
            if None in (x, y, z):
                break
            f[i], f[i + 1], f[i + 2] = f"{x * sx:.4f}", f"{y * sy:.4f}", f"{z * sz:.4f}"


# ================================================================== defect mutants
def d_wall_on_roof(idf, ctx):
    walls = surfaces(idf, "WALL", ("OUTDOORS",))
    roofs = surfaces(idf, "ROOF", ("OUTDOORS",))
    if not walls or not roofs:
        return None
    wc = fget(walls[0], "construction_name")
    for r in roofs:
        fset(r, "construction_name", wc)
    return f"exterior wall construction on {len(roofs)} roof surfaces"


def d_drop_facade_windows(idf, ctx):
    ws = windows(idf)
    if not ws:
        return None
    by: Dict[str, list] = {}
    for w in ws:
        base = idf.get("BuildingSurface:Detailed", fget(w, "building_surface_name"))
        if base is None:
            continue
        by.setdefault(facade_of(wall_azimuth(idf, base)), []).append(w)
    if not by:
        return None
    fac, ws2 = max(by.items(), key=lambda kv: sum(poly_area(_verts(w)) for w in kv[1]))
    for w in ws2:
        idf.remove(w)
    return f"removed the {len(ws2)} windows of the {fac} facade"


def d_single_glazing(idf, ctx):
    g = idf.by_class("WindowMaterial:SimpleGlazingSystem")
    if not g:
        return None
    for o in g:
        fset(o, "u_factor", 5.8)
        fset(o, "solar_heat_gain_coefficient", 0.82)
        fset(o, "visible_transmittance", 0.88)
    return "glazing replaced by single clear glass (U 5.8, SHGC 0.82)"


def d_lpd_unit_error(idf, ctx):
    n = 0
    for o in idf.by_class("Lights"):
        for f in ("watts_per_zone_floor_area", "lighting_level", "watts_per_person"):
            v = _num(fget(o, f))
            if v:
                fset(o, f, round(v / 10.764, 4))
                n += 1
    return f"lighting power divided by 10.764 (W/ft2 value entered as W/m2) in {n} objects" if n else None


def d_people_x3(idf, ctx):
    n = 0
    for o in idf.by_class("People"):
        for f in ("number_of_people", "people_per_floor_area"):
            v = _num(fget(o, f))
            if v:
                fset(o, f, round(v * 3, 6))
                n += 1
        v = _num(fget(o, "floor_area_per_person"))
        if v:
            fset(o, "floor_area_per_person", round(v / 3, 6))
            n += 1
    return f"occupants tripled ({n} objects)" if n else None


def d_epd_x2(idf, ctx):
    n = 0
    for o in idf.by_class("ElectricEquipment"):
        for f in ("design_level", "watts_per_zone_floor_area", "watts_per_person"):
            v = _num(fget(o, f))
            if v:
                fset(o, f, round(v * 2, 4))
                n += 1
    return f"plug loads doubled ({n} objects)" if n else None


def d_heating_sp_up3(idf, ctx):
    names = setpoint_schedules(idf, "heating")
    ok = [schedule_shift(idf, n, 3.0) for n in names]
    return f"heating setpoints raised by 3 K ({sum(ok)} schedules)" if any(ok) else None


def d_cooling_sp_down3(idf, ctx):
    names = setpoint_schedules(idf, "cooling")
    ok = [schedule_shift(idf, n, -3.0) for n in names]
    return f"cooling setpoints lowered by 3 K ({sum(ok)} schedules)" if any(ok) else None


def d_rotate_180(idf, ctx):
    return rotate(idf, 180).description


def d_infiltration_x5(idf, ctx):
    n = 0
    for o in idf.by_class("ZoneInfiltration:DesignFlowRate"):
        for f in ("design_flow_rate", "flow_rate_per_floor_area", "flow_rate_per_exterior_surface_area", "air_changes_per_hour"):
            v = _num(fget(o, f))
            if v:
                fset(o, f, round(v * 5, 8))
                n += 1
    return f"infiltration multiplied by 5 ({n} objects)" if n else None


def d_footprint_x115(idf, ctx):
    _scale_vertices(idf, 1.15, 1.15, 1.0)
    return "plan dimensions scaled by 1.15 (floor area +32 %)"


def d_height_x12(idf, ctx):
    _scale_vertices(idf, 1.0, 1.0, 1.2)
    return "all heights scaled by 1.2"


def d_lights_always_on(idf, ctx):
    ls = idf.by_class("Lights")
    if not ls:
        return None
    name = "Mutant Always On"
    if not idf.get("Schedule:Compact", name):
        idf.add("Schedule:Compact", [name, "", "Through: 12/31", "For: AllDays", "Until: 24:00", 1])
    for o in ls:
        fset(o, "schedule_name", name)
    return "lights on 8,760 h a year"


def d_cop_low(idf, ctx):
    n = 0
    for o in idf.by_class("HVACTemplate:*", "Coil:Cooling:DX:SingleSpeed", "Coil:Heating:DX:SingleSpeed"):
        for f in ("cooling_coil_gross_rated_cop", "cooling_coil_gross_rated_cooling_cop", "heat_pump_heating_coil_rated_cop",
                  "heat_pump_heating_coil_gross_rated_cop", "gross_rated_cooling_cop", "gross_rated_heating_cop"):
            if _num(fget(o, f)):
                fset(o, f, 2.0)
                n += 1
    return f"rated COPs set to 2.0 ({n} fields)" if n else None


def d_hvac_to_ideal(idf, ctx):
    zt = _hvac_templates(idf)
    if not zt or all(o.key == "HVACTEMPLATE:ZONE:IDEALLOADSAIRSYSTEM" for o in zt):
        return None
    for o in zt:
        zone, therm = fget(o, "zone_name"), fget(o, "template_thermostat_name")
        idf.remove(o)
        new = idf.add("HVACTemplate:Zone:IdealLoadsAirSystem", [zone])
        fset(new, "template_thermostat_name", therm)
    for o in idf.by_class("HVACTemplate:System:*"):
        idf.remove(o)
    return f"HVAC replaced by ideal loads in {len(zt)} zones"


def d_party_wall_exposed(idf, ctx):
    adi = surfaces(idf, "WALL", ("ADIABATIC",))
    if not adi:
        return None
    for o in adi:
        fset(o, "outside_boundary_condition", "Outdoors")
        fset(o, "sun_exposure", "SunExposed")
        fset(o, "wind_exposure", "WindExposed")
    return f"{len(adi)} adiabatic party walls made exterior walls"


def d_site_moved(idf, ctx):
    o = idf.first("Site:Location")
    if not o:
        return None
    lat = _num(fget(o, "latitude"), 0.0)
    fset(o, "latitude", round(lat + 5.0, 3))
    return "site latitude moved by 5 degrees"


def d_remove_doors(idf, ctx):
    ds = doors(idf)
    if not ds:
        return None
    for o in ds:
        idf.remove(o)
    return f"removed {len(ds)} doors"


DEFECTS: Dict[str, tuple] = {
    "wall_on_roof": (d_wall_on_roof, "envelope"), "drop_facade_windows": (d_drop_facade_windows, "fenestration"),
    "single_glazing": (d_single_glazing, "fenestration"), "remove_doors": (d_remove_doors, "fenestration"),
    "lpd_unit_error": (d_lpd_unit_error, "loads"), "people_x3": (d_people_x3, "loads"), "epd_x2": (d_epd_x2, "loads"),
    "heating_sp_up3": (d_heating_sp_up3, "control"), "cooling_sp_down3": (d_cooling_sp_down3, "control"),
    "rotate_180": (d_rotate_180, "fenestration"), "infiltration_x5": (d_infiltration_x5, "infiltration"),
    "footprint_x115": (d_footprint_x115, "geometry"), "height_x12": (d_height_x12, "geometry"),
    "lights_always_on": (d_lights_always_on, "schedules"), "cop_low": (d_cop_low, "hvac"),
    "hvac_to_ideal": (d_hvac_to_ideal, "hvac"), "party_wall_exposed": (d_party_wall_exposed, "envelope"),
    "site_moved": (d_site_moved, "site"),
}


# ================================================================== admissible variants
def _exterior_constructions(idf):
    names = set()
    for o in surfaces(idf, None, ("OUTDOORS",)):
        names.add(fget(o, "construction_name").upper())
    return [c for c in idf.by_class("Construction") if c.name.upper() in names]


def a_outdoor_air(idf, ctx, per_person=0.0075):
    n = 0
    for o in _hvac_templates(idf):
        if fidx(o, "outdoor_air_method") is None:
            continue
        # a zero rate rather than "None": not every template accepts "None"
        fset(o, "outdoor_air_method", "Flow/Person")
        fset(o, "outdoor_air_flow_rate_per_person", round(max(per_person, 0.0), 6))
        fset(o, "outdoor_air_flow_rate_per_zone_floor_area", "")
        n += 1
    for o in idf.by_class("DesignSpecification:OutdoorAir"):
        fset(o, "outdoor_air_flow_per_person", round(max(per_person, 0.0), 6))
        n += 1
    return f"outdoor air {per_person * 1000:.2f} L/s per person ({n} objects)" if n else None


def a_fan(idf, ctx, factor=2.0, eff=None):
    n = 0
    for o in idf.by_class("HVACTemplate:*", "Fan:*"):
        for f in ("supply_fan_delta_pressure", "pressure_rise"):
            v = _num(fget(o, f))
            if v:
                fset(o, f, round(v * factor, 2))
                n += 1
        if eff:
            for f in ("supply_fan_total_efficiency", "fan_total_efficiency"):
                if _num(fget(o, f)):
                    fset(o, f, round(eff, 3))
    return f"fan pressure x{factor:.2f}" + (f", efficiency {eff:.2f}" if eff else "") + f" ({n} fans)" if n else None


def a_slab_insulation(idf, ctx, thickness=0.05):
    if thickness <= 0:
        return None
    gs = surfaces(idf, "FLOOR", ("GROUND", "GROUNDFCFACTORMETHOD", "GROUNDSLABPREPROCESSORAVERAGE"))
    if not gs:
        return None
    mat = f"Slab XPS {int(round(thickness * 1000))}mm"
    if not idf.get("Material", mat):
        idf.add("Material", [mat, "MediumRough", round(thickness, 4), 0.029, 35, 1400, 0.9, 0.6, 0.6])
    done = set()
    for s in gs:
        cn = fget(s, "construction_name")
        if cn.upper() in done:
            continue
        c = idf.get("Construction", cn)
        if c is None:
            continue
        new = f"{cn} insulated"
        if not idf.get("Construction", new):
            idf.add("Construction", [new, mat] + c.fields[1:])
        done.add(cn.upper())
        for s2 in gs:
            if fget(s2, "construction_name").upper() == cn.upper():
                fset(s2, "construction_name", new)
    return f"{thickness * 1000:.0f} mm insulation under the slab"


def _edges(pts):
    return [(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]


def _overlap(e1, e2, tol=0.02):
    """Length shared by two horizontal segments on one line (0 when they are not collinear)."""
    (a, b), (c, d) = e1, e2
    ux, uy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(ux, uy)
    if n < tol:
        return 0.0
    ux, uy = ux / n, uy / n
    if any(abs((p[0] - a[0]) * uy - (p[1] - a[1]) * ux) > tol for p in (c, d)):
        return 0.0
    t = sorted(((c[0] - a[0]) * ux + (c[1] - a[1]) * uy, (d[0] - a[0]) * ux + (d[1] - a[1]) * uy))
    return max(0.0, min(n, t[1]) - max(0.0, t[0]))


def a_slab_ffactor(idf, ctx, f_factor=1.2634):
    """Ground floors by the F-factor method instead of a layered slab on BuildingSurface ground temperatures.

    F = 1.2634 W/(m·K) is the uninsulated slab of ASHRAE 90.1 Appendix A (0.73 Btu/(h·ft·°F)). Each floor gets a
    Construction:FfactorGroundFloor with its area and the length of its edges under exterior walls of its zone;
    EnergyPlus then takes the method's ground temperatures from the weather file.
    """
    floors = surfaces(idf, "FLOOR", ("GROUND",))
    if not floors:
        return None
    bottoms: Dict[str, list] = {}
    for w in surfaces(idf, "WALL", ("OUTDOORS",)):
        v = _verts(w)
        zmin = min(p[2] for p in v)
        bottoms.setdefault(fget(w, "zone_name").upper(), []).extend(
            e for e in _edges(v) if abs(e[0][2] - zmin) < 0.02 and abs(e[1][2] - zmin) < 0.02)
    total = 0.0
    for s in floors:
        v = _verts(s)
        z = v[0][2]
        walls = [b for b in bottoms.get(fget(s, "zone_name").upper(), []) if abs(b[0][2] - z) < 0.05]
        perim = sum(_overlap(e, b) for e in _edges(v) for b in walls)
        name = f"FFactor {s.name}"[:100]
        idf.add("Construction:FfactorGroundFloor", [name, f_factor, round(poly_area(v), 4), round(perim, 4)])
        fset(s, "construction_name", name)
        fset(s, "outside_boundary_condition", "GroundFCfactorMethod")
        total += perim
    return f"{len(floors)} ground floors by the F-factor method (F {f_factor} W/(m·K), exposed perimeter {total:.1f} m)"


# Modelling idioms that the pilot agent used and the references do not; applied by scripts/idioms.py
IDIOMS: Dict[str, tuple] = {"slab_ffactor": (a_slab_ffactor, "envelope")}


def a_exterior_absorptance(idf, ctx, alpha=0.9):
    mats = set()
    for c in _exterior_constructions(idf):
        if len(c.fields) > 1:
            mats.add(c.fields[1].upper())
    n = 0
    for m in idf.by_class("Material"):
        if m.name.upper() in mats:
            fset(m, "solar_absorptance", alpha)
            n += 1
    return f"exterior solar absorptance {alpha:.2f} ({n} materials)" if n else None


def a_internal_mass(idf, ctx, ratio=1.0):
    if ratio <= 0:
        return None
    if not idf.get("Material", "Furniture wood 25mm"):
        idf.add("Material", ["Furniture wood 25mm", "MediumSmooth", 0.025, 0.15, 600, 1630, 0.9, 0.6, 0.6])
        idf.add("Construction", ["Furniture", "Furniture wood 25mm"])
    areas = zone_floor_areas(idf)
    cond = ctx.get("conditioned_zones")
    n = 0
    for z in idf.by_class("Zone"):
        if cond is not None and z.name.upper() not in cond:
            continue
        a = areas.get(z.name.upper(), 0.0)
        if a > 0:
            o = idf.add("InternalMass", [f"{z.name} furniture", "Furniture", z.name])
            fset(o, "surface_area", round(a * ratio, 2))
            n += 1
    return f"furniture mass {ratio:.2f} m2 per m2 of floor in {n} zones" if n else None


def a_sizing(idf, ctx, heat=1.0, cool=1.0):
    o = idf.first("Sizing:Parameters")
    if not o:
        return None
    fset(o, "heating_sizing_factor", round(heat, 3))
    fset(o, "cooling_sizing_factor", round(cool, 3))
    return f"sizing factors {heat:.2f} heating, {cool:.2f} cooling"


def a_ground_temperature(idf, ctx, delta=3.0):
    o = idf.first("Site:GroundTemperature:BuildingSurface")
    if not o:
        return None
    o.fields = [f"{(_num(v, 0.0) + delta):.2f}" if _num(v) is not None else v for v in o.fields]
    return f"ground temperatures {delta:+.1f} K"


def a_door_insulated(idf, ctx):
    ds = doors(idf)
    if not ds:
        return None
    if not idf.get("Material", "Insulated door panel"):
        idf.add("Material", ["Insulated door panel", "MediumSmooth", 0.045, 0.03, 50, 1400, 0.9, 0.6, 0.6])
        idf.add("Construction", ["Insulated Door", "Insulated door panel"])
    for o in ds:
        fset(o, "construction_name", "Insulated Door")
    return f"{len(ds)} doors insulated"


ADMISSIBLE: Dict[str, tuple] = {
    "oa_7.5Lps": (lambda m, c: a_outdoor_air(m, c, 0.0075), "hvac"),
    "oa_none": (lambda m, c: a_outdoor_air(m, c, 0.0), "hvac"),
    "fan_pressure_x2": (lambda m, c: a_fan(m, c, 2.0), "hvac"),
    "slab_xps_50mm": (lambda m, c: a_slab_insulation(m, c, 0.05), "envelope"),
    "absorptance_0.9": (lambda m, c: a_exterior_absorptance(m, c, 0.9), "envelope"),
    "absorptance_0.3": (lambda m, c: a_exterior_absorptance(m, c, 0.3), "envelope"),
    "furniture_mass": (lambda m, c: a_internal_mass(m, c, 1.0), "loads"),
    "sizing_1.0": (lambda m, c: a_sizing(m, c, 1.0, 1.0), "hvac"),
    "ground_+3K": (lambda m, c: a_ground_temperature(m, c, 3.0), "site"),
    "door_insulated": (a_door_insulated, "fenestration"),
}


# ================================================================== equivalent rewrites
def e_rename_zones(idf, ctx):
    zs = idf.by_class("Zone")
    if not zs:
        return None
    for z in list(zs):
        _rename(idf, z.name, f"Room {z.name}")
    return f"{len(zs)} zones renamed"


def e_split_windows(idf, ctx):
    ws = [w for w in windows(idf) if len(_verts(w)) == 4]
    if not ws:
        return None
    start = VERTEX_START["FENESTRATIONSURFACE:DETAILED"]
    for w in ws:
        p = _verts(w)
        m14 = tuple((a + b) / 2 for a, b in zip(p[0], p[3]))
        m23 = tuple((a + b) / 2 for a, b in zip(p[1], p[2]))
        head = w.fields[:start]
        a = list(head)
        a[0] = f"{w.name} a"
        b = list(head)
        b[0] = f"{w.name} b"
        a += [f"{c:.4f}" for c in p[0] + p[1] + m23 + m14]
        b += [f"{c:.4f}" for c in m14 + m23 + p[2] + p[3]]
        idf.remove(w)
        idf.add("FenestrationSurface:Detailed", a)
        idf.add("FenestrationSurface:Detailed", b)
    return f"{len(ws)} windows each split into two halves"


def e_people_as_density(idf, ctx):
    """Occupants written the other way round: a count becomes a density, a density a count."""
    areas = zone_floor_areas(idf)
    n = 0
    for o in idf.by_class("People"):
        a = areas.get(fget(o, "zone_or_zonelist_or_space_or_spacelist_name").upper())
        if not a:
            continue
        meth = fget(o, "number_of_people_calculation_method").upper()
        if meth == "PEOPLE" and _num(fget(o, "number_of_people")) is not None:
            fset(o, "number_of_people_calculation_method", "People/Area")
            fset(o, "people_per_floor_area", round(_num(fget(o, "number_of_people")) / a, 8))
            fset(o, "number_of_people", "")
            n += 1
        elif meth == "PEOPLE/AREA" and _num(fget(o, "people_per_floor_area")) is not None:
            fset(o, "number_of_people_calculation_method", "People")
            fset(o, "number_of_people", round(_num(fget(o, "people_per_floor_area")) * a, 6))
            fset(o, "people_per_floor_area", "")
            n += 1
    return f"occupancy rewritten (count <-> density) in {n} zones" if n else None


def e_lights_as_level(idf, ctx):
    areas = zone_floor_areas(idf)
    n = 0
    for o in idf.by_class("Lights"):
        if fget(o, "design_level_calculation_method").upper() != "WATTS/AREA":
            continue
        a = areas.get(fget(o, "zone_or_zonelist_or_space_or_spacelist_name").upper())
        d = _num(fget(o, "watts_per_zone_floor_area"))
        if not a or d is None:
            continue
        fset(o, "design_level_calculation_method", "LightingLevel")
        fset(o, "lighting_level", round(d * a, 4))
        fset(o, "watts_per_zone_floor_area", "")
        n += 1
    return f"lighting written as a total power in {n} zones" if n else None


def e_reverse_order(idf, ctx):
    idf.objects = [o for o in idf.objects if o.key == "VERSION"] + [o for o in reversed(idf.objects) if o.key != "VERSION"]
    return "objects written in reverse order"


EQUIVALENT: Dict[str, tuple] = {
    "rename_zones": (e_rename_zones, "geometry"), "split_windows": (e_split_windows, "fenestration"),
    "people_as_density": (e_people_as_density, "loads"), "lights_as_level": (e_lights_as_level, "loads"),
    "reverse_order": (e_reverse_order, "other"),
}

FAMILIES = {"defect": DEFECTS, "admissible": ADMISSIBLE, "equivalent": EQUIVALENT}

# The input each admissible operator changes (names follow the ``unstated_inputs`` ledger of the virtual items).
ADMISSIBLE_INPUT = {"oa_7.5Lps": "outdoor_air", "oa_none": "outdoor_air", "fan_pressure_x2": "fans",
                    "slab_xps_50mm": "slab", "absorptance_0.9": "absorptance", "absorptance_0.3": "absorptance",
                    "furniture_mass": "internal_mass", "sizing_1.0": "sizing", "ground_+3K": "ground",
                    "door_insulated": "doors"}

# Inputs that the documents of an item state. Changing one is admissible only where the documents leave it open;
# on these items the operator contradicts the documents and is graded as a defect. The virtual items state none
# of them (their ledgers list slab, ground temperature, absorptance, doors, sizing, internal mass and outdoor air,
# and fans where there is a fan), nor does P04, whose narrative names materials only.
STATED_INPUTS: Dict[str, Dict[str, str]] = {
    "P02-lupton-heat-pump": {
        "slab": 'input2.txt: "The floor is a 4" concrete slab on grade."',
        "internal_mass": 'input2.txt: "An internal mass of 14.86 m² of 9" wood side panels is included."',
        "fans": 'input2.txt: "The fan is a continuous Fan:OnOff, 0.75 total efficiency, 250 Pa."',
        "outdoor_air": 'input2.txt: "Outdoor air is 0.00944 m³/s per person"'},
    "P08-bestest-l100a-cos": {
        "absorptance": "L100A_Text_C.txt: exterior shortwave absorptance 0.6 for walls and roof",
        "doors": "L100A_Text_C.txt, Table 2-3: doors 40 ft², R 3.04 h·ft²·°F/Btu",
        "internal_mass": "L100A_Text_C.txt, Section 2.2.4 and Table 2-3: interior walls 1024 ft², 1425 Btu/°F"},
}


# What each defect operator changes.
DEFECT_TARGET = {"wall_on_roof": "roof_construction", "drop_facade_windows": "windows", "single_glazing": "glazing",
                 "remove_doors": "doors", "lpd_unit_error": "lighting_power", "people_x3": "occupancy",
                 "epd_x2": "plug_loads", "heating_sp_up3": "setpoints", "cooling_sp_down3": "setpoints",
                 "rotate_180": "orientation", "infiltration_x5": "infiltration", "footprint_x115": "floor_area",
                 "height_x12": "heights", "lights_always_on": "lighting_schedule", "cop_low": "hvac",
                 "hvac_to_ideal": "hvac", "party_wall_exposed": "party_walls", "site_moved": "site"}

# Targets that the documents of an item leave open. A defect operator there does not contradict the documents, so
# it is reported but not counted in completeness (a sheet that rejected it would be unsound). The virtual items
# state every target except the facets their ledger omits; P02 and P08 state all of them.
OPEN_TARGETS: Dict[str, Dict[str, str]] = {
    "V24-rowhouse-houston": {"hvac": "assumptions.yaml: omitted_facets [hvac]"},
    "P04-office-narrative": {
        "hvac": "input4.txt describes no HVAC system",
        "setpoints": "input4.txt states no thermostat setpoints",
        "infiltration": "input4.txt does not mention infiltration",
        "lighting_schedule": "input4.txt gives a lighting power density but no schedule",
        "site": 'task.md: "Location is not stated; the task fixes the weather file"',
        "roof_construction": 'input4.txt: "The roof contains thermal insulation" (no layers)'},
}


# Defect operators that leave a particular building unchanged: on these items the mutant is the same building.
IDENTITY_ON: Dict[str, Dict[str, str]] = {
    "P08-bestest-l100a-cos": {
        "rotate_180": "the L100A box is symmetric under a half turn: the south and north walls each hold six windows "
                      "and a door of one construction, the east and west walls three windows each"},
}


def role(item_id: str, family: str, name: str) -> str:
    """How the fact sheet of ``item_id`` should treat the mutant.

    'defect' (reject), 'admissible' or 'equivalent' (accept), or 'open': a defect operator whose target the
    documents leave open, so neither verdict is required.
    """
    if family == "admissible" and ADMISSIBLE_INPUT.get(name) in STATED_INPUTS.get(item_id, {}):
        return "defect"
    if family == "defect" and name in IDENTITY_ON.get(item_id, {}):
        return "equivalent"
    if family == "defect" and DEFECT_TARGET.get(name) in OPEN_TARGETS.get(item_id, {}):
        return "open"
    return family


def role_source(item_id: str, family: str, name: str) -> Optional[str]:
    """The document evidence behind a role that differs from the operator's family."""
    if family == "admissible":
        return STATED_INPUTS.get(item_id, {}).get(ADMISSIBLE_INPUT.get(name, ""))
    if family == "defect":
        return IDENTITY_ON.get(item_id, {}).get(name) or OPEN_TARGETS.get(item_id, {}).get(DEFECT_TARGET.get(name, ""))
    return None


def apply(idf: IDF, family: str, name: str, ctx: Optional[dict] = None) -> Optional[str]:
    fn = FAMILIES[family][name][0]
    return fn(idf, ctx or {})
