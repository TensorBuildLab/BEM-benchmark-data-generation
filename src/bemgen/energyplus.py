"""Run EnergyPlus on a model, locally or in the official Docker image.

Engine selection (first match wins):

1. ``BEMGEN_ENERGYPLUS`` points to an ``energyplus`` executable -> local run.
2. Docker is on PATH -> ``nrel/energyplus:<version>`` (override with
   ``BEMGEN_DOCKER_IMAGE``).

Every run works on a copy of the model. The copy may be *instrumented*: a
``Output:SQLite`` object and an ``AllSummary`` report are added when missing,
because the QA gates read their facts from the SQLite output. Instrumentation
never changes the physics, and each change is recorded in the run manifest.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Union

from .idf import IDF

DEFAULT_VERSION = "23.1"
DEFAULT_IMAGE = {"23.1": "nrel/energyplus:23.1.0"}


@dataclass
class RunResult:
    run_dir: str
    completed: bool = False          # EnergyPlus reached "Completed Successfully"
    fatal: bool = False
    severe: int = 0
    warnings: int = 0
    elapsed_s: float = 0.0
    returncode: int = -1
    severe_messages: List[str] = field(default_factory=list)
    warning_kinds: dict = field(default_factory=dict)
    instrumentation: List[str] = field(default_factory=list)
    sql: str = ""
    expanded_idf: str = ""
    err: str = ""

    @property
    def ok(self) -> bool:
        return self.completed and not self.fatal

    def to_dict(self):
        return asdict(self)


class Engine:
    name = "engine"

    def command(self, run_dir: Path, idf: str, epw: Optional[str], expand: bool) -> List[str]:
        raise NotImplementedError


class LocalEngine(Engine):
    name = "local"

    def __init__(self, exe: str):
        self.exe = exe

    def command(self, run_dir, idf, epw, expand):
        cmd = [self.exe]
        if expand:
            cmd.append("-x")
        if epw:
            cmd += ["-w", str(run_dir / epw)]
        cmd += ["-d", str(run_dir / "out"), str(run_dir / idf)]
        return cmd


class DockerEngine(Engine):
    name = "docker"

    def __init__(self, image: str):
        self.image = image

    def command(self, run_dir, idf, epw, expand):
        mount = str(Path(run_dir).resolve())
        cmd = ["docker", "run", "--rm", "-v", f"{mount}:/run", "-w", "/run", self.image, "energyplus"]
        if expand:
            cmd.append("-x")
        if epw:
            cmd += ["-w", epw]
        cmd += ["-d", "out", idf]
        return cmd


def default_engine(version: str = DEFAULT_VERSION) -> Engine:
    exe = os.environ.get("BEMGEN_ENERGYPLUS")
    if exe:
        return LocalEngine(exe)
    if shutil.which("docker"):
        return DockerEngine(os.environ.get("BEMGEN_DOCKER_IMAGE", DEFAULT_IMAGE.get(version, f"nrel/energyplus:{version}.0")))
    raise RuntimeError("No EnergyPlus engine: set BEMGEN_ENERGYPLUS or install Docker")


# ------------------------------------------------------------------ helpers
def instrument(idf: IDF, design_days_only: bool = False) -> List[str]:
    """Add the outputs the QA gates need; return what was changed."""
    notes = []
    sq = idf.by_class("Output:SQLite")
    if not sq:
        idf.add("Output:SQLite", ["SimpleAndTabular"])
        notes.append("added Output:SQLite,SimpleAndTabular")
    elif sq[0].get(0).strip().upper() != "SIMPLEANDTABULAR":
        sq[0].set(0, "SimpleAndTabular")
        notes.append("set Output:SQLite to SimpleAndTabular")
    sty = idf.first("OutputControl:Table:Style")
    if sty is not None and sty.get(1).strip().upper() not in ("", "NONE", "JTOGJ"):
        sq = idf.by_class("Output:SQLite")
        sq[0].set(1, "JtoGJ")
        notes.append(f"Output:SQLite tabular data forced to SI GJ (model asks for {sty.get(1)} tables)")
    rep = idf.by_class("Output:Table:SummaryReports")
    if not rep:
        idf.add("Output:Table:SummaryReports", ["AllSummary"])
        notes.append("added Output:Table:SummaryReports,AllSummary")
    elif not any(f.strip().upper() in ("ALLSUMMARY", "ALLSUMMARYANDMONTHLY", "ALLSUMMARYANDSIZINGPERIOD",
                                       "ALLSUMMARYMONTHLYANDSIZINGPERIOD") for f in rep[0].fields):
        rep[0].fields = ["AllSummary"]
        for extra in rep[1:]:
            idf.remove(extra)
        notes.append("replaced Output:Table:SummaryReports with AllSummary")
    if not any(o.get(1).strip().upper() == "ZONE TOTAL INTERNAL TOTAL HEATING ENERGY" for o in idf.by_class("Output:Variable")):
        idf.add("Output:Variable", ["*", "Zone Total Internal Total Heating Energy", "RunPeriod"])
        notes.append("added Output:Variable Zone Total Internal Total Heating Energy (RunPeriod)")
    if design_days_only:
        sc = idf.first("SimulationControl")
        if sc is None:
            sc = idf.add("SimulationControl", ["No", "No", "No", "Yes", "No"])
        # fields: zone sizing, system sizing, plant sizing, sizing periods, weather file
        sc.set(3, "Yes")
        sc.set(4, "No")
        notes.append("SimulationControl: sizing periods only")
    return notes


_ELAPSED = re.compile(r"Elapsed Time=(\d+)hr\s+(\d+)min\s+([\d.]+)sec")


def parse_err(path: Union[str, Path]) -> dict:
    p = Path(path)
    out = {"completed": False, "fatal": False, "severe": 0, "warnings": 0, "elapsed_s": 0.0,
           "severe_messages": [], "warning_kinds": {}}
    if not p.is_file():
        return out
    text = p.read_text(errors="replace")
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        s = ln.strip()
        if "** Severe  **" in s:
            out["severe_messages"].append(s.split("** Severe  **", 1)[1].strip()[:300])
        elif "**  Fatal  **" in s:
            out["fatal"] = True
            out["severe_messages"].append("FATAL: " + s.split("**  Fatal  **", 1)[1].strip()[:300])
        elif "** Warning **" in s:
            msg = s.split("** Warning **", 1)[1].strip()
            kind = re.sub(r"[\"'=].*", "", re.sub(r"\d+(\.\d+)?", "#", msg))[:80].strip()
            out["warning_kinds"][kind] = out["warning_kinds"].get(kind, 0) + 1
    m = re.search(r"EnergyPlus (Completed Successfully|Terminated--Fatal Error Detected)-- (\d+) Warning; (\d+) Severe Errors", text)
    if m:
        out["completed"] = m.group(1).startswith("Completed")
        out["fatal"] = out["fatal"] or not out["completed"]
        out["warnings"] = int(m.group(2))
        out["severe"] = int(m.group(3))
    em = _ELAPSED.findall(text)
    if em:
        h, mi, se = em[-1]
        out["elapsed_s"] = int(h) * 3600 + int(mi) * 60 + float(se)
    return out


def _finished(err: Path) -> bool:
    """True when the error file carries EnergyPlus's final status line."""
    if not err.is_file():
        return False
    text = err.read_text(errors="replace")
    return "EnergyPlus Completed" in text or "EnergyPlus Terminated" in text


