#!/usr/bin/env python3
import os
import subprocess
import sys
import time
import tempfile
import atexit

from pyaofit import *

if __name__ == "__main__":
	parser = get_default_args_parser()
	args = parser.parse_args()
	campaign = run_defaults(args)

	printVerbose("Compiling...")
	ct_begin = time.time();
	printVerbose(campaign['buildCommand'])
	compile_process = subprocess.run(campaign['buildCommand'], shell=True)
	buildStatus = compile_process.returncode
	ct_end = time.time();
	printVerbose("Compiling took " + str(ct_end - ct_begin) + " seconds.")
	if buildStatus != 0:
		sys.exit("Compile Error!")

	printVerbose("Preparing to run software")
	experiment_dir = campaign.experiment_directory
	if os.path.exists(experiment_dir):
		sys.exit("The directory " + experiment_dir + " already exists. Please delete it or move it away.")
	else:
		printVerbose("Creating directory " + experiment_dir)
		os.makedirs(experiment_dir)
	(variableFD, variableFileName) = tempfile.mkstemp(text=True)
	atexit.register(os.remove, variableFileName)
	atexit.register(os.close, variableFD)
	(occurencesFD, occurencesFileName) = tempfile.mkstemp(text=True)
	atexit.register(os.remove, occurencesFileName)
	atexit.register(os.close, occurencesFD)

	printVerbose("########## Occurence Count ##########")
	with open(variableFileName, 'w') as f:
		writeConfig(generateOccurenceCountConfig(campaign), f)
	printVerbose(campaign['experimentCommand'] + " " + variableFileName + " " + occurencesFileName)
	count_process = subprocess.run(campaign['experimentCommand'] + " " + variableFileName + " " + occurencesFileName, shell=True)
	print("Count Occurences Run: program returned " + str(count_process.returncode) + "\n\n")

	with open(occurencesFileName, 'r') as f:
		output_lines = f.read().splitlines()
	normal_output_ended = False
	occurences = []
	jpids = []
	i = 1
	for line in output_lines:
		if normal_output_ended:
			if i <= campaign.numberOfTargets:
				occurences.append(int(line))
			else:
				jpids.append(int(line))
			i += 1
		elif line == "Experiment ends.":
			normal_output_ended = True
	if normal_output_ended == False:
		sys.exit("Application was not executed correctly.")
	printVerbose("Received occurences: " + str(occurences))
	printVerbose("Received JPIDs: " + str(jpids))

	printVerbose("Preparing campaign '" + campaign.name + "'...")
	experiment_dir = campaign.experiment_directory + "goldenrun/"
	os.makedirs(experiment_dir)
	with open(experiment_dir + "configuration", 'w') as f:
		writeConfig(generateGoldenRunConfig(campaign), f)

	exp = 0
	for experiment in campaign['experiments']:
		printVerbose("########## Experiment " + str(exp) + " ##########")
		target = campaign.getTarget(experiment['target'])
		target_id = campaign.getTargetId(experiment['target'])
		if target_id == None or target == None:
			sys.exit("You requested a non-existent target in experiment " + str(exp))
		injection_mode = experiment['injection_mode']

		printVerbose("Experiment mode: " + experiment['experiment_mode'])
		printVerbose("Injection mode: " + experiment['injection_mode'])
		if experiment['experiment_mode'] == "call_count":
			experiment_counter_start = experiment['callCount']
			experiment_counter_stop = experiment['callCount']
		elif experiment['experiment_mode'] == "each_occurrence_once":
			experiment_counter_start = 0
			experiment_counter_stop = int(occurences[target_id])
		else:
			sys.exit("Unknown experiment_mode.")

		if "acmodelfilename" in campaign and "noerrorattributequalifier" in campaign:
			ignoreErrorSituations = ignorableErrorSituationsForJPID(campaign.directory + campaign["acmodelfilename"], campaign["noerrorattributequalifier"], jpids[target_id])
			printVerbose("Ignore Error Situations: " + str(ignoreErrorSituations))
		else:
			ignoreErrorSituations = []

		for i in range(experiment_counter_start, experiment_counter_stop+1):
			if experiment['injection_mode'] == "each":
				injection_counter_start = 0
				injection_counter_stop = len(target['error_situations']) - 1
			elif experiment['injection_mode'] in ["replace", "invert", "offsetplus", "offsetminus"]:
				injection_counter_start = 0
				injection_counter_stop = 0
			else:
				sys.exit("Unknown injection_mode.")
			for j in range(injection_counter_start, injection_counter_stop+1):
				if target['error_situations'][j]["id"] != None and target['error_situations'][j]["id"] in ignoreErrorSituations:
					printVerbose("Skipped experiment " + str(j) + ", because it was in `ignoreErrorSituations`.")
					continue;

				vars = {}
				vars[campaign.prefix + '_countOccurences'] = "false"
				if experiment['injection_mode'] == "each":
					vars[campaign.prefix + '_injection_mode'] = '(injection_type)replace'
				else:
					vars[campaign.prefix + '_injection_mode'] = '(injection_type)' + experiment['injection_mode']
				vars[campaign.prefix + '_loglevel'] = int(campaign['logLevel'])
				for targetid in range(0, campaign.numberOfTargets):
					if targetid == target_id:
						vars[campaign.prefix + '_activeTargets[' + str(targetid) + ']'] = 1
						if experiment['injection_mode'] == "each":
							vars[campaign.prefix + '_valueID[' + str(targetid) + ']'] = j
						else:
							vars[campaign.prefix + '_callCountLimits[' + str(targetid) + ']'] = i
							if "error_situation_index" in experiment:
								vars[campaign.prefix + '_valueID[' + str(targetid) + ']'] = int(experiment["error_situation_index"])
							else:
								vars[campaign.prefix + '_valueID[' + str(targetid) + ']'] = 0
					else:
						# If not active, do not set every variable to save time.
						vars[campaign.prefix + '_activeTargets[' + str(targetid) + ']'] = 0

				experiment_dir = campaign.experiment_directory + "exp_" + str(exp) + "_" + str(i) + "_" + str(j) + "/"
				os.makedirs(experiment_dir)
				with open(experiment_dir + "configuration", 'w') as f:
					writeConfig(vars, f)
		exp += 1

	print("Generated all experiments.")
