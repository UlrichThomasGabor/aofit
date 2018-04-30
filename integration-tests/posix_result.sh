#!/bin/bash
set -ue
cd $(dirname "$0")

cd posix_result

../../generate_aspect.py testcampaign.json
ls testcampaign.ah