def needs_expand(idf: IDF) -> bool:
    return any(o.key.startswith("HVACTEMPLATE:") for o in idf)


def run_model(model: Union[str, Path, IDF], weather: Optional[Union[str, Path]], run_dir: Union[str, Path],
              side_files: Sequence[Union[str, Path]] = (), engine: Optional[Engine] = None,
              design_days_only: bool = False, timeout: int = 7200, reuse: bool = True,
              instrument_model: bool = True) -> RunResult:
    """Run one model in ``run_dir`` (created). Returns a :class:`RunResult`.

    With ``reuse`` a previous completed run in the same folder, made from the
    same input text, is returned without running again.
    """
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    idf = model.copy() if isinstance(model, IDF) else IDF.load(model)
    notes = instrument(idf, design_days_only) if instrument_model else []
    text = idf.to_text()
    manifest = run_dir / "run.json"
    if reuse and manifest.is_file() and (run_dir / "in.idf").is_file():
        try:
            old = json.loads(manifest.read_text())
        except ValueError:  # manifest of an interrupted run
            old = {}
        # reuse only a run that EnergyPlus finished (completed or terminated) and whose manifest agrees with its
        # error file (a killed client records a failure for a run the engine went on to finish), and a completed
        # one only while its SQLite output is still there (prune_run_dir may have removed it)
        err = run_dir / "out" / "eplusout.err"
        if (run_dir / "in.idf").read_text(encoding="utf-8") == text and old.get("completed") is not None \
                and _finished(err) and parse_err(err)["completed"] == bool(old["completed"]) \
                and (not old["completed"] or (run_dir / "out" / "eplusout.sql").is_file()):
            return RunResult(**old)
    import hashlib
    h = hashlib.sha256(text.encode("utf-8"))
    for f in ([weather] if weather else []) + sorted(str(x) for x in side_files):
        h.update(Path(f).read_bytes())
    engine = engine or default_engine()
    h.update(getattr(engine, "image", getattr(engine, "exe", "")).encode())
    key = h.hexdigest()[:32]
    cache = Path(os.environ.get("BEMGEN_RUN_CACHE", Path.home() / ".cache" / "bemgen" / "runs")) / key
    if reuse and (cache / "run.json").is_file():
        (run_dir / "in.idf").write_text(text, encoding="utf-8")
        if (run_dir / "out").exists():
            shutil.rmtree(run_dir / "out")
        shutil.copytree(cache / "out", run_dir / "out")
        d = json.loads((cache / "run.json").read_text())
        out = run_dir / "out"
        d.update(run_dir=str(run_dir), sql=str(out / "eplusout.sql") if (out / "eplusout.sql").is_file() else "",
                 expanded_idf=str(out / "eplusout.expidf") if (out / "eplusout.expidf").is_file() else "",
                 err=str(out / "eplusout.err"))
        manifest.write_text(json.dumps(d, indent=1))
        return RunResult(**d)
    (run_dir / "in.idf").write_text(text, encoding="utf-8")
    for f in side_files:
        shutil.copy2(f, run_dir / Path(f).name)
    epw = None
    if weather:
        shutil.copy2(weather, run_dir / "w.epw")
        epw = "w.epw"
    out = run_dir / "out"
    if out.exists():
        shutil.rmtree(out)
    cmd = engine.command(run_dir, "in.idf", epw, needs_expand(idf))
    t0 = time.time()
    try:
        cp = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        rc = cp.returncode
        (run_dir / "stdout.txt").write_text((cp.stdout or "")[-20000:] + "\n" + (cp.stderr or "")[-5000:])
    except subprocess.TimeoutExpired:
        rc = -9
    e = parse_err(out / "eplusout.err")
    res = RunResult(run_dir=str(run_dir), returncode=rc, instrumentation=notes,
                    completed=e["completed"], fatal=e["fatal"] or rc not in (0,), severe=e["severe"],
                    warnings=e["warnings"], elapsed_s=e["elapsed_s"] or round(time.time() - t0, 1),
                    severe_messages=e["severe_messages"][:50], warning_kinds=e["warning_kinds"],
                    sql=str(out / "eplusout.sql") if (out / "eplusout.sql").is_file() else "",
                    expanded_idf=next((str(out / n) for n in ("eplusout.expidf", "expanded.idf") if (out / n).is_file()), ""),
                    err=str(out / "eplusout.err"))
    if rc == 0 and e["completed"]:
        res.fatal = False
    manifest.write_text(json.dumps(res.to_dict(), indent=1))
    if res.completed:
        try:
            (cache / "out").mkdir(parents=True, exist_ok=True)
            for n in ("eplusout.sql", "eplusout.eio", "eplusout.err", "eplusout.expidf"):
                if (out / n).is_file():
                    shutil.copy2(out / n, cache / "out" / n)
            (cache / "run.json").write_text(json.dumps(res.to_dict(), indent=1))
        except OSError:
            pass
    return res


