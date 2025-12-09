# Scheduler Comparison Experiments - User Guide

Complete guide for running and analyzing OpenDC scheduler experiments.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Directory Structure](#directory-structure)
3. [Available Schedulers](#available-schedulers)
4. [Running Experiments](#running-experiments)
5. [Parameter Sweep](#parameter-sweep)
6. [Analysis and Visualization](#analysis-and-visualization)
7. [Configuration Reference](#configuration-reference)

---

## Quick Start

### Prerequisites

```bash
# Ensure OpenDC is built
cd /home/energyless
./build_opendc_runner.sh
```

### Run Comparison Experiments

```bash
# Run all scheduler comparisons
cd /home/energyless/scheduler_comparison_experiments
./scripts/run_all_experiments.sh

# Or run individual experiments
./OpenDCExperimentRunner/bin/OpenDCExperimentRunner \
  --experiment-path configs/baseline/baseline_random_experiment.json
```

### Analyze Results

```bash
# Open the comparison notebook
jupyter notebook notebooks/run_comparison_experiments.ipynb
```

---

## Directory Structure

```
scheduler_comparison_experiments/
├── configs/                      # Experiment configurations
│   ├── baseline/                 # Baseline scheduler configs
│   │   ├── baseline_random_experiment.json
│   │   └── baseline_mem_experiment.json
│   ├── workflow_aware/           # Workflow-aware scheduler configs
│   │   ├── workflow_aware_experiment.json
│   │   └── workflow_aware_parallelism_experiment.json
│   ├── carbon_aware/             # Carbon-aware scheduler configs
│   │   ├── carbon_aware_experiment.json
│   │   └── timeshift_experiment.json
│   └── parameter_sweep/          # Parameter optimization configs
│       ├── sweep_baseline_current.json
│       ├── sweep_aggressive_low_threshold.json
│       └── ... (8 more sweep configs)
├── docs/                         # Documentation
│   ├── USER_GUIDE.md            # This file
│   ├── SCHEDULER_ALGORITHMS.md  # Pseudocode and algorithms
│   └── CHANGELOG.md             # Change history
├── notebooks/                    # Jupyter notebooks
│   ├── run_comparison_experiments.ipynb
│   └── carbon_parameter_sweep_analysis.ipynb
├── scripts/                      # Utility scripts
│   ├── run_all_experiments.sh
│   ├── run_parameter_sweep.sh
│   └── carbon_aware_parameter_sweep.py
├── parameter_sweep_results/      # Parameter optimization results
└── comparison_results.csv        # Experiment metrics
```

---

## Available Schedulers

### Baseline Schedulers

**Random Scheduler**
- Randomly assigns tasks to available hosts
- No optimization
- Useful as baseline for comparison

**Memory Scheduler**
- Prioritizes hosts with more available memory
- Simple heuristic-based scheduling
- Better than random for memory-intensive workloads

### Workflow-Aware Schedulers

**Workflow-Aware Scheduler**
- Considers task dependencies and critical paths
- Prioritizes tasks based on:
  - Urgency (deadline proximity)
  - Critical dependency chain length
  - Parallelism opportunities (optional)
- Parameters:
  - `taskDeadlineScore`: Enable deadline-based prioritization
  - `weightUrgency`: Weight for urgency score (default: 0.2)
  - `weightCriticalDependencyChain`: Weight for criticality (default: 0.2)
  - `enableParallelismScore`: Enable parallelism scoring (default: false)
  - `weightParallelism`: Weight for parallelism (default: 0.0)

**Workflow-Aware with Parallelism**
- Enhanced version with parallelism scoring enabled
- Prioritizes tasks that unlock more parallel execution
- Better for workflows with high parallelism potential

### Carbon-Aware Schedulers

**Carbon-Aware Workflow Scheduler**
- Threshold-based carbon optimization
- Delays tasks during high carbon intensity periods
- Respects workflow deadlines and dependencies
- Parameters:
  - `carbonDelayThreshold`: Percentile threshold for "high carbon" (default: 0.2)
  - `maxDelayHours`: Maximum delay in hours (default: 4)
  - `forecastHorizon`: Hours to look ahead (default: 24)
  - `slackThresholdMultiplier`: Safety margin multiplier (default: 2.0)
  - `prioritizeCriticalPath`: Conservative with critical tasks (default: true)

**Timeshift Scheduler**
- Delays deferrable tasks during high carbon periods
- Uses forecast to predict low-carbon windows
- Parameters:
  - `windowSize`: Time window in hours (default: 168 = 1 week)
  - `forecast`: Enable carbon forecasting (default: true)
  - `shortForecastThreshold`: Short-term threshold (default: 0.2)
  - `longForecastThreshold`: Long-term threshold (default: 0.35)

---

## Running Experiments

### Single Experiment

```bash
cd /home/energyless

# Run specific scheduler
./OpenDCExperimentRunner/bin/OpenDCExperimentRunner \
  --experiment-path scheduler_comparison_experiments/configs/carbon_aware/carbon_aware_experiment.json

# Check results
ls output/carbon_aware_workflow_scheduler/raw-output/
```

### All Experiments

```bash
cd /home/energyless/scheduler_comparison_experiments
./scripts/run_all_experiments.sh
```

This runs all 5 schedulers:
1. Baseline Random
2. Baseline Memory
3. Workflow-Aware
4. Carbon-Aware
5. Timeshift

### Custom Workload

Edit any experiment JSON file:

```json
{
  "name": "my_custom_experiment",
  "workloads": [
    {
      "pathToFile": "input/synthetic_traces/YOUR_WORKLOAD_HERE",
      "type": "ComputeWorkload"
    }
  ],
  ...
}
```

---

## Parameter Sweep

### What is Parameter Sweep?

Automated testing of different parameter combinations to find optimal scheduler configuration.

### Run Parameter Sweep

```bash
cd /home/energyless/scheduler_comparison_experiments

# Run all 10 configurations
./scripts/run_parameter_sweep.sh

# Or run individual sweep config
../OpenDCExperimentRunner/bin/OpenDCExperimentRunner \
  --experiment-path configs/parameter_sweep/sweep_aggressive_low_threshold.json
```

### Sweep Configurations

10 pre-configured parameter combinations:

1. **baseline_current** - Current production settings
2. **aggressive_low_threshold** - Lower carbon threshold, longer delays
3. **very_aggressive** - Minimal threshold, maximum delays
4. **conservative_high_safety** - High safety margins
5. **balanced_workflow_aware** - Balanced with workflow awareness
6. **medium_slack_workflow** - Medium slack with workflow
7. **short_horizon_reactive** - Quick reactions, short horizon
8. **long_horizon** - Extended forecast horizon
9. **tight_threshold_long_delay** - Tight threshold, long delays
10. **no_workflow_awareness** - Pure carbon optimization

### Analyze Sweep Results

```bash
# View results
cat parameter_sweep_results/sweep_summary_*.txt

# Or use the analysis notebook
jupyter notebook notebooks/carbon_parameter_sweep_analysis.ipynb
```

Results include:
- Ranked configurations by carbon reduction
- Makespan vs. carbon trade-offs
- Optimal parameter JSON file

---

## Analysis and Visualization

### Jupyter Notebooks

**run_comparison_experiments.ipynb**
- Load and visualize all scheduler results
- Compare metrics (makespan, carbon, energy, utilization)
- Generate Gantt charts
- Carbon intensity timeline analysis
- Export results to CSV

**carbon_parameter_sweep_analysis.ipynb**
- Interactive parameter exploration
- Real-time visualizations
- Scatter plots, heatmaps, bar charts
- Recommendations for optimal settings

### Key Metrics

**Makespan** - Total time to complete all tasks
- Lower is better
- Measured in hours

**Carbon Emissions** - Total CO2 emissions
- Lower is better
- Measured in kg CO2

**Energy Consumption** - Total energy used
- Lower is better
- Measured in kWh

**Resource Utilization** - CPU/memory usage
- Higher is better (more efficient)
- Measured as percentage

**Wait Time** - Average task scheduling delay
- Lower is better
- Measured in hours

### Visualization Types

**Makespan Comparison** - Bar charts by topology
**Carbon Emissions** - Bar charts by topology
**Resource Utilization** - Grouped bar charts
**Energy Consumption** - Bar charts by topology
**Gantt Charts** - Task scheduling timeline
**Carbon Intensity Overlay** - Dual-panel charts showing carbon + scheduling
**Performance Summary** - Percentage improvements vs. baseline

---

## Configuration Reference

### Experiment JSON Structure

```json
{
  "name": "experiment_name",
  "topologies": [
    {
      "pathToFile": "input/topologies/sample_NL_small.json"
    }
  ],
  "workloads": [
    {
      "pathToFile": "input/synthetic_traces/workload_name",
      "type": "ComputeWorkload"
    }
  ],
  "allocationPolicies": [
    {
      "type": "carbonAware",  // or "workflowAware", "timeshift", etc.
      "filters": [...],
      "weighers": [...],
      // Scheduler-specific parameters
      "carbonDelayThreshold": 0.2,
      "maxDelayHours": 4,
      "forecastHorizon": 24
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

### Carbon-Aware Parameters

```json
{
  "type": "carbonAware",
  "carbonDelayThreshold": 0.2,      // 0.0-1.0 (lower = delay more often)
  "maxDelayHours": 4,                // 1-16 hours
  "forecastHorizon": 24,             // 12-96 hours
  "slackThresholdMultiplier": 2.0,  // 1.0-3.0 (higher = more conservative)
  "prioritizeCriticalPath": true    // true/false
}
```

### Workflow-Aware Parameters

```json
{
  "type": "workflowAware",
  "taskDeadlineScore": true,                  // Enable deadline scoring
  "weightUrgency": 0.2,                       // 0.0-1.0
  "weightCriticalDependencyChain": 0.2,       // 0.0-1.0
  "enableParallelismScore": false,            // Enable parallelism
  "weightParallelism": 0.0,                   // 0.0-1.0
  "parallelismDecayRate": 0.15,               // 0.0-1.0
  "taskLookaheadThreshold": 1000              // Number of tasks
}
```

---

## Troubleshooting

### Experiment Fails to Run

```bash
# Rebuild OpenDC
cd /home/energyless
./build_opendc_runner.sh

# Check experiment config path
ls scheduler_comparison_experiments/configs/carbon_aware/carbon_aware_experiment.json
```

### No Results Generated

Check output directory:
```bash
ls -la output/
```

Verify experiment name matches directory name.

### Notebook Won't Load Results

Ensure experiments completed:
```bash
# Check for parquet files
ls output/carbon_aware_workflow_scheduler/raw-output/0/seed=0/*.parquet
```

### Parameter Sweep Takes Too Long

Edit `carbon_aware_parameter_sweep.py`:
- Reduce number of configurations
- Use smaller workload
- Decrease `max_tasks` parameter

---

## Tips and Best Practices

✅ **Always rebuild** after changing scheduler code
✅ **Use parameter sweep** to find optimal settings
✅ **Compare multiple topologies** for robust results
✅ **Export CSV** for statistical analysis
✅ **Save Gantt charts** for presentations
✅ **Document** your custom configurations
✅ **Backup results** before re-running experiments

---

## Further Reading

- `SCHEDULER_ALGORITHMS.md` - Detailed pseudocode and algorithms
- `CHANGELOG.md` - Version history and updates
- OpenDC Documentation: [opendc.org](https://opendc.org)

---

**Last Updated:** December 9, 2025
