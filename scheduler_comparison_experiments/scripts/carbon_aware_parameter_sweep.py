#!/usr/bin/env python3
"""
Carbon-Aware Scheduler Parameter Sweep

Runs experiments across different carbon-aware scheduler configurations
to identify the optimal settings for carbon reduction.

Key Parameters to Tune:
- carbonDelayThreshold: Percentile threshold for high carbon (0.1-0.5)
- maxDelayHours: Maximum delay window (2-12 hours)
- forecastHorizon: How far ahead to look (12-72 hours)
- slackThresholdMultiplier: Safety margin for deadlines (1.2-3.0)
- prioritizeCriticalPath: Enable workflow-aware heuristics (True/False)
"""

import subprocess
import json
import pandas as pd
import numpy as np
from pathlib import Path
import itertools
from datetime import datetime

# Base directory
BASE_DIR = Path("/home/energyless")
RUNNER_PATH = BASE_DIR / "OpenDCExperimentRunner/bin/OpenDCExperimentRunner"
EXPERIMENTS_DIR = BASE_DIR / "scheduler_comparison_experiments"
OUTPUT_DIR = BASE_DIR / "output"
RESULTS_DIR = EXPERIMENTS_DIR / "parameter_sweep_results"

# Create results directory
RESULTS_DIR.mkdir(exist_ok=True)

