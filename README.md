# PlumeViz

[![DOI](https://zenodo.org/badge/818824604.svg)](https://zenodo.org/doi/10.5281/zenodo.13685923)

## Overview

PlumeViz is a Python interface for running, processing, and visualizing one-dimensional volcanic plume simulations with the USGS **Plumeria** model.

The current version provides:

- a Python API for constructing and running Plumeria simulations
- a command-line interface for single runs and parameter sweeps
- support for modifying and running existing Plumeria input files
- automatic parsing of Plumeria summary and vertical-profile output
- profile plotting utilities
- a lightweight web interface for single runs and small comparison sweeps
- managed installation and execution of a supported Plumeria engine

PlumeViz is designed to make Plumeria easier to use without replacing the underlying model. The core package handles input generation, model execution, output parsing, parameter studies, and visualization while preserving direct access to Plumeria input and output files.

## Why Plumes Matter

Volcanic plumes transport ash, gases, water, and heat through the atmosphere. Their dynamics influence eruption hazards, aviation safety, atmospheric transport, and the climatic effects of large eruptions.

One-dimensional plume models provide an efficient way to explore how vent conditions, atmospheric properties, entrainment, and external water affect plume evolution and maximum height.

The 2022 Hunga eruption at Hunga Tonga-Hunga Ha'apai provides an especially striking example of a water-rich volcanic plume reaching the stratosphere.

<figure>
    <figcaption>2022 Hunga eruption plume</figcaption>
    <img src="tonga_plume.gif" alt="2022 Hunga eruption plume" width="300"/>
    <figcaption>
        <small>
            GIF source:
            <a href="https://www.jma.go.jp/jma/kishou/info/coment.html">
                Japan Meteorological Agency
            </a>
        </small>
    </figcaption>
</figure>

## Features

### Single simulations

Generate a Plumeria input file, execute the model, parse the output, and inspect the resulting plume solution.

### Parameter sweeps

Run Cartesian parameter sweeps from the command line or Python API and export the resulting simulation summaries to CSV.

### Existing Plumeria input files

PlumeViz can modify selected parameters in an existing Plumeria input file while preserving the rest of the file. This allows existing Plumeria configurations, including files using external atmospheric data, to remain usable.


### Web interface

The included web interface provides a deliberately lightweight interface for interactive Plumeria use.

It supports:

- single simulations with vertical-profile plots
- comparison sweeps varying one parameter
- up to 10 simulations per comparison
- layered plume-profile plots
- plume-height comparisons
- CSV export

Larger parameter studies are better handled through the command-line interface or Python API.

## Installation

Clone the repository:

```bash
git clone https://github.com/elcarrillo/PlumeViz.git
cd PlumeViz
````

Create and activate a virtual environment:

### macOS/Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

### Windows

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

Install PlumeViz:

```bash
python -m pip install -e .
```

For the web interface:

```bash
python -m pip install -e '.[web]'
```

For development and testing:

```bash
python -m pip install -e '.[dev]'
```

PlumeViz requires Python 3.10 or newer.

## Plumeria Engine

PlumeViz can manage a supported copy of the USGS Plumeria model.

Check the current engine status:

```bash
plumeviz engine status
```

Install the managed Plumeria engine:

```bash
plumeviz engine install
```

The current managed engine targets Plumeria 3.0.0.

Building the managed engine requires the standard Plumeria build tools, including `make` and `gfortran`.

PlumeViz can also use an explicitly supplied Plumeria executable instead of the managed engine.

## Command-Line Interface

### Single Run

A basic simulation can be run with:

```bash
plumeviz run \
    --vent-diameter 10 \
    --vent-velocity 100 \
    --magma-temperature 900 \
    --added-water-fraction 0.2 \
    --workdir results/example_run
```

The command writes the Plumeria input and output files and reports the parsed simulation results.

### Parameter Sweep

Multiple parameter values can be explored with:

```bash
plumeviz sweep \
    --vary vent_velocity=75,100,125 \
    --vary added_water_fraction=0,0.1,0.2 \
    --workdir results/example_sweep \
    --csv results/example_sweep/results.csv
```

PlumeViz evaluates the Cartesian product of the supplied parameter values.

### Existing Input File

An existing Plumeria input file can also be used as the basis of a sweep:

```bash
plumeviz sweep \
    --input path/to/input.inp \
    --vary vent_velocity=75,100,125 \
    --vary added_water_fraction=0,0.1,0.2 \
    --workdir results/template_sweep \
    --csv results/template_sweep/results.csv
```

Only the requested parameters and output location are modified. Other records in the original input file are preserved.

## Web Interface

Install the web dependencies:

```bash
python -m pip install -e '.[web]'
```

Launch PlumeViz:

```bash
streamlit run web/app.py
```

The application will open in a local web browser.

The web interface is intended for interactive exploration rather than large batch studies. Single simulations produce full vertical-profile plots, while comparison sweeps can overlay up to 10 plume solutions.

## Python API

A simulation can also be constructed directly in Python:

```python
from plumeviz.engine.manager import find_plumeria_executable
from plumeviz.io.input_file import PlumeriaInput
from plumeviz.simulation import run_simulation


executable = find_plumeria_executable()

config = PlumeriaInput(
    output_path="results/output.txt",
    vent_diameter=10,
    vent_velocity=100,
    magma_temperature=900,
    added_water_fraction=0.2,
)

result = run_simulation(
    config=config,
    executable=executable,
    input_path="results/input.inp",
)

print(result.values)
```

The full vertical plume profile can be parsed separately:

```python
from plumeviz.io.profile_parser import parse_plumeria_profile


profile = parse_plumeria_profile(
    "results/output.txt"
)

print(profile.head())
```

## Core Repository Structure

```text
PlumeViz/
├── src/
│   └── plumeviz/
│       ├── engine/
│       ├── io/
│       ├── plotting/
│       ├── cli.py
│       ├── parameters.py
│       ├── simulation.py
│       └── sweep.py
├── web/
│   └── app.py
├── tests/
├── legacy/
├── pyproject.toml
├── README.md
└── LICENSE
```

The current PlumeViz package is contained in `src/plumeviz`.

Older PlumeViz code retained for historical reference is stored under `legacy/` and is not part of the current package API.

## Testing

Run the standard test suite with:

```bash
python -m pytest -v
```

Real-engine integration tests are marked separately:

```bash
python -m pytest -v -m integration
```

## Plumeria

PlumeViz is a wrapper around the Plumeria volcanic plume model developed by Larry G. Mastin of the U.S. Geological Survey.

For details about the underlying model, see:

* Mastin, L. G. (2007), A user-friendly one-dimensional model for wet volcanic plumes, *Geochemistry, Geophysics, Geosystems*, 8, Q03014. [https://doi.org/10.1029/2006GC001455](https://doi.org/10.1029/2006GC001455)
* Mastin, L. G. (2014), Testing the accuracy of a 1-D volcanic plume model in estimating mass eruption rate, *Journal of Geophysical Research: Atmospheres*, 119, 2474–2495. [https://doi.org/10.1002/2013JD020604](https://doi.org/10.1002/2013JD020604)
* Mastin, L. G. (2024), *plumeria_wd software*. U.S. Geological Survey software program. [https://doi.org/10.5066/P1HVRKVN](https://doi.org/10.5066/P1HVRKVN)

## Citation

If you use PlumeViz in research, please cite the archived release:

[https://doi.org/10.5281/zenodo.13685923](https://doi.org/10.5281/zenodo.13685923)

Please also cite the appropriate Plumeria publications and software release.

## License

PlumeViz is distributed under the MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgements

Special thanks to Larry Mastin for developing and maintaining Plumeria.

The development of the original PlumeViz workflow was informed by research and discussions with Liam Kelly, Kristen Fauria, and Tushar Mittal.

## Contact

For questions about PlumeViz, contact Edgar Carrillo at [edgarc.ec@gmail.com](mailto:edgarc.ec@gmail.com).
