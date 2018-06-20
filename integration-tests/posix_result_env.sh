#!/bin/bash
set -ue
cd $(dirname "$0")

filename=$(basename -- "$0")
cd "${filename%%.*}"

../../generate_aspect.py testcampaign.json > /dev/null

rm -Rf testcampaign_experiments
../../generate_experiments.py testcampaign.json > /dev/null

../../run_experiments.py testcampaign.json > /dev/null 2>&1

cat testcampaign_experiments/exp_0_1_0/output.log
