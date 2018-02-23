#!/bin/bash
set -ue
cd $(dirname $(realpath "$0"))

echo "Validating schema_examples/interface_*.json against schemas/interface.schema."
echo ""

for i in $(find ../schema_examples -name "interface_*.json"); do
	echo "Validating JSON file $(basename "${i}")"
	ajv -d "${i}" -s ../schemas/interface.schema
done
