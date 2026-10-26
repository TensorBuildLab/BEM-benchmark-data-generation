"""Model-editing operators with a change log.

The same operators serve two purposes:

* **repair** (source S1): a curator fixes a harvested reference so that it agrees
  with its documents (add the internal mass the text specifies, change a
  thermostat to heating-only, ...);
* **paired transformation** (source S2): a validated seed is changed in a
  controlled way (relocate, rotate, add insulation, swap glazing, ...) and the
  documents and fact sheet are changed with it, so the ground truth stays exact.

Every operator returns a :class:`Change` that goes into the item's change log.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, List, Optional

from .idf import IDF, IDFObject


@dataclass
class Change:
    op: str
    facet: str
    description: str
    objects: List[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


def _f(x, d=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


def _verts(o: IDFObject) -> List[tuple]:
    start = 11 if o.key == "BUILDINGSURFACE:DETAILED" else 9
    vals = [_f(x, None) for x in o.fields[start:]]
    pts = []
    for i in range(0, len(vals) - 2, 3):
        if None in vals[i:i + 3]:
            break
        pts.append(tuple(vals[i:i + 3]))
    return pts


def _newell(pts):
    nx = ny = nz = 0.0
    for i in range(len(pts)):
        x1, y1, z1 = pts[i]
        x2, y2, z2 = pts[(i + 1) % len(pts)]
        nx += (y1 - y2) * (z1 + z2)
        ny += (z1 - z2) * (x1 + x2)
        nz += (x1 - x2) * (y1 + y2)
    return nx, ny, nz


def wall_azimuth(idf: IDF, wall: IDFObject) -> float:
    """True azimuth (deg from north, clockwise) of a wall's outward normal."""
    nx, ny, _ = _newell(_verts(wall))
    az = math.degrees(math.atan2(nx, ny)) % 360
    b = idf.first("Building")
    north = b.num(1, 0.0) if b else 0.0
    z = idf.get("Zone", wall.get(3))
    rel = z.num(1, 0.0) if z else 0.0
    return (az + (north or 0.0) + (rel or 0.0)) % 360


