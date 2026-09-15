from __future__ import annotations

import re

from pathlib import Path
from typing import Any


SUPPORTED_TEMPLATE_PARAMETERS = {
    "vent_diameter": ("vent diameter",),
    "vent_velocity": ("exit velocity",),
    "added_water_fraction": ("mass fraction added water",),
    "magma_temperature": ("magma temperature",),
    "relative_humidity": ("air relative humidity",),
}


def _read_lines(path: Path) -> list[str]:
    with path.open(
        "r",
        encoding="utf-8",
        errors="strict",
        newline="",
    ) as file:
        return file.readlines()


def _write_lines(
    path: Path,
    lines: list[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        file.writelines(lines)


def _format_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:g}"

    return str(value)


def _first_data_line(lines: list[str]) -> int:
    """
    Return the first nonblank, non-comment record.

    In a Plumeria input this is the output-file record.
    """

    for index, line in enumerate(lines):
        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("#"):
            continue

        return index

    raise ValueError(
        "Input file contains no Plumeria data records."
    )


def _find_parameter_line(
    lines: list[str],
    parameter: str,
) -> int:
    markers = SUPPORTED_TEMPLATE_PARAMETERS[parameter]
    matches: list[int] = []

    for index, line in enumerate(lines):
        if "#" not in line:
            continue

        data, _, comment = line.partition("#")

        if not data.strip():
            continue

        comment = comment.strip().lower()

        if any(marker in comment for marker in markers):
            matches.append(index)

    if len(matches) == 0:
        raise ValueError(
            f"Could not locate {parameter!r} in the input file."
        )

    if len(matches) > 1:
        raise ValueError(
            f"Found multiple candidate records for "
            f"{parameter!r}; refusing to guess."
        )

    return matches[0]


def _replace_first_value(
    line: str,
    value: Any,
) -> str:
    """
    Replace only the first value on a Plumeria data record.

    Everything after that first token is preserved, including optional
    values and inline comments.
    """

    match = re.match(
        r"^(\s*)(\S+)(.*?)(\r?\n)?$",
        line,
    )

    if match is None:
        raise ValueError(
            f"Could not modify Plumeria record: {line!r}"
        )

    prefix, _, remainder, newline = match.groups()

    return (
        prefix
        + _format_value(value)
        + remainder
        + (newline or "")
    )


def _replace_output_path(
    line: str,
    output_path: str | Path,
) -> str:
    """
    Replace the output-file record while preserving indentation,
    inline comments, and line ending.
    """

    match = re.match(
        r"^(\s*)(.*?)(\s*(?:#.*)?)(\r?\n)?$",
        line,
    )

    if match is None:
        raise ValueError(
            f"Could not modify output record: {line!r}"
        )

    prefix, _, suffix, newline = match.groups()

    return (
        prefix
        + str(output_path)
        + suffix
        + (newline or "")
    )


def write_modified_plumeria_input(
    template_path: str | Path,
    destination: str | Path,
    output_path: str | Path,
    updates: dict[str, Any],
) -> Path:
    """
    Copy an existing Plumeria input and modify only requested records.

    All untouched records, including atmospheric-file settings, wind
    syntax, optional parameters, comments, and formatting, are preserved.
    """

    template_path = Path(template_path).expanduser()
    destination = Path(destination).expanduser()

    if not template_path.is_file():
        raise FileNotFoundError(
            f"Plumeria input file not found: {template_path}"
        )

    unknown = set(updates) - set(
        SUPPORTED_TEMPLATE_PARAMETERS
    )

    if unknown:
        raise ValueError(
            "Unsupported template parameter(s): "
            + ", ".join(sorted(unknown))
        )

    lines = _read_lines(template_path)

    output_index = _first_data_line(lines)
    lines[output_index] = _replace_output_path(
        lines[output_index],
        output_path,
    )

    for parameter, value in updates.items():
        index = _find_parameter_line(
            lines,
            parameter,
        )

        lines[index] = _replace_first_value(
            lines[index],
            value,
        )

    _write_lines(
        destination,
        lines,
    )

    return destination
