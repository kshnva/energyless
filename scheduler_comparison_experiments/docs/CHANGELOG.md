# Changelog

This document tracks all major changes, enhancements, and fixes to the scheduler comparison project.

---

## Table of Contents

1. [Recent Updates (2025)](#recent-updates-2025)
2. [Carbon-Aware Scheduler Evolution](#carbon-aware-scheduler-evolution)
3. [Workflow-Aware Scheduler Evolution](#workflow-aware-scheduler-evolution)
4. [Visualization & Analysis Tools](#visualization--analysis-tools)
5. [Infrastructure & Testing](#infrastructure--testing)

---

## Recent Updates (2025)

### Workflow-Aware Parallelism Merge

**Date**: January 2025  
**Status**: ✅ Complete

Merged parallelism-aware scoring improvements from upstream while preserving threshold-based carbon-aware scheduler.

**Changes**:
- Added parallelism scoring to `WorkflowAwareScheduler`
- New parameters: `enableParallelismScore`, `weightParallelism`, `parallelismDecayRate`
- Parallelism scoring only activates when ready pool is small (< `taskLookaheadThreshold`)
- Created `workflow_aware_parallelism_experiment.json` with parallelism enabled

**Configuration Updates**:
```kotlin
// New WorkflowAwareScheduler parameters
enableParallelismScore = false  // Default: disabled
weightParallelism = 0.0         // Weight for parallelism score
parallelismDecayRate = 0.15     // Decay rate for parallelism calculation
```

**Files Modified**:
- `WorkflowAwareScheduler.kt` - Added parallelism scoring logic
- `AllocationPolicySpec.kt` - Added parallelism parameters
- Experiment configs updated with new parameters

**Documentation**: See `WORKFLOW_AWARE_MERGE_NOTES.md` for detailed merge notes

---

### Notebook Cleanup & Reorganization

**Date**: January 2025  
**Status**: ✅ Complete

Comprehensive cleanup of `run_comparison_experiments.ipynb` to improve organization and reduce duplication.

**Improvements**:
- Reorganized into 9 clear sections with numbered hierarchy
- Consolidated all function definitions into Section 5
- Removed ~13 duplicate analysis cells
- Reduced file size by 39% (1369 → 840 lines)
- Reduced cell count by 30% (43 → 30 cells)

**New Structure**:
1. Workload Analysis Functions
2. Run Experiments
3. Load Results
4. Calculate Metrics
5. Visualization Functions (consolidated)
6. Comparative Visualizations
7. Detailed Scheduler Analysis
8. Timeshift Analysis
9. Export Results

**Documentation**: See `NOTEBOOK_CLEANUP_SUMMARY.md` for details

---

### Project Structure Reorganization

**Date**: January 2025  
**Status**: ✅ Complete

Reorganized project into logical directory structure with comprehensive documentation.

**New Directory Structure**:
```
scheduler_comparison_experiments/
├── configs/
│   ├── baseline/          # Baseline scheduler configs
│   ├── carbon_aware/      # Carbon-aware configs
│   ├── workflow_aware/    # Workflow-aware configs
│   └── parameter_sweep/   # Parameter sweep experiments
├── docs/
│   ├── USER_GUIDE.md             # Comprehensive usage guide
│   ├── SCHEDULER_ALGORITHMS.md   # Detailed pseudocode
│   └── CHANGELOG.md              # This file
├── notebooks/                     # Jupyter analysis notebooks
└── scripts/                       # Execution and generation scripts
```

**Documentation Created**:
- `docs/USER_GUIDE.md` - Complete user guide with quick start, configs, troubleshooting
- `docs/SCHEDULER_ALGORITHMS.md` - Detailed pseudocode for both schedulers
- `docs/CHANGELOG.md` - Consolidated version history

---

## Carbon-Aware Scheduler Evolution

### Threshold-Based Carbon Delays (Current Implementation)

**Date**: December 2024  
**Status**: ✅ Active Implementation

Replaced greedy carbon-aware approach with percentile threshold-based delays.

**Key Changes**:
- Uses `carbonDelayThreshold` percentile to define "high carbon" periods
- Delays deferrable tasks only when above threshold AND sufficient slack exists
- Avoids greedy optimization that caused excessive delays

**Algorithm**:
```
IF current_carbon > PERCENTILE(forecast, carbonDelayThreshold):
    IF slack > (maxDelayHours × slackThresholdMultiplier):
        DELAY task
```

**Parameters**:
- `carbonDelayThreshold: Double` (default 0.5) - Percentile for high carbon
- `maxDelayHours: Double` (default 4.0) - Maximum delay duration
- `slackThresholdMultiplier: Double` (default 1.5) - Safety margin

**Documentation**: See `CARBON_THRESHOLD_FIX.md`, `CARBON_AWARE_DELAY_FIX.md`

---

### Adaptive Forecast Horizon

**Date**: December 2024  
**Status**: ✅ Implemented

Added adaptive forecast horizon that adjusts based on task deadlines.

**Purpose**: 
- Prevents using long-term forecasts for tasks with short deadlines
- Improves carbon regime detection for urgent tasks
- Maintains at least 1-hour minimum for stable percentile calculations

**Algorithm**:
```
timeUntilDeadlineHours = (task.deadline - currentTime) / 3600000
adaptiveHorizonHours = MIN(forecastHorizon, MAX(1, timeUntilDeadlineHours))
forecast = carbonModel.getForecast(adaptiveHorizonHours)
```

**Benefits**:
- More accurate carbon regime classification for short-deadline tasks
- Better delay decisions based on task-specific timeframes
- Maintains safety with minimum 1-hour window

**Documentation**: See `ADAPTIVE_FORECAST_HORIZON.md`

---

### Critical Path Protection

**Date**: December 2024  
**Status**: ✅ Implemented

Enhanced slack requirements for tasks likely on the critical path.

**Features**:
- **Queue Position Tracking**: Early tasks (position < 5) require 50% more slack
- **Busy Period Detection**: High queue depth (> 20) requires 20% more slack
- **Critical Path Skip Counter**: Tracks how often critical tasks avoid delays

**Safety Mechanisms**:
```
IF queuePosition < 5:
    minSlackNeeded *= 1.5
    
IF queueDepth > 20:
    minSlackNeeded *= 1.2
```

**Documentation**: See `CARBON_AWARE_CONFIG_UPDATE.md`

---

### Carbon Visualization Enhancements

**Date**: December 2024  
**Status**: ✅ Complete

Added comprehensive carbon intensity visualization to Gantt charts.

**Features**:
- Carbon intensity overlay with color gradient (green=low, red=high)
- Configurable percentile thresholds for visualization
- Deadline markers with time-to-deadline annotations
- Multi-day carbon testing support

**Visualization Functions**:
- `plot_gantt_with_carbon_intensity()` - Main visualization function
- `plot_deadline_markers()` - Add deadline annotations
- `plot_carbon_background()` - Carbon intensity gradient overlay

**Documentation**: See `CARBON_INTENSITY_VISUALIZATION_GUIDE.md`, `CARBON_VISUALIZATION_SUMMARY.md`, `DEADLINE_MARKERS_UPDATE.md`

---

### Greedy Carbon-Aware Approach (Deprecated)

**Date**: November 2024  
**Status**: ⚠️ Replaced by threshold-based approach

Initial implementation that scheduled tasks at predicted minimum carbon time.

**Why Deprecated**:
- Caused excessive delays waiting for "perfect" low-carbon periods
- Resulted in deadline violations for tasks with moderate slack
- Ignored workflow dependencies and queue position

**Replacement**: Threshold-based approach with workflow-aware safety (see above)

**Documentation**: See `GREEDY_CARBON_AWARE_SUMMARY.md`, `HYBRID_CARBON_AWARE_PSEUDOCODE.md`

---

## Workflow-Aware Scheduler Evolution

### Parallelism Scoring

**Date**: January 2025  
**Status**: ✅ Implemented

Added optional parallelism-aware scoring to prioritize tasks that unlock parallel execution.

**Features**:
- Calculates how many downstream tasks become ready when a task completes
- Uses decay rate to balance immediate vs. distant parallelism
- Only activates when ready pool is small (< `taskLookaheadThreshold`)

**Algorithm**:
```
IF enableParallelismScore AND readyCount < taskLookaheadThreshold:
    parallelismScore = task.calculateParallelismScore(parallelismDecayRate)
    totalScore += weightParallelism × parallelismScore
```

**Use Cases**:
- Workloads with high potential for parallel execution
- Scenarios where resource utilization is critical
- DAG workflows with multiple independent branches

**Documentation**: See `WORKFLOW_AWARE_MERGE_NOTES.md`

---

### Task Lookahead Optimization

**Date**: December 2024  
**Status**: ✅ Implemented

Limits task evaluation to `taskLookaheadThreshold` for performance.

**Rationale**:
- Large ready queues (1000+ tasks) can slow scheduling decisions
- Most high-priority tasks appear near the front of the queue
- Lookahead provides good balance between quality and performance

**Configuration**:
```kotlin
taskLookaheadThreshold: Int = 1000  // Max tasks to evaluate per round
```

---

### Multi-Criteria Scoring

**Date**: November 2024  
**Status**: ✅ Core Feature

Weighted combination of urgency, critical path, and optional parallelism.

**Scoring Formula**:
```
score = (weightUrgency × urgencyScore) +
        (weightCriticalDependencyChain × chainScore) +
        (weightParallelism × parallelismScore)
```

**Components**:
- **Urgency**: Inverse of slack (1 / (deadline - currentTime))
- **Critical Path**: Length of longest dependency chain
- **Parallelism**: Number of tasks unlocked (optional)

**Typical Weights**:
- Balanced: `[0.2, 0.2, 0.0]` - Equal urgency and critical path
- Deadline-focused: `[0.6, 0.1, 0.0]` - Prioritize urgent tasks
- Parallelism-focused: `[0.2, 0.1, 0.7]` - Maximize resource utilization

---

## Visualization & Analysis Tools

### Multi-Day Carbon Testing

**Date**: December 2024  
**Status**: ✅ Implemented

Extended carbon trace support to multi-day experiments.

**Features**:
- Load carbon traces spanning multiple days
- Test scheduler behavior over extended periods
- Analyze carbon savings across different time scales

**Usage**:
```python
carbon_trace = pd.read_parquet("carbon_traces/US-CA_2021-2024.parquet")
# Filter to specific date range
trace_subset = carbon_trace[carbon_trace['datetime'].between(start, end)]
```

**Documentation**: See `MULTI_DAY_CARBON_TESTING_UPDATE.md`, `RESULTS_REVIEW_MULTI_DAY_TESTING.md`

---

### Gantt Chart Enhancements

**Date**: December 2024  
**Status**: ✅ Complete

Improved Gantt chart visualization with carbon overlays and deadline markers.

**Features**:
- Color-coded task states (running, completed, delayed)
- Carbon intensity background gradient
- Deadline markers with countdown annotations
- Configurable percentile thresholds

**Functions**:
- `create_gantt_chart()` - Base Gantt chart
- `plot_gantt_with_carbon_intensity()` - With carbon overlay
- `plot_deadline_markers()` - Add deadline annotations

---

### Comparative Analysis Notebook

**Date**: November-December 2024  
**Status**: ✅ Active

Jupyter notebook for comprehensive scheduler comparison.

**Analysis Sections**:
1. Workload analysis and trace generation
2. Experiment execution
3. Results loading and preprocessing
4. Metric calculation (deadline violations, carbon emissions, latency)
5. Visualization generation
6. Statistical comparison
7. Detailed scheduler breakdowns
8. Export to CSV/plots

**Key Metrics**:
- Deadline violations (count and percentage)
- Total carbon emissions (gCO2)
- Average task latency
- Workflow completion time
- Carbon reduction percentage

---

## Infrastructure & Testing

### Build System Updates

**Date**: December 2024  
**Status**: ✅ Complete

Verified build system after scheduler changes.

**Commands**:
```bash
cd opendc
./gradlew clean build -x test
./gradlew :opendc-experiments:opendc-experiments-compute:installDist
```

**Documentation**: See `REBUILD_VERIFICATION.md`

---

### Synthetic Trace Generation

**Date**: November 2024  
**Status**: ✅ Implemented

Created scripts for generating synthetic workflow traces with configurable parameters.

**Features**:
- Balanced tree workflows
- Configurable branch factors and depths
- Deadline slack variation
- Task duration distributions

**Scripts**:
- `generate_synthetic_traces.sh` - Main generation script
- `workflow_balanced_tree_experiment.ipynb` - Analysis notebook

**Documentation**: See `TRACE_GENERATION_UPDATES.md`

---

### Parameter Sweep Framework

**Date**: November 2024  
**Status**: ✅ Complete

Created systematic parameter sweep experiments for both schedulers.

**Sweep Parameters**:

**Carbon-Aware**:
- `carbonDelayThreshold`: [0.3, 0.5, 0.7]
- `maxDelayHours`: [2, 4, 6]
- `slackThresholdMultiplier`: [1.3, 1.5, 2.0]

**Workflow-Aware**:
- `weightUrgency`: [0.1, 0.3, 0.5]
- `weightCriticalDependencyChain`: [0.1, 0.3, 0.5]
- `weightParallelism`: [0.0, 0.3, 0.5]

**Analysis**:
- Automated result aggregation
- Performance-carbon tradeoff analysis
- Pareto frontier identification

**Documentation**: See `PARAMETER_SWEEP_GUIDE.md`, `SWEEP_SUMMARY.md`

---

### Timeshift Baseline

**Date**: November 2024  
**Status**: ✅ Implemented

Created timeshift baseline experiment to isolate carbon variation effects.

**Purpose**: 
- Run identical workload at different times of day
- Measure carbon variation from grid intensity alone
- Establish baseline for scheduler comparison

**Experiment**: `timeshift_experiment.json`

**Documentation**: See `TIMESHIFT_BASELINE_APPROACH.md`, `TIMESHIFT_SCHEDULER_SETUP.md`

---

## Migration Notes

### From Greedy to Threshold-Based Carbon Scheduler

**Breaking Changes**:
- Removed `carbonOptimizationWindow` parameter
- Added `carbonDelayThreshold` parameter
- Changed delay logic from "find minimum" to "threshold check"

**Migration**:
```json
// Old (greedy)
{
  "carbonOptimizationWindow": 6
}

// New (threshold-based)
{
  "carbonDelayThreshold": 0.5,
  "maxDelayHours": 4.0,
  "slackThresholdMultiplier": 1.5
}
```

**Impact**: Fewer deadline violations, more predictable delays

---

### Workflow-Aware Config Updates

**New Parameters**:
```json
{
  "enableParallelismScore": false,
  "weightParallelism": 0.0,
  "parallelismDecayRate": 0.15
}
```

**Backward Compatibility**: New parameters have sensible defaults; old configs still work

---

## Known Issues & Limitations

### Carbon-Aware Scheduler

1. **Forecast Dependency**: Requires accurate carbon forecasts; poor forecasts degrade performance
2. **Memory Usage**: Tracks metadata for all tasks; cleaned up on completion but can grow in large workloads
3. **Percentile Sensitivity**: Performance varies with `carbonDelayThreshold`; requires tuning

### Workflow-Aware Scheduler

1. **Lookahead Limit**: Only evaluates first `taskLookaheadThreshold` tasks; may miss high-priority tasks deep in queue
2. **Parallelism Overhead**: Parallelism scoring adds computational cost; only use when beneficial
3. **Weight Tuning**: Optimal weights vary by workload; parameter sweep recommended

---

## Future Enhancements

### Planned Features

1. **Dynamic Weight Adjustment**: Automatically tune weights based on workload characteristics
2. **Multi-Objective Optimization**: Pareto-optimal scheduling for carbon vs. performance
3. **Machine Learning Integration**: Predict optimal delay decisions using historical data
4. **Distributed Scheduling**: Support for multi-datacenter carbon-aware scheduling

### Under Consideration

1. **Real-Time Carbon API**: Integration with live carbon intensity APIs
2. **Cost-Aware Scheduling**: Combined carbon and electricity cost optimization
3. **Renewable Energy Tracking**: Schedule tasks based on renewable generation forecasts
4. **Carbon Budget Constraints**: Hard limits on total emissions per time period

---

## References

### Documentation

- [USER_GUIDE.md](USER_GUIDE.md) - Complete usage guide
- [SCHEDULER_ALGORITHMS.md](SCHEDULER_ALGORITHMS.md) - Detailed pseudocode
- [README.md](../README.md) - Project overview

### Original Documentation (Archived)

These files have been consolidated into this changelog:

- `WORKFLOW_AWARE_MERGE_NOTES.md`
- `NOTEBOOK_CLEANUP_SUMMARY.md`
- `CARBON_THRESHOLD_FIX.md`
- `ADAPTIVE_FORECAST_HORIZON.md`
- `CARBON_AWARE_CONFIG_UPDATE.md`
- `CARBON_AWARE_DELAY_FIX.md`
- `CARBON_INTENSITY_VISUALIZATION_GUIDE.md`
- `CARBON_VISUALIZATION_SUMMARY.md`
- `DEADLINE_MARKERS_UPDATE.md`
- `GREEDY_CARBON_AWARE_SUMMARY.md`
- `HYBRID_CARBON_AWARE_PSEUDOCODE.md`
- `MULTI_DAY_CARBON_TESTING_UPDATE.md`
- `RESULTS_REVIEW_MULTI_DAY_TESTING.md`
- `REBUILD_VERIFICATION.md`
- `TRACE_GENERATION_UPDATES.md`
- `WORKFLOW_AWARE_CARBON_STRATEGIES.md`
- `PARAMETER_SWEEP_GUIDE.md`
- `SWEEP_SUMMARY.md`
- `TIMESHIFT_BASELINE_APPROACH.md`
- `TIMESHIFT_SCHEDULER_SETUP.md`

---

*Last Updated: January 2025*
