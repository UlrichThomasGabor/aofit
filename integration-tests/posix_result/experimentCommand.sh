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

GDBCOMMANDS=$(mktemp)
trap "rm -Rf $GDBCOMMANDS" EXIT

echo "" > $GDBCOMMANDS
if [[ $(command -v lldb &>/dev/null ; echo $?) == 0 ]]; then
	echo "process launch --stop-at-entry -o $EXPERIMENT_DIR/output.log -e $EXPERIMENT_DIR/output.log --" >> $GDBCOMMANDS
	# List all variables:
	# $ target variable
	# Change one variable:
	# $ expr test_probabilities[0] = 2
	# Set a breakpoint:
	# $ break -n main
	cat "$1" | sed 's/^/expr /' >> $GDBCOMMANDS
	echo "continue" >> $GDBCOMMANDS
	echo "exit" >> $GDBCOMMANDS
	cd $BASEPATH/testproject/
	lldb -s $GDBCOMMANDS $BASEPATH/testproject/a.out
else
	echo "break *0x0" >> $GDBCOMMANDS # Break on entry.
	echo "run >& $EXPERIMENT_DIR/output.log" >> $GDBCOMMANDS
	# List all variables:
	# $ info variables
	# Change one variable:
	# $ set variable idx = 1
	cat "$1" | sed 's/^/set variable /' >> $GDBCOMMANDS
	echo "continue" >> $GDBCOMMANDS
	echo "quit" >> $GDBCOMMANDS
	cd $BASEPATH/testproject/
	gdb -x $GDBCOMMANDS $BASEPATH/testproject/a.out
fi

if [[ "$OCCURENCESFILE" != "" ]]; then
	cp $EXPERIMENT_DIR/output.log "$OCCURENCESFILE"
fi
