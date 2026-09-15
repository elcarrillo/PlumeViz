from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PlumeriaInput:
    output_path: str | Path

    vent_diameter: float
    vent_velocity: float
    magma_temperature: float

    gas_fraction: float = 0.03
    added_water_fraction: float = 0.0
    added_water_temperature: float = 17.5
    relative_humidity: float = 0.0

    air_temperature: float = 0.0
    thermal_lapse_rate: float = -0.0065
    tropopause_elevation: float = 11000.0
    tropopause_thickness: float = 9000.0
    upper_lapse_rate: float = 0.0016

    wind_speed: float = 0.0
    wind_direction: float = 90.0

    vent_elevation: float = 0.0
    magma_specific_heat: float = 1000.0
    magma_density: float = 2500.0


def render_plumeria_input(config: PlumeriaInput) -> str:
    """Render one Plumeria WD input file."""
    lines = [
        "#  Input file for the Fortran version of Plumeria.",
        "#  Lines that begin with a '#' are comment lines.",
        "",
        "#  Output file name",
        str(config.output_path),
        "",
        "#  Information on whether to read met. input file.",
        "#  The first line should supply a yes or no. If that line is yes, the next line",
        "#  should be the name of the input file used.",
        "no                                #are you supplying a file of atmospheric properties?",
        "",
        " #",
        "#  Tropospheric properties (used only if no atmospheric file is used)",
        "",
        f"{config.air_temperature}                   #Air temperature at vent, Celsius.",
        f"{config.relative_humidity:g}            #Air relative humidity",
        f"{config.thermal_lapse_rate}              #thermal lapse rate in troposphere (K/m upward--should be negative)",
        f"{config.tropopause_elevation}               #Elevation of tropopause (m asl)",
        f"{config.tropopause_thickness}               #Tropopause thickness, m",
        f"{config.upper_lapse_rate}               #thermal lapse rate above tropopause (K/m--should be positive)",
        f"{config.wind_speed}   {config.wind_direction}          #wind speed, m/s, [optional wind slope, m/s per m], wind dir (deg. E of N)",
        "",
        "#  Vent properties",
        "",
        f"{config.vent_elevation}                            #Vent elevation (m asl)",
        f"{config.vent_diameter}                #vent diameter (m)",
        f"{config.vent_velocity}                 #exit velocity (m/s)",
        f"{config.added_water_fraction}  {config.added_water_temperature}                 #mass fraction added water",
        "",
        "#   Magma properties",
        "",
        f"{config.magma_temperature}                 #magma temperature",
        f"{config.gas_fraction}                 #mass fraction gas in magma",
        f"{config.magma_specific_heat}                #magma specific heat, J/kg K",
        f"{config.magma_density}                #magma density (DRE), kg/m3",
    ]

    return "\n".join(lines) + "\n"


def write_plumeria_input(
    path: str | Path,
    config: PlumeriaInput,
) -> Path:
    """Write one Plumeria WD input file and return its path."""
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_plumeria_input(config), encoding="utf-8")
    return path
