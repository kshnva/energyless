# Complete Setup Guide for EnergyLess Project

This guide walks you through setting up the entire EnergyLess datacenter simulation environment, including detailed instructions for configuring and running workflow-aware and carbon-aware experiments.

## Table of Contents

### Setup
- [Overview](#overview)
- [Step 1: Initialize Git Submodules](#step-1-initialize-git-submodules)
- [Step 2: Install Python Dependencies](#step-2-install-python-dependencies)
- [Step 3: Install Java 21](#step-3-install-java-21-required-for-opendc)
- [Step 4: Build OpenDC Experiment Runner](#step-4-build-opendc-experiment-runner)
- [Step 5: Generate Synthetic Traces](#step-5-generate-synthetic-traces)
- [Step 6: Verify Everything Works](#step-6-verify-everything-works)

### Running Experiments
- [Quick Start: Running Your First Experiment](#quick-start-running-your-first-experiment)
- [Experiment Configuration Guide](#experiment-configuration-guide)
- [Setting Up Workflow Experiments](#setting-up-workflow-experiments)
- [Comparing Schedulers](#comparing-schedulers)

### Reference
- [Directory Structure](#directory-structure)
- [Common Issues & Solutions](#common-issues--solutions)
- [Next Steps](#next-steps)
- [Resources](#resources)

## Overview

The project has three main components:
1. **opendc** - The datacenter simulator (requires building)
2. **opendc-traces** - Synthetic workload trace generator
3. **carbon_traces** - Real-world carbon intensity data

## Step 1: Initialize Git Submodules

```bash
cd /home/energyless
git submodule update --init --recursive
```

This will initialize:
- `opendc` - Main simulator code
- `opendc-traces` - Workload generation tools

Verify with:
```bash
git submodule status
# Should show no '-' prefix (means initialized)
```

## Step 2: Install Python Dependencies

### For Jupyter Notebooks
```bash
pip install pyarrow==17.0.0 pandas numpy matplotlib
```

### For Trace Generation
```bash
pip install -r opendc-traces/requirements.txt
```

## Step 3: Install Java 21 (Required for OpenDC)

The OpenDC Experiment Runner requires Java 21:

```bash
# Check current version
java -version

# If not Java 21, install it:
sudo apt update
sudo apt install -y openjdk-21-jdk

# Verify
java -version
# Should show: openjdk version "21.x.x"
```

## Step 4: Build OpenDC Experiment Runner

```bash
cd /home/energyless
chmod +x build_opendc_runner.sh
./build_opendc_runner.sh
```

This will:
- Use Gradle to build the OpenDC runner
- Extract it to `OpenDCExperimentRunner/`
- Take 5-10 minutes on first build

Verify the build:
```bash
./OpenDCExperimentRunner/bin/OpenDCExperimentRunner --help
```

## Step 5: Generate Synthetic Traces

```bash
cd /home/energyless
chmod +x generate_synthetic_traces.sh
./generate_synthetic_traces.sh
```

This generates various synthetic workload patterns in `input/synthetic_traces/`.

See [GENERATE_TRACES_GUIDE.md](GENERATE_TRACES_GUIDE.md) for detailed trace generation options.

## Step 6: Verify Everything Works

### Test 1: Check Python can read parquet files
```bash
python3 -c "import pandas as pd; import pyarrow; print('PyArrow version:', pyarrow.__version__); df = pd.read_parquet('carbon_traces/NL_2021-2024.parquet'); print(f'✅ Loaded {len(df)} carbon intensity records')"
```

### Test 2: Check OpenDC Runner
```bash
./OpenDCExperimentRunner/bin/OpenDCExperimentRunner --help
```

### Test 3: Run a notebook
```bash
# Open the demo notebook
cd resources/opendc-demos
jupyter notebook 1.first_experiment.ipynb
# Or use VS Code's notebook interface
```

## Quick Start: Running Your First Experiment

1. **Prepare an experiment config** (example: `input/experiments/sample_experiment.json`)

2. **Run the experiment**:
```bash
cd /home/energyless
./OpenDCExperimentRunner/bin/OpenDCExperimentRunner --experiment-path input/experiments/sample_experiment.json
```

3. **Analyze results**:
   - Output goes to `output/<experiment_name>/`
   - Use Jupyter notebooks to visualize results

## Experiment Configuration Guide

### Basic Experiment JSON Structure

All experiments require a JSON configuration file with the following structure:

```json
{
  "name": "my_experiment",
  "topologies": [ /* datacenter locations */ ],
  "workloads": [ /* workload traces to run */ ],
  "allocationPolicies": [ /* optional: scheduler policies */ ],
  "exportModels": [ /* output configuration */ ]
}
```

### Example 1: Simple Experiment (No Custom Scheduler)

**File: `input/experiments/sample_experiment.json`**

```json
{
  "name": "sample_experiment",
  "topologies": [
    {
      "pathToFile": "input/topologies/sample_NL.json"
    },
    {
      "pathToFile": "input/topologies/sample_BE.json"
    }
  ],
  "workloads": [
    {
      "pathToFile": "input/workflow_traces/sample",
      "type": "ComputeWorkload"
    }
  ],
  "exportModels": [
    {
      "exportInterval": 3600,
      "printFrequency": 24,
      "filesToExport": ["host", "powerSource", "service", "task"]
    }
  ]
}
```

**What this does:**
- Runs the same workload on 2 datacenter locations (Netherlands and Belgium)
- Uses default scheduler
- Exports metrics every 3600ms (1 hour simulation time)
- Records host, power, service, and task data

### Example 2: Workflow-Aware Scheduler Experiment

**File: `input/experiments/workflow_experiment.json`**

```json
{
  "name": "workflow_experiment",
  "topologies": [
    {
      "pathToFile": "input/topologies/sample_NL.json"
    },
    {
      "pathToFile": "input/topologies/sample_BE.json"
    }
  ],
  "workloads": [
    {
      "pathToFile": "input/synthetic_traces/balanced_tree_depth4_branching5_deadline_default",
      "type": "ComputeWorkload"
    }
  ],
  "allocationPolicies": [
    {
      "type": "workflowAware",
      "filters": [
        {
          "type": "Compute"
        }
      ],
      "weighers": [
        {
          "type": "Ram",
          "multiplier": 1.0
        }
      ],
      "taskDeadlineScore": false,
      "weightUrgency": 0.2,
      "weightCriticalDependencyChain": 0.2,
      "subsetSize": 1
    }
  ],
  "exportModels": [
    {
      "exportInterval": 3600,
      "printFrequency": 24,
      "filesToExport": ["host", "powerSource", "service", "task"]
    }
  ]
}
```

**Workflow-Aware Scheduler Parameters:**
- `type`: `"workflowAware"` - Uses dependency-aware scheduling
- `weightUrgency`: `0.2` - Priority weight for tasks close to deadline
- `weightCriticalDependencyChain`: `0.2` - Priority for tasks on critical path
- `taskDeadlineScore`: `false` - Don't use deadline scoring (use weights instead)
- `filters`: Only schedule on Compute nodes
- `weighers`: Use RAM capacity for host selection (1.0 multiplier)
- `subsetSize`: `1` - Consider 1 host at a time for placement

**When to use:** Workloads with task dependencies (DAG structures) where task ordering matters

### Example 3: Carbon-Aware Workflow Scheduler

**File: `input/experiments/carbon_aware_workflow_experiment.json`**

```json
{
  "name": "carbon_aware_workflow_experiment",
  "topologies": [
    {
      "pathToFile": "input/topologies/sample_NL.json"
    },
    {
      "pathToFile": "input/topologies/sample_BE.json"
    }
  ],
  "workloads": [
    {
      "pathToFile": "input/synthetic_traces/balanced_tree_depth2_branching2_deadline_default",
      "type": "ComputeWorkload"
    }
  ],
  "allocationPolicies": [
    {
      "type": "carbonAware",
      "filters": [
        {
          "type": "Compute"
        }
      ],
      "weighers": [
        {
          "type": "Ram",
          "multiplier": 1.0
        }
      ],
      "slotLengthMs": 3600000,
      "horizonSlots": 168,
      "enableOptimization": true,
      "maxOptimizationTasks": 25,
      "optimizationTimeoutMs": 5000,
      "subsetSize": 1
    }
  ],
  "exportModels": [
    {
      "exportInterval": 3600,
      "printFrequency": 24,
      "filesToExport": ["host", "powerSource", "service", "task"]
    }
  ]
}
```

**Carbon-Aware Scheduler Parameters:**
- `type`: `"carbonAware"` - Optimizes for carbon emissions
- `slotLengthMs`: `3600000` - Planning time slot length (1 hour)
- `horizonSlots`: `168` - Planning horizon (168 hours = 1 week)
- `enableOptimization`: `true` - Use global optimization (DFS with branch-and-bound)
- `maxOptimizationTasks`: `25` - Max tasks to optimize together
- `optimizationTimeoutMs`: `5000` - 5 second timeout per optimization

**When to use:** Minimize carbon emissions by delaying tasks to low-carbon periods

### Configuration Parameters Reference

#### Topologies
```json
"topologies": [
  {
    "pathToFile": "input/topologies/sample_NL.json"
  }
]
```
- Defines datacenter hardware and location
- Can specify multiple topologies to compare locations
- Must include carbon trace data

#### Workloads
```json
"workloads": [
  {
    "pathToFile": "input/synthetic_traces/balanced_tree_depth4_branching5_deadline_default",
    "type": "ComputeWorkload"
  }
]
```
- `pathToFile`: Path to workload directory (contains tasks.parquet, fragments.parquet)
- `type`: `"ComputeWorkload"` for task-based workloads

**Available synthetic workloads:**
- `balanced_tree_depth{N}_branching{M}_deadline_default` - Tree-structured DAGs
- `mostly_parallel_*` - Many independent tasks
- `highly_dependent_*` - Long dependency chains
- `random_dag_*` - Random DAG structures

#### Allocation Policies (Schedulers)

**Default (if omitted):** First-fit scheduler

**Workflow-Aware:**
```json
{
  "type": "workflowAware",
  "weightUrgency": 0.2,
  "weightCriticalDependencyChain": 0.2,
  "taskDeadlineScore": false
}
```

**Carbon-Aware:**
```json
{
  "type": "carbonAware",
  "slotLengthMs": 3600000,
  "horizonSlots": 168,
  "enableOptimization": true,
  "maxOptimizationTasks": 25
}
```

#### Export Models
```json
"exportModels": [
  {
    "exportInterval": 3600,
    "printFrequency": 24,
    "filesToExport": ["host", "powerSource", "service", "task"]
  }
]
```
- `exportInterval`: How often to record metrics (ms of simulation time)
- `printFrequency`: Console progress updates every N intervals
- `filesToExport`: Which parquet files to generate
  - `host`: CPU/memory utilization per host
  - `powerSource`: Energy consumption and carbon emissions
  - `service`: Task execution status over time
  - `task`: Individual task completion records

## Setting Up Workflow Experiments

### Step 1: Choose or Generate a Workload

**Option A: Use existing synthetic traces**
```bash
ls input/synthetic_traces/
# Pick a workload like: balanced_tree_depth4_branching5_deadline_default
```

**Option B: Generate custom traces**
```bash
# Edit opendc-traces/workload/generate_synthetic_workflow_examples.py
# Then run:
./generate_synthetic_traces.sh
```

See [GENERATE_TRACES_GUIDE.md](GENERATE_TRACES_GUIDE.md) for detailed trace generation.

### Step 2: Verify Workload Structure

```python
import pandas as pd
import pyarrow.parquet as pq

# Load workload
workload_path = "input/synthetic_traces/balanced_tree_depth4_branching5_deadline_default"
tasks = pd.read_parquet(f"{workload_path}/tasks.parquet")

print(f"Total tasks: {len(tasks)}")
print(f"Columns: {tasks.columns.tolist()}")

# Check dependencies (NOTE: parents/children are numpy arrays, not lists!)
tasks_with_deps = tasks[tasks['parents'].apply(lambda x: len(x) > 0)]
print(f"Tasks with dependencies: {len(tasks_with_deps)}")
```

**Important:** When checking dependencies, use `len(x) > 0` NOT `isinstance(x, list)` because pandas converts Arrow list types to numpy arrays.

### Step 3: Create Experiment JSON

Create a file in `input/experiments/my_workflow_experiment.json`:

```json
{
  "name": "my_workflow_experiment",
  "topologies": [
    {
      "pathToFile": "input/topologies/sample_NL.json"
    }
  ],
  "workloads": [
    {
      "pathToFile": "input/synthetic_traces/YOUR_WORKLOAD_HERE",
      "type": "ComputeWorkload"
    }
  ],
  "allocationPolicies": [
    {
      "type": "workflowAware",
      "weightUrgency": 0.2,
      "weightCriticalDependencyChain": 0.2,
      "filters": [{"type": "Compute"}],
      "weighers": [{"type": "Ram", "multiplier": 1.0}],
      "taskDeadlineScore": false,
      "subsetSize": 1
    }
  ],
  "exportModels": [
    {
      "exportInterval": 3600,
      "printFrequency": 24,
      "filesToExport": ["host", "powerSource", "service", "task"]
    }
  ]
}
```

### Step 4: Run the Experiment

```bash
cd /home/energyless
./OpenDCExperimentRunner/bin/OpenDCExperimentRunner --experiment-path input/experiments/my_workflow_experiment.json
```

### Step 5: Analyze Results

Results are saved to `output/my_workflow_experiment/raw-output/`:

```
output/my_workflow_experiment/
├── raw-output/
│   ├── 0/              # First topology (e.g., Netherlands)
│   │   └── seed=0/
│   │       ├── host.parquet
│   │       ├── powerSource.parquet
│   │       ├── service.parquet
│   │       └── task.parquet
│   └── 1/              # Second topology (e.g., Belgium)
│       └── seed=0/
│           └── ...
```

**Load results in Python:**
```python
import pandas as pd

base_path = "output/my_workflow_experiment/raw-output/0/seed=0"

df_host = pd.read_parquet(f"{base_path}/host.parquet")
df_power = pd.read_parquet(f"{base_path}/powerSource.parquet")
df_task = pd.read_parquet(f"{base_path}/task.parquet")
df_service = pd.read_parquet(f"{base_path}/service.parquet")

# Calculate carbon emissions
carbon_kg = df_power.carbon_emission.sum() / 1000
energy_kwh = df_power.energy_usage.sum() / 3_600_000

print(f"Carbon emissions: {carbon_kg:.2f} kg CO2")
print(f"Energy consumption: {energy_kwh:.2f} kWh")
```

## Comparing Schedulers

To compare workflow-aware vs carbon-aware schedulers:

1. **Create two experiment configs** with identical workloads and topologies but different `allocationPolicies`

2. **Run both experiments:**
```bash
./OpenDCExperimentRunner/bin/OpenDCExperimentRunner --experiment-path input/experiments/workflow_experiment.json
./OpenDCExperimentRunner/bin/OpenDCExperimentRunner --experiment-path input/experiments/carbon_aware_workflow_experiment.json
```

3. **Compare results** using the `scheduler_comparison.ipynb` notebook or create your own analysis

Key metrics to compare:
- **Carbon emissions** (kg CO2)
- **Runtime** (hours to complete workload)
- **CPU utilization** (resource efficiency)
- **Task scheduling patterns** (when tasks execute)
- **Energy consumption** (kWh)

## Directory Structure

```
/home/energyless/
├── opendc/                          # Simulator source code (submodule)
├── opendc-traces/                   # Trace generator (submodule)
├── OpenDCExperimentRunner/          # Built simulator (created by build script)
├── carbon_traces/                   # Real carbon intensity data
├── input/                           # Input workload traces
│   └── synthetic_traces/           # Generated synthetic traces
├── resources/opendc-demos/          # Demo notebooks and experiments
│   ├── 1.first_experiment.ipynb    # Tutorial notebook
│   ├── experiments/                 # Experiment configurations
│   ├── topologies/                  # Datacenter definitions
│   ├── workload_traces/            # Sample workloads
│   └── output/                     # Simulation results
├── build_opendc_runner.sh          # Build script
├── generate_synthetic_traces.sh    # Trace generation script
└── requirements.txt                # Python dependencies
```

## Common Issues & Solutions

### Issue: "No module named 'pyarrow'"

**Solution**: 
```bash
pip install pyarrow==17.0.0
# Then restart Jupyter kernel
```

### Issue: "UnsupportedClassVersionError" (Java version)

**Solution**: 
```bash
sudo apt install -y openjdk-21-jdk
java -version  # Verify it's 21.x
```

### Issue: "./gradlew: No such file or directory"

**Solution**: 
```bash
git submodule update --init --recursive opendc
```

### Issue: Submodules are empty

**Solution**: 
```bash
cd /home/energyless
git submodule update --init --recursive
```

### Issue: Build fails with Gradle errors

**Solution**: 
```bash
cd opendc
./gradlew clean
cd ..
./build_opendc_runner.sh
```

### Issue: "The provided path to the workload does not exist"

**Solution**: 
```bash
# Check the workload path in your experiment JSON
ls input/synthetic_traces/
# Make sure pathToFile matches an actual directory
# Example: "input/synthetic_traces/balanced_tree_depth4_branching5_deadline_default"
```

### Issue: Experiment hangs or runs forever

**Possible causes:**
1. **Large workload with many tasks** - Some schedulers (especially carbon-aware) can be slow with 500+ tasks
2. **Scheduler bug** - Check if there are known issues with the scheduler version
3. **Infinite loop in optimization** - Carbon-aware scheduler may get stuck

**Solutions:**
```bash
# Try a smaller workload first
# For example, use depth2_branching2 instead of depth4_branching5

# Add timeout to the experiment run
timeout 300 ./OpenDCExperimentRunner/bin/OpenDCExperimentRunner --experiment-path input/experiments/workflow_experiment.json
```

### Issue: Results show 0 active tasks or 0% CPU utilization

**This may indicate a scheduler bug.** Check:

1. **Verify workload has dependencies:**
```python
import pandas as pd
tasks = pd.read_parquet("input/synthetic_traces/YOUR_WORKLOAD/tasks.parquet")
# NOTE: parents/children are numpy arrays, not Python lists
tasks_with_deps = tasks[tasks['parents'].apply(lambda x: len(x) > 0)]
print(f"Tasks with dependencies: {len(tasks_with_deps)}/{len(tasks)}")
```

2. **Check task output file:**
```python
df_task = pd.read_parquet("output/YOUR_EXPERIMENT/raw-output/0/seed=0/task.parquet")
print(df_task.columns.tolist())
print(df_task.head())
# Look for time_submitted, time_started, time_finished columns
```

3. **Report to development team** - This is a known issue being investigated

### Issue: "isinstance(x, list)" returns False for dependencies

**Problem:** When loading parquet files with pandas, list columns are converted to numpy arrays.

**Solution:** Use `len(x) > 0` instead of `isinstance(x, list)`:

```python
# ❌ WRONG
tasks_with_parents = df_tasks[df_tasks['parents'].apply(lambda x: len(x) > 0 if isinstance(x, list) else False)]

# ✅ CORRECT
tasks_with_parents = df_tasks[df_tasks['parents'].apply(lambda x: len(x) > 0)]
```

## Next Steps

1. ✅ Complete setup using this guide
2. 📖 Read [GENERATE_TRACES_GUIDE.md](GENERATE_TRACES_GUIDE.md) for custom trace generation
3. 🚀 Run the tutorial: `resources/opendc-demos/1.first_experiment.ipynb`
4. 🔬 Create your own experiments by:
   - Designing datacenter topologies (JSON)
   - Generating/selecting workload traces
   - Configuring experiment parameters
   - Running simulations
   - Analyzing carbon emissions and performance

## Resources

- OpenDC Documentation: https://atlarge-research.github.io/opendc/
- OpenDC Website: https://opendc.org/
- Carbon Scheduler Paper: `carbon_scheduler_explainer.pdf`
- Sample Experiments: `resources/opendc-demos/experiments/`

## Support

If you encounter issues:
1. Check this guide and the troubleshooting section
2. Verify all prerequisites are installed
3. Check that submodules are initialized
4. Ensure you're using Java 21 and PyArrow 17.0.0
