from plumeviz.parameters import (
    logarithmic_vent_diameters,
)


def test_logarithmic_vent_diameters():
    values = logarithmic_vent_diameters(
        min_diameter=1,
        max_diameter=16,
        points_per_interval=5,
    )

    assert values == [
        1.0,
        1.25,
        1.5,
        1.75,
        2.0,
        2.5,
        3.0,
        3.5,
        4.0,
        5.0,
        6.0,
        7.0,
        8.0,
        10.0,
        12.0,
        14.0,
        16.0,
    ]


def test_logarithmic_vent_diameters_respect_minimum():
    values = logarithmic_vent_diameters(
        min_diameter=5,
        max_diameter=16,
        points_per_interval=3,
    )

    assert min(values) == 5.0
    assert max(values) == 16.0
