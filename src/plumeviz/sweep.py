from __future__ import annotations

from dataclasses import fields, replace
from itertools import product
from pathlib import Path
from typing import Iterable, Any

import pandas as pd

from plumeviz.io.input_file import PlumeriaInput
from plumeviz.simulation import run_simulation

def adjusted_vent_diameter(
    dry_diameter: float,
    dry_density: float,
    wet_density: float,
    water_fraction: float,
) -> float:

    """calculate vent diameter at constant dry-equivalent mass flux"""
    return dry_diameter * (
        dry_density / (wet_density * (1.0 - water_fraction))) ** 0.5



def run_adjusted_water_series(
    base_config: PlumeriaInput,
    dry_diameter: float,
    water_fractions: Iterable[float],
    executable: str | Path,
    workdir: str | Path,
    *,
    probe_densities: dict[float, float] | None = None,
    timeout: float = 1.0,
) -> pd.DataFrame:
    """run a water series at constant dry-equivalent mass flux"""

    workdir = Path(workdir).expanduser()
    workdir.mkdir(parents=True, exist_ok=True)

    water_fractions = list(water_fractions)

    if any(not 0.0 <= w < 1.0 for w in water_fractions):
        raise ValueError("water fractions must satisfy 0 <= w < 1")

    dry_dir = workdir / "dry"

    dry_config = replace(
        base_config,
        output_path=dry_dir / "output.txt",
        vent_diameter=dry_diameter,
        added_water_fraction=0.0,
    )

    dry_result = run_simulation(
        dry_config,
        executable,
        dry_dir / "input.inp",
        timeout=timeout,
    )

    executed_dry_diameter = dry_diameter
    dry_numerical_retry = False

    if not dry_result.ok:
        output_text = dry_result.run.output_path.read_text(
            errors="ignore"
        )

        if "stepsize is approximately zero" in output_text:
            for label, retry_dry_diameter in (
                ("plus", dry_diameter + 1.0e-4),
                ("minus", dry_diameter - 1.0e-4),
            ):
                if retry_dry_diameter <= 0.0:
                    continue

                retry_dry_dir = workdir / f"dry_retry_{label}"

                retry_dry_config = replace(
                    base_config,
                    output_path=retry_dry_dir / "output.txt",
                    vent_diameter=retry_dry_diameter,
                    added_water_fraction=0.0,
                )

                retry_dry_result = run_simulation(
                    retry_dry_config,
                    executable,
                    retry_dry_dir / "input.inp",
                    timeout=timeout,
                )

                if retry_dry_result.ok:
                    dry_result = retry_dry_result
                    executed_dry_diameter = retry_dry_diameter
                    dry_numerical_retry = True
                    break

        if not dry_result.ok:
            raise RuntimeError("dry reference run failed")

    dry_density = dry_result.values["mixture density (kg/m3)"]
    dry_mass_flux = dry_result.values["mass flux total (kg/s)"]

    rows: list[dict[str, Any]] = []

    rows.append(
        {
            **dry_result.values,
            "executed water fraction": 0.0,
            "numerical retry": False,
            "status": dry_result.run.status,
            "returncode": dry_result.run.returncode,
            "input_path": str(dry_result.run.input_path),
            "output_path": str(dry_result.run.output_path),
            "dry reference diameter (m)": dry_diameter,
            "executed dry diameter (m)": executed_dry_diameter,
            "dry numerical retry": dry_numerical_retry,
            "adjusted vent diameter (m)": dry_diameter,
            "dry mixture density (kg/m3)": dry_density,
            "probe wet mixture density (kg/m3)": dry_density,
            "dry reference mass flux (kg/s)": dry_mass_flux,
            "dry equivalent mass flux (kg/s)": dry_mass_flux,
            "mass flux relative error": 0.0,
        }
    )

    for index, water_fraction in enumerate(water_fractions, start=1):
        if water_fraction == 0.0:
            continue

        adjusted_dir = workdir / f"w_{index:03d}_adjusted"

        if probe_densities is None:
            probe_dir = workdir / f"w_{index:03d}_probe"

            probe_config = replace(
                base_config,
                output_path=probe_dir / "output.txt",
                vent_diameter=dry_diameter,
                added_water_fraction=water_fraction,
            )

            probe_result = run_simulation(
                probe_config,
                executable,
                probe_dir / "input.inp",
                timeout=timeout,
            )

            if not probe_result.ok:
                raise RuntimeError(
                    f"wet probe run failed for w={water_fraction}"
                )

            wet_density = probe_result.values[
                "mixture density (kg/m3)"
            ]
        else:
            try:
                wet_density = probe_densities[water_fraction]
            except KeyError as exc:
                raise ValueError(
                    f"missing probe density for w={water_fraction}"
                ) from exc

        wet_diameter = adjusted_vent_diameter(
            dry_diameter,
            dry_density,
            wet_density,
            water_fraction,
        )

        adjusted_config = replace(
            base_config,
            output_path=adjusted_dir / "output.txt",
            vent_diameter=wet_diameter,
            added_water_fraction=water_fraction,
        )

        adjusted_result = run_simulation(
            adjusted_config,
            executable,
            adjusted_dir / "input.inp",
            timeout=timeout,
        )

        executed_water_fraction = water_fraction
        numerical_retry = False

        if not adjusted_result.ok:
            output_text = adjusted_result.run.output_path.read_text(
                errors="ignore"
            )

            if "stepsize is approximately zero" in output_text:
                for label, retry_water_fraction in (
                    ("plus", water_fraction + 1.0e-4),
                    ("minus", water_fraction - 1.0e-4),
                ):
                    if not 0.0 <= retry_water_fraction < 1.0:
                        continue

                    retry_probe_dir = (
                        workdir
                        / f"w_{index:03d}_retry_{label}_probe"
                    )
                    retry_adjusted_dir = (
                        workdir
                        / f"w_{index:03d}_retry_{label}_adjusted"
                    )

                    retry_probe_config = replace(
                        base_config,
                        output_path=retry_probe_dir / "output.txt",
                        vent_diameter=dry_diameter,
                        added_water_fraction=retry_water_fraction,
                    )

                    retry_probe_result = run_simulation(
                        retry_probe_config,
                        executable,
                        retry_probe_dir / "input.inp",
                        timeout=timeout,
                    )

                    if not retry_probe_result.ok:
                        continue

                    retry_wet_density = retry_probe_result.values[
                        "mixture density (kg/m3)"
                    ]

                    retry_wet_diameter = adjusted_vent_diameter(
                        dry_diameter,
                        dry_density,
                        retry_wet_density,
                        retry_water_fraction,
                    )

                    retry_config = replace(
                        base_config,
                        output_path=retry_adjusted_dir / "output.txt",
                        vent_diameter=retry_wet_diameter,
                        added_water_fraction=retry_water_fraction,
                    )

                    retry_result = run_simulation(
                        retry_config,
                        executable,
                        retry_adjusted_dir / "input.inp",
                        timeout=timeout,
                    )

                    if retry_result.ok:
                        adjusted_result = retry_result
                        wet_density = retry_wet_density
                        wet_diameter = retry_wet_diameter
                        executed_water_fraction = retry_water_fraction
                        numerical_retry = True
                        break

        if not adjusted_result.ok:
            rows.append(
                {
                    "status": adjusted_result.run.status,
                    "returncode": adjusted_result.run.returncode,
                    "input_path": str(adjusted_result.run.input_path),
                    "output_path": str(adjusted_result.run.output_path),
                    "mass fraction water added": water_fraction,
                    "executed water fraction": executed_water_fraction,
                    "numerical retry": numerical_retry,
                    "vent diameter (m)": wet_diameter,
                    "dry reference diameter (m)": dry_diameter,
                    "executed dry diameter (m)": executed_dry_diameter,
                    "dry numerical retry": dry_numerical_retry,
                    "adjusted vent diameter (m)": wet_diameter,
                    "dry mixture density (kg/m3)": dry_density,
                    "probe wet mixture density (kg/m3)": wet_density,
                    "dry reference mass flux (kg/s)": dry_mass_flux,
                    "dry equivalent mass flux (kg/s)": float("nan"),
                    "mass flux relative error": float("nan"),
                    "calculated height (km)": float("nan"),
                }
            )
            continue

        total_mass_flux = adjusted_result.values[
            "mass flux total (kg/s)"
        ]

        dry_equivalent_mass_flux = (
            total_mass_flux * (1.0 - executed_water_fraction)
        )

        relative_error = (
            dry_equivalent_mass_flux - dry_mass_flux
        ) / dry_mass_flux

        rows.append(
            {
                **adjusted_result.values,
                "mass fraction water added": water_fraction,
                "executed water fraction": executed_water_fraction,
                "numerical retry": numerical_retry,
                "status": adjusted_result.run.status,
                "returncode": adjusted_result.run.returncode,
                "input_path": str(adjusted_result.run.input_path),
                "output_path": str(adjusted_result.run.output_path),
                "dry reference diameter (m)": dry_diameter,
                "executed dry diameter (m)": executed_dry_diameter,
                "dry numerical retry": dry_numerical_retry,
                "adjusted vent diameter (m)": wet_diameter,
                "dry mixture density (kg/m3)": dry_density,
                "probe wet mixture density (kg/m3)": wet_density,
                "dry reference mass flux (kg/s)": dry_mass_flux,
                "dry equivalent mass flux (kg/s)": dry_equivalent_mass_flux,
                "mass flux relative error": relative_error,
            }
        )

    return pd.DataFrame(rows)