def facade_of(az: float) -> str:
    return ["N", "E", "S", "W"][int(((az + 45) % 360) // 90)]


def exterior_walls(idf: IDF) -> List[IDFObject]:
    return [o for o in idf.by_class("BuildingSurface:Detailed")
            if o.get(1).upper() == "WALL" and o.get(5).upper() == "OUTDOORS"]


# ------------------------------------------------------------------ repairs
def add_internal_mass(idf: IDF, zone: str, area: float, layers: List[tuple], name: str = "Internal Mass") -> Change:
    """layers: (name, thickness m, k W/mK, rho, cp)."""
    names = []
    for nm, t, k, rho, cp in layers:
        if not idf.get("Material", nm):
            idf.add("Material", [nm, "MediumSmooth", t, k, rho, cp, 0.9, 0.6, 0.6], "! source: repair (internal mass layers)")
        names.append(nm)
    idf.add("Construction", [f"{name} Construction"] + names, "! source: repair")
    idf.add("InternalMass", [name, f"{name} Construction", zone, "", area], "! source: repair (stated in the documents)")
    return Change("add_internal_mass", "envelope", f"added {area} m2 internal mass to zone {zone}", [name])


def add_windows_by_wwr(idf: IDF, wwr: Dict[str, float], u: float, shgc: float, vt: float, sill: float = 0.9,
                       head_clear: float = 0.3, glazing_name: str = "Repair Glazing") -> Change:
    """Add one centred window per exterior wall so that each true facade reaches the given WWR."""
    if not idf.get("WindowMaterial:SimpleGlazingSystem", glazing_name):
        idf.add("WindowMaterial:SimpleGlazingSystem", [glazing_name, u, shgc, vt], "! source: repair (assumed glazing)")
        idf.add("Construction", [f"{glazing_name} Construction", glazing_name], "! source: repair")
    made = []
    for w in exterior_walls(idf):
        fac = facade_of(wall_azimuth(idf, w))
        frac = wwr.get(fac, 0.0)
        pts = _verts(w)
        if frac <= 0 or len(pts) != 4:
            continue
        zs = [p[2] for p in pts]
        z0, z1 = min(zs), max(zs)
        H = z1 - z0
        bottom = [p for p in pts if abs(p[2] - z0) < 1e-6]
        if len(bottom) != 2 or H < 1.0:
            continue
        # the lower-left vertex follows the upper-left one in UpperLeftCorner/Counterclockwise order
        ll, lr = pts[1], pts[2]
        if abs(ll[2] - z0) > 1e-6 or abs(lr[2] - z0) > 1e-6:
            ll, lr = bottom
        L = math.hypot(lr[0] - ll[0], lr[1] - ll[1])
        ux, uy = (lr[0] - ll[0]) / L, (lr[1] - ll[1]) / L
        area = frac * L * H
        s_sill = min(sill, max(0.1, H - head_clear - 0.5))
        h = min(H - s_sill - head_clear, max(0.6, area / max(0.2, L - 0.4)))
        wdt = min(L - 0.4, area / h)
        s = (L - wdt) / 2
        def P(d, z):
            return (ll[0] + ux * d, ll[1] + uy * d, z0 + z)
        v = [P(s, s_sill + h), P(s, s_sill), P(s + wdt, s_sill), P(s + wdt, s_sill + h)]
        nm = f"{w.name} Window"
        flat = []
        for p in v:
            flat += [round(c, 4) for c in p]
        idf.add("FenestrationSurface:Detailed", [nm, "Window", f"{glazing_name} Construction", w.name, "", "autocalculate",
                                                 "", 1, 4] + flat, "! source: repair (window sizes assumed)")
        made.append(nm)
    return Change("add_windows_by_wwr", "fenestration", f"added {len(made)} windows for WWR {wwr}", made)


def add_door(idf: IDF, facade: str, width: float = 0.91, height: float = 2.13, u: float = 2.0, name: str = "Repair Door") -> Change:
    walls = sorted((w for w in exterior_walls(idf) if facade_of(wall_azimuth(idf, w)) == facade),
                   key=lambda w: min(p[2] for p in _verts(w)))
    if not walls:
        return Change("add_door", "fenestration", f"no {facade} wall found; door not added")
    w = walls[0]
    pts = _verts(w)
    z0 = min(p[2] for p in pts)
    ll, lr = pts[1], pts[2]
    L = math.hypot(lr[0] - ll[0], lr[1] - ll[1])
    ux, uy = (lr[0] - ll[0]) / L, (lr[1] - ll[1]) / L
    if not idf.get("Material:NoMass", f"{name} Panel"):
        idf.add("Material:NoMass", [f"{name} Panel", "MediumSmooth", round(1 / u - 0.17, 3), 0.9, 0.6, 0.6], "! source: repair")
        idf.add("Construction", [f"{name} Construction", f"{name} Panel"], "! source: repair")
    s = 0.3
    v = [(ll[0] + ux * s, ll[1] + uy * s, z0 + height), (ll[0] + ux * s, ll[1] + uy * s, z0),
         (ll[0] + ux * (s + width), ll[1] + uy * (s + width), z0), (ll[0] + ux * (s + width), ll[1] + uy * (s + width), z0 + height)]
    # keep the door clear of a window on the same wall: shrink the window from the door side if they overlap
    for win in idf.by_class("FenestrationSurface:Detailed"):
        if win.get(3).upper() == w.name.upper() and win.get(1).upper() == "WINDOW":
            wp = _verts(win)
            d0 = min((p[0] - ll[0]) * ux + (p[1] - ll[1]) * uy for p in wp)
            if d0 < s + width + 0.2:
                shift = s + width + 0.2 - d0
                new = []
                for p in wp:
                    d = (p[0] - ll[0]) * ux + (p[1] - ll[1]) * uy
                    if abs(d - d0) < 1e-6:
                        p = (p[0] + ux * shift, p[1] + uy * shift, p[2])
                    new.append(p)
                flat = []
                for p in new:
                    flat += [round(c, 4) for c in p]
                win.fields = win.fields[:9] + flat
    flat = []
    for p in v:
        flat += [round(c, 4) for c in p]
    nm = f"{w.name} {name}"
    idf.add("FenestrationSurface:Detailed", [nm, "Door", f"{name} Construction", w.name, "", "autocalculate", "", 1, 4] + flat,
            "! source: repair (stated door; size assumed)")
    return Change("add_door", "fenestration", f"added a {width} x {height} m door on the {facade} facade", [nm])


def thermostat_single(idf: IDF, zone_pattern: str, mode: str, setpoint_c: float) -> Change:
    """Replace the control of matching zones with a single heating or cooling setpoint."""
    import fnmatch
    sched = f"Repair {mode.capitalize()} Setpoint"
    if not idf.get("Schedule:Compact", sched):
        idf.add("Schedule:Compact", [sched, "Any Number", "Through: 12/31", "For: AllDays", "Until: 24:00", setpoint_c], "! source: repair")
    ctrl_type = "Repair Control Type"
    code = 1 if mode == "heating" else 2
    if not idf.get("Schedule:Compact", f"{ctrl_type} {code}"):
        idf.add("Schedule:Compact", [f"{ctrl_type} {code}", "Any Number", "Through: 12/31", "For: AllDays", "Until: 24:00", code], "! source: repair")
    cls = "ThermostatSetpoint:SingleHeating" if mode == "heating" else "ThermostatSetpoint:SingleCooling"
    spname = f"Repair Single {mode.capitalize()} SP"
    if not idf.get(cls, spname):
        idf.add(cls, [spname, sched], "! source: repair (documents specify single-mode control)")
    changed = []
    # zones controlled through HVAC templates: give them their own single-mode template thermostat
    for zt in idf.by_class("HVACTemplate:Zone:*"):
        if not fnmatch.fnmatch(zt.get(0).upper(), zone_pattern.upper()):
            continue
        tname = f"{zt.get(0)} {mode.capitalize()} Only"
        if not idf.get("HVACTemplate:Thermostat", tname):
            # templates always expand to a dual setpoint: make the other mode unreachable
            f = [tname, "", setpoint_c, "", 50.0] if mode == "heating" else [tname, "", -30.0, "", setpoint_c]
            idf.add("HVACTemplate:Thermostat", f, "! source: repair (single-mode control per documents; other setpoint unreachable)")
        ti = 2 if zt.key == "HVACTEMPLATE:ZONE:UNITARY" else 1
        zt.fields[ti] = tname
        changed.append(zt.get(0))
    for o in idf.by_class("ZoneControl:Thermostat"):
        if fnmatch.fnmatch(o.get(1).upper(), zone_pattern.upper()):
            o.fields = [o.get(0), o.get(1), f"{ctrl_type} {code}", cls, spname]
            o.comment = "! source: repair (thermostat set to single-mode control per documents)"
            changed.append(o.name)
    return Change("thermostat_single", "control", f"{len(changed)} zone controls set to {mode}-only at {setpoint_c} C", changed)


def set_people_total(idf: IDF, total: float) -> Change:
    ppl = [o for o in idf.by_class("People") if o.get(3).upper() == "PEOPLE"]
    cur = sum(_f(o.get(4)) for o in ppl)
    if not ppl or cur <= 0:
        return Change("set_people_total", "loads", "no People objects with a count; nothing changed")
    for o in ppl:
        o.set(4, round(_f(o.get(4)) * total / cur, 6))
        o.comment = "! source: repair (occupant total per documents)"
    return Change("set_people_total", "loads", f"scaled {len(ppl)} People objects from {cur:g} to {total:g} occupants",
                  [o.name for o in ppl])


def set_equipment_total(idf: IDF, total_w: float, zone_areas: Dict[str, float]) -> Change:
    """Set ElectricEquipment so the building total design level is ``total_w`` (W), split by floor area."""
    eq = idf.by_class("ElectricEquipment")
    tot_a = sum(zone_areas.get(o.get(1).upper(), 0.0) for o in eq)
    for o in eq:
        a = zone_areas.get(o.get(1).upper(), 0.0)
        o.fields[3] = "EquipmentLevel"
        o.set(4, round(total_w * a / tot_a, 4) if tot_a else 0)
        o.set(5, "")
        o.set(6, "")
        o.comment = "! source: repair (design level = maximum of the measured series)"
    return Change("set_equipment_total", "loads", f"equipment design level set to {total_w:g} W in total", [o.name for o in eq])


def set_surface_construction(idf: IDF, surface: str, construction: str) -> Change:
    o = idf.get("BuildingSurface:Detailed", surface)
    old = o.get(2)
    o.fields[2] = construction
    o.comment = "! source: repair (construction assignment corrected)"
    return Change("set_surface_construction", "envelope", f"{surface}: {old} -> {construction}", [surface])


def add_sizing_factors(idf: IDF, heat: float = 1.25, cool: float = 1.15) -> Change:
    sp = idf.first("Sizing:Parameters")
    if sp:
        sp.fields = [str(heat), str(cool)] + sp.fields[2:]
    else:
        idf.add("Sizing:Parameters", [heat, cool], "! source: repair (sizing factors)")
    return Change("add_sizing_factors", "hvac", f"sizing factors heating {heat}, cooling {cool}")


# ------------------------------------------------------------- transforms
def relocate(idf: IDF, epw: Path, ddy: Path) -> Change:
    from .generators.virtual import read_epw_header, design_days
    h = read_epw_header(epw)
    for o in idf.by_class("Site:Location"):
        idf.remove(o)
    idf.add("Site:Location", [f"{h['city']} {h['state']}", h["lat"], h["lon"], h["tz"], h["elev"]], "! source: transform (relocate)")
    for o in idf.by_class("SizingPeriod:DesignDay"):
        idf.remove(o)
    for dd in design_days(ddy):
        idf.add("SizingPeriod:DesignDay", dd, "! source: transform (relocate)")
    return Change("relocate", "site", f"moved to {h['city']} {h['state']} ({h['lat']}, {h['lon']}, {h['elev']} m)")


VERTEX_START = {"BUILDINGSURFACE:DETAILED": 11, "FENESTRATIONSURFACE:DETAILED": 9, "WALL:DETAILED": 10,
                "ROOFCEILING:DETAILED": 10, "FLOOR:DETAILED": 10, "SHADING:SITE:DETAILED": 3,
                "SHADING:BUILDING:DETAILED": 3, "SHADING:ZONE:DETAILED": 4}


def rotate(idf: IDF, degrees: float) -> Change:
    """Turn the building clockwise in plan by ``degrees``.

    With relative coordinates the building north axis is changed. With world coordinates
    EnergyPlus ignores the north axis, so every vertex is rotated about the origin.
    """
    g = idf.first("GlobalGeometryRules")
    world = g is not None and g.get(2).strip().upper() in ("WORLD", "ABSOLUTE")
    if not world:
        b = idf.first("Building")
        old = b.num(1, 0.0) or 0.0
        b.set(1, round((old + degrees) % 360, 3))
        return Change("rotate", "site", f"building north axis {old:g} -> {(old + degrees) % 360:g} deg")
    th = math.radians(degrees)
    c, s = math.cos(th), math.sin(th)
    n = 0
    for o in idf:
        k = o.key
        start = VERTEX_START.get(k)
        if start is None:
            if k == "DAYLIGHTING:REFERENCEPOINT":
                x, y = _f(o.get(3)), _f(o.get(4))
                o.fields[3], o.fields[4] = f"{x * c + y * s:.4f}", f"{y * c - x * s:.4f}"
            continue
        f = o.fields
        for i in range(start, len(f) - 2, 3):
            x, y = _f(f[i], None), _f(f[i + 1], None)
            if x is None or y is None:
                break
            f[i], f[i + 1] = f"{x * c + y * s:.4f}", f"{y * c - x * s:.4f}"
        n += 1
    return Change("rotate", "site", f"rotated {n} surfaces {degrees:g} deg clockwise about the origin (world coordinates)")


def add_wall_insulation(idf: IDF, construction: str, thickness: float, k: float = 0.029, name: str = "Added XPS") -> Change:
    mat = f"{name} {int(thickness * 1000)}mm"
    if not idf.get("Material", mat):
        idf.add("Material", [mat, "MediumRough", thickness, k, 35, 1400, 0.9, 0.6, 0.6], "! source: transform (retrofit)")
    c = idf.get("Construction", construction)
    # insulation goes immediately inside the outermost layer (exterior insulation and finish)
    c.fields = [c.fields[0], c.fields[1], mat] + c.fields[2:]
    c.comment = "! source: transform (retrofit insulation added)"
    return Change("add_wall_insulation", "envelope", f"added {thickness * 1000:.0f} mm insulation (k {k}) to {construction}", [construction])


def set_glazing(idf: IDF, u: float, shgc: float, vt: float, name: str = "Retrofit Glazing") -> Change:
    if not idf.get("WindowMaterial:SimpleGlazingSystem", name):
        idf.add("WindowMaterial:SimpleGlazingSystem", [name, u, shgc, vt], "! source: transform (glazing replacement)")
        idf.add("Construction", [f"{name} Construction", name], "! source: transform")
    n = 0
    for o in idf.by_class("FenestrationSurface:Detailed"):
        if o.get(1).upper() in ("WINDOW", "GLASSDOOR"):
            o.fields[2] = f"{name} Construction"
            if len(o.fields) > 6:
                o.fields[6] = ""      # frame and divider dropped: the simple glazing U is the whole-window value
            n += 1
    for o in idf.by_class("Window"):   # simple window objects: name, construction, surface, frame and divider, ...
        o.fields[1] = f"{name} Construction"
        if len(o.fields) > 3:
            o.fields[3] = ""
        n += 1
    return Change("set_glazing", "fenestration", f"{n} windows to U {u}, SHGC {shgc}, VT {vt}")



HVAC_CLASSES = ["AirLoopHVAC*", "Coil:*", "Fan:*", "Controller:*", "AvailabilityManager*", "SetpointManager:*",
                "OutdoorAir:Mixer", "OutdoorAir:NodeList", "NodeList", "Branch", "BranchList", "Connector:*",
                "ConnectorList", "ZoneHVAC:*", "AirTerminal:*", "Sizing:System", "Sizing:Zone",
                "DesignSpecification:OutdoorAir", "DesignSpecification:ZoneAirDistribution"]


def one_system_per_zone(idf: IDF, oa_per_area: float = 0.000432, supplemental: str = "Gas") -> Change:
    """Replace the air-side HVAC with one packaged single-zone heat pump per thermostat-controlled zone.

    Repairs a common defect: one single-zone unitary system, controlled from one zone, serving several
    zones, so that the other zones are never controlled. The model's own ZoneControl:Thermostat objects
    are kept (the templates get no thermostat of their own) and the rated COPs of the removed DX coils
    are carried over, so only the system layout changes.
    """
    from .schema import get_schema
    S = get_schema("23.1")

    def cop(cls, default):
        for o in idf.by_class(cls):
            fields = S._layout(o.cls)[1]
            for k in ("gross_rated_cooling_cop", "gross_rated_heating_cop"):
                if k in fields:
                    v = _f(o.get(fields.index(k)), None)
                    if v:
                        return v
        return default
    cop_c = cop("Coil:Cooling:DX:SingleSpeed", 3.0)
    cop_h = cop("Coil:Heating:DX:SingleSpeed", 2.75)
    zones = [o.get(1) for o in idf.by_class("ZoneControl:Thermostat")]
    removed = [o for o in idf.by_class(*HVAC_CLASSES)]
    # an earlier template expansion left objects named "HVACTemplate..."; the new templates would
    # create the same names, so rename them (and every reference to them) first
    ren = {o.name.upper(): "Model" + o.name[len("HVACTemplate"):] for o in idf
           if o not in removed and o.fields and o.name.upper().startswith("HVACTEMPLATE")}
    for o in idf:
        o.fields = [ren.get(str(v).strip().upper(), v) for v in o.fields]
    for o in removed:
        idf.remove(o)

    def add(cls, **kw):
        fields = S._layout(cls)[1]
        vals = [""] * len(fields)
        for k, v in kw.items():
            vals[fields.index(k)] = v
        while vals and vals[-1] == "":
            vals.pop()
        return idf.add(cls, vals, "! source: repair (one packaged heat pump per zone)")
    for zn in zones:
        sysname = f"{zn} PSZ-HP"
        add("HVACTemplate:Zone:Unitary", zone_name=zn, template_unitary_system_name=sysname,
            template_thermostat_name="", supply_air_maximum_flow_rate="autosize",
            outdoor_air_method="Flow/Area", outdoor_air_flow_rate_per_zone_floor_area=oa_per_area)
        add("HVACTemplate:System:UnitaryHeatPump:AirToAir", name=sysname, control_zone_or_thermostat_location_name=zn,
            cooling_supply_air_flow_rate="autosize", heating_supply_air_flow_rate="autosize",
            supply_fan_placement="BlowThrough", supply_fan_total_efficiency=0.6, supply_fan_delta_pressure=500,
            supply_fan_motor_efficiency=0.9, cooling_coil_type="SingleSpeedDX", cooling_design_supply_air_temperature=12.8,
            cooling_coil_gross_rated_total_capacity="autosize", cooling_coil_gross_rated_sensible_heat_ratio="autosize",
            cooling_coil_gross_rated_cop=cop_c, heat_pump_heating_coil_type="SingleSpeedDXHeatPump",
            heating_design_supply_air_temperature=45, heat_pump_heating_coil_gross_rated_capacity="autosize",
            heat_pump_heating_coil_rated_cop=cop_h, heat_pump_heating_minimum_outdoor_dry_bulb_temperature=-8,
            supplemental_heating_coil_type=supplemental, supplemental_heating_coil_capacity="autosize",
            maximum_outdoor_air_flow_rate="autosize", minimum_outdoor_air_flow_rate="autosize",
            economizer_type="NoEconomizer")
    return Change("one_system_per_zone", "hvac",
                  f"one heat pump controlled from one zone served {len(zones)} zones; replaced by one packaged heat pump "
                  f"per zone (COP {cop_c:g} cooling, {cop_h:g} heating, {supplemental.lower()} supplemental heat kept); "
                  f"{len(removed)} HVAC objects removed", zones)


def set_lighting_density(idf: IDF, w_m2: float, why: str = "") -> Change:
    """Set every Lights object to a lighting power density in W/m2 of zone floor area."""
    ls = idf.by_class("Lights")
    for o in ls:
        while len(o.fields) < 7:
            o.fields.append("")
        o.fields[3] = "Watts/Area"
        o.fields[4] = ""
        o.fields[5] = str(w_m2)
        o.fields[6] = ""
        o.comment = "! source: repair (lighting power density" + (f"; {why}" if why else "") + ")"
    return Change("set_lighting_density", "loads", f"lighting power density set to {w_m2:g} W/m2 in {len(ls)} Lights objects"
                  + (f" ({why})" if why else ""), [o.name for o in ls])
