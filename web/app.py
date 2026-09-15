from __future__ import annotations

import math
import tempfile
import matplotlib.pyplot as plt

from pathlib import Path

import pandas as pd
import streamlit as st

from plumeviz.engine.manager import (
    build_plumeria,
    find_plumeria_executable,
)
from plumeviz.io.input_file import PlumeriaInput
from plumeviz.io.profile_parser import parse_plumeria_profile

from plumeviz.plotting.profile import (
    plot_plumeria_profile,
    plot_plumeria_profile_comparison,
)

from plumeviz.simulation import run_simulation
from plumeviz.sweep import run_sweep


st.set_page_config(
    page_title="PlumeViz",
    page_icon="🌀",
    layout="wide",
)


def new_workdir(prefix: str) -> Path:
    return Path(
        tempfile.mkdtemp(
            prefix=f"plumeviz_{prefix}_",
        )
    )


def parse_values(text: str) -> list[float]:
    values = [
        value.strip()
        for value in text.split(",")
        if value.strip()
    ]

    if not values:
        raise ValueError(
            "at least one sweep value is required"
        )

    return [
        float(value)
        for value in values
    ]


def input_widgets(prefix: str) -> dict[str, float | None]:
    left, middle, right = st.columns(3)

    with left:
        vent_diameter = st.number_input(
            "Vent diameter (m)",
            min_value=0.001,
            value=50.0,
            key=f"{prefix}_vent_diameter",
        )

        vent_velocity = st.number_input(
            "Vent velocity (m/s)",
            min_value=0.0,
            value=200.0,
            key=f"{prefix}_vent_velocity",
        )

        magma_temperature = st.number_input(
            "Magma temperature (°C)",
            value=900.0,
            key=f"{prefix}_magma_temperature",
        )

    with middle:
        gas_fraction = st.number_input(
            "Gas fraction",
            min_value=0.0,
            max_value=1.0,
            value=0.03,
            key=f"{prefix}_gas_fraction",
        )

        added_water_fraction = st.number_input(
            "Added water fraction",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            key=f"{prefix}_added_water_fraction",
        )

        added_water_temperature = st.number_input(
            "Added water temperature (°C)",
            value=17.5,
            key=f"{prefix}_added_water_temperature",
        )

    with right:
        relative_humidity = st.number_input(
            "Relative humidity (%)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            key=f"{prefix}_relative_humidity",
        )

        air_temperature = st.number_input(
            "Air temperature at vent (°C)",
            value=0.0,
            key=f"{prefix}_air_temperature",
        )

        vent_elevation = st.number_input(
            "Vent elevation (m)",
            value=0.0,
            key=f"{prefix}_vent_elevation",
        )

    with st.expander("Advanced Settings"):
        a, b, c = st.columns(3)

        with a:
            thermal_lapse_rate = st.number_input(
                "Tropospheric lapse rate (K/m)",
                value=-0.0065,
                format="%.6f",
                key=f"{prefix}_thermal_lapse_rate",
            )

            tropopause_elevation = st.number_input(
                "Tropopause elevation (m)",
                value=11000.0,
                key=f"{prefix}_tropopause_elevation",
            )

            tropopause_thickness = st.number_input(
                "Tropopause thickness (m)",
                value=9000.0,
                key=f"{prefix}_tropopause_thickness",
            )

        with b:
            upper_lapse_rate = st.number_input(
                "Upper lapse rate (K/m)",
                value=0.0016,
                format="%.6f",
                key=f"{prefix}_upper_lapse_rate",
            )

            wind_speed = st.number_input(
                "Wind speed (m/s)",
                min_value=0.0,
                value=0.0,
                key=f"{prefix}_wind_speed",
            )

            wind_direction = st.number_input(
                "Wind direction (° E of N)",
                value=90.0,
                key=f"{prefix}_wind_direction",
            )

        with c:
            use_wind_slope = st.checkbox(
                "Use wind slope",
                key=f"{prefix}_use_wind_slope",
            )

            wind_slope = None

            if use_wind_slope:
                wind_slope = st.number_input(
                    "Wind slope (1/s)",
                    value=0.0,
                    format="%.6f",
                    key=f"{prefix}_wind_slope",
                )

            magma_specific_heat = st.number_input(
                "Magma specific heat (J/kg K)",
                value=1000.0,
                key=f"{prefix}_magma_specific_heat",
            )

            magma_density = st.number_input(
                "Magma density (kg/m³)",
                value=2500.0,
                key=f"{prefix}_magma_density",
            )

    return {
        "vent_diameter": vent_diameter,
        "vent_velocity": vent_velocity,
        "magma_temperature": magma_temperature,
        "gas_fraction": gas_fraction,
        "added_water_fraction": added_water_fraction,
        "added_water_temperature": added_water_temperature,
        "relative_humidity": relative_humidity,
        "air_temperature": air_temperature,
        "thermal_lapse_rate": thermal_lapse_rate,
        "tropopause_elevation": tropopause_elevation,
        "tropopause_thickness": tropopause_thickness,
        "upper_lapse_rate": upper_lapse_rate,
        "wind_speed": wind_speed,
        "wind_direction": wind_direction,
        "wind_slope": wind_slope,
        "vent_elevation": vent_elevation,
        "magma_specific_heat": magma_specific_heat,
        "magma_density": magma_density,
    }


