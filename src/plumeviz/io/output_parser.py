from __future__ import annotations

from pathlib import Path
import math


COLUMNS = [
    "Relative humidity, %",
    "Air temperature at vent (C)",
    "Air pressure at vent, atm",
    "vent diameter (m)",
    "vent elevation (m)",
    "initial velocity (m/s)",
    "magma temperature (c)",
    "weight fraction gas",
    "magma specific heat (j/kg k)",
    "magma density (kg/m3)",
    "mixture density (kg/m3)",
    "mass fraction water added",
    "mass flux total (kg/s)",
    "mass flux solids (kg/s)",
    "calculated height (km)",
    "sparks height (km)",
    "mastin et al 2009 height (km)",
]


HEADER_KEYS = {
    0: "Relative humidity, %",
    1: "Air temperature at vent (C):",
    2: "Air pressure  at vent, atmospheres:",
    3: "Vent diameter (m):",
    4: "Vent elevation (m):",
    5: "Initial velocity (m/s):",
    6: "Magma temperature (C):",
    7: "Weight fraction gas:",
    8: "Magma specific heat, (J/kg K):",
    9: "Magma density, (kg/m3):",
    10: "Mixture density (kg/m3):",
    11: "Mass fraction water added:",
    12: "Mass flux, (kg/s):",
    13: "Mass flux of solids, (kg/s):",
}


def _parse_after(line: str, separator: str) -> float:
    _, found, right = line.partition(separator)

    if not found or not right:
        return math.nan

    token = right.strip().split()[0]
    token = token.rstrip(",")
    token = token.replace("D", "E").replace("d", "E")
    token = token.replace(",", "")

    try:
        return float(token)
    except ValueError:
        return math.nan


def parse_plumeria_output(path: str | Path) -> dict[str, float]:
    """
    Parse one Plumeria WD output file.

    Returns the same core fields used by the existing PlumeViz extractor.
    """
    path = Path(path).expanduser()

    values = [math.nan] * len(COLUMNS)
    lines = path.read_text(errors="replace").splitlines()

    for line in lines:
        for index, key in HEADER_KEYS.items():
            if key in line:
                values[index] = _parse_after(line, ":")

    for line in lines:
        if "Maximum height =" in line or "Calculated height =" in line:
            values[14] = _parse_after(line, "=")

        elif "height calculated from Sparks curve" in line:
            values[15] = _parse_after(line, "=")

        elif "height calculated from Mastin et al. (2009, eq. 1)" in line:
            values[16] = _parse_after(line, "=")

    return dict(zip(COLUMNS, values))