def run_adjusted_water_sweep(
    base_config: PlumeriaInput,
    dry_diameters: Iterable[float],
    water_fractions: Iterable[float],
    executable: str | Path,
    workdir: str | Path,
    *,
    timeout: float = 1.0,
) -> pd.DataFrame:
    """run adjusted water series across multiple dry vent diameters"""

    workdir = Path(workdir).expanduser()
    workdir.mkdir(parents=True, exist_ok=True)

    dry_diameters = list(dry_diameters)
    water_fractions = list(water_fractions)

    if not dry_diameters:
        raise ValueError("dry diameters cannot be empty")

    if any(not 0.0 <= w < 1.0 for w in water_fractions):
        raise ValueError("water fractions must satisfy 0 <= w < 1")

    probe_densities: dict[float, float] = {}
    probe_diameter = dry_diameters[0]
    probe_root = workdir / "probes"

    for index, water_fraction in enumerate(
        water_fractions,
        start=1,
    ):
        if water_fraction == 0.0:
            continue

        probe_dir = probe_root / f"w_{index:03d}"

        probe_config = replace(
            base_config,
            output_path=probe_dir / "output.txt",
            vent_diameter=probe_diameter,
            added_water_fraction=water_fraction,
        )

        probe_result = run_simulation(
            probe_config,
            executable,
            probe_dir / "input.inp",
            timeout=timeout,
        )

        if not probe_result.ok:
            output_text = probe_result.run.output_path.read_text(
                errors="ignore"
            )

            if "stepsize is approximately zero" in output_text:
                for label, retry_probe_diameter in (
                    ("plus", probe_diameter + 1.0e-4),
                    ("minus", probe_diameter - 1.0e-4),
                ):
                    if retry_probe_diameter <= 0.0:
                        continue

                    retry_probe_dir = (
                        probe_root
                        / f"w_{index:03d}_retry_{label}"
                    )

                    retry_probe_config = replace(
                        base_config,
                        output_path=retry_probe_dir / "output.txt",
                        vent_diameter=retry_probe_diameter,
                        added_water_fraction=water_fraction,
                    )

                    retry_probe_result = run_simulation(
                        retry_probe_config,
                        executable,
                        retry_probe_dir / "input.inp",
                        timeout=timeout,
                    )

                    if retry_probe_result.ok:
                        probe_result = retry_probe_result
                        break

        if not probe_result.ok:
            raise RuntimeError(
                f"wet probe run failed for w={water_fraction}"
            )

        probe_densities[water_fraction] = (
            probe_result.values["mixture density (kg/m3)"]
        )

    frames: list[pd.DataFrame] = []

    for index, dry_diameter in enumerate(
        dry_diameters,
        start=1,
    ):
        diameter_dir = workdir / f"diameter_{index:04d}"

        results = run_adjusted_water_series(
            base_config=base_config,
            dry_diameter=dry_diameter,
            water_fractions=water_fractions,
            executable=executable,
            workdir=diameter_dir,
            probe_densities=probe_densities,
            timeout=timeout,
        )

        frames.append(results)

    return pd.concat(
        frames,
        ignore_index=True,
    )


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
