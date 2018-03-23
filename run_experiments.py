#!/usr/bin/env python3
import os
import subprocess
import sys

from pyaofit import *

if __name__ == "__main__":
	parser = get_default_args_parser()
	args = parser.parse_args()
	campaign = run_defaults(args)

	printVerbose("Running campaign '" + campaign.name + "'...")
	experiment_dirs = [ f.name for f in os.scandir(campaign.experiment_directory) if f.is_dir() and "configuration" in os.listdir(f.path) ]
	# Move goldenrun to the front.
	experiment_dirs.remove("goldenrun")
	experiment_dirs.insert(0, "goldenrun")
	printVerbose("experiment_dirs: " + str(experiment_dirs))

	for experiment_dir in experiment_dirs:
		printVerbose("########## " + experiment_dir + " ##########")
		printVerbose(campaign.absolute_experimentCommand + " configuration")
		process = subprocess.run(campaign.absolute_experimentCommand + " configuration", cwd=campaign.experiment_directory + experiment_dir, shell=True)
		printVerbose("Execution returned: " + str(process.returncode))

	print("Campaign '" + campaign.name + "' finished.")
