from pathlib import Path

import pytest

from plumeviz.engine.manager import find_plumeria_executable
from plumeviz.io.input_file import PlumeriaInput
from plumeviz.simulation import run_simulation


pytestmark = pytest.mark.integration


def test_managed_engine_known_good_case(tmp_path: Path):
    executable = find_plumeria_executable()

    if executable is None:
        pytest.skip("managed plumeria engine not installed")

    config = PlumeriaInput(
        output_path=tmp_path / "output.txt",
        vent_diameter=10,
        vent_velocity=100,
        magma_temperature=900,
        added_water_fraction=0.2,
    )

    result = run_simulation(
        config,
        executable,
        tmp_path / "input.inp",
    )

    assert result.ok
    assert result.run.returncode == 0
    assert result.values["calculated height (km)"] == pytest.approx(2.069)
    assert result.values["sparks height (km)"] == pytest.approx(2.537)
    assert result.values["mastin et al 2009 height (km)"] == pytest.approx(2.951)
