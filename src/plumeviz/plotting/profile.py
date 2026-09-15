from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.figure import Figure


def plot_plumeria_profile(
    profile: pd.DataFrame,
    summary: dict[str, float] | None = None,
) -> Figure:
    """plot vertical plumeria solution profiles"""

    z = profile["z"] / 1000.0
    temperature = profile["T_mix"] - 273.15

    vapor = np.where(
        profile["m_w"] > 0,
        profile["m_w"],
        np.nan,
    )

    air = np.where(
        profile["m_a"] > 0,
        profile["m_a"],
        np.nan,
    )

    liquid = np.where(
        profile["m_l"] > 0,
        profile["m_l"],
        np.nan,
    )

    ice = np.where(
        profile["m_i"] > 0,
        profile["m_i"],
        np.nan,
    )

    fig, axes = plt.subplots(
        1,
        5,
        figsize=(15, 7),
        sharey=True,
    )

    axes[0].plot(
        profile["u"],
        z,
        linewidth=2,
    )

    axes[1].plot(
        temperature,
        z,
        linewidth=2,
    )

    axes[2].plot(
        profile["rho_mix"],
        z,
        linewidth=2,
        label=r"$\rho_m$",
    )

    axes[2].plot(
        profile["rho_air"],
        z,
        linewidth=2,
        label=r"$\rho_a$",
    )

    axes[3].semilogx(
        vapor,
        z,
        linewidth=2,
        label=r"$m_v$",
    )

    axes[3].semilogx(
        air,
        z,
        linewidth=2,
        label=r"$m_a$",
    )

    axes[4].semilogx(
        liquid,
        z,
        linewidth=2,
        label=r"$m_l$",
    )

    axes[4].semilogx(
        ice,
        z,
        linewidth=2,
        label=r"$m_i$",
    )

    labels = [
        r"$u$ [m/s]",
        r"$T_{mix}$ [°C]",
        r"$\rho$ [kg/m³]",
        "mass fraction, vapor & air",
        "mass fraction, liquid & ice",
    ]

    for axis, label in zip(axes, labels):
        axis.set_xlabel(label)
        axis.grid(
            True,
            linestyle="--",
            linewidth=0.5,
        )
        axis.minorticks_on()
        axis.tick_params(
            axis="both",
            direction="in",
        )

    axes[0].set_ylabel(
        "height above vent [km]"
    )

    axes[2].legend()
    axes[3].legend()
    axes[4].legend()

    axes[3].set_xlim(
        left=1e-7,
        right=1.1,
    )

    axes[4].set_xlim(
        left=1e-7,
        right=1.1,
    )

    if summary is not None:
        mass_flux = summary.get(
            "mass flux total (kg/s)"
        )

        diameter = summary.get(
            "vent diameter (m)"
        )

        title_parts = []

        if mass_flux is not None:
            title_parts.append(
                f"MER = {mass_flux:.3g} kg/s"
            )

        if diameter is not None:
            title_parts.append(
                f"d = {diameter:g} m"
            )

        if title_parts:
            fig.suptitle(
                ", ".join(title_parts)
            )

    fig.tight_layout()

    return fig


def plot_plumeria_profile_comparison(
    profiles: list[pd.DataFrame],
    labels: list[str],
) -> Figure:
    """plot multiple vertical plumeria solutions for comparison"""

    if len(profiles) != len(labels):
        raise ValueError(
            "profiles and labels must have the same length"
        )

    if not profiles:
        raise ValueError(
            "at least one profile is required"
        )

    fig, axes = plt.subplots(
        1,
        5,
        figsize=(15, 7),
        sharey=True,
    )

    for profile, label in zip(
        profiles,
        labels,
    ):
        z = profile["z"] / 1000.0
        temperature = profile["T_mix"] - 273.15

        line = axes[0].plot(
            profile["u"],
            z,
            linewidth=2,
            label=label,
        )[0]

        color = line.get_color()

        axes[1].plot(
            temperature,
            z,
            linewidth=2,
            color=color,
        )

        axes[2].plot(
            profile["rho_mix"],
            z,
            linewidth=2,
            color=color,
        )

        axes[2].plot(
            profile["rho_air"],
            z,
            linewidth=1.5,
            linestyle="--",
            color=color,
        )

        vapor = np.where(
            profile["m_w"] > 0,
            profile["m_w"],
            np.nan,
        )

        air = np.where(
            profile["m_a"] > 0,
            profile["m_a"],
            np.nan,
        )

        liquid = np.where(
            profile["m_l"] > 0,
            profile["m_l"],
            np.nan,
        )

        ice = np.where(
            profile["m_i"] > 0,
            profile["m_i"],
            np.nan,
        )

        axes[3].semilogx(
            vapor,
            z,
            linewidth=2,
            color=color,
        )

        axes[3].semilogx(
            air,
            z,
            linewidth=1.5,
            linestyle="--",
            color=color,
        )

        axes[4].semilogx(
            liquid,
            z,
            linewidth=2,
            color=color,
        )

        axes[4].semilogx(
            ice,
            z,
            linewidth=1.5,
            linestyle="--",
            color=color,
        )

    labels_x = [
        r"$u$ [m/s]",
        r"$T_{mix}$ [°C]",
        r"$\rho$ [kg/m³]",
        "mass fraction, vapor & air",
        "mass fraction, liquid & ice",
    ]

    for axis, label in zip(
        axes,
        labels_x,
    ):
        axis.set_xlabel(label)
        axis.grid(
            True,
            linestyle="--",
            linewidth=0.5,
        )
        axis.minorticks_on()
        axis.tick_params(
            axis="both",
            direction="in",
        )

    axes[0].set_ylabel(
        "height above vent [km]"
    )

    axes[3].set_xlim(
        left=1e-7,
        right=1.1,
    )

    axes[4].set_xlim(
        left=1e-7,
        right=1.1,
    )

    axes[0].legend(
        title="runs",
    )

    axes[2].text(
        0.04,
        0.96,
        "solid: mixture\n--: atmosphere",
        transform=axes[2].transAxes,
        va="top",
    )

    axes[3].text(
        0.04,
        0.96,
        "solid: vapor\n--: air",
        transform=axes[3].transAxes,
        va="top",
    )

    axes[4].text(
        0.04,
        0.96,
        "solid: liquid\n--: ice",
        transform=axes[4].transAxes,
        va="top",
    )

    fig.tight_layout()

    return fig
