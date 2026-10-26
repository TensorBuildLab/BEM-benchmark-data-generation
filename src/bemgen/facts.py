"""Extract *model facts* from an EnergyPlus model and its simulation outputs.

A model fact is a value that a building description can state and a reviewer
can check: a floor area, a wall U-factor, a window-to-wall ratio, a lighting
power density, a thermostat setpoint, the kind of HVAC system, an annual
heating energy. Most facts are read from EnergyPlus's own reports (the
SQLite output and the ``.eio`` file), so that HVACTemplate expansion, zone
multipliers and geometry transforms are handled by EnergyPlus itself.
The remaining facts (HVAC classification, rated COPs, setpoint schedules,
provenance tags) are read from the expanded input.
"""
from __future__ import annotations

import math
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional

from .idf import IDF, provenance_tag

ORIENT = {"North (315 to 45 deg)": "N", "East (45 to 135 deg)": "E",
          "South (135 to 225 deg)": "S", "West (225 to 315 deg)": "W", "Total": "total"}


def _f(x) -> Optional[float]:
    try:
        v = float(str(x).strip())
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


class SQL:
    def __init__(self, path):
        self.path = str(path)
        self.c = sqlite3.connect(self.path)
        self.has_tab = bool(self.c.execute(
            "select name from sqlite_master where name='TabularDataWithStrings'").fetchall())

    def table(self, report: str, table: str, report_for: str = "Entire Facility") -> Dict[str, Dict[str, str]]:
        """Return {row: {column[units]: value}} for one tabular report table."""
        if not self.has_tab:
            return {}
        rows = self.c.execute(
            "select RowName, ColumnName, Units, Value from TabularDataWithStrings "
            "where ReportName=? and TableName=? and ReportForString=?", (report, table, report_for)).fetchall()
        out: Dict[str, Dict[str, str]] = defaultdict(dict)
        for r, col, unit, val in rows:
            out[r][f"{col} [{unit}]" if unit else col] = val.strip() if isinstance(val, str) else val
        return dict(out)

    def rows(self, q: str, args=()):
        try:
            return self.c.execute(q, args).fetchall()
        except sqlite3.Error:
            return []


def _parse_eio(path: Path) -> Dict[str, List[List[str]]]:
    out: Dict[str, List[List[str]]] = defaultdict(list)
    if not path.is_file():
        return out
    for ln in path.read_text(errors="replace").splitlines():
        if ln.startswith("!") or "," not in ln:
            continue
        parts = [p.strip() for p in ln.split(",")]
        out[parts[0]].append(parts[1:])
    return out


# ------------------------------------------------------------------ HVAC
HVAC_CLASSES = [
    ("ideal_loads", ["ZONEHVAC:IDEALLOADSAIRSYSTEM"]),
    ("ptac", ["ZONEHVAC:PACKAGEDTERMINALAIRCONDITIONER"]),
    ("pthp", ["ZONEHVAC:PACKAGEDTERMINALHEATPUMP"]),
    ("vrf", ["ZONEHVAC:TERMINALUNIT:VARIABLEREFRIGERANTFLOW"]),
    ("water_to_air_hp", ["ZONEHVAC:WATERTOAIRHEATPUMP"]),
    ("fan_coil", ["ZONEHVAC:FOURPIPEFANCOIL"]),
    ("baseboard", ["ZONEHVAC:BASEBOARD:CONVECTIVE:ELECTRIC", "ZONEHVAC:BASEBOARD:CONVECTIVE:WATER",
                   "ZONEHVAC:BASEBOARD:RADIANTCONVECTIVE:ELECTRIC", "ZONEHVAC:BASEBOARD:RADIANTCONVECTIVE:WATER"]),
    ("radiant", ["ZONEHVAC:LOWTEMPERATURERADIANT:VARIABLEFLOW", "ZONEHVAC:LOWTEMPERATURERADIANT:ELECTRIC",
                 "ZONEHVAC:LOWTEMPERATURERADIANT:CONSTANTFLOW"]),
    ("unit_heater", ["ZONEHVAC:UNITHEATER"]),
    ("window_ac", ["ZONEHVAC:WINDOWAIRCONDITIONER"]),
    ("erv", ["ZONEHVAC:ENERGYRECOVERYVENTILATOR"]),
    ("dehumidifier", ["ZONEHVAC:DEHUMIDIFIER:DX"]),
]


