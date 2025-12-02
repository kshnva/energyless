#! /bin/bash

python opendc-traces/workload/generate_synthetic_workflow_examples.py

rm -rf input/synthetic_traces

cp -r synthetic_workflow_traces/ input/synthetic_traces

rm -rf synthetic_workflow_traces

echo "Synthetic traces generated and moved to input/synthetic_traces"