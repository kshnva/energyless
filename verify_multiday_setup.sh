#!/bin/bash
# Verification script for multi-day carbon testing setup

echo "======================================================================"
echo "MULTI-DAY CARBON TESTING SETUP VERIFICATION"
echo "======================================================================"
echo ""

# Check 1: Trace generator updated
echo "✓ Check 1: Trace Generator Durations"
echo "----------------------------------------------------------------------"
if grep -q "3_600_000 + random.randint(0, 10_800_000)" /home/energyless/opendc-traces/workload/generate_synthetic_workflow_examples.py; then
    echo "  ✅ carbon_test_long: 1-4 hour tasks (3.6M - 14.4M ms)"
else
    echo "  ❌ carbon_test_long: Still using old durations"
fi

if grep -q "7_200_000 + random.randint(0, 14_400_000)" /home/energyless/opendc-traces/workload/generate_synthetic_workflow_examples.py; then
    echo "  ✅ carbon_test_chains: 2-6 hour tasks (7.2M - 21.6M ms)"
else
    echo "  ❌ carbon_test_chains: Still using old durations"
fi

if grep -q "padding_ms: int = 604_800_000" /home/energyless/opendc-traces/workload/generate_synthetic_workflow_examples.py; then
    echo "  ✅ Deadline padding: 7 days (604.8M ms)"
else
    echo "  ❌ Deadline padding: Still using old value"
fi
echo ""

# Check 2: Synthetic traces exist
echo "✓ Check 2: Synthetic Traces Generated"
echo "----------------------------------------------------------------------"
if ls /home/energyless/input/synthetic_traces/carbon_test_long_* 1> /dev/null 2>&1; then
    COUNT=$(ls -d /home/energyless/input/synthetic_traces/carbon_test_long_* 2>/dev/null | wc -l)
    echo "  ✅ Found $COUNT carbon_test_long workload variants"
else
    echo "  ❌ No carbon_test_long workloads found"
fi

if ls /home/energyless/input/synthetic_traces/carbon_test_chains_* 1> /dev/null 2>&1; then
    COUNT=$(ls -d /home/energyless/input/synthetic_traces/carbon_test_chains_* 2>/dev/null | wc -l)
    echo "  ✅ Found $COUNT carbon_test_chains workload variants"
else
    echo "  ❌ No carbon_test_chains workloads found"
fi
echo ""

# Check 3: Topology using DE carbon trace
echo "✓ Check 3: Carbon Trace Configuration"
echo "----------------------------------------------------------------------"
if grep -q "DE_2021-2024.parquet" /home/energyless/input/topologies/sample_NL_small.json; then
    echo "  ✅ Using Germany (DE) carbon trace"
else
    if grep -q "NL_2021-2024.parquet" /home/energyless/input/topologies/sample_NL_small.json; then
        echo "  ⚠️  Still using Netherlands (NL) trace"
    else
        echo "  ❓ Unknown carbon trace configuration"
    fi
fi
echo ""

# Check 4: Experiment configuration
echo "✓ Check 4: Experiment Workload Configuration"
echo "----------------------------------------------------------------------"
for exp in baseline_random baseline_mem workflow_aware carbon_aware; do
    CONFIG="/home/energyless/scheduler_comparison_experiments/${exp}_experiment.json"
    if [ -f "$CONFIG" ]; then
        if grep -q "carbon_test_long_n120" "$CONFIG"; then
            echo "  ✅ $exp: Using carbon_test_long_n120"
        else
            WORKLOAD=$(grep -o '"pathToFile": "[^"]*"' "$CONFIG" | head -1 | cut -d'"' -f4 | rev | cut -d'/' -f1 | rev)
            echo "  ⚠️  $exp: Using $WORKLOAD"
        fi
    else
        echo "  ❌ $exp: Config file not found"
    fi
done
echo ""

# Check 5: Visualization functions
echo "✓ Check 5: Visualization Functions Fixed"
echo "----------------------------------------------------------------------"
if grep -q "xlim_min = min(power\['timestamp_s'\].min()" /home/energyless/scheduler_comparison_experiments/run_comparison_experiments.ipynb; then
    echo "  ✅ Visualization functions start at first valid CI value"
else
    echo "  ❌ Visualization functions still start at 0"
fi
echo ""

# Summary
echo "======================================================================"
echo "VERIFICATION COMPLETE"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "  1. Open run_comparison_experiments.ipynb"
echo "  2. Run experiment cells (may take several minutes)"
echo "  3. Review visualizations for multi-day carbon patterns"
echo "  4. Compare carbon-aware vs baseline schedulers"
echo ""
echo "Expected improvements with multi-day setup:"
echo "  • Daily carbon intensity cycles visible in plots"
echo "  • Carbon-aware delays tasks by hours/days (not minutes)"
echo "  • 15-40% carbon reduction expected"
echo "  • Clear task clustering in low-carbon windows"
echo ""
