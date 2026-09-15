from __future__ import annotations

import argparse
import sys

from pathlib import Path

from plumeviz.engine.manager import (
    PLUMERIA_VERSION,
    build_plumeria,
    find_plumeria_executable,
)
from plumeviz.io.input_file import PlumeriaInput
from plumeviz.simulation import run_simulation
from plumeviz.sweep import export_sweep_csv, run_sweep


def _add_input_arguments(
    parser: argparse.ArgumentParser,
    *,
    required_core: bool,
) -> None:
    parser.add_argument(
        "--vent-diameter",
        type=float,
        required=required_core,
        help="Vent diameter in meters.",
    )
    parser.add_argument(
        "--vent-velocity",
        type=float,
        required=required_core,
        help="Vent exit velocity in m/s.",
    )
    parser.add_argument(
        "--magma-temperature",
        type=float,
        required=required_core,
        help="Magma temperature in Celsius.",
    )

    parser.add_argument("--gas-fraction", type=float, default=0.03)
    parser.add_argument("--added-water-fraction", type=float, default=0.0)
    parser.add_argument("--added-water-temperature", type=float, default=17.5)

    parser.add_argument("--relative-humidity", type=float, default=0.0)
    parser.add_argument("--air-temperature", type=float, default=0.0)
    parser.add_argument("--thermal-lapse-rate", type=float, default=-0.0065)

    parser.add_argument("--tropopause-elevation", type=float, default=11000.0)
    parser.add_argument("--tropopause-thickness", type=float, default=9000.0)
    parser.add_argument("--upper-lapse-rate", type=float, default=0.0016)

    parser.add_argument("--wind-speed", type=float, default=0.0)
    parser.add_argument("--wind-direction", type=float, default=90.0)

    parser.add_argument("--vent-elevation", type=float, default=0.0)

    parser.add_argument("--magma-specific-heat", type=float, default=1000.0)
    parser.add_argument("--magma-density", type=float, default=2500.0)

    parser.add_argument(
        "--executable",
        type=Path,
        help="Override the Plumeria executable.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=1.0,
        help="Maximum runtime per simulation in seconds.",
    )


def _resolve_executable(
    explicit: Path | None,
) -> Path:
    executable = find_plumeria_executable(explicit)

    if executable is None:
        raise RuntimeError(
            "No Plumeria executable found. "
            "Run 'plumeviz engine install' first."
        )

    return executable


def _config_from_args(
    args: argparse.Namespace,
    output_path: Path,
    parameters: dict[str, list[float]] | None = None,
) -> PlumeriaInput:
    parameters = parameters or {}

    core_values = {}

    for name in (
        "vent_diameter",
        "vent_velocity",
        "magma_temperature",
    ):
        value = getattr(args, name)

        if value is None:
            varied = parameters.get(name)

            if varied:
                value = varied[0]
            else:
                option = name.replace("_", "-")
                raise ValueError(
                    f"--{option} is required unless {name} "
                    "is supplied with --vary."
                )

        core_values[name] = value

    return PlumeriaInput(
        output_path=output_path,
        vent_diameter=core_values["vent_diameter"],
        vent_velocity=core_values["vent_velocity"],
        magma_temperature=core_values["magma_temperature"],
        gas_fraction=args.gas_fraction,
        added_water_fraction=args.added_water_fraction,
        added_water_temperature=args.added_water_temperature,
        relative_humidity=args.relative_humidity,
        air_temperature=args.air_temperature,
        thermal_lapse_rate=args.thermal_lapse_rate,
        tropopause_elevation=args.tropopause_elevation,
        tropopause_thickness=args.tropopause_thickness,
        upper_lapse_rate=args.upper_lapse_rate,
        wind_speed=args.wind_speed,
        wind_direction=args.wind_direction,
        vent_elevation=args.vent_elevation,
        magma_specific_heat=args.magma_specific_heat,
        magma_density=args.magma_density,
    )


def _parse_variations(
    items: list[str],
) -> dict[str, list[float]]:
    parameters: dict[str, list[float]] = {}

    for item in items:
        if "=" not in item:
            raise ValueError(
                f"Invalid --vary value {item!r}. "
                "Use name=value1,value2,..."
            )

        name, raw_values = item.split("=", 1)
        name = name.strip().replace("-", "_")

        if not name:
            raise ValueError("Sweep parameter name cannot be empty.")

        parts = [
            value.strip()
            for value in raw_values.split(",")
            if value.strip()
        ]

        if not parts:
            raise ValueError(
                f"No values supplied for sweep parameter {name!r}."
            )

        try:
            values = [float(value) for value in parts]
        except ValueError as exc:
            raise ValueError(
                f"All values for {name!r} must be numeric."
            ) from exc

        parameters[name] = values

    return parameters


