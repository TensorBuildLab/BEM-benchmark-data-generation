"""Unit tests that need neither EnergyPlus nor weather files (the schema is needed for some)."""
from __future__ import annotations

import math

import pytest

from bemgen.idf import IDF, provenance_tag
from bemgen.spec import Spec, Fact, evaluate_check, grade
from bemgen.facts import get_path, _count_levels
from bemgen.qa import scan_text_leaks, plausibility

SAMPLE = """! header comment

Version,23.1;

! source: stated (input1.txt)
Zone,
  Living Zone,   !- Name
  0;             !- Direction of Relative North

Lights, L1, Living Zone, Always, Watts/Area, , 5;
"""


def test_parse_roundtrip_and_comments():
    idf = IDF.from_text(SAMPLE)
    assert len(idf) == 3
    z = idf.get("ZONE", "living zone")
    assert z is not None and z.get(1) == "0"
    assert provenance_tag(z) == "stated (input1.txt)"
    again = IDF.from_text(idf.to_text())
    assert [o.fields for o in again] == [o.fields for o in idf]


def test_by_class_glob():
    idf = IDF.from_text("ZoneInfiltration:DesignFlowRate, a, z;\nZoneInfiltration:FlowCoefficient, b, z;\nZone, z;")
    assert len(idf.by_class("ZoneInfiltration:*")) == 2


FACTS = {"geometry": {"n_levels": 2, "zones": {"F1_ZONE": {"volume": 10.0}, "F2_ZONE": {"volume": 12.0}}},
         "fenestration": {"wwr": {"S": 0.31, "N": 0.0}, "doors_by_direction": {"S": 1}},
         "hvac": {"primary": "central_ashp", "tags": ["central_ashp"], "cooling_cops": [3.0, 3.5]},
         "control": {"any_cooling": False}}


@pytest.mark.parametrize("check,expect", [
    ({"path": "geometry.n_levels", "op": "eq", "value": 2}, True),
    ({"path": "fenestration.wwr.S", "op": "approx", "value": 0.30, "tol": 0.02}, True),
    ({"path": "fenestration.wwr.S", "op": "approx", "value": 0.25, "tol": 0.02}, False),
    ({"path": "geometry.zones[*].volume", "op": "gt", "value": 5}, True),
    ({"path": "geometry.zones[F2*].volume", "op": "approx", "value": 12, "tol": 0.1}, True),
    ({"path": "fenestration.doors_by_direction", "op": "contains", "value": "S"}, True),
    ({"path": "hvac.primary", "op": "in", "value": ["ptac", "central_ashp"]}, True),
    ({"path": "hvac.cooling_cops", "op": "approx", "value": 3.5, "tol": 0.05, "agg": "any"}, True),
    ({"path": "control.any_cooling", "op": "false"}, True),
    ({"path": "missing.path", "op": "eq", "value": 1}, None),
    ({"any_of": [{"path": "fenestration.wwr.N", "op": "gt", "value": 0}, {"path": "geometry.n_levels", "op": "eq", "value": 2}]}, True),
])
def test_checks(check, expect):
    assert evaluate_check(check, FACTS)["pass"] is expect


def test_grade_weights_and_unverifiable():
    spec = Spec("x", [Fact("a", "geometry", "stated", "", {"path": "geometry.n_levels", "op": "eq", "value": 2}, severity="critical"),
                      Fact("b", "fenestration", "stated", "", {"path": "fenestration.wwr.S", "op": "eq", "value": 0.5}, severity="minor"),
                      Fact("c", "loads", "derived", "", {"path": "loads.lpd", "op": "eq", "value": 5}, severity="major"),
                      Fact("d", "loads", "assumed", "", {"path": "fenestration.wwr.S", "op": "range", "min": 0.1, "max": 0.5})])
    g = grade(spec, FACTS)
    assert g["n_pass"] == 2 and g["n_fail"] == 1 and g["n_na"] == 1
    assert math.isclose(g["conformance"], 3 / 6)        # critical passes; minor fails; major unverifiable
    assert g["plausibility"] == 1.0


def test_count_levels_merges_close_floors():
    assert _count_levels([0.0, 0.0, 0.3, 3.5, 3.6, 7.0]) == 3


def test_leak_scan():
    hits = scan_text_leaks("The curves were replaced in feat-009. File C:/UAStudy/x.csv")
    kinds = {k for k, _ in hits}
    assert "development ticket reference" in kinds and "absolute local path" in kinds


def test_plausibility_rules_apply_conditionally():
    f = {"results": {"unmet_occupied_heating_h": 500}, "control": {"any_heating": False}}
    assert not any(r["id"] == "PL-unmet-heat" for r in plausibility(f))
    f["control"]["any_heating"] = True
    assert any(r["id"] == "PL-unmet-heat" and r["pass"] is False for r in plausibility(f))


def test_get_path_case_insensitive():
    assert get_path({"A": {"b": 1}}, "a.B") == 1


def test_range_bounds_absorb_float_noise():
    from bemgen.spec import evaluate_check
    facts = {"loads": {"people_total": 577.000003}}
    assert evaluate_check({"path": "loads.people_total", "op": "range", "min": 100, "max": 577}, facts)["pass"] is True
    facts = {"loads": {"people_total": 578.0}}
    assert evaluate_check({"path": "loads.people_total", "op": "range", "min": 100, "max": 577}, facts)["pass"] is False
