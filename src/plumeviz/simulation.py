from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from plumeviz.engine.runner import RunResult, run_plumeria
from plumeviz.io.input_file import PlumeriaInput, write_plumeria_input
from plumeviz.io.output_parser import parse_plumeria_output


@dataclass(frozen=True)
class SimulationResult:
    run: RunResult
    values: dict[str, float]

    @property
    def ok(self) -> bool:
        return self.run.ok


def run_simulation(
    config: PlumeriaInput,
    executable: str | Path,
    input_path: str | Path,
    *,
    timeout: float = 1.0,
) -> SimulationResult:
    """
    Generate, run, and parse one Plumeria simulation.
    """
    input_path = Path(input_path).expanduser()
    output_path = Path(config.output_path).expanduser()

    write_plumeria_input(input_path, config)

    run = run_plumeria(
        executable,
        input_path,
        output_path,
        timeout=timeout,
    )

    values = {}

    if run.ok:
        values = parse_plumeria_output(output_path)

    return SimulationResult(
        run=run,
        values=values,
    )