def classify_hvac(idf: IDF, schema=None) -> dict:
    keys = Counter(o.key for o in idf)
    tags = [t for t, cl in HVAC_CLASSES if any(keys.get(c) for c in cl)]
    n_loops = keys.get("AIRLOOPHVAC", 0)
    if n_loops:
        has_dx_heat = any(keys.get(k) for k in ("COIL:HEATING:DX:SINGLESPEED", "COIL:HEATING:DX:MULTISPEED",
                                                "COIL:HEATING:DX:VARIABLESPEED"))
        has_vav = any(k.startswith("AIRTERMINAL:SINGLEDUCT:VAV") for k in keys)
        has_furnace = any(k.startswith("AIRLOOPHVAC:UNITARY:FURNACE") or k.startswith("AIRLOOPHVAC:UNITARYHEATCOOL")
                          for k in keys)
        if keys.get("AIRLOOPHVAC:UNITARYHEATPUMP:AIRTOAIR") or (keys.get("AIRLOOPHVAC:UNITARYSYSTEM") and has_dx_heat):
            tags.append("central_ashp")
        elif has_vav:
            tags.append("vav")
        elif has_furnace or keys.get("AIRLOOPHVAC:UNITARYSYSTEM"):
            tags.append("central_unitary")
        else:
            tags.append("air_loop")
    if keys.get("PLANTLOOP"):
        tags.append("plant_loop")
    if any(k.startswith("HEATEXCHANGER:AIRTOAIR") for k in keys) or keys.get("ZONEHVAC:ENERGYRECOVERYVENTILATOR"):
        tags.append("heat_recovery")
    if any(k.startswith("WATERHEATER:") for k in keys):
        tags.append("water_heater")
    if any(k.startswith("WATERHEATER:HEATPUMP") for k in keys):
        tags.append("heat_pump_water_heater")
    if any(k.startswith("SOLARCOLLECTOR:") for k in keys):
        tags.append("solar_thermal")
    primary = next((t for t in ["ideal_loads", "central_ashp", "vav", "central_unitary", "ptac", "pthp", "vrf",
                                "water_to_air_hp", "fan_coil", "radiant", "baseboard", "unit_heater", "window_ac",
                                "air_loop"] if t in tags), "none")
    heat_fuels = set()
    for o in idf.by_class("Coil:Heating:Fuel", "Coil:Heating:Gas"):
        heat_fuels.add((o.get(2) or "NaturalGas") if o.key == "COIL:HEATING:FUEL" else "NaturalGas")
    if idf.by_class("Coil:Heating:Electric", "Coil:Heating:DX:*", "ZoneHVAC:Baseboard:*:Electric"):
        heat_fuels.add("Electricity")
    if idf.by_class("Boiler:HotWater"):
        for o in idf.by_class("Boiler:HotWater"):
            heat_fuels.add(o.get(1) or "NaturalGas")
    cops = {}
    if schema is not None:
        for cls, key, label in [("Coil:Cooling:DX:SingleSpeed", "gross_rated_cooling_cop", "cooling_cop"),
                                ("Coil:Cooling:DX:TwoSpeed", "high_speed_gross_rated_cooling_cop", "cooling_cop"),
                                ("Coil:Heating:DX:SingleSpeed", "gross_rated_heating_cop", "heating_cop")]:
            for o in idf.by_class(cls):
                try:
                    v = o.num(schema.field_index(cls, key))
                except (ValueError, KeyError):
                    v = None
                if v is not None:
                    cops.setdefault(label + "s", []).append(v)
        for label in ("cooling_cop", "heating_cop"):
            if cops.get(label + "s"):
                cops[label] = cops[label + "s"][0]      # first coil (the primary system in simple models)
    served = sorted({o.get(0).upper() for o in idf.by_class("ZoneHVAC:EquipmentConnections")})
    return {"primary": primary, "tags": sorted(set(tags)), "n_air_loops": n_loops, "heating_fuels": sorted(heat_fuels),
            "zones_with_equipment": served, "n_zones_with_equipment": len(served), **cops}


