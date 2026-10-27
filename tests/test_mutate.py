"""Mutation operators apply to a released reference and keep it schema-valid."""
from pathlib import Path

import pytest

from bemgen import mutate
from bemgen.idf import IDF

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "benchmark" / "items" / "S3" / "V21-rowhouse-chicago" / "reference" / "model.idf"


@pytest.fixture(scope="module")
def schema():
    from bemgen.schema import get_schema
    try:
        return get_schema("23.1")
    except FileNotFoundError:
        pytest.skip("EnergyPlus schema not installed (run `bemgen setup`)")


@pytest.mark.parametrize("family,name", [(f, n) for f, ops in mutate.FAMILIES.items() for n in ops])
def test_operator_keeps_model_valid(schema, family, name):
    m = IDF.load(REF)
    desc = mutate.apply(m, family, name, {})
    if desc is None:
        pytest.skip(f"{name} does not apply to this reference")
    errors = [i for i in schema.validate(m) if i.severity == "error"]
    assert not errors, errors[:3]


def test_equivalent_rewrites_change_text_not_counts():
    m = IDF.load(REF)
    n_people = len(m.by_class("People"))
    mutate.apply(m, "equivalent", "people_as_density", {})
    assert len(m.by_class("People")) == n_people
    assert all(mutate.fget(o, "number_of_people_calculation_method").upper() == "PEOPLE/AREA" for o in m.by_class("People"))


def test_roles_follow_the_documents():
    # an admissible operator on an input the documents state is a defect there
    assert mutate.role("P02-lupton-heat-pump", "admissible", "oa_none") == "defect"
    assert mutate.role("V01-small-office-phoenix", "admissible", "oa_none") == "admissible"
    # a defect operator on a target the documents leave open needs no verdict
    assert mutate.role("P04-office-narrative", "defect", "cop_low") == "open"
    assert mutate.role("V24-rowhouse-houston", "defect", "hvac_to_ideal") == "open"
    # a half turn of a symmetric building is the same building
    assert mutate.role("P08-bestest-l100a-cos", "defect", "rotate_180") == "equivalent"
    assert mutate.role("V21-rowhouse-chicago", "defect", "rotate_180") == "defect"
    for item, fam, op in [("P02-lupton-heat-pump", "admissible", "slab_xps_50mm"), ("P04-office-narrative", "defect", "site_moved"),
                          ("P08-bestest-l100a-cos", "defect", "rotate_180")]:
        assert mutate.role_source(item, fam, op)


def test_slab_ffactor_counts_only_exposed_edges(schema):
    m = IDF.load(REF)
    desc = mutate.a_slab_ffactor(m, {})
    assert desc and "F-factor" in desc
    cons = m.by_class("Construction:FfactorGroundFloor")
    assert cons
    # a row house: party walls are adiabatic, so the exposed perimeter is shorter than the floor perimeter
    floor = [s for s in mutate.surfaces(m, "FLOOR") if mutate.fget(s, "outside_boundary_condition").upper() == "GROUNDFCFACTORMETHOD"]
    assert floor
    pts = mutate._verts(floor[0])
    full = sum(((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5 for a, b in mutate._edges(pts))
    assert 0 < float(cons[0].fields[3]) < full
    errors = [i for i in schema.validate(m) if i.severity == "error"]
    assert not errors, errors[:3]
