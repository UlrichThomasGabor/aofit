#!/bin/bash
set -ue
cd $(dirname $(realpath "$0"))

echo "Validating schema_examples/posix_*.json against schemas/posix_interface.schema."
echo ""

for i in $(find ../schema_examples -name "posix_*.json"); do
	echo "Validating JSON file $(basename "${i}")"
	ajv -d "${i}" -s ../schemas/posix_interface.schema
done
