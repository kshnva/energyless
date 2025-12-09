# Scheduler Comparison Experiments

Comprehensive experiment suite comparing workflow-aware and carbon-aware schedulers for datacenter workload optimization using OpenDC.

## 📚 Documentation

- **[USER_GUIDE.md](docs/USER_GUIDE.md)** - Complete setup, usage, and troubleshooting guide
- **[SCHEDULER_ALGORITHMS.md](docs/SCHEDULER_ALGORITHMS.md)** - Detailed scheduler pseudocode and algorithms
- **[CHANGELOG.md](docs/CHANGELOG.md)** - Version history and migration notes

## Quick Start

```bash
# 1. Run comparison experiments
jupyter notebook notebooks/run_comparison_experiments.ipynb

# 2. Run parameter sweep
python scripts/carbon_aware_parameter_sweep.py

# 3. Run custom experiment
../OpenDCExperimentRunner/bin/runner \
  --experiment-path configs/carbon_aware/carbon_aware_experiment.json \
  --output-path ../output/
```

## Directory Structure

```
scheduler_comparison_experiments/
├── configs/                        # Experiment configurations
│   ├── baseline/                   # Baseline scheduler configs
│   │   ├── baseline_random_experiment.json
│   │   └── baseline_mem_experiment.json
│   ├── carbon_aware/               # Carbon-aware configs
│   │   ├── carbon_aware_experiment.json
│   │   └── timeshift_experiment.json
│   ├── workflow_aware/             # Workflow-aware configs
│   │   ├── workflow_aware_experiment.json
│   │   └── workflow_aware_parallelism_experiment.json
│   └── parameter_sweep/            # Parameter sweep experiments
│       ├── sweep_carbon_0.3_4_1.3.json
│       ├── sweep_workflow_0.3_0.3_0.3.json
│       └── ...
│
├── docs/                           # Documentation
│   ├── USER_GUIDE.md               # Complete usage guide
│   ├── SCHEDULER_ALGORITHMS.md     # Scheduler pseudocode
│   └── CHANGELOG.md                # Version history
│
├── notebooks/                      # Analysis notebooks
│   ├── run_comparison_experiments.ipynb
│   ├── scheduler_comparison.ipynb
│   └── workflow_balanced_tree_experiment.ipynb
│
├── scripts/                        # Execution scripts
│   ├── build_opendc_runner.sh
│   ├── generate_synthetic_traces.sh
│   └── carbon_aware_parameter_sweep.py
│
├── parameter_sweep_results/        # Sweep experiment results
└── comparison_results.csv          # Comparison experiment results
```

## Schedulers Overview

### 1. Baseline Schedulers

**Random Scheduler** (`configs/baseline/baseline_random_experiment.json`)
- Standard OpenDC random placement
- No optimization
- Performance baseline

**Memory Scheduler** (`configs/baseline/baseline_mem_experiment.json`)
- Memory-optimized placement
- Standard OpenDC policy
- Resource utilization baseline

### 2. Workflow-Aware Scheduler

**Standard** (`configs/workflow_aware/workflow_aware_experiment.json`)
- Multi-criteria task scoring (urgency + critical path)
- Configurable weights for urgency and dependency chain
- No parallelism scoring (disabled by default)

**Parallelism-Enhanced** (`configs/workflow_aware/workflow_aware_parallelism_experiment.json`)
- All standard features plus parallelism awareness
- Prioritizes tasks unlocking parallel execution
- Activated when ready pool is small

**Key Parameters**:
```json
{
  "taskDeadlineScore": true,
  "weightUrgency": 0.2,
  "weightCriticalDependencyChain": 0.2,
  "enableParallelismScore": false,
  "weightParallelism": 0.0,
  "taskLookaheadThreshold": 1000
}
```

### 3. Carbon-Aware Workflow Scheduler

**Standard** (`configs/carbon_aware/carbon_aware_experiment.json`)
- Threshold-based carbon delays
- Adaptive forecast horizon
- Workflow-aware safety mechanisms
- Critical path protection

**Timeshift Baseline** (`configs/carbon_aware/timeshift_experiment.json`)
- Identical workload at different times
- Measures carbon variation from grid alone
- Baseline for carbon reduction analysis

**Key Parameters**:
```json
{
  "carbonDelayThreshold": 0.5,
  "maxDelayHours": 4.0,
  "forecastHorizon": 24,
  "slackThresholdMultiplier": 1.5,
  "prioritizeCriticalPath": true
}
```

**📖 Full algorithm details in [docs/SCHEDULER_ALGORITHMS.md](docs/SCHEDULER_ALGORITHMS.md)**
  - Deadline: Default settings

## Topology Configuration

All experiments run on two datacenter topologies:
1. **Netherlands** (`sample_NL.json`)
2. **Belgium** (`sample_BE.json`)

This allows comparison across different geographic locations with varying carbon intensity profiles.

## Running the Experiments

### Option 1: Run Individual Experiments

