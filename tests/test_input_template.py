from pathlib import Path

import pytest

from plumeviz.io.input_template import (
    write_modified_plumeria_input,
)


def test_template_modifies_only_requested_fields(
    plumeria_template: Path,
    tmp_path: Path,
):
    destination = tmp_path / "modified.inp"
    output = tmp_path / "output.txt"

    original = plumeria_template.read_text()

    write_modified_plumeria_input(
        template_path=plumeria_template,
        destination=destination,
        output_path=output,
        updates={
            "vent_velocity": 123,
            "added_water_fraction": 0.2,
        },
    )

    modified = destination.read_text()

    assert str(output) in modified
    assert "123                 #exit velocity" in modified
    assert "0.2    15.0" in modified

    assert (
        "10.0   0.002   90.0   #wind speed"
        in modified
    )

    assert "0.1 0.2 0.3" in modified

    assert (
        "10.0   0.002   90.0   #wind speed"
        in original
    )


def test_template_rejects_unknown_parameter(
    plumeria_template: Path,
    tmp_path: Path,
):
    with pytest.raises(ValueError):
        write_modified_plumeria_input(
            template_path=plumeria_template,
            destination=tmp_path / "bad.inp",
            output_path=tmp_path / "output.txt",
            updates={
                "not_a_parameter": 1,
            },
        )