def prune_run_dir(run_dir: Union[str, Path]) -> None:
    """Delete the bulky files of a finished, scored run to save disk space.

    The weather copy goes. A completed run loses its whole output folder, which the run
    cache still holds, so a rerun restores it from there instead of simulating again.
    A failed run keeps only ``eplusout.err``.
    """
    run_dir = Path(run_dir)
    (run_dir / "w.epw").unlink(missing_ok=True)
    out = run_dir / "out"
    manifest = run_dir / "run.json"
    completed = manifest.is_file() and json.loads(manifest.read_text()).get("completed")
    if completed:
        shutil.rmtree(out, ignore_errors=True)
    elif out.is_dir():
        for f in out.iterdir():
            if f.name != "eplusout.err":
                shutil.rmtree(f, ignore_errors=True) if f.is_dir() else f.unlink(missing_ok=True)


@dataclass
class Job:
    model: Union[str, Path, IDF]
    weather: Optional[Union[str, Path]]
    run_dir: Union[str, Path]
    side_files: Sequence[Union[str, Path]] = ()
    design_days_only: bool = False


def run_many(jobs: Iterable[Job], workers: int = 4, engine: Optional[Engine] = None, reuse: bool = True) -> List[RunResult]:
    jobs = list(jobs)
    engine = engine or default_engine()
    with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        futs = [ex.submit(run_model, j.model, j.weather, j.run_dir, j.side_files, engine,
                          j.design_days_only, 7200, reuse) for j in jobs]
        return [f.result() for f in futs]