```bash
# Run baseline random scheduler
./OpenDCExperimentRunner/bin/OpenDCExperimentRunner --experiment-path scheduler_comparison_experiments/baseline_random_experiment.json

# Run baseline memory scheduler
./OpenDCExperimentRunner/bin/OpenDCExperimentRunner --experiment-path scheduler_comparison_experiments/baseline_mem_experiment.json

# Run workflow-aware scheduler
./OpenDCExperimentRunner/bin/OpenDCExperimentRunner --experiment-path scheduler_comparison_experiments/workflow_aware_experiment.json

# Run carbon-aware scheduler
./OpenDCExperimentRunner/bin/OpenDCExperimentRunner --experiment-path scheduler_comparison_experiments/carbon_aware_experiment.json
```

### Option 2: Run All Experiments (Batch)

Create a bash script to run all experiments sequentially:

```bash
#!/bin/bash
cd /home/energyless

experiments=(
    "scheduler_comparison_experiments/baseline_random_experiment.json"
    "scheduler_comparison_experiments/baseline_mem_experiment.json"
    "scheduler_comparison_experiments/workflow_aware_experiment.json"
    "scheduler_comparison_experiments/carbon_aware_experiment.json"
)

for exp in "${experiments[@]}"; do
    echo "Running experiment: $exp"
    ./OpenDCExperimentRunner/bin/OpenDCExperimentRunner --experiment-path "$exp"
    echo "Completed: $exp"
    echo "----------------------------------------"
done

echo "All experiments completed!"
```

### Option 3: Use the Jupyter Notebook

Use the provided `run_comparison_experiments.ipynb` notebook to:
- Run all experiments
- Load and analyze results
- Generate comparison visualizations

## Output Structure

Results are stored in the `output/` directory:

```
output/
├── baseline_random_scheduler/
│   └── raw-output/
│       ├── 0/  # Netherlands
│       │   └── seed=0/
│       │       ├── host.parquet
│       │       ├── powerSource.parquet
│       │       ├── service.parquet
│       │       └── task.parquet
│       └── 1/  # Belgium
│           └── seed=0/
│               └── ...
├── baseline_mem_scheduler/
├── workflow_aware_scheduler/
└── carbon_aware_workflow_scheduler/
```

## Key Metrics to Compare

When analyzing the results, focus on these metrics:

### 1. **Runtime & Makespan**
- Total time to complete the workflow
- Task execution times
- Wait times between tasks

```python
# Calculate makespan
makespan = df_service.timestamp.max() - df_service.timestamp.min()
```

### 2. **Carbon Emissions**
- Total CO2 emissions (kg)
- Carbon intensity over time
- Emissions per task

```python
# Calculate carbon emissions
df_power['carbon_emissions_kg'] = df_power['power_draw'] * df_power['carbon_intensity'] / 1000
total_carbon = df_power['carbon_emissions_kg'].sum()
```

### 3. **Resource Utilization**
- CPU utilization
- Memory utilization
- Server active time

```python
# Calculate CPU utilization
cpu_utilization = df_host['cpu_usage'].mean()
```

### 4. **Task Scheduling Patterns**
- Task start times
- Task dependencies met
- Idle time between tasks

### 5. **Energy Consumption**
- Total energy used (kWh)
- Power draw over time
- Energy per task

```python
# Calculate total energy
total_energy_kwh = df_power['power_draw'].sum() / 1000
```

## Analysis Workflow

1. **Run all experiments** (see above)
2. **Load results** into pandas DataFrames
3. **Calculate metrics** for each scheduler
4. **Compare and visualize** results
5. **Document findings**

## Expected Outcomes

### Baseline Random
- **Pros**: Simple, no overhead
- **Cons**: Poor resource utilization, high carbon emissions, long makespan
- **Use case**: Reference baseline only

### Baseline Memory
- **Pros**: Better resource packing
- **Cons**: Doesn't consider carbon or dependencies
- **Use case**: Traditional cloud scheduling

### Workflow-Aware
- **Pros**: Optimized makespan, respects dependencies, reduced wait times
- **Cons**: May not optimize for carbon
- **Use case**: Time-critical workflows

### Carbon-Aware
- **Pros**: Minimized carbon emissions, time-shifting to low-carbon periods
- **Cons**: Potentially longer makespan
- **Use case**: Carbon-conscious computing with flexible deadlines

## Customization

To modify the experiments:

1. **Change workload**: Update the `pathToFile` in the `workloads` section
2. **Add topologies**: Add more datacenter locations in `topologies`
3. **Tune scheduler parameters**: Modify weights, filters, or optimization settings
4. **Adjust export intervals**: Change `exportInterval` in `exportModels`

## Troubleshooting

- **Experiments fail**: Check that workload traces exist in `input/synthetic_traces/`
- **No carbon data**: Ensure carbon traces are in `carbon_traces/` directory
- **Memory issues**: Reduce `maxOptimizationTasks` for carbon-aware scheduler
- **Long runtime**: Use smaller workloads or reduce `horizonSlots`

## References

- [OpenDC Documentation](https://opendc.org)
- [Setup Guide](../SETUP_GUIDE.md)
- [Scheduler Comparison Notebook](../scheduler_comparison.ipynb)
