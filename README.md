# Energyless: OpenDC Carbon-Aware Scheduling

This project implements and evaluates custom schedulers for datacenter workload scheduling with carbon-awareness and workflow optimization capabilities using the [OpenDC](https://opendc.org/) simulation platform.

## Quick Start

**Prerequisites**: Java 21, Python ≥ 3.10

```bash
# 1. Setup Python environment
python3 -m venv energyless-env
source energyless-env/bin/activate
pip install -r requirements.txt

# 2. Build OpenDC experiment runner
chmod +x build_opendc_runner.sh
./build_opendc_runner.sh

# 3. Run scheduler comparison experiments
cd scheduler_comparison_experiments
jupyter notebook notebooks/run_comparison_experiments.ipynb
```

**📚 For detailed setup and usage instructions, see [scheduler_comparison_experiments/docs/USER_GUIDE.md](scheduler_comparison_experiments/docs/USER_GUIDE.md)**

---

## Project Overview

This project extends OpenDC with two custom schedulers:

1. **Workflow-Aware Scheduler**: Prioritizes tasks based on deadline urgency, critical path length, and optional parallelism scoring
2. **Carbon-Aware Workflow Scheduler**: Delays deferrable tasks during high-carbon periods while maintaining workflow deadlines

### Key Features

- ✅ **Carbon-aware scheduling** with adaptive forecast horizon
- ✅ **Workflow-aware** task prioritization with dependency analysis
- ✅ **Threshold-based delays** (not greedy optimization) for stable carbon reduction
- ✅ **Critical path protection** to prevent deadline violations
- ✅ **Comprehensive analysis tools** including Gantt charts with carbon overlays
- ✅ **Parameter sweep framework** for configuration optimization

---

## Project Structure

```
.
├── scheduler_comparison_experiments/   # Main experiment directory
│   ├── configs/                        # Experiment configurations
│   │   ├── baseline/                   # Baseline scheduler configs
│   │   ├── carbon_aware/               # Carbon-aware configs
│   │   ├── workflow_aware/             # Workflow-aware configs
│   │   └── parameter_sweep/            # Parameter sweep experiments
│   ├── docs/                           # Comprehensive documentation
│   │   ├── USER_GUIDE.md               # Complete usage guide
│   │   ├── SCHEDULER_ALGORITHMS.md     # Detailed pseudocode
│   │   └── CHANGELOG.md                # Version history
│   ├── notebooks/                      # Analysis notebooks
│   │   ├── run_comparison_experiments.ipynb
│   │   ├── scheduler_comparison.ipynb
│   │   └── workflow_balanced_tree_experiment.ipynb
│   └── scripts/                        # Execution scripts
│       ├── build_opendc_runner.sh
│       ├── generate_synthetic_traces.sh
│       └── carbon_aware_parameter_sweep.py
│
├── OpenDCExperimentRunner/             # Built experiment runner (executable)
├── opendc/                             # OpenDC source code (modified)
├── carbon_traces/                      # Regional carbon intensity data
├── input/                              # Experiment inputs
│   ├── experiments/                    # Experiment configs
│   ├── topologies/                     # Datacenter models
│   └── workload_traces/                # Workload traces
├── output/                             # Experiment results
└── resources/                          # Reference repos
```

---

## Documentation

- **[User Guide](scheduler_comparison_experiments/docs/USER_GUIDE.md)** - Complete setup, usage, and troubleshooting
- **[Scheduler Algorithms](scheduler_comparison_experiments/docs/SCHEDULER_ALGORITHMS.md)** - Detailed pseudocode and algorithm explanations
- **[Changelog](scheduler_comparison_experiments/docs/CHANGELOG.md)** - Version history and migration notes
- **[Setup Guide](SETUP_GUIDE.md)** - Initial project setup instructions

---

## Schedulers

### Workflow-Aware Scheduler

Optimizes task execution using multi-criteria scoring:

- **Deadline urgency**: Inverse of slack time
- **Critical path**: Length of longest dependency chain
- **Parallelism** (optional): Prioritizes tasks unlocking parallel execution

**Use cases**: Tight deadlines, complex dependencies, resource utilization

### Carbon-Aware Workflow Scheduler

Reduces operational carbon emissions while respecting workflows:

- **Threshold-based delays**: Delays tasks during high-carbon periods (above percentile threshold)
- **Adaptive forecast horizon**: Adjusts forecast window based on task deadlines
- **Workflow protection**: Extra slack requirements for critical path tasks
- **Queue position tracking**: Prioritizes early tasks as likely critical

**Use cases**: Carbon reduction goals, batch workloads, flexible deadlines

**📖 Full algorithm details in [SCHEDULER_ALGORITHMS.md](scheduler_comparison_experiments/docs/SCHEDULER_ALGORITHMS.md)**

---

## Running Experiments

### Basic Comparison

```bash
cd scheduler_comparison_experiments
jupyter notebook notebooks/run_comparison_experiments.ipynb
```

### Parameter Sweep

```bash
cd scheduler_comparison_experiments
python scripts/carbon_aware_parameter_sweep.py
```

### Custom Experiments

Edit configs in `scheduler_comparison_experiments/configs/`, then run:

```bash
cd scheduler_comparison_experiments
./OpenDCExperimentRunner/bin/runner \
  --experiment-path configs/carbon_aware/carbon_aware_experiment.json \
  --output-path ../output/
```

**📖 Complete experiment guide in [USER_GUIDE.md](scheduler_comparison_experiments/docs/USER_GUIDE.md)**

---

## Carbon Traces

Regional carbon intensity data from [OpenDC Traces](https://github.com/atlarge-research/opendc-traces/tree/main/carbon/traces):

- 100+ regions worldwide (2021-2024)
- Hourly granularity
- Parquet format for efficient loading

**Location**: `carbon_traces/`  
**Format**: `{REGION}_2021-2024.parquet`

---

## Development

### Building OpenDC

After modifying OpenDC source code:

```bash
./build_opendc_runner.sh
```

This rebuilds the experiment runner with your changes.

### Key Code Locations

- **Schedulers**: `opendc/opendc-compute/opendc-compute-simulator/src/main/kotlin/org/opendc/compute/simulator/scheduler/`
  - `WorkflowAwareScheduler.kt`
  - `CarbonAwareWorkflowScheduler.kt`
- **Allocation Policies**: `opendc/opendc-experiments/opendc-experiments-base/src/main/kotlin/org/opendc/experiments/base/experiment/specs/allocation/AllocationPolicySpec.kt`
- **Scheduler Factory**: `opendc/opendc-compute/opendc-compute-simulator/src/main/kotlin/org/opendc/compute/simulator/scheduler/ComputeSchedulers.kt`

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