# Base experiment configuration (template)
BASE_CONFIG = {
    "name": "carbon_aware_sweep",
    "topologies": [
        {"pathToFile": "input/topologies/sample_NL_small.json"}
    ],
    "workloads": [
        {
            "pathToFile": "input/synthetic_traces/carbon_test_long_n120_edge_prob0.3_seed1_deadline_default",
            "type": "ComputeWorkload"
        }
    ],
    "allocationPolicies": [
        {
            "type": "carbonAware",
            "filters": [
                {"type": "Compute"},
                {"type": "VCpu", "allocationRatio": 1.0},
                {"type": "Ram", "allocationRatio": 1.0}
            ],
            "weighers": [
                {"type": "Ram", "multiplier": 1.0}
            ],
            "subsetSize": 1,
            # Parameters to be swept (defaults below)
            "carbonDelayThreshold": 0.2,
            "maxDelayHours": 8,
            "forecastHorizon": 48,
            "slackThresholdMultiplier": 1.5,
            "prioritizeCriticalPath": False
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

# Parameter sweep ranges
SWEEP_CONFIGS = [
    # Baseline: current configuration
    {
        "name": "baseline_current",
        "carbonDelayThreshold": 0.2,
        "maxDelayHours": 8,
        "forecastHorizon": 48,
        "slackThresholdMultiplier": 1.5,
        "prioritizeCriticalPath": False
    },
    
    # Aggressive carbon optimization
    {
        "name": "aggressive_low_threshold",
        "carbonDelayThreshold": 0.1,  # Only delay during top 10% high carbon
        "maxDelayHours": 12,
        "forecastHorizon": 72,
        "slackThresholdMultiplier": 2.0,
        "prioritizeCriticalPath": True
    },
    
    # Conservative approach (safety first)
    {
        "name": "conservative_high_safety",
        "carbonDelayThreshold": 0.3,
        "maxDelayHours": 4,
        "forecastHorizon": 24,
        "slackThresholdMultiplier": 2.5,
        "prioritizeCriticalPath": True
    },
    
    # Balanced workflow-aware
    {
        "name": "balanced_workflow_aware",
        "carbonDelayThreshold": 0.2,
        "maxDelayHours": 8,
        "forecastHorizon": 48,
        "slackThresholdMultiplier": 2.0,
        "prioritizeCriticalPath": True
    },
    
    # Long forecast horizon
    {
        "name": "long_horizon",
        "carbonDelayThreshold": 0.15,
        "maxDelayHours": 10,
        "forecastHorizon": 72,
        "slackThresholdMultiplier": 2.0,
        "prioritizeCriticalPath": True
    },
    
    # Short forecast, quick decisions
    {
        "name": "short_horizon_reactive",
        "carbonDelayThreshold": 0.25,
        "maxDelayHours": 6,
        "forecastHorizon": 12,
        "slackThresholdMultiplier": 1.8,
        "prioritizeCriticalPath": True
    },
    
    # Very aggressive (maximum carbon reduction attempt)
    {
        "name": "very_aggressive",
        "carbonDelayThreshold": 0.05,  # Delay during top 5% high carbon
        "maxDelayHours": 16,
        "forecastHorizon": 96,
        "slackThresholdMultiplier": 2.5,
        "prioritizeCriticalPath": True
    },
    
    # Medium slack, workflow-aware
    {
        "name": "medium_slack_workflow",
        "carbonDelayThreshold": 0.2,
        "maxDelayHours": 8,
        "forecastHorizon": 48,
        "slackThresholdMultiplier": 1.8,
        "prioritizeCriticalPath": True
    },
    
    # Tight threshold, long delay window
    {
        "name": "tight_threshold_long_delay",
        "carbonDelayThreshold": 0.15,
        "maxDelayHours": 12,
        "forecastHorizon": 60,
        "slackThresholdMultiplier": 2.2,
        "prioritizeCriticalPath": True
    },
    
    # Workflow-disabled comparison
    {
        "name": "no_workflow_awareness",
        "carbonDelayThreshold": 0.2,
        "maxDelayHours": 8,
        "forecastHorizon": 48,
        "slackThresholdMultiplier": 1.5,
        "prioritizeCriticalPath": False
    }
]


def create_experiment_config(config_params):
    """Create experiment JSON with given parameters."""
    config = BASE_CONFIG.copy()
    config["name"] = f"carbon_aware_sweep_{config_params['name']}"
    
    # Update allocation policy parameters
    policy = config["allocationPolicies"][0].copy()
    policy.update({
        "carbonDelayThreshold": config_params["carbonDelayThreshold"],
        "maxDelayHours": config_params["maxDelayHours"],
        "forecastHorizon": config_params["forecastHorizon"],
        "slackThresholdMultiplier": config_params["slackThresholdMultiplier"],
        "prioritizeCriticalPath": config_params["prioritizeCriticalPath"]
    })
    config["allocationPolicies"][0] = policy
    
    return config


def run_experiment(config_params, config_num, total_configs):
    """Run a single experiment with given configuration."""
    config = create_experiment_config(config_params)
    exp_name = config_params['name']
    
    # Save experiment config
    config_file = EXPERIMENTS_DIR / f"sweep_{exp_name}.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"Experiment {config_num}/{total_configs}: {exp_name}")
    print(f"{'='*80}")
    print(f"Parameters:")
    print(f"  carbonDelayThreshold: {config_params['carbonDelayThreshold']}")
    print(f"  maxDelayHours: {config_params['maxDelayHours']}")
    print(f"  forecastHorizon: {config_params['forecastHorizon']}")
    print(f"  slackThresholdMultiplier: {config_params['slackThresholdMultiplier']}")
    print(f"  prioritizeCriticalPath: {config_params['prioritizeCriticalPath']}")
    print(f"\nRunning experiment...")
    
    # Run experiment
    result = subprocess.run(
        [str(RUNNER_PATH), "--experiment-path", str(config_file)],
        capture_output=True,
        text=True,
        cwd=str(BASE_DIR)
    )
    
    if result.returncode != 0:
        print(f"❌ Experiment failed!")
        print(result.stderr)
        return None
    
    print(f"✅ Experiment completed!")
    
    # Load and parse results
    output_name = f"carbon_aware_sweep_{exp_name}"
    output_path = OUTPUT_DIR / output_name / "raw-output/0/seed=0"
    
    try:
        metrics = parse_experiment_results(output_path, exp_name, config_params)
        return metrics
    except Exception as e:
        print(f"❌ Failed to parse results: {e}")
        return None


def parse_experiment_results(output_path, exp_name, config_params):
    """Parse experiment results and calculate metrics."""
    power_df = pd.read_parquet(output_path / "powerSource.parquet")
    task_df = pd.read_parquet(output_path / "task.parquet")
    host_df = pd.read_parquet(output_path / "host.parquet")
    service_df = pd.read_parquet(output_path / "service.parquet")
    
    # Calculate metrics
    metrics = {
        'experiment': exp_name,
        
        # Configuration parameters
        'carbonDelayThreshold': config_params['carbonDelayThreshold'],
        'maxDelayHours': config_params['maxDelayHours'],
        'forecastHorizon': config_params['forecastHorizon'],
        'slackThresholdMultiplier': config_params['slackThresholdMultiplier'],
        'prioritizeCriticalPath': config_params['prioritizeCriticalPath'],
        
        # Carbon metrics (PRIMARY OBJECTIVE)
        'total_carbon_kg': power_df['carbon_emission'].sum(),
        'avg_carbon_intensity': power_df['carbon_intensity'].mean(),
        
        # Energy metrics
        'total_energy_kwh': power_df['energy_usage'].sum() / (1000 * 1000),
        
        # Performance metrics
        'makespan_hours': task_df['finish_time'].max() / (1000 * 3600),
        'avg_task_wait_time_hours': task_df['scheduling_delay'].mean() / (1000 * 3600),
        'max_task_wait_time_hours': task_df['scheduling_delay'].max() / (1000 * 3600),
        
        # Task completion
        'total_tasks': len(task_df),
        'completed_tasks': len(task_df[task_df['task_state'] == 'COMPLETED']),
        
        # Resource utilization
        'avg_cpu_utilization': host_df['cpu_utilization'].mean() * 100,
        'avg_cpu_usage': host_df['cpu_usage'].mean() * 100,
    }
    
    # Calculate derived metrics
    metrics['completion_rate'] = metrics['completed_tasks'] / metrics['total_tasks'] * 100
    
    return metrics


def main():
    """Run parameter sweep and analyze results."""
    print("="*80)
    print("CARBON-AWARE SCHEDULER PARAMETER SWEEP")
    print("="*80)
    print(f"\nTotal configurations to test: {len(SWEEP_CONFIGS)}")
    print(f"Results will be saved to: {RESULTS_DIR}")
    print(f"\nStarting sweep at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all experiments
    all_metrics = []
    
    for i, config in enumerate(SWEEP_CONFIGS, 1):
        metrics = run_experiment(config, i, len(SWEEP_CONFIGS))
        if metrics:
            all_metrics.append(metrics)
    
    # Create results DataFrame
    df_results = pd.DataFrame(all_metrics)
    
    # Save raw results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = RESULTS_DIR / f"sweep_results_{timestamp}.csv"
    df_results.to_csv(csv_file, index=False)
    print(f"\n✅ Raw results saved to: {csv_file}")
    
    # Analysis and ranking
    print("\n" + "="*80)
    print("RESULTS ANALYSIS")
    print("="*80)
    
    # Sort by carbon emissions (primary objective)
    df_sorted = df_results.sort_values('total_carbon_kg')
    
    print("\n🏆 TOP 5 CONFIGURATIONS (Lowest Carbon Emissions):")
    print("-"*80)
    
    for rank, (idx, row) in enumerate(df_sorted.head(5).iterrows(), 1):
        print(f"\n{rank}. {row['experiment']}")
        print(f"   Total Carbon: {row['total_carbon_kg']:.2f} kg CO2")
        print(f"   Makespan: {row['makespan_hours']:.2f} hours")
        print(f"   Avg Wait Time: {row['avg_task_wait_time_hours']:.2f} hours")
        print(f"   Completion Rate: {row['completion_rate']:.1f}%")
        print(f"   Parameters:")
        print(f"     - carbonDelayThreshold: {row['carbonDelayThreshold']}")
        print(f"     - maxDelayHours: {row['maxDelayHours']}")
        print(f"     - forecastHorizon: {row['forecastHorizon']}")
        print(f"     - slackThresholdMultiplier: {row['slackThresholdMultiplier']}")
        print(f"     - prioritizeCriticalPath: {row['prioritizeCriticalPath']}")
    
    # Calculate improvements vs baseline
    baseline = df_results[df_results['experiment'] == 'baseline_current'].iloc[0]
    
    print("\n\n📊 IMPROVEMENTS VS BASELINE:")
    print("-"*80)
    
    for idx, row in df_sorted.iterrows():
        if row['experiment'] == 'baseline_current':
            continue
        
        carbon_improvement = ((baseline['total_carbon_kg'] - row['total_carbon_kg']) / 
                             baseline['total_carbon_kg']) * 100
        makespan_change = ((row['makespan_hours'] - baseline['makespan_hours']) / 
                          baseline['makespan_hours']) * 100
        wait_change = ((row['avg_task_wait_time_hours'] - baseline['avg_task_wait_time_hours']) / 
                       baseline['avg_task_wait_time_hours']) * 100
        
        print(f"\n{row['experiment']}:")
        print(f"   Carbon: {carbon_improvement:+.2f}% ({row['total_carbon_kg']:.2f} kg)")
        print(f"   Makespan: {makespan_change:+.2f}% ({row['makespan_hours']:.2f} hrs)")
        print(f"   Wait Time: {wait_change:+.2f}% ({row['avg_task_wait_time_hours']:.2f} hrs)")
    
    # Save summary
    summary_file = RESULTS_DIR / f"sweep_summary_{timestamp}.txt"
    with open(summary_file, 'w') as f:
        f.write("CARBON-AWARE SCHEDULER PARAMETER SWEEP SUMMARY\n")
        f.write("="*80 + "\n\n")
        f.write(f"Sweep completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total configurations tested: {len(df_results)}\n\n")
        f.write("\nTOP CONFIGURATION:\n")
        f.write("-"*80 + "\n")
        best = df_sorted.iloc[0]
        f.write(f"Name: {best['experiment']}\n")
        f.write(f"Total Carbon: {best['total_carbon_kg']:.2f} kg CO2\n")
        f.write(f"Carbon Improvement: {((baseline['total_carbon_kg'] - best['total_carbon_kg']) / baseline['total_carbon_kg']) * 100:.2f}%\n")
        f.write(f"Makespan: {best['makespan_hours']:.2f} hours\n")
        f.write(f"Parameters:\n")
        f.write(f"  carbonDelayThreshold: {best['carbonDelayThreshold']}\n")
        f.write(f"  maxDelayHours: {best['maxDelayHours']}\n")
        f.write(f"  forecastHorizon: {best['forecastHorizon']}\n")
        f.write(f"  slackThresholdMultiplier: {best['slackThresholdMultiplier']}\n")
        f.write(f"  prioritizeCriticalPath: {best['prioritizeCriticalPath']}\n")
    
    print(f"\n✅ Summary saved to: {summary_file}")
    
    print("\n" + "="*80)
    print(f"SWEEP COMPLETED at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    return df_results


if __name__ == "__main__":
    results = main()
