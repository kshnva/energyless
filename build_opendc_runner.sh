#!/bin/bash

set -e

cd opendc

./gradlew clean
./gradlew :opendc-experiments:opendc-experiments-base:assembleDist

cd opendc-experiments/opendc-experiments-base/build/distributions

mv OpenDCExperimentRunner.zip ../../../../..
cd ../../../../..

unzip -o OpenDCExperimentRunner.zip
rm OpenDCExperimentRunner.zip

echo "OpenDCExperimentRunner built and extracted successfully."