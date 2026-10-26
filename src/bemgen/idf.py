"""Minimal, dependency-free reader and writer for EnergyPlus IDF text.

The parser keeps every object in file order with its field values as strings
and the full-line comments written directly above it. Comments matter here:
practice models often carry provenance notes such as ``! source: stated``
that the QA gates read.
"""
from __future__ import annotations

import copy
import fnmatch
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, List, Optional


@dataclass
class IDFObject:
    cls: str
    fields: List[str]
    comment: str = ""          # full-line comments directly above the object
    line: int = 0              # 1-based line where the object starts

    @property
    def key(self) -> str:
        return self.cls.upper()

    @property
    def name(self) -> str:
        return self.fields[0] if self.fields else ""

    def get(self, i: int, default: str = "") -> str:
        return self.fields[i] if i < len(self.fields) else default

    def num(self, i: int, default: Optional[float] = None) -> Optional[float]:
        try:
            return float(self.get(i))
        except (TypeError, ValueError):
            return default

    def set(self, i: int, value) -> None:
        while len(self.fields) <= i:
            self.fields.append("")
        self.fields[i] = _fmt(value)

    def copy(self) -> "IDFObject":
        return copy.deepcopy(self)


def _fmt(v) -> str:
    if isinstance(v, float):
        s = f"{v:.10g}"
        return s
    return str(v)


class IDF:
    """An ordered collection of IDF objects with case-insensitive class lookup."""

    def __init__(self, objects: Optional[Iterable[IDFObject]] = None, header: str = ""):
        self.objects: List[IDFObject] = list(objects or [])
        self.header = header

    # ------------------------------------------------------------------ I/O
    @classmethod
    def from_text(cls, text: str) -> "IDF":
        objs: List[IDFObject] = []
        pending: List[str] = []     # comment lines directly above the next object
        header: List[str] = []      # comment lines before the first object
        buf = ""
        start_line = 0
        for ln, raw in enumerate(text.splitlines(), start=1):
            code, bang, comment = raw.partition("!")
            if not buf.strip() and not code.strip():
                if bang:
                    pending.append(("!" + comment).rstrip())
                else:                       # blank line: detach comments above it
                    if not objs:
                        header.extend(pending)
                    pending = []
                continue
            if not buf.strip():
                start_line = ln
            buf += code + "\n"
            while ";" in buf:
                obj_text, buf = buf.split(";", 1)
                toks = [t.strip() for t in obj_text.replace("\n", " ").split(",")]
                if toks and toks[0]:
                    objs.append(IDFObject(toks[0], toks[1:], "\n".join(pending).strip(), start_line))
                pending = []
                start_line = ln
        return cls(objs, header="\n".join(header).strip())

    @classmethod
    def load(cls, path) -> "IDF":
        raw = Path(path).read_bytes()
        for enc in ("utf-8-sig", "latin-1"):
            try:
                return cls.from_text(raw.decode(enc))
            except UnicodeDecodeError:
                continue
        raise ValueError(f"cannot decode {path}")

    def to_text(self, schema=None, keep_comments: bool = True) -> str:
        out: List[str] = []
        if self.header:
            out.append(self.header)
            out.append("")
        for o in self.objects:
            if keep_comments and o.comment:
                out.append(o.comment)
            names = schema.field_names(o.cls, len(o.fields)) if schema else [""] * len(o.fields)
            if not o.fields:
                out.append(f"{o.cls};")
                out.append("")
                continue
            out.append(f"{o.cls},")
            for i, v in enumerate(o.fields):
                end = ";" if i == len(o.fields) - 1 else ","
                nm = names[i] if i < len(names) and names[i] else ""
                out.append(f"  {v}{end}" + (f"  !- {nm}" if nm else ""))
            out.append("")
        return "\n".join(out) + "\n"

    def save(self, path, schema=None) -> None:
        Path(path).write_text(self.to_text(schema), encoding="utf-8")

    # --------------------------------------------------------------- access
    def __iter__(self) -> Iterator[IDFObject]:
        return iter(self.objects)

    def __len__(self) -> int:
        return len(self.objects)

    def by_class(self, *classes: str) -> List[IDFObject]:
        keys = {c.upper() for c in classes}
        pats = [k for k in keys if any(ch in k for ch in "*?[")]
        return [o for o in self.objects
                if o.key in keys or any(fnmatch.fnmatchcase(o.key, p) for p in pats)]

    def first(self, cls: str) -> Optional[IDFObject]:
        r = self.by_class(cls)
        return r[0] if r else None

    def get(self, cls: str, name: str) -> Optional[IDFObject]:
        n = name.upper()
        for o in self.by_class(cls):
            if o.name.upper() == n:
                return o
        return None

    def classes(self) -> dict:
        counts: dict = {}
        for o in self.objects:
            counts[o.cls] = counts.get(o.cls, 0) + 1
        return counts

    def add(self, cls: str, fields: Iterable, comment: str = "") -> IDFObject:
        o = IDFObject(cls, [_fmt(f) for f in fields], comment)
        self.objects.append(o)
        return o

    def remove(self, obj: IDFObject) -> None:
        self.objects = [o for o in self.objects if o is not obj]

    def remove_class(self, cls: str) -> int:
        before = len(self.objects)
        self.objects = [o for o in self.objects if o.key != cls.upper()]
        return before - len(self.objects)

    def copy(self) -> "IDF":
        return IDF([o.copy() for o in self.objects], self.header)

    def version(self) -> str:
        v = self.first("Version")
        return v.get(0) if v else ""


_COMMENT_SOURCE = re.compile(r"!\s*source\s*:\s*(.+)", re.I)


def provenance_tag(obj: IDFObject) -> Optional[str]:
    """Return the text of a ``! source: ...`` comment above an object, if any."""
    for line in obj.comment.splitlines():
        m = _COMMENT_SOURCE.search(line)
        if m:
            return m.group(1).strip()
    return None
