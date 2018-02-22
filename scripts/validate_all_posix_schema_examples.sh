#!/bin/bash
set -ue
cd $(dirname $(realpath "$0"))

echo "Validating schema_examples/posix_*.json against schemas/posix_interface.schema."
echo ""

for i in $(find ../schema_examples -name "posix_*.json"); do
	echo "Validating JSON file $(basename "${i}")"
	jsonschema -i "${i}" ../schemas/posix_interface.schema
	if [ $? = 0 ]; then
		echo "ok"
	fi
done
