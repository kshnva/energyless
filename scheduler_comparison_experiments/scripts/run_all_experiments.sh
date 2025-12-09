#!/bin/bash
# Scheduler Comparison Experiments Runner
# This script runs all scheduler comparison experiments in sequence

echo "=================================="
echo "Scheduler Comparison Experiments"
echo "=================================="
echo ""

cd /home/energyless

RUNNER="./OpenDCExperimentRunner/bin/OpenDCExperimentRunner"
BASE_PATH="scheduler_comparison_experiments"

# Check if runner exists
if [ ! -f "$RUNNER" ]; then
    echo "❌ Error: OpenDCExperimentRunner not found at $RUNNER"
    echo "Please build OpenDC first using ./build_opendc_runner.sh"
    exit 1
fi

# Define experiments
experiments=(
    "baseline_random_experiment.json:Baseline Random Scheduler"
    "baseline_mem_experiment.json:Baseline Memory Scheduler"
    "workflow_aware_experiment.json:Workflow-Aware Scheduler"
    "carbon_aware_experiment.json:Carbon-Aware Scheduler"
)

total=${#experiments[@]}
current=0

# Run each experiment
for exp_info in "${experiments[@]}"; do
    IFS=':' read -r exp_file exp_name <<< "$exp_info"
    current=$((current + 1))
    
    echo ""
    echo "[$current/$total] Running: $exp_name"
    echo "----------------------------------------"
    echo "Config: $BASE_PATH/$exp_file"
    echo ""
    
    $RUNNER --experiment-path "$BASE_PATH/$exp_file"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ $exp_name completed successfully!"
    else
        echo ""
        echo "❌ $exp_name failed!"
        echo ""
        read -p "Continue with remaining experiments? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    echo "========================================"
done

echo ""
echo "=================================="
echo "✅ All Experiments Completed!"
echo "=================================="
echo ""
echo "Results are available in the output/ directory:"
echo "  - output/baseline_random_scheduler/"
echo "  - output/baseline_mem_scheduler/"
echo "  - output/workflow_aware_scheduler/"
echo "  - output/carbon_aware_workflow_scheduler/"
echo ""
echo "Use the Jupyter notebook to analyze results:"
echo "  jupyter notebook scheduler_comparison_experiments/run_comparison_experiments.ipynb"
echo ""
