from pathlib import Path
from types import SimpleNamespace

import plumeviz.engine.runner as runner_module
import plumeviz.io.output_parser as output_parser_module

from plumeviz.io.input_file import PlumeriaInput
from plumeviz.sweep import (
    run_sweep,
    run_template_sweep,
)


def test_generated_cartesian_sweep(
    monkeypatch,
    tmp_path: Path,
):
    captured = []

    def fake_run_simulation(
        config,
        executable,
        input_path,
        timeout,
    ):
        captured.append(config)

        return SimpleNamespace(
            run=SimpleNamespace(
                status="success",
                returncode=0,
            ),
            values={
                "calculated height (km)": 1.0,
            },
        )

    monkeypatch.setattr(
        "plumeviz.sweep.run_simulation",
        fake_run_simulation,
    )

    base = PlumeriaInput(
        output_path=tmp_path / "unused.txt",
        vent_diameter=10,
        vent_velocity=100,
        magma_temperature=900,
    )

    results = run_sweep(
        base_config=base,
        parameters={
            "vent_velocity": [75, 100],
            "added_water_fraction": [0.0, 0.2],
        },
        executable="fake",
        workdir=tmp_path / "runs",
    )

    assert len(results) == 4

    assert set(
        zip(
            results["vent_velocity"],
            results["added_water_fraction"],
        )
    ) == {
        (75, 0.0),
        (75, 0.2),
        (100, 0.0),
        (100, 0.2),
    }

    assert len(captured) == 4


def test_template_cartesian_sweep(
    monkeypatch,
    plumeria_template: Path,
    tmp_path: Path,
):
    def fake_run_plumeria(
        executable,
        input_path,
        output_path,
        timeout,
    ):
        return SimpleNamespace(
            status="success",
            returncode=0,
            ok=True,
        )

    monkeypatch.setattr(
        runner_module,
        "run_plumeria",
        fake_run_plumeria,
    )

    monkeypatch.setattr(
        output_parser_module,
        "parse_plumeria_output",
        lambda path: {
            "calculated height (km)": 1.0,
        },
    )

    workdir = tmp_path / "template_runs"

    results = run_template_sweep(
        template_path=plumeria_template,
        parameters={
            "vent_velocity": [75, 100],
            "added_water_fraction": [0.0, 0.2],
        },
        executable="fake",
        workdir=workdir,
    )

    assert len(results) == 4
    assert set(results["status"]) == {"success"}

    fourth_input = (
        workdir
        / "run_000004"
        / "input.inp"
    ).read_text()

    assert "100" in fourth_input
    assert "0.2    15.0" in fourth_input
    assert "10.0   0.002   90.0" in fourth_input
