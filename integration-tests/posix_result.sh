#!/bin/bash
set -ue
cd $(dirname "$0")

filename=$(basename -- "$0")
cd "${filename%%.*}"

../../generate_aspect.py testcampaign.json
ls testcampaign.ah
