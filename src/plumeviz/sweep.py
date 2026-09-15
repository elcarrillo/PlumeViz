from __future__ import annotations

from dataclasses import fields, replace
from itertools import product
from pathlib import Path
from typing import Iterable, Any

import pandas as pd

from plumeviz.io.input_file import PlumeriaInput
from plumeviz.simulation import run_simulation


def run_sweep(
    base_config: PlumeriaInput,
    parameters: dict[str, Iterable[Any]],
    executable: str | Path,
    workdir: str | Path,
    *,
    timeout: float = 1.0,
) -> pd.DataFrame:
    """
    Run a Cartesian parameter sweep of Plumeria simulations.

    Each simulation gets its own directory containing:
        input.inp
        output.txt

    Returns one DataFrame row per simulation.
    """
    workdir = Path(workdir).expanduser()
    workdir.mkdir(parents=True, exist_ok=True)

    valid_fields = {field.name for field in fields(PlumeriaInput)}
    valid_fields.remove("output_path")

    unknown = set(parameters) - valid_fields

    if unknown:
        raise ValueError(
            "Unknown PlumeriaInput parameter(s): "
            + ", ".join(sorted(unknown))
        )

    names = list(parameters)
    values = [list(parameters[name]) for name in names]

    if any(len(value_list) == 0 for value_list in values):
        raise ValueError("Sweep parameter lists cannot be empty!")

    rows: list[dict[str, Any]] = []

    for index, combination in enumerate(product(*values), start=1):
        varied = dict(zip(names, combination))

        run_id = f"run_{index:06d}"
        run_dir = workdir / run_id

        input_path = run_dir / "input.inp"
        output_path = run_dir / "output.txt"

        config = replace(
            base_config,
            output_path=output_path,
            **varied,
        )

        result = run_simulation(
            config,
            executable,
            input_path,
            timeout=timeout,
        )

        row: dict[str, Any] = {
            "run_id": run_id,
            **varied,
            "status": result.run.status,
            "returncode": result.run.returncode,
            "input_path": str(input_path),
            "output_path": str(output_path),
        }

        row.update(result.values)
        rows.append(row)

    return pd.DataFrame(rows)


def export_sweep_csv(
    results: pd.DataFrame,
    path: str | Path,
) -> Path:
    """Write sweep results to CSV and return the output path"""

    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)

    results.to_csv(path, index=False)

    return path

def run_template_sweep(
    template_path: str | Path,
    parameters: dict[str, Iterable[Any]],
    executable: str | Path,
    workdir: str | Path,
    *,
    timeout: float = 1.0,
) -> pd.DataFrame:
    """
    Run a Cartesian sweep from an existing Plumeria input file.

    The original input is preserved. Each run gets a copied input in which
    only the requested sweep parameters and output filename are changed.
    """

    from plumeviz.engine.runner import run_plumeria
    from plumeviz.io.input_template import (
        SUPPORTED_TEMPLATE_PARAMETERS,
        write_modified_plumeria_input,
    )
    from plumeviz.io.output_parser import parse_plumeria_output

    template_path = Path(template_path).expanduser()
    workdir = Path(workdir).expanduser()

    if not template_path.is_file():
        raise FileNotFoundError(
            f"Plumeria input file not found: {template_path}"
        )

    workdir.mkdir(parents=True, exist_ok=True)

    unknown = set(parameters) - set(
        SUPPORTED_TEMPLATE_PARAMETERS
    )

    if unknown:
        raise ValueError(
            "Unsupported template sweep parameter(s): "
            + ", ".join(sorted(unknown))
        )

    names = list(parameters)
    values = [list(parameters[name]) for name in names]

    if any(len(value_list) == 0 for value_list in values):
        raise ValueError(
            "Sweep parameter lists cannot be empty"
        )

    rows: list[dict[str, Any]] = []

    for index, combination in enumerate(
        product(*values),
        start=1,
    ):
        varied = dict(zip(names, combination))

        run_id = f"run_{index:06d}"
        run_dir = workdir / run_id

        input_path = run_dir / "input.inp"
        output_path = run_dir / "output.txt"

        write_modified_plumeria_input(
            template_path=template_path,
            destination=input_path,
            output_path=output_path,
            updates=varied,
        )

        run = run_plumeria(
            executable,
            input_path,
            output_path,
            timeout=timeout,
        )

        row: dict[str, Any] = {
            "run_id": run_id,
            **varied,
            "status": run.status,
            "returncode": run.returncode,
            "input_path": str(input_path),
            "output_path": str(output_path),
        }

        if run.ok:
            row.update(
                parse_plumeria_output(output_path)
            )

        rows.append(row)

    return pd.DataFrame(rows)
