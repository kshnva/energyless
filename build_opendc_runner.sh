#!/bin/bash

set -e

cd opendc

./gradlew clean
./gradlew :opendc-experiments:opendc-experiments-base:assembleDist

cd opendc-experiments/opendc-experiments-base/build/distributions

# Extract the tar file directly to the project root
tar -xf OpenDCExperimentRunner.tar -C ../../../../..

cd ../../../../..

echo "OpenDCExperimentRunner built and extracted successfully."