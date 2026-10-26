"""Weather helpers: pinning, fetching and building EPW files.

``epw_from_converter_csv`` turns a file in the EnergyPlus Weather Converter
CSV layout (as shipped with measured-data case studies) into an EPW. Hours
outside the measured period are spliced from a template EPW of the same site
and flagged in the header comments; hours with missing direct-normal
irradiance get it from global and diffuse horizontal irradiance and the solar
position.
"""
from __future__ import annotations

import io
import math
import urllib.request
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from .item import sha256


def fetch_onebuilding(url: str, dest_dir) -> Path:
    """Download a climate.onebuilding.org zip and extract its .epw/.ddy/.stat."""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    data = urllib.request.urlopen(url, timeout=120).read()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        out = None
        for n in z.namelist():
            if n.lower().endswith((".epw", ".ddy", ".stat")):
                p = dest_dir / Path(n).name
                p.write_bytes(z.read(n))
                if n.lower().endswith(".epw"):
                    out = p
    if out is None:
        raise RuntimeError(f"no EPW in {url}")
    return out


def _solar_cos_zenith(lat, lon, tz, dt_mid: datetime) -> float:
    """Cosine of the solar zenith angle at local standard time ``dt_mid`` (NOAA approximations)."""
    doy = dt_mid.timetuple().tm_yday
    hour = dt_mid.hour + dt_mid.minute / 60.0
    g = 2 * math.pi / 365.0 * (doy - 1 + (hour - 12) / 24.0)
    eqt = 229.18 * (0.000075 + 0.001868 * math.cos(g) - 0.032077 * math.sin(g)
                    - 0.014615 * math.cos(2 * g) - 0.040849 * math.sin(2 * g))
    decl = (0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g) - 0.006758 * math.cos(2 * g)
            + 0.000907 * math.sin(2 * g) - 0.002697 * math.cos(3 * g) + 0.00148 * math.sin(3 * g))
    tst = hour * 60 + eqt + 4 * lon - 60 * tz
    ha = math.radians(tst / 4.0 - 180.0)
    la = math.radians(lat)
    return math.sin(la) * math.sin(decl) + math.cos(la) * math.cos(decl) * math.cos(ha)


def epw_from_converter_csv(csv_path, template_epw, out_path, location_name: Optional[str] = None) -> dict:
    """Build an EPW from a Weather Converter CSV, splicing unmeasured hours from ``template_epw``."""
    tmpl = Path(template_epw).read_text(errors="replace").splitlines()
    header, data = tmpl[:8], tmpl[8:]
    loc = header[0].split(",")
    lat, lon, tz = float(loc[6]), float(loc[7]), float(loc[8])
    # EPW missing-value sentinels by column (EnergyPlus Auxiliary Programs, EPW format)
    sentinel = {6: 99.9, 7: 99.9, 8: 999, 9: 999999, 10: 9999, 11: 9999, 12: 9999, 13: 9999, 14: 9999, 15: 9999,
                16: 999999, 17: 999999, 18: 999999, 19: 9999, 20: 999, 21: 999, 22: 99, 23: 99, 24: 9999,
                25: 99999, 28: 999, 29: 0.999, 30: 999, 31: 99, 32: 999, 33: 999, 34: 99}
    measured = {}
    for ln in Path(csv_path).read_text(errors="replace").splitlines():
        parts = ln.split(",")
        if len(parts) < 30 or "/" not in parts[0] or ":" not in parts[1]:
            continue
        try:
            d = datetime.strptime(parts[0].strip(), "%Y/%m/%d")
            db = float(parts[3])
        except ValueError:
            continue
        if db >= 99.9:            # unmeasured hour: keep template
            continue
        # converter CSV: date, time, source, then 27 values (no present-weather columns)
        measured[(d.month, d.day, int(parts[1].split(":")[0]))] = (d.year, [x.strip() for x in parts[3:30]])
    out_lines, n_meas, n_ghi, n_filled = [], 0, 0, 0
    year_used = None
    for ln in data:
        p = ln.split(",")
        m, dday, hh = int(p[1]), int(p[2]), int(p[3])
        key = (m, dday, hh)
        if key not in measured:
            if year_used:
                p[0] = str(year_used)
            out_lines.append(",".join(p))
            continue
        yr, v = measured[key]
        year_used = yr
        row = [str(yr), str(m), str(dday), str(hh), p[4], p[5]] + v[0:20] + [p[26], p[27]] + v[20:27]
        for j, sent in sentinel.items():
            try:
                miss = float(row[j]) >= sent
            except (ValueError, IndexError):
                miss = True
            if miss and j not in (13,):
                if j < len(p):
                    row[j] = p[j]
                    n_filled += 1
        try:
            dni, dhi = float(row[14]), float(row[15])
            if float(row[13]) >= 9999 and dni < 9999 and dhi < 9999:
                cz = _solar_cos_zenith(lat, lon, tz, datetime(yr, m, dday) + timedelta(hours=hh - 0.5))
                row[13] = f"{max(0.0, dni * max(cz, 0.0) + dhi):.1f}"
                n_ghi += 1
        except ValueError:
            pass
        out_lines.append(",".join(row))
        n_meas += 1
    year_used = year_used or 2021
    name = location_name or loc[1]
    loc[1] = name
    header[0] = ",".join(loc)
    header[5] = (f"COMMENTS 1,Measured hours ({n_meas}) from {Path(csv_path).name}; other hours spliced from "
                 f"{Path(template_epw).name}; global horizontal derived from direct and diffuse ({n_ghi} h); {n_filled} missing fields taken from the template")
    start_dow = datetime(year_used, 1, 1).strftime("%A")
    header[7] = f"DATA PERIODS,1,1,Data,{start_dow}, 1/ 1,12/31"
    Path(out_path).write_text("\n".join(header + out_lines) + "\n", encoding="utf-8")
    return {"measured_hours": n_meas, "ghi_derived": n_ghi, "fields_from_template": n_filled, "year": year_used,
            "sha256": sha256(out_path)}
