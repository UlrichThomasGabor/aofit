#!/bin/bash
set -ue
cd $(dirname $(realpath "$0"))

echo "Validating schema_examples/campaign_*.json against schemas/campaign.schema."
echo ""

for i in $(find ../schema_examples -name "campaign_*.json"); do
	echo "Validating JSON file $(basename "${i}")"
	ajv -d "${i}" -s ../schemas/campaign.schema -r ../schemas/interface.schema
done
