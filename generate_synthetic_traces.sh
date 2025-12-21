#! /bin/bash

cd opendc-traces/workload
# Use python from current environment (pyenv/virtualenv aware)
python generate_synthetic_workflow_examples.py
cd ..

rm -rf input/synthetic_traces

cp -r opendc-traces/workload/synthetic_workflow_traces/ input/synthetic_traces

rm -rf opendc-traces/workload/synthetic_workflow_traces

echo "Synthetic traces generated and moved to input/synthetic_traces"