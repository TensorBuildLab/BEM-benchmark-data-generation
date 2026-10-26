"""Generator tests: need the EnergyPlus schema (``bemgen setup``) and the weather files in work/weather.
They do not run EnergyPlus."""
from __future__ import annotations

import math
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
W = ROOT / "work" / "weather"

schema_missing = False
try:
    from bemgen.schema import get_schema
    get_schema()
except FileNotFoundError:
    schema_missing = True

pytestmark = pytest.mark.skipif(schema_missing or not W.is_dir(), reason="schema or weather files not available")


def _program(**kw):
    from bemgen.generators.s3 import city
    from bemgen.generators.virtual import Program, SPACE_TYPES
    base = dict(id="T", btype="office", city=city("Tucson", W), length=30, width=20, n_floors=2, f2f=3.6,
                zoning="core_perimeter", hours=SPACE_TYPES["office"]["hours"], hvac="psz_hp")
    base.update(kw)
    return Program(**base)


def test_builder_is_schema_valid():
    from bemgen.generators.virtual import build_idf
    from bemgen.schema import get_schema
    idf = build_idf(_program(party_walls=["W"], garage={"side": "E", "depth": 6.0}, north_axis=90), W)
    assert [i for i in get_schema().validate(idf) if i.severity == "error"] == []


def test_interzone_surfaces_are_paired():
    from bemgen.generators.virtual import build_idf
    idf = build_idf(_program(), W)
    surf = {o.name.upper(): o for o in idf.by_class("BuildingSurface:Detailed")}
    for o in surf.values():
        if o.get(5).upper() == "SURFACE":
            other = surf[o.get(6).upper()]
            assert other.get(6).upper() == o.name.upper()


def test_facade_walls_with_rotation_and_garage():
    from bemgen.generators.s3 import facade_walls
    p = _program(zoning="per_floor", wwr={"S": 0.4, "E": 0.0, "N": 0.2, "W": 0.0}, north_axis=90,
                 garage={"side": "E", "depth": 6.0})
    wall, win = facade_walls(p)
    # building south faces true west after a 90 degree rotation
    assert math.isclose(win["W"], 0.4 * 30 * 3.6 * 2)
    assert win["S"] == 0.0 and wall["S"] > 0          # garage end wall and upper east wall


def test_program_facts_cover_probes():
    from bemgen.generators.s3 import program_facts
    p = _program(probes=["layers", "precedence"], units="IP")
    spec = program_facts(p)
    probes = {f.probe for f in spec.facts}
    assert {"layers", "precedence", "units"} <= probes
    assert spec.by_kind()["stated"] > 10


def test_render_writes_documents(tmp_path):
    from bemgen.generators.render import render
    files = render(_program(probes=["window_dims", "layers"], units="IP"), tmp_path)
    assert {"brief.md", "floorplan.png", "windows.csv", "envelope_layers.csv"} <= set(files)
    txt = (tmp_path / "brief.md").read_text()
    assert "sq ft" in txt or "'-" in txt
