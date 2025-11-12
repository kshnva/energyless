# Energyless : OpenDC carbon aware scheduling

This setup allows 

---

## General Instructions

* **Java:** version **21**
* **Python:** version **≥ 3.10**

Setup environment:

* in order to run experiments from notebook, create virtual environment, activate and install requirements using below commands
```bash
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
```

To build or rebuild the experiment runner (eg following source code update):

```bash
chmod +x build_opendc_runner.sh
./build_opendc_runner.sh
```

---

## Project Structure

```
.
├── OpenDCExperimentRunner/         # Built opendc experiment runner (executable)
├── build_opendc_runner.sh          # Script to build opendc experiment runner
├── input/                          # Experiment configs, workloads, topologies
├── output/                         # Experiment outputs
├── carbon_traces/                  # Regional carbon intensity data
├── opendc/                         # OpenDC source code
├── resources/                      # Reference repos (footprinter, opendc-demos)
├── sample_run.ipynb                # Example notebook
└── requirements.txt
```

---

## Folder Details

* **OpenDCExperimentRunner/**
  Built by `build_opendc_runner.sh`; contains binaries, scripts and libraries to run experiments.

* **input/**
  Defines simulation setups:

  * `experiments/` → experiment configurations (can setup allocation policy here as well)
  * `topologies/` → data center models
  * `workload_traces/` → workload traces

* **output/**
  Output lorem ipsum output yeah

* **carbon_traces/**
  Contains `.parquet` carbon data from https://github.com/atlarge-research/opendc-traces/tree/main/carbon/traces.
  Optionally its possible to fetch this info from ENTSOE api on demand ( [ENTSOE api wrapper](https://github.com/EnergieID/entsoe-py) ). But the current setup works for our project.

* **opendc/**
  Local clone of OpenDC source; modify and rebuild using the build script.

* **resources/**
  Contains reference repositories such as `footprinter` and `opendc-demos`.