# -------------------------------------------------------------- control
def _thermostats(idf: IDF, sched: Dict[str, dict]) -> dict:
    sp_objs = {}
    for o in idf.by_class("ThermostatSetpoint:SingleHeating"):
        sp_objs[o.name.upper()] = ("single_heating", o.get(1), None)
    for o in idf.by_class("ThermostatSetpoint:SingleCooling"):
        sp_objs[o.name.upper()] = ("single_cooling", None, o.get(1))
    for o in idf.by_class("ThermostatSetpoint:SingleHeatingOrCooling"):
        sp_objs[o.name.upper()] = ("single_heating_or_cooling", o.get(1), o.get(1))
    for o in idf.by_class("ThermostatSetpoint:DualSetpoint"):
        sp_objs[o.name.upper()] = ("dual", o.get(1), o.get(2))
    zones = {}
    zlists = {o.name.upper(): [f.upper() for f in o.fields[1:] if f] for o in idf.by_class("ZoneList")}
    for o in idf.by_class("ZoneControl:Thermostat"):
        target = o.get(1).upper()
        kinds, heat, cool = [], [], []
        # fields: name, zone/zonelist, control type schedule, (object type, object name) x n
        for j in range(4, len(o.fields), 2):
            nm = o.get(j).upper()
            if nm in sp_objs:
                k, h, c = sp_objs[nm]
                kinds.append(k)
                if h:
                    heat.append(sched.get(h.upper(), {}))
                if c:
                    cool.append(sched.get(c.upper(), {}))
        hmax = max((s.get("max") for s in heat if s.get("max") is not None), default=None)
        hmin = min((s.get("min") for s in heat if s.get("min") is not None), default=None)
        cmin = min((s.get("min") for s in cool if s.get("min") is not None), default=None)
        cmax = max((s.get("max") for s in cool if s.get("max") is not None), default=None)
        rec = {"types": sorted(set(kinds)), "heating_setpoint": hmax, "heating_setback": hmin,
               "cooling_setpoint": cmin, "cooling_setup": cmax,
               "heats": any(k in ("single_heating", "dual", "single_heating_or_cooling") for k in kinds),
               "cools": any(k in ("single_cooling", "dual", "single_heating_or_cooling") for k in kinds)}
        for zone in zlists.get(target, [target]):
            zones[zone] = dict(rec)
    # ZoneList targets: expand later by caller if needed
    hs = [z["heating_setpoint"] for z in zones.values() if z["heating_setpoint"] is not None]
    cs = [z["cooling_setpoint"] for z in zones.values() if z["cooling_setpoint"] is not None]
    return {"zones": zones, "n_controlled_zones": len(zones),
            "heating_setpoint": max(hs) if hs else None, "cooling_setpoint": min(cs) if cs else None,
            "any_heating": any(z["heats"] for z in zones.values()),
            "any_cooling": any(z["cools"] for z in zones.values())}


def _schedule_ranges_static(idf: IDF) -> Dict[str, dict]:
    """Min/max of numeric values in Schedule:Compact/Constant/Day objects (used when no SQL)."""
    out = {}
    for o in idf.by_class("Schedule:Constant"):
        v = o.num(2)
        out[o.name.upper()] = {"min": v, "max": v, "type": o.get(1)}
    for o in idf.by_class("Schedule:Compact"):
        vals = []
        for f in o.fields[2:]:
            s = f.strip()
            if re.match(r"^(through|for|until|interpolate)", s, re.I):
                continue
            v = _f(s)
            if v is not None:
                vals.append(v)
        out[o.name.upper()] = {"min": min(vals) if vals else None, "max": max(vals) if vals else None, "type": o.get(1)}
    return out


# ------------------------------------------------------------- geometry
def _count_levels(zs, tol: float = 1.0) -> int:
    """Number of distinct floor elevations (zones within ``tol`` m count as one level)."""
    levels = []
    for z in sorted(zs):
        if not levels or z - levels[-1] > tol:
            levels.append(z)
    return len(levels)


def _poly_area(pts) -> float:
    n = len(pts)
    if n < 3:
        return 0.0
    cx = cy = cz = 0.0
    for i in range(n):
        x1, y1, z1 = pts[i]
        x2, y2, z2 = pts[(i + 1) % n]
        cx += y1 * z2 - z1 * y2
        cy += z1 * x2 - x1 * z2
        cz += x1 * y2 - y1 * x2
    return 0.5 * math.sqrt(cx * cx + cy * cy + cz * cz)


def surface_vertices(o) -> List[tuple]:
    """Vertices of BuildingSurface:Detailed / FenestrationSurface:Detailed objects."""
    k = o.key
    if k == "BUILDINGSURFACE:DETAILED":
        start = 10
    elif k == "FENESTRATIONSURFACE:DETAILED":
        start = 8
    elif k in ("WALL:DETAILED", "ROOFCEILING:DETAILED", "FLOOR:DETAILED"):
        start = 9
    else:
        return []
    vals = [_f(x) for x in o.fields[start + 1:]]
    pts = []
    for i in range(0, len(vals) - 2, 3):
        if None in vals[i:i + 3]:
            break
        pts.append(tuple(vals[i:i + 3]))
    return pts


def _verts_any(o) -> List[tuple]:
    """Vertices of detailed surfaces, including Shading:*:Detailed objects."""
    if o.key.startswith("SHADING:") and o.key.endswith(":DETAILED"):
        start = 3 if o.key == "SHADING:ZONE:DETAILED" else 2    # first vertex field after the vertex count
        vals = [_f(x) for x in o.fields[start + 1:]]
        pts = []
        for i in range(0, len(vals) - 2, 3):
            if None in vals[i:i + 3]:
                break
            pts.append(tuple(vals[i:i + 3]))
        return pts
    return surface_vertices(o)


