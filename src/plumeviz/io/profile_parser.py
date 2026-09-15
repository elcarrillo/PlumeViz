from __future__ import annotations

from pathlib import Path

import pandas as pd


PROFILE_COLUMNS = [
    "i",
    "s",
    "z",
    "x",
    "y",
    "m_m",
    "m_a",
    "m_w",
    "m_l",
    "m_i",
    "v",
    "u",
    "r",
    "T_mix",
    "T_air",
    "rho_mix",
    "rho_air",
    "time",
    "p_air",
    "water",
    "ice",
]


def parse_plumeria_profile(
    path: str | Path,
) -> pd.DataFrame:
    """parse the vertical profile block from plumeria output"""

    path = Path(path).expanduser()

    if not path.is_file():
        raise FileNotFoundError(
            f"plumeria output file not found: {path}"
        )

    lines = path.read_text(
        encoding="utf-8",
        errors="ignore",
    ).splitlines()

    header_index = None

    for index, line in enumerate(lines):
        fields = line.split()

        if (
            fields[:5] == ["i", "s", "z", "x", "y"]
            and "rho_mix" in fields
            and "p_air" in fields
        ):
            header_index = index
            break

    if header_index is None:
        raise ValueError(
            "plumeria profile header not found"
        )

    rows: list[list[float]] = []

    for line in lines[header_index + 2:]:
        fields = line.split()

        if len(fields) != len(PROFILE_COLUMNS):
            if rows:
                break

            continue

        try:
            row = [float(value) for value in fields]
        except ValueError:
            if rows:
                break

            continue

        rows.append(row)

    if not rows:
        raise ValueError(
            "no plumeria profile data found"
        )

    return pd.DataFrame(
        rows,
        columns=PROFILE_COLUMNS,
    )
