#!/bin/bash
set -ue
cd $(dirname "$0")

filename=$(basename -- "$0")
cd "${filename%%.*}"

../../generate_aspect.py testcampaign.json > /dev/null

rm -Rf testcampaign_experiments
../../generate_experiments.py testcampaign.json > /dev/null

../../run_experiments.py testcampaign.json > /dev/null 2>&1

# The output contains the original fp value, which changes between runs, so replace it.
cat testcampaign_experiments/exp_0_1_0/output.log | sed -E 's/-[0-9]+ --->/-xxxxxxx --->/g'
