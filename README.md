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

---

## Other Resources

* **Carbon emission tutorial:** - [Running Carbon Emission Experiments](https://atlarge-research.github.io/opendc/docs/tutorials/Carbon%20Emission/2.1%20Running/)

* **Input artifacts and parameters:** - [OpenDC Input Documentation](https://atlarge-research.github.io/opendc/docs/category/input)
  Checkout sections **Allocation Policy** and **Topology > Power Source**

* **Output artifacts and parameters:** - [OpenDC Output Documentation](https://atlarge-research.github.io/opendc/docs/documentation/Output)

* **Relevant code locations:**

  * **Allocation Policies:**
    `opendc-experiments/opendc-experiments-base/src/main/kotlin/org/opendc/experiments/base/experiment/specs/allocation/AllocationPolicySpec.kt`
  * **Prefab Schedulers mapping:**
    `opendc-compute/opendc-compute-simulator/src/main/kotlin/org/opendc/compute/simulator/scheduler/ComputeSchedulers.kt`
  * **Parsing and processing experiment JSON:**
    `opendc-experiments/opendc-experiments-base/src/main/kotlin/org/opendc/experiments/base/experiment/`
  * **Executing experiment JSON:**
    `opendc-experiments/opendc-experiments-base/src/main/kotlin/org/opendc/experiments/base/runner/`


