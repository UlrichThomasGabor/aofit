#!/bin/bash
set -ue
BASEPATH=$(dirname $(realpath "$0"))
EXPERIMENT_DIR=$(pwd)

if [[ $# -lt 1 ]]; then
	echo "Pass the filename to the variable script." >&2
	exit 1
fi
if [[ $# -ge 2 ]]; then
	OCCURENCESFILE="$2"
else
	OCCURENCESFILE=""
fi

rm -Rf $EXPERIMENT_DIR/output.log

ENVVARS=$(mktemp)
trap "rm -Rf $ENVVARS" EXIT

source $1 # Should be in adequate shape, achieved by writeConfig()
cd $BASEPATH/testproject/ && ./a.out > $EXPERIMENT_DIR/output.log 2>&1

if [[ "$OCCURENCESFILE" != "" ]]; then
	cp $EXPERIMENT_DIR/output.log "$OCCURENCESFILE"
fi
