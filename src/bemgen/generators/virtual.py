"""Source S3: virtual buildings whose ground truth is known by construction.

A :class:`Program` is a compact, semantic description of a building (form,
envelope, loads, schedules, controls, HVAC). :func:`build_idf` turns it into an
EnergyPlus model; :mod:`bemgen.generators.render` turns the same program into
the documents a modeller would receive; :func:`program_facts` writes the fact
sheet. Because all three come from one program, the reference, the documents
and the fact sheet cannot disagree, and probes of domain expertise (units,
layer-to-U conversion, orientation, party walls, code lookups, schedules,
precedence rules, distractors, HVAC vocabulary) can be placed on purpose.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field, asdict
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..idf import IDF
from ..schema import get_schema

# ------------------------------------------------------------------ libraries
# (name, thickness m, conductivity W/mK, density kg/m3, specific heat J/kgK)
MATERIALS = {
    "stucco": ("Stucco 25mm", 0.025, 0.72, 1856, 840),
    "brick": ("Face brick 100mm", 0.1, 0.89, 1920, 790),
    "cmu": ("Concrete block 200mm", 0.2, 1.11, 800, 920),
    "concrete": ("Cast concrete 200mm", 0.2, 1.73, 2243, 837),
    "osb": ("OSB sheathing 12mm", 0.0127, 0.12, 640, 1210),
    "plywood": ("Plywood 16mm", 0.0159, 0.12, 544, 1210),
    "batt_r13": ("Batt insulation 89mm", 0.089, 0.045, 12, 960),
    "batt_r19": ("Batt insulation 140mm", 0.14, 0.045, 12, 960),
    "xps_50": ("XPS board 50mm", 0.05, 0.029, 35, 1400),
    "xps_75": ("XPS board 75mm", 0.075, 0.029, 35, 1400),
    "polyiso_100": ("Polyiso board 100mm", 0.1, 0.024, 30, 1470),
    "polyiso_150": ("Polyiso board 150mm", 0.15, 0.024, 30, 1470),
    "mineral_wool_100": ("Mineral wool 100mm", 0.1, 0.036, 64, 840),
    "gypsum": ("Gypsum board 13mm", 0.0127, 0.16, 800, 1090),
    "roof_membrane": ("Roof membrane 10mm", 0.0095, 0.16, 1121, 1460),
    "metal_deck": ("Metal deck 1.5mm", 0.0015, 45.0, 7680, 418),
    "carpet": ("Carpet pad 12mm", 0.0127, 0.06, 288, 1380),
}
ASSEMBLIES = {
    "wall_woodframe": ["stucco", "osb", "batt_r13", "gypsum"],
    "wall_woodframe_ci": ["stucco", "xps_50", "osb", "batt_r19", "gypsum"],
    "wall_cmu_ci": ["stucco", "xps_50", "cmu", "gypsum"],
    "wall_brick_steel": ["brick", "mineral_wool_100", "gypsum"],
    "wall_concrete_ci": ["stucco", "xps_75", "concrete", "gypsum"],
    "roof_insulated_deck": ["roof_membrane", "polyiso_100", "metal_deck"],
    "roof_insulated_deck_hi": ["roof_membrane", "polyiso_150", "metal_deck"],
    "roof_wood": ["roof_membrane", "plywood", "batt_r19", "gypsum"],
    "slab": ["concrete", "carpet"],
    "interior_floor": ["concrete"],
    "interior_wall": ["gypsum", "gypsum"],
}
FILM_IN = {"wall": 0.12, "roof": 0.10, "floor": 0.16}      # m2K/W (ISO 6946-like, for documents)
FILM_OUT = 0.04

SPACE_TYPES = {
    "office": {"lpd": (6.5, 10.8), "epd": (6.0, 12.0), "occ": (4.0, 6.5), "activity": 120,
               "hours": {"weekday": (7, 18), "saturday": (8, 12), "sunday": None}},
    "retail": {"lpd": (9.0, 15.0), "epd": (2.0, 5.0), "occ": (8.0, 16.0), "activity": 130,
               "hours": {"weekday": (9, 21), "saturday": (9, 21), "sunday": (10, 18)}},
    "school": {"lpd": (7.0, 10.0), "epd": (4.0, 8.0), "occ": (18.0, 25.0), "activity": 110,
               "hours": {"weekday": (7, 16), "saturday": None, "sunday": None}},
    "house": {"lpd": (3.0, 6.0), "epd": (3.0, 6.0), "occ": None, "activity": 110, "hours": "residential"},
    "apartment": {"lpd": (3.0, 6.0), "epd": (3.0, 7.0), "occ": None, "activity": 110, "hours": "residential"},
}


@dataclass
class City:
    name: str
    state: str
    epw: str
    ddy: str
    climate_zone: str
    lat: float = 0.0
    lon: float = 0.0
    tz: float = 0.0
    elev: float = 0.0
    station: str = ""


@dataclass
class Program:
    id: str
    btype: str
    city: City
    shape: str = "rect"                 # rect | L
    length: float = 30.0                # x extent (m), building coordinates
    width: float = 20.0                 # y extent (m)
    wing_length: float = 0.0            # L shape: wing extends north from the west part
    wing_width: float = 0.0
    n_floors: int = 1
    f2f: float = 3.5
    north_axis: float = 0.0
    zoning: str = "per_floor"           # per_floor | core_perimeter
    perimeter_depth: float = 4.57
    wwr: Dict[str, float] = field(default_factory=lambda: {"S": 0.3, "E": 0.2, "N": 0.2, "W": 0.2})
    sill: float = 0.9
    wall: str = "wall_woodframe"
    roof: str = "roof_insulated_deck"
    win_u: float = 2.0
    win_shgc: float = 0.35
    win_vt: float = 0.5
    lpd: float = 8.0
    epd: float = 8.0
    occ_density: Optional[float] = 5.0  # people per 100 m2 (non-residential)
    people: Optional[float] = None      # total people (residential)
    activity: float = 120.0
    hours: dict = field(default_factory=dict)
    infiltration_ach: float = 0.3
    hvac: str = "psz_hp"                # ideal | ptac | pthp | psz_hp | none
    heat_sp: float = 21.0
    cool_sp: float = 24.0
    heat_setback: Optional[float] = None
    cool_setup: Optional[float] = None
    cop_cool: float = 3.5
    cop_heat: float = 3.2
    party_walls: List[str] = field(default_factory=list)   # facades (building coords) that are adiabatic
    garage: Optional[Dict] = None        # {"side": "W", "depth": 6.5}: attached unconditioned zone
    doors: List[str] = field(default_factory=lambda: ["S"])
    year: int = 2023
    probes: List[str] = field(default_factory=list)
    style: str = "narrative"
    units: str = "SI"
    info_level: str = "complete"         # complete | partial
    omitted: List[str] = field(default_factory=list)   # facets not stated in the documents
    notes: Dict[str, str] = field(default_factory=dict)

    def to_dict(self):
        d = asdict(self)
        return d

    # ---------------------------------------------------------- derived values
    def footprint(self) -> List[Tuple[float, float]]:
        L, W = self.length, self.width
        if self.shape == "L":
            wl, ww = self.wing_length, self.wing_width
            return [(0, 0), (L, 0), (L, W), (wl, W), (wl, W + ww), (0, W + ww)]
        return [(0, 0), (L, 0), (L, W), (0, W)]

    def footprint_area(self) -> float:
        return polygon_area(self.footprint())

    def floor_area(self) -> float:
        return self.footprint_area() * self.n_floors

    def garage_area(self) -> float:
        if not self.garage:
            return 0.0
        return self.garage["depth"] * (self.width if self.garage["side"] in ("W", "E") else self.length)

    def total_people(self) -> float:
        if self.people is not None:
            return self.people
        return round(self.floor_area() * (self.occ_density or 0) / 100.0, 2)

    def facade_azimuth(self, facade: str) -> float:
        base = {"N": 0.0, "E": 90.0, "S": 180.0, "W": 270.0}[facade]
        return (base + self.north_axis) % 360.0

    def true_facade(self, facade: str) -> str:
        az = self.facade_azimuth(facade)
        return ["N", "E", "S", "W"][int(((az + 45) % 360) // 90)]


def polygon_area(pts) -> float:
    a = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2.0


def assembly_r(name: str, kind: str, films: bool = True) -> float:
    r = sum(MATERIALS[m][1] / MATERIALS[m][2] for m in ASSEMBLIES[name])
    if films:
        r += FILM_IN[kind] + FILM_OUT
    return r


# ------------------------------------------------------------------ weather
def read_epw_header(epw: Path) -> dict:
    loc = Path(epw).read_text(errors="replace").splitlines()[0].split(",")
    return {"city": loc[1], "state": loc[2], "lat": float(loc[6]), "lon": float(loc[7]), "tz": float(loc[8]),
            "elev": float(loc[9]), "station": loc[5]}


def epw_monthly_means(epw: Path) -> List[float]:
    sums = [0.0] * 12
    cnt = [0] * 12
    for ln in Path(epw).read_text(errors="replace").splitlines()[8:]:
        p = ln.split(",")
        try:
            m = int(p[1]) - 1
            sums[m] += float(p[6])
            cnt[m] += 1
        except (ValueError, IndexError):
            continue
    return [s / c if c else 15.0 for s, c in zip(sums, cnt)]


def design_days(ddy: Path) -> List[List[str]]:
    """Pick the 99.6 % heating and 0.4 % cooling design days from a DDY file."""
    idf = IDF.load(ddy)
    dds = idf.by_class("SizingPeriod:DesignDay")
    heat = next((o for o in dds if "99.6%" in o.name and "Htg" in o.name and "Condns DB" in o.name
                 and "Wind" not in o.name and "Humidification" not in o.name), None)
    cool = next((o for o in dds if ".4%" in o.name and "Clg" in o.name and "Condns DB=>MWB" in o.name), None)
    if heat is None or cool is None:
        heat = heat or next(o for o in dds if "Htg" in o.name)
        cool = cool or next(o for o in dds if "Clg" in o.name)
    return [heat.fields, cool.fields]


# ------------------------------------------------------------------ builder
class Builder:
    def __init__(self, version="23.1"):
        self.S = get_schema(version)
        self.idf = IDF()

    def add(self, cls: str, ext: Optional[list] = None, comment: str = "", **kw):
        fields = self.S._layout(cls)[1]
        vals = [""] * len(fields)
        for k, v in kw.items():
            if k not in fields:
                raise KeyError(f"{cls} has no field {k}")
            vals[fields.index(k)] = v
        if ext is not None and not self.S._layout(cls)[2] and "vertex_1_x_coordinate" in fields:
            i0 = fields.index("vertex_1_x_coordinate")
            for j, v in enumerate(ext):
                vals[i0 + j] = v
            ext = None
        if ext is None:
            while vals and vals[-1] == "":
                vals.pop()
        else:
            vals += list(ext)
        return self.idf.add(cls, vals, comment)


def _wall_vertices(a, b, z0, z1):
    return [(a[0], a[1], z1), (a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1)]


def _flat(vs):
    out = []
    for v in vs:
        out += [round(c, 4) for c in v]
    return out


def _zones_for_floor(p: Program) -> List[Tuple[str, List[Tuple[float, float]]]]:
    fp = p.footprint()
    if p.zoning == "core_perimeter" and p.shape == "rect":
        L, W, d = p.length, p.width, p.perimeter_depth
        return [("Perimeter_S", [(0, 0), (L, 0), (L - d, d), (d, d)]),
                ("Perimeter_E", [(L, 0), (L, W), (L - d, W - d), (L - d, d)]),
                ("Perimeter_N", [(L, W), (0, W), (d, W - d), (L - d, W - d)]),
                ("Perimeter_W", [(0, W), (0, 0), (d, d), (d, W - d)]),
                ("Core", [(d, d), (L - d, d), (L - d, W - d), (d, W - d)])]
    return [("Zone", fp)]


def _edge_facade(a, b) -> str:
    dx, dy = b[0] - a[0], b[1] - a[1]
    # outward normal of a CCW edge is (dy, -dx)
    nx, ny = dy, -dx
    if abs(nx) >= abs(ny):
        return "E" if nx > 0 else "W"
    return "N" if ny > 0 else "S"


def schedule_profile(p: Program):
    """Hourly fractions (occupancy, lighting, equipment) for weekday, saturday, sunday."""
    if p.hours == "residential" or p.btype in ("house", "apartment"):
        occ_wd = [1.0] * 7 + [0.5, 0.3] + [0.2] * 8 + [0.6, 0.8, 0.9, 0.9, 0.9, 1.0, 1.0]
        occ_we = [1.0] * 8 + [0.8] * 14 + [1.0, 1.0]
        lig_wd = [0.05] * 6 + [0.3, 0.4, 0.2] + [0.1] * 8 + [0.4, 0.6, 0.8, 0.8, 0.6, 0.3, 0.1]
        lig_we = [0.05] * 7 + [0.3, 0.3] + [0.2] * 8 + [0.5, 0.7, 0.8, 0.8, 0.6, 0.3, 0.1]
        eq_wd = [0.3] * 6 + [0.5, 0.6, 0.4] + [0.3] * 8 + [0.6, 0.8, 0.8, 0.7, 0.6, 0.5, 0.4]
        eq_we = [0.3] * 7 + [0.6] * 15 + [0.5, 0.4]
        return {"weekday": (occ_wd, lig_wd, eq_wd), "saturday": (occ_we, lig_we, eq_we), "sunday": (occ_we, lig_we, eq_we)}
    out = {}
    for day in ("weekday", "saturday", "sunday"):
        hrs = p.hours.get(day)
        occ, lig, eq = [], [], []
        for h in range(24):
            on = hrs is not None and hrs[0] <= h < hrs[1]
            occ.append(0.95 if on else 0.0)
            lig.append(0.9 if on else 0.05)
            eq.append(0.9 if on else 0.3)
        out[day] = (occ, lig, eq)
    return out


def _compact(name, limits, prof, which):
    """Schedule:Compact fields from hourly fractions (merges equal consecutive hours)."""
    f = [name, limits, "Through: 12/31"]
    for label, day in (("For: Weekdays SummerDesignDay WinterDesignDay", "weekday"), ("For: Saturday", "saturday"),
                       ("For: Sunday Holidays AllOtherDays", "sunday")):
        vals = prof[day][which]
        f.append(label)
        for h in range(24):
            if h == 23 or vals[h + 1] != vals[h]:
                f += [f"Until: {h + 1:02d}:00", f"{vals[h]:g}"]
    return f


def expected_eflh(p: Program, which: int) -> float:
    """Equivalent full-load hours of a schedule over the run year (no holidays)."""
    prof = schedule_profile(p)
    d0 = date(p.year, 1, 1)
    tot = 0.0
    for i in range((date(p.year + 1, 1, 1) - d0).days):
        wd = (d0 + timedelta(days=i)).weekday()
        day = "weekday" if wd < 5 else ("saturday" if wd == 5 else "sunday")
        tot += sum(prof[day][which])
    return tot


def build_idf(p: Program, weather_dir: Path) -> IDF:
    B = Builder()
    epw = Path(weather_dir) / p.city.epw
    hdr = read_epw_header(epw)
    B.add("Version", version_identifier="23.1")
    B.add("SimulationControl", do_zone_sizing_calculation="Yes", do_system_sizing_calculation="Yes",
          do_plant_sizing_calculation="No", run_simulation_for_sizing_periods="No",
          run_simulation_for_weather_file_run_periods="Yes")
    B.add("Building", name=p.id, north_axis=round(p.north_axis, 2), terrain="Suburbs",
          loads_convergence_tolerance_value=0.04, temperature_convergence_tolerance_value=0.4,
          solar_distribution="FullExterior", maximum_number_of_warmup_days=25, minimum_number_of_warmup_days=6)
    B.add("Timestep", number_of_timesteps_per_hour=4)
    B.add("Sizing:Parameters", heating_sizing_factor=1.25, cooling_sizing_factor=1.15)
    B.add("Site:Location", name=f"{p.city.name} {p.city.state}", latitude=hdr["lat"], longitude=hdr["lon"],
          time_zone=hdr["tz"], elevation=hdr["elev"])
    mm = epw_monthly_means(epw)
    gt = [round(min(26.0, max(10.0, 0.5 * t + 9.0)), 1) for t in mm]
    B.idf.add("Site:GroundTemperature:BuildingSurface", gt, "! source: assumed (half the monthly mean air temperature plus 9 C)")
    for dd in design_days(Path(weather_dir) / p.city.ddy):
        B.idf.add("SizingPeriod:DesignDay", dd)
    B.add("RunPeriod", name="Annual", begin_month=1, begin_day_of_month=1, begin_year=p.year, end_month=12,
          end_day_of_month=31, end_year=p.year, use_weather_file_holidays_and_special_days="No",
          use_weather_file_daylight_saving_period="No", apply_weekend_holiday_rule="No",
          use_weather_file_rain_indicators="Yes", use_weather_file_snow_indicators="Yes")
    B.add("GlobalGeometryRules", starting_vertex_position="UpperLeftCorner", vertex_entry_direction="Counterclockwise",
          coordinate_system="Relative")
    # schedules
    B.add("ScheduleTypeLimits", name="Fraction", lower_limit_value=0, upper_limit_value=1, numeric_type="Continuous")
    B.add("ScheduleTypeLimits", name="Temperature", numeric_type="Continuous")
    B.add("ScheduleTypeLimits", name="Any Number")
    prof = schedule_profile(p)
    for nm, which in (("Occupancy", 0), ("Lighting", 1), ("Equipment", 2)):
        B.idf.add("Schedule:Compact", _compact(f"{nm} Schedule", "Fraction", prof, which))
    B.idf.add("Schedule:Compact", ["Activity Schedule", "Any Number", "Through: 12/31", "For: AllDays", "Until: 24:00", f"{p.activity:g}"])
    B.idf.add("Schedule:Compact", ["Always On", "Fraction", "Through: 12/31", "For: AllDays", "Until: 24:00", "1"])
    # thermostat schedules (setback follows occupied hours of the occupancy profile)
    def sp_sched(name, occ_val, unocc_val):
        if unocc_val is None:
            return ["Through: 12/31", "For: AllDays", "Until: 24:00", f"{occ_val:g}"]
        f = ["Through: 12/31"]
        for label, day in (("For: Weekdays", "weekday"), ("For: Saturday", "saturday"),
                           ("For: SummerDesignDay WinterDesignDay", None),
                           ("For: Sunday Holidays AllOtherDays", "sunday")):
            f.append(label)
            if day is None:
                f += ["Until: 24:00", f"{occ_val:g}"]
                continue
            occ = prof[day][0]      # recovery starts two hours before occupancy (simple optimum start)
            vals = [occ_val if max(occ[h:h + 3]) > 0.1 else unocc_val for h in range(24)]
            for h in range(24):
                if h == 23 or vals[h + 1] != vals[h]:
                    f += [f"Until: {h + 1:02d}:00", f"{vals[h]:g}"]
        return f
    B.idf.add("Schedule:Compact", ["Heating Setpoint", "Temperature"] + sp_sched("h", p.heat_sp, p.heat_setback))
    B.idf.add("Schedule:Compact", ["Cooling Setpoint", "Temperature"] + sp_sched("c", p.cool_sp, p.cool_setup))
    # materials and constructions
    used = set()
    for a in (p.wall, p.roof, "slab", "interior_floor", "interior_wall"):
        for m in ASSEMBLIES[a]:
            used.add(m)
    for m in sorted(used):
        nm, t, k, rho, cp = MATERIALS[m]
        B.add("Material", name=nm, roughness="MediumRough", thickness=t, conductivity=k, density=rho,
              specific_heat=cp, thermal_absorptance=0.9, solar_absorptance=0.6, visible_absorptance=0.6)
    def cons(name, asm, reverse=False):
        layers = [MATERIALS[m][0] for m in ASSEMBLIES[asm]]
        if reverse:
            layers = layers[::-1]
        B.idf.add("Construction", [name] + layers)
    cons("Exterior Wall", p.wall)
    cons("Roof", p.roof)
    cons("Slab", "slab")
    cons("Interior Floor", "interior_floor")
    cons("Interior Ceiling", "interior_floor", True)
    cons("Interior Wall", "interior_wall")
    B.add("WindowMaterial:SimpleGlazingSystem", name="Glazing", u_factor=p.win_u, solar_heat_gain_coefficient=p.win_shgc,
          visible_transmittance=p.win_vt)
    B.idf.add("Construction", ["Window", "Glazing"])
    B.add("Material", name="Door panel", roughness="MediumSmooth", thickness=0.045, conductivity=0.15, density=600,
          specific_heat=1630, thermal_absorptance=0.9, solar_absorptance=0.6, visible_absorptance=0.6)
    B.idf.add("Construction", ["Exterior Door", "Door panel"])
    # geometry: zones per floor, plus optional garage
    zones = []          # (name, z0, z1, polygon, conditioned)
    for k in range(p.n_floors):
        z0, z1 = k * p.f2f, (k + 1) * p.f2f
        for zn, poly in _zones_for_floor(p):
            zones.append((f"F{k + 1}_{zn}", z0, z1, poly, True, k))
    if p.garage:
        g = p.garage
        if g["side"] == "W":
            poly = [(-g["depth"], 0), (0, 0), (0, p.width), (-g["depth"], p.width)]
        else:
            poly = [(p.length, 0), (p.length + g["depth"], 0), (p.length + g["depth"], p.width), (p.length, p.width)]
        zones.append(("Garage", 0.0, p.f2f, poly, False, 0))
    for zn, z0, z1, poly, cond, k in zones:
        B.add("Zone", name=zn, direction_of_relative_north=0, x_origin=0, y_origin=0, z_origin=0, type=1, multiplier=1,
              ceiling_height="autocalculate", volume="autocalculate", floor_area="autocalculate",
              part_of_total_floor_area="Yes" if cond else "No")
    # edges shared between zones on the same level -> interzone walls
    edge_owner = {}
    for zn, z0, z1, poly, cond, k in zones:
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]
            edge_owner[(k, _r(a), _r(b))] = zn
    door_done = set()
    nwin = 0
    for zn, z0, z1, poly, cond, k in zones:
        top = k == p.n_floors - 1 or zn == "Garage"
        ground = k == 0
        # floor
        fl = [(x, y, z0) for x, y in reversed(poly)]
        if ground:
            B.add("BuildingSurface:Detailed", ext=_flat(fl), name=f"{zn}_Floor", surface_type="Floor", construction_name="Slab",
                  zone_name=zn, outside_boundary_condition="Ground", sun_exposure="NoSun", wind_exposure="NoWind",
                  view_factor_to_ground="autocalculate", number_of_vertices=len(fl))
        else:
            B.add("BuildingSurface:Detailed", ext=_flat(fl), name=f"{zn}_Floor", surface_type="Floor",
                  construction_name="Interior Floor", zone_name=zn, outside_boundary_condition="Surface",
                  outside_boundary_condition_object=f"{zn.replace(f'F{k + 1}_', f'F{k}_')}_Ceiling", sun_exposure="NoSun",
                  wind_exposure="NoWind", view_factor_to_ground="autocalculate", number_of_vertices=len(fl))
        cl = [(x, y, z1) for x, y in poly]
        if top:
            B.add("BuildingSurface:Detailed", ext=_flat(cl), name=f"{zn}_Roof", surface_type="Roof", construction_name="Roof",
                  zone_name=zn, outside_boundary_condition="Outdoors", sun_exposure="SunExposed", wind_exposure="WindExposed",
                  view_factor_to_ground="autocalculate", number_of_vertices=len(cl))
        else:
            B.add("BuildingSurface:Detailed", ext=_flat(cl), name=f"{zn}_Ceiling", surface_type="Ceiling",
                  construction_name="Interior Ceiling", zone_name=zn, outside_boundary_condition="Surface",
                  outside_boundary_condition_object=f"{zn.replace(f'F{k + 1}_', f'F{k + 2}_')}_Floor", sun_exposure="NoSun",
                  wind_exposure="NoWind", view_factor_to_ground="autocalculate", number_of_vertices=len(cl))
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]
            wname = f"{zn}_Wall_{i + 1}"
            vs = _wall_vertices(a, b, z0, z1)
            other = edge_owner.get((k, _r(b), _r(a)))
            if other is not None:
                oi = _edge_index(zones, other, b, a)
                B.add("BuildingSurface:Detailed", ext=_flat(vs), name=wname, surface_type="Wall",
                      construction_name="Interior Wall", zone_name=zn, outside_boundary_condition="Surface",
                      outside_boundary_condition_object=f"{other}_Wall_{oi + 1}", sun_exposure="NoSun", wind_exposure="NoWind",
                      view_factor_to_ground="autocalculate", number_of_vertices=4)
                continue
            fac = _edge_facade(a, b)
            if zn != "Garage" and fac in p.party_walls:
                B.add("BuildingSurface:Detailed", ext=_flat(vs), name=wname, surface_type="Wall",
                      construction_name="Exterior Wall", zone_name=zn, outside_boundary_condition="Adiabatic",
                      sun_exposure="NoSun", wind_exposure="NoWind", view_factor_to_ground="autocalculate", number_of_vertices=4)
                continue
            B.add("BuildingSurface:Detailed", ext=_flat(vs), name=wname, surface_type="Wall", construction_name="Exterior Wall",
                  zone_name=zn, outside_boundary_condition="Outdoors", sun_exposure="SunExposed", wind_exposure="WindExposed",
                  view_factor_to_ground="autocalculate", number_of_vertices=4)
            if zn == "Garage":
                continue
            seg = math.hypot(b[0] - a[0], b[1] - a[1])
            ux, uy = (b[0] - a[0]) / seg, (b[1] - a[1]) / seg
            s0, s1 = 0.3, seg - 0.3
            if fac in p.doors and k == 0 and (fac not in door_done):
                door_done.add(fac)
                dw, dh = 0.91, 2.13
                ds = 0.5
                dv = _wall_vertices((a[0] + ux * ds, a[1] + uy * ds), (a[0] + ux * (ds + dw), a[1] + uy * (ds + dw)), z0, z0 + dh)
                B.add("FenestrationSurface:Detailed", ext=_flat(dv), name=f"{wname}_Door", surface_type="Door",
                      construction_name="Exterior Door", building_surface_name=wname, view_factor_to_ground="autocalculate",
                      multiplier=1, number_of_vertices=4)
                s0 = ds + dw + 0.3
            frac = p.wwr.get(fac, 0.0)
            if frac <= 0:
                continue
            area = frac * seg * p.f2f
            avail = max(0.2, s1 - s0)
            h = min(p.f2f - p.sill - 0.3, max(1.0, area / avail))
            w = min(avail, area / h)
            if w * h < area * 0.98:          # tall enough? raise the head, lower the sill if needed
                h = min(p.f2f - 0.35, area / avail)
                w = min(avail, area / h)
            sill = min(p.sill, p.f2f - 0.3 - h)
            mid = s0 + (avail - w) / 2
            wv = _wall_vertices((a[0] + ux * mid, a[1] + uy * mid), (a[0] + ux * (mid + w), a[1] + uy * (mid + w)),
                                z0 + sill, z0 + sill + h)
            nwin += 1
            B.add("FenestrationSurface:Detailed", ext=_flat(wv), name=f"{wname}_Window", surface_type="Window",
                  construction_name="Window", building_surface_name=wname, view_factor_to_ground="autocalculate",
                  multiplier=1, number_of_vertices=4)
    # loads
    cond_zones = [z for z in zones if z[4]]
    tot_area = sum(polygon_area(z[3]) for z in cond_zones)
    for zn, z0, z1, poly, cond, k in cond_zones:
        a = polygon_area(poly)
        npeople = p.total_people() * a / tot_area
        B.add("People", name=f"{zn} People", zone_or_zonelist_or_space_or_spacelist_name=zn,
              number_of_people_schedule_name="Occupancy Schedule", number_of_people_calculation_method="People",
              number_of_people=round(npeople, 4), fraction_radiant=0.3, sensible_heat_fraction="autocalculate",
              activity_level_schedule_name="Activity Schedule")
        B.add("Lights", name=f"{zn} Lights", zone_or_zonelist_or_space_or_spacelist_name=zn, schedule_name="Lighting Schedule",
              design_level_calculation_method="Watts/Area", watts_per_zone_floor_area=p.lpd, return_air_fraction=0,
              fraction_radiant=0.42, fraction_visible=0.18)
        B.add("ElectricEquipment", name=f"{zn} Equipment", zone_or_zonelist_or_space_or_spacelist_name=zn,
              schedule_name="Equipment Schedule", design_level_calculation_method="Watts/Area",
              watts_per_zone_floor_area=p.epd, fraction_latent=0, fraction_radiant=0.5, fraction_lost=0)
    for zn, z0, z1, poly, cond, k in zones:
        B.add("ZoneInfiltration:DesignFlowRate", name=f"{zn} Infiltration", zone_or_zonelist_or_space_or_spacelist_name=zn,
              schedule_name="Always On", design_flow_rate_calculation_method="AirChanges/Hour",
              air_changes_per_hour=p.infiltration_ach if cond else 1.0, constant_term_coefficient=1,
              temperature_term_coefficient=0, velocity_term_coefficient=0, velocity_squared_term_coefficient=0)
    # HVAC
    if p.hvac != "none":
        B.add("HVACTemplate:Thermostat", name="Thermostat", heating_setpoint_schedule_name="Heating Setpoint",
              cooling_setpoint_schedule_name="Cooling Setpoint")
        for zn, z0, z1, poly, cond, k in cond_zones:
            if p.hvac == "ideal":
                B.add("HVACTemplate:Zone:IdealLoadsAirSystem", zone_name=zn, template_thermostat_name="Thermostat")
            elif p.hvac == "ptac":
                B.add("HVACTemplate:Zone:PTAC", zone_name=zn, template_thermostat_name="Thermostat",
                      cooling_supply_air_flow_rate="autosize", heating_supply_air_flow_rate="autosize",
                      outdoor_air_method="Flow/Person", outdoor_air_flow_rate_per_person=0.00236,
                      supply_fan_operating_mode_schedule_name="", supply_fan_placement="DrawThrough",
                      supply_fan_total_efficiency=0.7, supply_fan_delta_pressure=75, supply_fan_motor_efficiency=0.9,
                      cooling_coil_type="SingleSpeedDX", cooling_coil_gross_rated_total_capacity="autosize",
                      cooling_coil_gross_rated_sensible_heat_ratio="autosize", cooling_coil_gross_rated_cooling_cop=p.cop_cool,
                      heating_coil_type="Electric", heating_coil_capacity="autosize")
            elif p.hvac == "pthp":
                B.add("HVACTemplate:Zone:PTHP", zone_name=zn, template_thermostat_name="Thermostat",
                      cooling_supply_air_flow_rate="autosize", heating_supply_air_flow_rate="autosize",
                      outdoor_air_method="Flow/Person", outdoor_air_flow_rate_per_person=0.00236,
                      supply_fan_placement="DrawThrough", supply_fan_total_efficiency=0.7, supply_fan_delta_pressure=75,
                      supply_fan_motor_efficiency=0.9, cooling_coil_type="SingleSpeedDX",
                      cooling_coil_gross_rated_total_capacity="autosize", cooling_coil_gross_rated_sensible_heat_ratio="autosize",
                      cooling_coil_gross_rated_cop=p.cop_cool, heat_pump_heating_coil_type="SingleSpeedDXHeatPump",
                      heat_pump_heating_coil_gross_rated_capacity="autosize", heat_pump_heating_coil_gross_rated_cop=p.cop_heat,
                      heat_pump_heating_minimum_outdoor_dry_bulb_temperature=-8, supplemental_heating_coil_type="Electric",
                      supplemental_heating_coil_capacity="autosize")
            elif p.hvac == "psz_hp":
                sysname = f"{zn} PSZ-HP"
                B.add("HVACTemplate:Zone:Unitary", zone_name=zn, template_unitary_system_name=sysname,
                      template_thermostat_name="Thermostat", supply_air_maximum_flow_rate="autosize",
                      outdoor_air_method="Flow/Person", outdoor_air_flow_rate_per_person=0.00236)
                B.add("HVACTemplate:System:UnitaryHeatPump:AirToAir", name=sysname, control_zone_or_thermostat_location_name=zn,
                      cooling_supply_air_flow_rate="autosize", heating_supply_air_flow_rate="autosize",
                      supply_fan_placement="BlowThrough", supply_fan_total_efficiency=0.6, supply_fan_delta_pressure=500,
                      supply_fan_motor_efficiency=0.9, cooling_coil_type="SingleSpeedDX", cooling_design_supply_air_temperature=12.8,
                      cooling_coil_gross_rated_total_capacity="autosize", cooling_coil_gross_rated_sensible_heat_ratio="autosize",
                      cooling_coil_gross_rated_cop=p.cop_cool, heat_pump_heating_coil_type="SingleSpeedDXHeatPump",
                      heating_design_supply_air_temperature=45, heat_pump_heating_coil_gross_rated_capacity="autosize",
                      heat_pump_heating_coil_rated_cop=p.cop_heat, heat_pump_heating_minimum_outdoor_dry_bulb_temperature=-8,
                      supplemental_heating_coil_type="Electric", supplemental_heating_coil_capacity="autosize",
                      maximum_outdoor_air_flow_rate="autosize", minimum_outdoor_air_flow_rate="autosize",
                      economizer_type="NoEconomizer")
    B.idf.add("Output:SQLite", ["SimpleAndTabular"])
    B.idf.add("Output:Table:SummaryReports", ["AllSummary"])
    B.idf.add("OutputControl:Table:Style", ["CommaAndHTML"])
    return B.idf


def _r(pt):
    return (round(pt[0], 4), round(pt[1], 4))


def _edge_index(zones, zname, a, b):
    for zn, z0, z1, poly, cond, k in zones:
        if zn != zname:
            continue
        for i in range(len(poly)):
            if _r(poly[i]) == _r(a) and _r(poly[(i + 1) % len(poly)]) == _r(b):
                return i
    raise ValueError("edge not found")
