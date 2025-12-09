#!/bin/bash

# Quick launcher for carbon-aware parameter sweep
# This script provides an easy way to run the parameter optimization

echo "================================================================================"
echo "  Carbon-Aware Scheduler Parameter Sweep"
echo "================================================================================"
echo ""
echo "This will test 10 different scheduler configurations to find optimal"
echo "carbon reduction parameters."
echo ""
echo "Estimated time: 20-50 minutes"
echo ""
echo "Results will be saved to: parameter_sweep_results/"
echo ""
echo "================================================================================"
echo ""

# Confirm before running
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Starting parameter sweep..."
echo ""

# Run the sweep
cd /home/energyless/scheduler_comparison_experiments
python3 carbon_aware_parameter_sweep.py

# Check if successful
if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================================"
    echo "✅ SWEEP COMPLETED SUCCESSFULLY!"
    echo "================================================================================"
    echo ""
    echo "Results saved to: parameter_sweep_results/"
    echo ""
    echo "Next steps:"
    echo "  1. Review: parameter_sweep_results/sweep_summary_*.txt"
    echo "  2. Check: parameter_sweep_results/sweep_results_*.csv for full data"
    echo "  3. Use: carbon_aware_optimal.json for your experiments"
    echo ""
else
    echo ""
    echo "================================================================================"
    echo "❌ SWEEP FAILED"
    echo "================================================================================"
    echo ""
    echo "Check the error messages above for details."
    echo ""
    exit 1
fi
