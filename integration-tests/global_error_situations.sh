#!/bin/bash
set -ue
cd $(dirname "$0")

filename=$(basename -- "$0")
cd "${filename%%.*}"

../../generate_aspect.py testcampaign.json > /dev/null

rm -Rf testcampaign_experiments
../../generate_experiments.py testcampaign.json > /dev/null

ls testcampaign_experiments
