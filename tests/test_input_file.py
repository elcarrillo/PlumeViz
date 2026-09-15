from plumeviz.io.input_file import (
    PlumeriaInput,
    render_plumeria_input,
)


def base_config(**updates):
    values = {
        "output_path": "output.txt",
        "vent_diameter": 10,
        "vent_velocity": 100,
        "magma_temperature": 900,
    }

    values.update(updates)

    return PlumeriaInput(**values)


def wind_line(text: str) -> str:
    return next(
        line
        for line in text.splitlines()
        if "#wind speed" in line
    )


def test_generated_input_without_wind_slope():
    line = wind_line(
        render_plumeria_input(base_config())
    )

    assert line.startswith("0.0   90.0")


def test_generated_input_with_wind_slope():
    line = wind_line(
        render_plumeria_input(
            base_config(wind_slope=0.002)
        )
    )

    assert line.startswith(
        "0.0   0.002   90.0"
    )


def test_generated_water_line_contains_temperature():
    text = render_plumeria_input(
        base_config(
            added_water_fraction=0.2,
            added_water_temperature=15.0,
        )
    )

    line = next(
        line
        for line in text.splitlines()
        if "#mass fraction added water" in line
    )

    assert line.split("#", 1)[0].split() == [
        "0.2",
        "15.0",
    ]