def _engine_status(args: argparse.Namespace) -> int:
    executable = find_plumeria_executable(
        version=args.version,
    )

    print(f"plumeria version: {args.version}")

    if executable is None:
        print("executable: not found")
        return 1

    print(f"executable: {executable}")
    return 0


def _engine_install(args: argparse.Namespace) -> int:
    executable = build_plumeria(
        version=args.version,
        force=args.force,
    )

    print(f"installed plumeria {args.version}")
    print(f"executable: {executable}")

    return 0


def _run(args: argparse.Namespace) -> int:
    executable = _resolve_executable(args.executable)

    workdir = args.workdir.expanduser()
    workdir.mkdir(parents=True, exist_ok=True)

    input_path = workdir / "input.inp"
    output_path = workdir / "output.txt"

    config = _config_from_args(
        args,
        output_path,
    )

    result = run_simulation(
        config,
        executable,
        input_path,
        timeout=args.timeout,
    )

    print(f"status: {result.run.status}")
    print(f"returncode: {result.run.returncode}")
    print(f"input: {input_path}")
    print(f"output: {output_path}")

    for name, value in result.values.items():
        print(f"{name}: {value}")

    return 0 if result.run.status == "success" else 1


def _sweep(args: argparse.Namespace) -> int:
    executable = _resolve_executable(args.executable)

    parameters = _parse_variations(args.vary)

    workdir = args.workdir.expanduser()

    config = _config_from_args(
        args,
        workdir / "unused.txt",
        parameters,
    )

    results = run_sweep(
        base_config=config,
        parameters=parameters,
        executable=executable,
        workdir=workdir,
        timeout=args.timeout,
    )

    print(f"runs: {len(results)}")
    print()
    print(results.to_string(index=False))

    if args.csv is not None:
        path = export_sweep_csv(
            results,
            args.csv,
        )
        print()
        print(f"csv: {path}")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="plumeviz",
        description="Run and manage Plumeria volcanic plume simulations.",
    )

    commands = parser.add_subparsers(
        dest="command",
        required=True,
    )

    engine_parser = commands.add_parser(
        "engine",
        help="Manage the Plumeria simulation engine.",
    )

    engine_commands = engine_parser.add_subparsers(
        dest="engine_command",
        required=True,
    )

    status_parser = engine_commands.add_parser(
        "status",
        help="Show the active Plumeria engine.",
    )
    status_parser.add_argument(
        "--version",
        default=PLUMERIA_VERSION,
        help=f"Plumeria version (default: {PLUMERIA_VERSION}).",
    )
    status_parser.set_defaults(func=_engine_status)

    install_parser = engine_commands.add_parser(
        "install",
        help="Fetch, patch, and build Plumeria.",
    )
    install_parser.add_argument(
        "--version",
        default=PLUMERIA_VERSION,
        help=f"Plumeria version (default: {PLUMERIA_VERSION}).",
    )
    install_parser.add_argument(
        "--force",
        action="store_true",
        help="Refetch and rebuild the engine.",
    )
    install_parser.set_defaults(func=_engine_install)

    run_parser = commands.add_parser(
        "run",
        help="Run one Plumeria simulation.",
    )
    _add_input_arguments(
        run_parser,
        required_core=True,
    )
    run_parser.add_argument(
        "--workdir",
        type=Path,
        default=Path("plumeviz_run"),
        help="Simulation working directory.",
    )
    run_parser.set_defaults(func=_run)

    sweep_parser = commands.add_parser(
        "sweep",
        help="Run a Cartesian parameter sweep.",
    )
    _add_input_arguments(
        sweep_parser,
        required_core=False,
    )
    sweep_parser.add_argument(
        "--vary",
        action="append",
        required=True,
        metavar="NAME=VALUES",
        help=(
            "Sweep parameter and comma-separated values. "
            "May be supplied multiple times."
        ),
    )
    sweep_parser.add_argument(
        "--workdir",
        type=Path,
        default=Path("plumeviz_sweep"),
        help="Sweep working directory.",
    )
    sweep_parser.add_argument(
        "--csv",
        type=Path,
        help="Optional CSV output path.",
    )
    sweep_parser.set_defaults(func=_sweep)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        return args.func(args)
    except (RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
