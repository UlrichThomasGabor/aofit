#!/usr/bin/env python3
import os
import subprocess
import sys

from pyaofit import *

if __name__ == "__main__":
	parser = get_default_args_parser()
	args = parser.parse_args()
	campaign = run_defaults(args)

	printVerbose("Generating aspect...")
	ah = generateAspect(campaign)

	printVerbose("Writing generated aspect into " + campaign.prefix + ".ah")
	with open(campaign.prefix + ".ah", 'w') as header_file:
		header_file.write(ah)

	printVerbose("done")
