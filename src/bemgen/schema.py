"""Field-level validation of IDF objects against the EnergyPlus epJSON schema.

The schema file (``Energy+.schema.epJSON``) ships with every EnergyPlus
installation. :func:`locate_schema` looks for it in ``BEMGEN_SCHEMA``, in the
EnergyPlus folder named by ``BEMGEN_ENERGYPLUS_DIR``, in common install
folders, and in the user cache that ``bemgen setup`` fills from the Docker
image.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

from .idf import IDF, IDFObject

CACHE = Path(os.environ.get("BEMGEN_CACHE", Path.home() / ".cache" / "bemgen"))


def locate_schema(version: str = "23.1") -> Path:
    cands: List[Path] = []
    if os.environ.get("BEMGEN_SCHEMA"):
        cands.append(Path(os.environ["BEMGEN_SCHEMA"]))
    if os.environ.get("BEMGEN_ENERGYPLUS_DIR"):
        cands.append(Path(os.environ["BEMGEN_ENERGYPLUS_DIR"]) / "Energy+.schema.epJSON")
    v = version.replace(".", "-")
    cands += [CACHE / version / "Energy+.schema.epJSON",
              Path(f"C:/EnergyPlusV{v}-0/Energy+.schema.epJSON"),
              Path(f"/usr/local/EnergyPlus-{v}-0/Energy+.schema.epJSON"),
              Path(f"/Applications/EnergyPlus-{v}-0/Energy+.schema.epJSON")]
    for c in cands:
        if c.is_file():
            return c
    raise FileNotFoundError(
        "EnergyPlus schema not found; run `bemgen setup` or set BEMGEN_SCHEMA "
        f"(looked in: {', '.join(str(c) for c in cands)})")


@dataclass
class Issue:
    severity: str          # error | warning | info
    code: str
    message: str
    cls: str = ""
    name: str = ""
    field: str = ""
    line: int = 0

    def to_dict(self):
        return asdict(self)


class Schema:
    def __init__(self, path: Optional[Path] = None, version: str = "23.1"):
        self.path = Path(path) if path else locate_schema(version)
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.version = version
        self.props: Dict[str, dict] = data["properties"]
        self.canon: Dict[str, str] = {k.upper(): k for k in self.props}
        # every list name that some object's name (or field) registers into
        self.name_lists = set()
        for spec in self.props.values():
            for ref in (spec.get("name") or {}).get("reference", []):
                self.name_lists.add(ref)

    # ---------------------------------------------------------- structure
    def has(self, cls: str) -> bool:
        return cls.upper() in self.canon

    def spec(self, cls: str) -> dict:
        return self.props[self.canon[cls.upper()]]

    def _layout(self, cls: str):
        s = self.spec(cls)
        lid = s.get("legacy_idd", {})
        fields = lid.get("fields", [])
        ext = lid.get("extensibles", [])
        return s, fields, ext, lid.get("extension")

    def field_key(self, cls: str, i: int) -> str:
        s, fields, ext, _ = self._layout(cls)
        if i < len(fields):
            return fields[i]
        if ext:
            return ext[(i - len(fields)) % len(ext)]
        return f"field_{i + 1}"

    def field_names(self, cls: str, n: int) -> List[str]:
        if not self.has(cls):
            return [""] * n
        s, fields, ext, _ = self._layout(cls)
        info = s.get("legacy_idd", {}).get("field_info", {})
        out = []
        for i in range(n):
            k = self.field_key(cls, i)
            nm = info.get(k, {}).get("field_name", k)
            if i >= len(fields) and ext:
                nm = f"{nm} {(i - len(fields)) // len(ext) + 1}"
            out.append(nm)
        return out

    def field_index(self, cls: str, key: str) -> int:
        _, fields, _, _ = self._layout(cls)
        return fields.index(key)

    def field_spec(self, cls: str, i: int) -> dict:
        s, fields, ext, extension = self._layout(cls)
        key = self.field_key(cls, i)
        if key == "name" and i == 0 and "name" in s:
            return s["name"]
        pp = s.get("patternProperties", {})
        props = next(iter(pp.values()), {}).get("properties", {}) if pp else {}
        if i < len(fields):
            return props.get(key, {})
        if extension and extension in props:
            return props[extension].get("items", {}).get("properties", {}).get(key, {})
        return {}

    def required_keys(self, cls: str) -> List[str]:
        s, fields, _, _ = self._layout(cls)
        pp = s.get("patternProperties", {})
        req = list(next(iter(pp.values()), {}).get("required", [])) if pp else []
        if (s.get("name") or {}).get("is_required"):
            req.insert(0, "name")
        return req

    def is_unique(self, cls: str) -> bool:
        s = self.spec(cls)
        return s.get("maxProperties") == 1

    # ---------------------------------------------------------- validation
    def validate(self, idf: IDF, check_references: bool = True) -> List[Issue]:
        issues: List[Issue] = []
        names: Dict[str, set] = {}
        counts: Dict[str, int] = {}
        for o in idf:
            if not self.has(o.cls):
                issues.append(Issue("error", "unknown-class", f"unknown object class '{o.cls}'", o.cls, o.name, line=o.line))
                continue
            canon = self.canon[o.key]
            counts[canon] = counts.get(canon, 0) + 1
            nspec = self.spec(canon).get("name") or {}
            if o.fields and nspec:
                for ref in nspec.get("reference", []):
                    names.setdefault(ref, set()).add(o.name.upper())
        for cls, n in counts.items():
            if n > 1 and self.is_unique(cls):
                issues.append(Issue("error", "duplicate-unique", f"{n} instances of unique object {cls}", cls))
        class_names = set(self.canon)
        for o in idf:
            if not self.has(o.cls):
                continue
            canon = self.canon[o.key]
            s, fields, ext, _ = self._layout(canon)
            if not ext and len(o.fields) > len(fields):
                issues.append(Issue("error", "too-many-fields",
                                    f"{len(o.fields)} fields given, {len(fields)} allowed", canon, o.name, line=o.line))
            req = set(self.required_keys(canon))
            for i, val in enumerate(o.fields[: len(fields)]):
                k = fields[i]
                if k in req and val == "":
                    issues.append(Issue("error", "required-blank", f"required field '{k}' is blank", canon, o.name, k, o.line))
            for k in req:
                if k in fields and fields.index(k) >= len(o.fields) and k != "name":
                    issues.append(Issue("error", "required-missing", f"required field '{k}' missing", canon, o.name, k, o.line))
            for i, val in enumerate(o.fields):
                if val == "":
                    continue
                fs = self.field_spec(canon, i)
                if not fs:
                    continue
                k = self.field_key(canon, i)
                issues += self._check_value(canon, o, k, val, fs, names, class_names, check_references)
        return issues

    def _check_value(self, cls, o: IDFObject, k, val, fs, names, class_names, check_refs) -> List[Issue]:
        out: List[Issue] = []
        alts = fs.get("anyOf") or [fs]
        num_alt = next((a for a in alts if a.get("type") == "number"), None)
        str_alts = [a for a in alts if a.get("type") == "string"]
        enums = set()
        for a in str_alts:
            for e in a.get("enum", []):
                enums.add(str(e).upper())
        free_string = any(a.get("type") == "string" and "enum" not in a for a in str_alts)
        v_up = val.upper()
        # EnergyPlus treats "autosize" and "autocalculate" as the same keyword in numeric fields
        if v_up in ("AUTOSIZE", "AUTOCALCULATE") and enums & {"AUTOSIZE", "AUTOCALCULATE"}:
            return out
        if num_alt is not None:
            try:
                x = float(val)
            except ValueError:
                if v_up in enums or free_string:
                    return out
                return [Issue("error", "not-a-number", f"'{val}' is not a number", cls, o.name, k, o.line)]
            lo, hi = num_alt.get("minimum"), num_alt.get("maximum")
            xlo, xhi = num_alt.get("exclusiveMinimum"), num_alt.get("exclusiveMaximum")
            if isinstance(xlo, bool):
                xlo = lo if xlo else None
                lo = None if xlo is not None else lo
            if isinstance(xhi, bool):
                xhi = hi if xhi else None
                hi = None if xhi is not None else hi
            if lo is not None and x < lo or xlo is not None and x <= xlo:
                out.append(Issue("error", "below-minimum", f"{val} below minimum {lo if lo is not None else xlo}", cls, o.name, k, o.line))
            if hi is not None and x > hi or xhi is not None and x >= xhi:
                out.append(Issue("error", "above-maximum", f"{val} above maximum {hi if hi is not None else xhi}", cls, o.name, k, o.line))
            return out
        if enums and not free_string and v_up not in enums:
            out.append(Issue("error", "bad-choice", f"'{val}' not one of {sorted(enums)[:8]}", cls, o.name, k, o.line))
            return out
        if check_refs:
            lists = []
            for a in alts:
                lists += a.get("object_list", [])
            known = [lst for lst in lists if lst in self.name_lists]
            if known and v_up not in class_names:
                if not any(v_up in names.get(lst, set()) for lst in known):
                    out.append(Issue("error", "dangling-reference",
                                     f"'{val}' not defined (expected one of: {', '.join(known[:3])})", cls, o.name, k, o.line))
        return out


@lru_cache(maxsize=4)
def get_schema(version: str = "23.1") -> Schema:
    return Schema(version=version)