def show_results(values: dict[str, float]) -> None:
    first, second, third = st.columns(3)

    first.metric(
        "Calculated Height",
        f'{values["calculated height (km)"]:.3f} km',
    )

    second.metric(
        "Sparks Height",
        f'{values["sparks height (km)"]:.3f} km',
    )

    third.metric(
        "Mastin et al. 2009 Height",
        f'{values["mastin et al 2009 height (km)"]:.3f} km',
    )

    st.dataframe(
        pd.DataFrame(
            {
                "Quantity": list(values),
                "Value": list(values.values()),
            }
        ),
        hide_index=True,
        use_container_width=True,
    )


st.title("PlumeViz")
st.caption("Plumeria volcanic plume simulations")

executable = find_plumeria_executable()

with st.sidebar:
    st.header("Plumeria Engine")

    if executable is None:
        st.warning("Plumeria is not installed")

        if st.button("Install Plumeria"):
            with st.spinner("Installing Plumeria"):
                executable = build_plumeria()

            st.success("Plumeria installed")
            st.rerun()

    else:
        st.success("Plumeria 3.0.0 ready")
        st.code(str(executable))

single_tab, sweep_tab = st.tabs(
    [
        "Single Run",
        "Small Sweep",
    ]
)


with single_tab:
    st.subheader("Single Run")

    single_values = input_widgets("single")

    if st.button(
        "Run Simulation",
        type="primary",
        disabled=executable is None,
    ):
        workdir = new_workdir("single")

        config = PlumeriaInput(
            output_path=workdir / "output.txt",
            **single_values,
        )

        with st.spinner("Running Plumeria"):
            result = run_simulation(
                config,
                executable,
                workdir / "input.inp",
            )

        if result.ok:
            st.success("Simulation completed")

            profile = parse_plumeria_profile(
                result.run.output_path
            )

            fig = plot_plumeria_profile(
                profile,
                result.values,
            )

            st.pyplot(
                fig,
                use_container_width=True,
            )

            show_results(result.values)

        else:
            st.error(
                f"Simulation failed with status: "
                f"{result.run.status}"
            )

            if result.run.stderr:
                st.code(result.run.stderr)


with sweep_tab:
    st.subheader("Comparison Sweep")
    st.caption(
        "Vary one parameter across a maximum of 10 simulations"
    )

    sweep_values = input_widgets("sweep")

    parameter_labels = {
        "Vent diameter": "vent_diameter",
        "Vent velocity": "vent_velocity",
        "Magma temperature": "magma_temperature",
        "Added water fraction": "added_water_fraction",
        "Relative humidity": "relative_humidity",
    }

    parameter_label = st.selectbox(
        "Sweep parameter",
        list(parameter_labels),
    )

    values_text = st.text_input(
        "Values",
        value="50, 75, 100, 125, 150",
    )

    if st.button(
        "Run Comparison Sweep",
        type="primary",
        disabled=executable is None,
    ):
        try:
            values = parse_values(
                values_text
            )

            if len(values) > 10:
                raise ValueError(
                    "comparison sweeps are limited to 10 runs"
                )

            parameter = parameter_labels[
                parameter_label
            ]

            parameters = {
                parameter: values,
            }

            workdir = new_workdir(
                "comparison"
            )

            base_config = PlumeriaInput(
                output_path=workdir / "unused.txt",
                **sweep_values,
            )

            with st.spinner(
                f"Running {len(values)} simulations"
            ):
                results = run_sweep(
                    base_config=base_config,
                    parameters=parameters,
                    executable=executable,
                    workdir=workdir,
                )

            successful = results[
                results["status"] == "success"
            ].copy()

            if successful.empty:
                st.error(
                    "No simulations completed successfully"
                )

            else:
                profiles = []
                run_labels = []

                for _, row in successful.iterrows():
                    profiles.append(
                        parse_plumeria_profile(
                            row["output_path"]
                        )
                    )

                    run_labels.append(
                        f"{parameter_label} = "
                        f"{row[parameter]:g}"
                    )

                comparison_fig = (
                    plot_plumeria_profile_comparison(
                        profiles,
                        run_labels,
                    )
                )

                st.success(
                    f"{len(successful)} simulations completed"
                )

                st.pyplot(
                    comparison_fig,
                    use_container_width=True,
                )

                st.subheader(
                    "Plume Height Comparison"
                )

                height_fig, height_ax = plt.subplots(
                    figsize=(8, 5)
                )

                height_ax.plot(
                    successful[parameter],
                    successful[
                        "calculated height (km)"
                    ],
                    marker="o",
                    label="Calculated",
                )

                height_ax.plot(
                    successful[parameter],
                    successful[
                        "sparks height (km)"
                    ],
                    marker="o",
                    label="Sparks",
                )

                height_ax.plot(
                    successful[parameter],
                    successful[
                        "mastin et al 2009 height (km)"
                    ],
                    marker="o",
                    label="Mastin et al. 2009",
                )

                height_ax.set_xlabel(
                    parameter_label
                )

                height_ax.set_ylabel(
                    "plume height [km]"
                )

                height_ax.grid(
                    True,
                    linestyle="--",
                    linewidth=0.5,
                )

                height_ax.legend()

                height_fig.tight_layout()

                st.pyplot(
                    height_fig,
                    use_container_width=True,
                )

                with st.expander(
                    "Raw Results"
                ):
                    st.dataframe(
                        results,
                        hide_index=True,
                        use_container_width=True,
                    )

                st.download_button(
                    "Download CSV",
                    data=results.to_csv(
                        index=False,
                    ).encode("utf-8"),
                    file_name=(
                        "plumeviz_comparison.csv"
                    ),
                    mime="text/csv",
                )

        except ValueError as exc:
            st.error(str(exc))
