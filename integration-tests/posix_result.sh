#!/bin/bash
set -ue
cd $(dirname "$0")

cd posix_result

../../aofit.py testcampaign.json >/dev/null
cat testcampaign.ah