# ---------------------------------------------------------------- main
def extract(idf: IDF, run_dir: Optional[str] = None, schema=None, expanded: Optional[IDF] = None) -> dict:
    """Return the model-fact dictionary for a model and (optionally) its run folder."""
    model = expanded or idf
    facts: dict = {"meta": {}, "site": {}, "geometry": {}, "envelope": {}, "fenestration": {}, "loads": {},
                   "infiltration": {}, "control": {}, "hvac": {}, "results": {}, "provenance": {}}
    # ---- static facts
    v = idf.first("Version")
    facts["meta"]["version"] = v.get(0) if v else ""
    ts = idf.first("Timestep")
    facts["meta"]["timestep"] = ts.num(0) if ts else None
    rp = idf.first("RunPeriod")
    if rp:
        facts["meta"]["run_period"] = {"begin_month": rp.num(1), "begin_day": rp.num(2), "begin_year": rp.num(3),
                                       "end_month": rp.num(4), "end_day": rp.num(5), "end_year": rp.num(6)}
        bm, bd, em, ed = rp.num(1), rp.num(2), rp.num(4), rp.num(5)
        facts["meta"]["annual_run"] = (bm, bd, em, ed) == (1, 1, 12, 31)
    facts["meta"]["n_design_days"] = len(idf.by_class("SizingPeriod:DesignDay"))
    facts["meta"]["n_objects"] = len(idf)
    facts["meta"]["uses_hvactemplate"] = any(o.key.startswith("HVACTEMPLATE:") for o in idf)
    facts["meta"]["schedule_files"] = [o.get(2) for o in idf.by_class("Schedule:File")]
    cm = idf.first("ZoneCapacitanceMultiplier:ResearchSpecial")
    if cm:
        facts["meta"]["capacitance_multiplier_temperature"] = cm.num(2, 1.0)
    pv_w = 0.0
    for o in idf.by_class("Generator:PVWatts"):
        pv_w += o.num(2, 0.0) or 0.0
    pv_unknown = False
    for o in idf.by_class("Generator:Photovoltaic"):
        perf = idf.get("PhotovoltaicPerformance:Simple", o.get(3)) if o.get(2).upper().endswith("SIMPLE") else None
        srf = next((x for x in idf.by_class("Shading:*", "BuildingSurface:Detailed") if x.name.upper() == o.get(1).upper()), None)
        if perf is None or srf is None:
            pv_unknown = True
            continue
        verts = _verts_any(srf)
        a = _poly_area(verts) if verts else 0.0
        pv_w += a * (perf.num(1, 0.0) or 0.0) * (perf.num(3, 0.0) or 0.0) * 1000.0
    facts["meta"]["pv_dc_kw"] = None if (pv_unknown and pv_w == 0) else pv_w / 1000.0
    facts["meta"]["n_pv_generators"] = len(idf.by_class("Generator:PVWatts", "Generator:Photovoltaic"))
    loc = idf.first("Site:Location")
    if loc:
        facts["site"].update({"name": loc.get(0), "latitude": loc.num(1), "longitude": loc.num(2),
                              "time_zone": loc.num(3), "elevation": loc.num(4)})
    b = idf.first("Building")
    if b:
        facts["site"]["north_axis"] = b.num(1, 0.0)
        facts["meta"]["building_name"] = b.get(0)
    g = facts["geometry"]
    zones = model.by_class("Zone")
    g["n_zones"] = len(zones)
    g["n_spaces"] = len(model.by_class("Space"))
    surf = model.by_class("BuildingSurface:Detailed", "Wall:*", "RoofCeiling:*", "Floor:*", "Roof", "Ceiling:*")
    sub = model.by_class("FenestrationSurface:Detailed", "Window", "Door", "GlazedDoor", "Window:Interzone",
                         "Door:Interzone", "GlazedDoor:Interzone")
    g["n_surfaces"] = len(surf)
    g["n_subsurfaces"] = len(sub)
    bc = Counter()
    for s in model.by_class("BuildingSurface:Detailed"):
        bc[s.get(5).lower() or "?"] += 1
    g["boundary_conditions"] = dict(bc)
    g["n_shading"] = len(model.by_class("Shading:*"))
    facts["hvac"] = classify_hvac(model, schema)
    facts["envelope"]["n_constructions"] = len(model.by_class("Construction"))
    facts["envelope"]["has_internal_mass"] = bool(model.by_class("InternalMass"))
    facts["infiltration"]["classes"] = sorted({o.cls for o in model.by_class("ZoneInfiltration:*")})
    facts["infiltration"]["n_objects"] = len(model.by_class("ZoneInfiltration:*"))
    # provenance tags written by the generator (e.g. "! source: stated")
    tags = [provenance_tag(o) for o in idf]
    tagged = [t for t in tags if t]
    kinds = Counter(t.split()[0].strip(";:,()").lower() for t in tagged)
    facts["provenance"] = {"n_objects": len(idf), "n_tagged": len(tagged),
                           "tagged_fraction": round(len(tagged) / max(1, len(idf)), 3), "kinds": dict(kinds)}
    sched_static = _schedule_ranges_static(model)

    if not run_dir:
        facts["control"] = _thermostats(model, sched_static)
        return facts

    run_dir = Path(run_dir)
    out = run_dir / "out" if (run_dir / "out").is_dir() else run_dir
    sqlp = out / "eplusout.sql"
    eio = _parse_eio(out / "eplusout.eio")
    if not sqlp.is_file():
        facts["control"] = _thermostats(model, sched_static)
        return facts
    sql = SQL(sqlp)
    # schedules from SQL (covers Schedule:Year/Week/Day and expanded templates)
    sched = dict(sched_static)
    for nm, typ, mn, mx in sql.rows("select ScheduleName, ScheduleType, ScheduleMinimum, ScheduleMaximum from Schedules"):
        sched[str(nm).upper()] = {"min": _f(mn), "max": _f(mx), "type": typ}
    facts["control"] = _thermostats(model, sched)

    gen = sql.table("InputVerificationandResultsSummary", "General")
    if gen:
        used = {"latitude": "Latitude", "longitude": "Longitude", "elevation": "Elevation", "time_zone": "Time Zone"}
        for key, row in used.items():
            v = _f(next(iter(gen.get(row, {}).values()), None))
            facts["site"][f"{key}_used"] = v
            if facts["site"].get(key) is None:
                facts["site"][key] = v          # no Site:Location: EnergyPlus takes the weather file location
        facts["meta"]["weather_file"] = next((v for k, v in gen.get("Weather File", {}).items()), "")
        facts["meta"]["hours_simulated"] = _f(next(iter(gen.get("Hours Simulated", {}).values()), None))
    # zones
    zrows = sql.rows("select ZoneName, FloorArea, Volume, CeilingHeight, Multiplier, ListMultiplier, MinimumZ, "
                     "MaximumZ, ExtGrossWallArea, ExtWindowArea, IsPartOfTotalArea from Zones")
    zs = sql.table("InputVerificationandResultsSummary", "Zone Summary")
    zinfo = {}
    for (nm, fa, vol, ch, mult, lmult, zmin, zmax, gwa, wa, part) in zrows:
        row = zs.get(nm, {})
        zinfo[nm] = {"floor_area": _f(fa), "volume": _f(vol), "ceiling_height": _f(ch),
                     "multiplier": (mult or 1) * (lmult or 1), "z_min": _f(zmin), "z_max": _f(zmax),
                     "ext_gross_wall_area": _f(gwa), "ext_window_area": _f(wa), "part_of_total": bool(part),
                     "conditioned": str(row.get("Conditioned (Y/N)", "")).strip().upper() in ("Y", "YES"),
                     "lighting_w_m2": _f(row.get("Lighting [W/m2]")),
                     "m2_per_person": _f(row.get("People [m2 per person]")),
                     "plug_w_m2": _f(row.get("Plug and Process [W/m2]")),
                     "underground_wall_area": _f(row.get("Underground Gross Wall Area [m2]"))}
    g["zones"] = zinfo
    area = sql.table("AnnualBuildingUtilityPerformanceSummary", "Building Area")
    g["total_floor_area"] = _f(area.get("Total Building Area", {}).get("Area [m2]"))
    g["conditioned_floor_area"] = _f(area.get("Net Conditioned Building Area", {}).get("Area [m2]"))
    g["unconditioned_floor_area"] = _f(area.get("Unconditioned Building Area", {}).get("Area [m2]"))
    g["n_conditioned_zones"] = sum(1 for z in zinfo.values() if z["conditioned"])
    g["underground_wall_area"] = sum((z["underground_wall_area"] or 0) * z["multiplier"] for z in zinfo.values())
    g["volume_total"] = sum((z["volume"] or 0) * z["multiplier"] for z in zinfo.values())
    g["conditioned_volume"] = sum((z["volume"] or 0) * z["multiplier"] for z in zinfo.values() if z["conditioned"])
    zmins = [z["z_min"] for z in zinfo.values() if z["z_min"] is not None]
    zmaxs = [z["z_max"] for z in zinfo.values() if z["z_max"] is not None]
    if zmins and zmaxs:
        g["building_height"] = round(max(zmaxs) - min(zmins), 3)
        cz = [z for z in zinfo.values() if z["conditioned"] and z["part_of_total"] and z["z_min"] is not None]
        base = cz or [z for z in zinfo.values() if z["z_min"] is not None]
        g["n_levels"] = _count_levels([z["z_min"] for z in base])
        g["n_levels_all_zones"] = _count_levels(zmins)
    cond_h = [z["ceiling_height"] for z in zinfo.values() if z["conditioned"] and z["ceiling_height"]]
    if cond_h:
        g["mean_ceiling_height_conditioned"] = sum(cond_h) / len(cond_h)
    # window-wall ratio
    wwr = sql.table("InputVerificationandResultsSummary", "Window-Wall Ratio")
    fen = facts["fenestration"]
    fen["wwr"] = {ORIENT[c.split(" [")[0]]: (_f(v) or 0.0) / 100.0
                  for c, v in wwr.get("Gross Window-Wall Ratio", {}).items() if c.endswith("[%]")}
    fen["window_area"] = {ORIENT[c.split(" [")[0]]: _f(v) for c, v in wwr.get("Window Opening Area", {}).items()
                          if c.endswith("[m2]")}
    fen["gross_wall_area"] = {ORIENT[c.split(" [")[0]]: _f(v) for c, v in wwr.get("Gross Wall Area", {}).items()
                              if c.endswith("[m2]")}
    # fenestration details
    ef = sql.table("EnvelopeSummary", "Exterior Fenestration")
    wins = {k: v for k, v in ef.items() if "Total or Average" not in k}
    fen["n_windows"] = len(wins)
    tot_a = sum(_f(w.get("Area of Multiplied Openings [m2]")) or 0 for w in wins.values())
    if wins and tot_a > 0:
        def wavg(col):
            num = sum((_f(w.get(col)) or 0) * (_f(w.get("Area of Multiplied Openings [m2]")) or 0) for w in wins.values())
            return num / tot_a
        fen["window_u"] = wavg("Glass U-Factor [W/m2-K]")
        fen["window_shgc"] = wavg("Glass SHGC")
        fen["window_vt"] = wavg("Glass Visible Transmittance")
        fen["window_assembly_u"] = wavg("Assembly U-Factor [W/m2-K]") if any(
            _f(w.get("Assembly U-Factor [W/m2-K]")) for w in wins.values()) else None
    fen["window_area_total"] = tot_a
    fen["windows_by_direction"] = dict(Counter(w.get("Cardinal Direction", "?") for w in wins.values()))
    doors = sql.table("EnvelopeSummary", "Exterior Door")
    fen["n_doors"] = len(doors)
    fen["door_area_total"] = sum(_f(d.get("Gross Area [m2]")) or 0 for d in doors.values())
    opaque = sql.table("EnvelopeSummary", "Opaque Exterior")
    door_dirs = []
    for d in doors.values():
        ps = opaque.get(d.get("Parent Surface", ""), {})
        door_dirs.append(ps.get("Cardinal Direction", "?"))
    fen["doors_by_direction"] = dict(Counter(door_dirs))
    by_cons = {}
    for d in doors.values():
        cn = d.get("Construction", "?")
        by_cons[cn] = by_cons.get(cn, 0.0) + (_f(d.get("Gross Area [m2]")) or 0.0)
    fen["door_area_by_construction"] = by_cons
    if doors:
        fen["door_u"] = sum((_f(d.get("U-Factor with Film [W/m2-K]")) or 0) * (_f(d.get("Gross Area [m2]")) or 0)
                            for d in doors.values()) / max(1e-9, fen["door_area_total"])
    # opaque envelope
    env = facts["envelope"]
    groups = defaultdict(lambda: [0.0, 0.0, 0.0])   # area, U*area (with film), U*area no film
    zone_of = {str(sn).upper(): zn for sn, zn in sql.rows(
        "select s.SurfaceName, z.ZoneName from Surfaces s join Zones z on s.ZoneIndex = z.ZoneIndex")}
    cond_names = {n.upper() for n, z in zinfo.items() if z["conditioned"]}
    env["scope"] = "conditioned zones" if cond_names else "all zones"
    for nm, r in opaque.items():
        if cond_names and zone_of.get(str(nm).upper(), "").upper() not in cond_names:
            continue
        tilt = _f(r.get("Tilt [deg]"))
        a = _f(r.get("Net Area [m2]")) or 0.0
        u = _f(r.get("U-Factor with Film [W/m2-K]"))
        un = _f(r.get("U-Factor no Film [W/m2-K]"))
        if tilt is None or u is None:
            continue
        kind = "roof" if tilt < 60 else ("wall" if tilt < 120 else "floor")
        groups[kind][0] += a
        groups[kind][1] += u * a
        groups[kind][2] += (un or 0) * a
    for kind, (a, ua, una) in groups.items():
        env[f"{kind}_area"] = a
        env[f"{kind}_u"] = ua / a if a else None
        env[f"{kind}_u_nofilm"] = una / a if a else None
    # composite opaque wall U: walls plus opaque doors hosted by them (some models put wall framing in door objects)
    wa, wua = env.get("wall_area") or 0.0, (env.get("wall_u") or 0.0) * (env.get("wall_area") or 0.0)
    for d in doors.values():
        host = d.get("Parent Surface", "")
        if cond_names and zone_of.get(str(host).upper(), "").upper() not in cond_names:
            continue
        a = _f(d.get("Gross Area [m2]")) or 0.0
        wa += a
        wua += a * (_f(d.get("U-Factor with Film [W/m2-K]")) or 0.0)
    env["wall_u_composite"] = wua / wa if wa else None
    gnd = sum(1 for o in model.by_class("BuildingSurface:Detailed") if o.get(5).lower().startswith("ground")
              or o.get(5).lower() == "foundation")
    env["n_ground_surfaces"] = gnd
    cons = {str(n).upper(): _f(u) for n, u in sql.rows("select Name, Uvalue from Constructions")}
    env["construction_u"] = cons
    # internal loads
    L = facts["loads"]
    zid = {i: n for i, n in sql.rows("select ZoneIndex, ZoneName from Zones")}
    mult = {n: z["multiplier"] for n, z in zinfo.items()}
    ppl = defaultdict(float)
    for zi, n in sql.rows("select ZoneIndex, NumberOfPeople from NominalPeople"):
        ppl[zid.get(zi)] += (_f(n) or 0) * mult.get(zid.get(zi), 1)
    lit = defaultdict(float)
    for zi, d in sql.rows("select ZoneIndex, DesignLevel from NominalLighting"):
        lit[zid.get(zi)] += (_f(d) or 0) * mult.get(zid.get(zi), 1)
    eq = defaultdict(float)
    for tbl in ("NominalElectricEquipment", "NominalGasEquipment", "NominalOtherEquipment", "NominalHotWaterEquipment",
                "NominalSteamEquipment"):
        for zi, d in sql.rows(f"select ZoneIndex, DesignLevel from {tbl}"):
            eq[zid.get(zi)] += (_f(d) or 0) * mult.get(zid.get(zi), 1)
    tfa = sum((z["floor_area"] or 0) * z["multiplier"] for z in zinfo.values() if z["part_of_total"]) or None
    cfa = sum((z["floor_area"] or 0) * z["multiplier"] for z in zinfo.values() if z["conditioned"]) or None
    L["people_total"] = sum(ppl.values())
    L["lighting_w_total"] = sum(lit.values())
    L["equipment_w_total"] = sum(eq.values())
    if tfa:
        L["lpd_w_m2"] = L["lighting_w_total"] / tfa
        L["epd_w_m2"] = L["equipment_w_total"] / tfa
        L["people_per_100m2"] = 100 * L["people_total"] / tfa
    if cfa:
        L["lpd_w_m2_conditioned"] = L["lighting_w_total"] / cfa
        L["epd_w_m2_conditioned"] = L["equipment_w_total"] / cfa
    L["zones"] = {z: {"people": ppl.get(z, 0.0), "lighting_w": lit.get(z, 0.0), "equipment_w": eq.get(z, 0.0)}
                  for z in zinfo}
    acts = []
    for o in model.by_class("People"):
        s = sched.get(o.get(9).upper(), {}) if len(o.fields) > 9 else {}   # activity level schedule
        if s.get("max") is not None:
            acts.append(s["max"])
    if acts:
        L["activity_w_per_person_max"] = max(acts)
    # infiltration (eio nominal statistics)
    inf = facts["infiltration"]
    stats = eio.get("ZoneInfiltration Airflow Stats Nominal", [])
    flows, ach_vol = 0.0, 0.0
    per_zone = {}
    for r in stats:
        if len(r) >= 8:
            zname = r[2]
            q = _f(r[5]) or 0.0
            flows += q * mult.get(zname, 1)
            per_zone[zname] = {"design_flow_m3s": q, "ach": _f(r[8]) if len(r) > 8 else None,
                               "flow_per_ext_area": _f(r[7]),
                               "coef_a": _f(r[9]) if len(r) > 9 else None, "coef_b": _f(r[10]) if len(r) > 10 else None,
                               "coef_c": _f(r[11]) if len(r) > 11 else None, "coef_d": _f(r[12]) if len(r) > 12 else None}
    inf["design_flow_m3s_total"] = flows
    inf["zones"] = per_zone
    vol_c = sum((zinfo[z]["volume"] or 0) * zinfo[z]["multiplier"] for z in per_zone if z in zinfo)
    if vol_c:
        inf["ach_design_weighted"] = 3600 * flows / vol_c
    cond_zones = [z for z in per_zone if z in zinfo and zinfo[z]["conditioned"]]
    if cond_zones:
        q = sum(per_zone[z]["design_flow_m3s"] * zinfo[z]["multiplier"] for z in cond_zones)
        v = sum((zinfo[z]["volume"] or 0) * zinfo[z]["multiplier"] for z in cond_zones)
        inf["ach_design_conditioned"] = 3600 * q / v if v else None
    # results
    R = facts["results"]
    site = sql.table("AnnualBuildingUtilityPerformanceSummary", "Site and Source Energy")
    R["site_energy_gj"] = _f(site.get("Total Site Energy", {}).get("Total Energy [GJ]"))
    R["eui_mj_m2"] = _f(site.get("Total Site Energy", {}).get("Energy Per Total Building Area [MJ/m2]"))
    R["eui_mj_m2_conditioned"] = _f(site.get("Total Site Energy", {}).get("Energy Per Conditioned Building Area [MJ/m2]"))
    eu = sql.table("AnnualBuildingUtilityPerformanceSummary", "End Uses")
    enduses = {}
    for row, cols in eu.items():
        if not row:
            continue
        enduses[row] = {c.split(" [")[0]: _f(v) for c, v in cols.items() if c.endswith("[GJ]") and (_f(v) or 0) != 0}
    R["end_uses_gj"] = enduses
    R["heating_gj"] = sum(enduses.get("Heating", {}).values())
    R["cooling_gj"] = sum(enduses.get("Cooling", {}).values())
    R["fans_gj"] = sum(enduses.get("Fans", {}).values())
    tot = enduses.get("Total End Uses", {})
    R["electricity_gj"] = tot.get("Electricity", 0.0)
    R["natural_gas_gj"] = tot.get("Natural Gas", 0.0)
    R["district_heating_gj"] = sum(v for k, v in tot.items() if k.startswith("District Heating"))
    R["district_cooling_gj"] = tot.get("District Cooling", 0.0)
    unmet = sql.table("SystemSummary", "Time Setpoint Not Met").get("Facility", {})
    R["unmet_heating_h"] = _f(unmet.get("During Heating [hr]"))
    R["unmet_cooling_h"] = _f(unmet.get("During Cooling [hr]"))
    R["unmet_occupied_heating_h"] = _f(unmet.get("During Occupied Heating [hr]"))
    R["unmet_occupied_cooling_h"] = _f(unmet.get("During Occupied Cooling [hr]"))
    hs = defaultdict(float)
    for zname, lt, des in sql.rows("select ZoneName, LoadType, CalcDesLoad from ZoneSizes"):
        hs[lt] += (_f(des) or 0) * mult.get(zname, 1)
    R["design_heating_load_w"] = hs.get("Heating")
    R["design_cooling_load_w"] = hs.get("Cooling")
    R["interior_lighting_gj"] = sum(enduses.get("Interior Lighting", {}).values())
    R["interior_equipment_gj"] = sum(enduses.get("Interior Equipment", {}).values())
    R["water_systems_gj"] = sum(enduses.get("Water Systems", {}).values())
    R["internal_electric_gj"] = R["interior_lighting_gj"] + R["interior_equipment_gj"]
    gains = sql.rows("select sum(d.Value) from ReportData d join ReportDataDictionary k on "
                     "d.ReportDataDictionaryIndex = k.ReportDataDictionaryIndex join Time t on d.TimeIndex = t.TimeIndex "
                     "where k.Name = 'Zone Total Internal Total Heating Energy' and (t.WarmupFlag = 0 or t.WarmupFlag is null) and "
                     "k.ReportingFrequency like 'Run Period%'")
    R["internal_gains_gj"] = (gains[0][0] / 1e9) if gains and gains[0][0] is not None else None
    if L.get("lighting_w_total"):
        R["lighting_eflh_h"] = R["interior_lighting_gj"] * 1e9 / 3600.0 / L["lighting_w_total"]
    if L.get("equipment_w_total"):
        R["equipment_eflh_h"] = R["interior_equipment_gj"] * 1e9 / 3600.0 / L["equipment_w_total"]
    if tfa and R.get("heating_gj") is not None:
        R["heating_mj_m2"] = 1000 * R["heating_gj"] / tfa
        R["cooling_mj_m2"] = 1000 * R["cooling_gj"] / tfa
    return facts


def get_path(facts: dict, path: str):
    """Resolve a dotted path. ``zones[*living*]`` selects dict entries by glob (case-insensitive)
    and returns a list of values."""
    import fnmatch
    cur = [facts]
    multi = False
    for part in re.findall(r"[^.\[\]]+(?:\[[^\]]*\])?", path):
        m = re.match(r"([^\[]+)(?:\[([^\]]*)\])?$", part)
        key, sel = m.group(1), m.group(2)
        nxt = []
        for c in cur:
            if not isinstance(c, dict):
                continue
            v = c.get(key)
            if v is None:
                # case-insensitive key match
                for k2 in c:
                    if isinstance(k2, str) and k2.lower() == key.lower():
                        v = c[k2]
                        break
            if v is None:
                continue
            if sel is not None:
                multi = True
                if isinstance(v, dict):
                    nxt += [vv for kk, vv in v.items() if fnmatch.fnmatch(str(kk).upper(), sel.upper())]
            else:
                nxt.append(v)
        cur = nxt
    if multi:
        return cur
    return cur[0] if cur else None
