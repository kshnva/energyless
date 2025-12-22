# Energyless : OpenDC carbon aware scheduling

*Data centers contribute a significant and growing share of global electricity consumption, motivating increasing interest in carbon-aware scheduling strategies. However, incorporating carbon-awareness into workflow-based scheduling remains challenging due to task dependencies, runtime uncertainty, and fluctuating grid conditions. We present EnergyLess, an extension to the OpenDC simulation platform designed to evaluate workflow-aware and carbon-aware scheduling policies under realistic carbon-intensity traces. Using a year-long Netherlands carbon-intensity dataset, we compare a FIFO baseline with a workflow-aware scheduler and a carbon-aware scheduler across synthetic, scientific, and real-world workflow traces. Our results show that the implemented carbon-aware scheduler yields marginal and inconsistent emission reductions and frequently increases makespan, indicating fundamental limitations in its design or implementation. In contrast, the workflowaware scheduler consistently improves execution efficiency for complex workflows, achieving makespan reductions of up to 6.72% and carbon reductions of up to 5.86% despite not explicitly optimizing for emissions. These findings suggest that reactive, task-level carbon shifting is insufficient for workflow scheduling and that structural workflow optimization is a necessary foundation for effective carbon-aware execution. More broadly, this study highlights the practical challenges of implementing carbonaware schedulers in simulation frameworks and underscores the importance of integrating carbon signals with global workflow reasoning.*

## Setup

[SETUP_GUIDE.md](./SETUP_GUIDE.md)

---

## Project Structure

```
.
├── OpenDCExperimentRunner/         # Built opendc experiment runner (executable)
├── build_opendc_runner.sh          # Script to build opendc experiment runner
├── generate_synthetic_traces.sh    # Script to generate all experimental data
├── input/                          # Experiment configs, workloads, topologies
├── output/                         # Experiment outputs
├── carbon_traces/                  # Regional carbon intensity data
├── opendc/                         # submodule pointing to OpenDC source code fork
├── opendc-traces/                  # submodule pointing to experimental data creation scripts
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

* **opendc-traces/**
  Local clone of submodule for experimental data generation scirpts. Run `generate_synthetic_traces.sh` to generate. Plese see the description of the submodule for details on workflow generation and parsing nuances.

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


