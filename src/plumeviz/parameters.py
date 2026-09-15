from __future__ import annotations

import math

import numpy as np


def logarithmic_vent_diameters(
    min_diameter: float,
    max_diameter: float,
    points_per_interval: int,
) -> list[float]:
    """
    Generate vent diameters using logarithmically increasing intervals.

    The diameter domain is divided into powers-of-two intervals, with
    linearly spaced values generated inside each interval.

    For example:

        1--2 m
        2--4 m
        4--8 m
        8--16 m

    Duplicate interval boundaries are removed from the final result.
    """

    if min_diameter <= 0:
        raise ValueError("min_diameter must be greater than zero.")

    if max_diameter < min_diameter:
        raise ValueError("max_diameter must be >= min_diameter.")

    if points_per_interval < 2:
        raise ValueError("points_per_interval must be at least 2.")

    interval_max_exponent = math.ceil(math.log2(max_diameter))

    diameters: list[float] = []

    for exponent in range(1, interval_max_exponent + 1):
        interval_min = 1.0 if exponent == 1 else 2.0 ** (exponent - 1)
        interval_max = min(2.0**exponent, max_diameter)

        if interval_max < min_diameter:
            continue

        interval_min = max(interval_min, min_diameter)

        values = np.linspace(
            interval_min,
            interval_max,
            points_per_interval,
        )

        diameters.extend(np.round(values, 4))

    return sorted(set(float(value) for value in diameters))
