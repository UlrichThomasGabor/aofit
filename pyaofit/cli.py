import argparse
import subprocess
import sys

from pyaofit import *

def get_default_args_parser():
	parser = argparse.ArgumentParser(description='Run campaign')
	parser.add_argument("campaign_filename", help="The campaign file.", default="campaign.json")
	parser.add_argument("--validate-json", action="store_true", default=False);
	parser.add_argument("--verbose", action="store_true", default=False);
	return parser

def run_defaults(args):
	makePrintVerbose(args.verbose)

	if args.validate_json:
		command = ["ajv", "-s", os.path.dirname(__file__) + "/../schemas/campaign.schema", "-r", os.path.dirname(__file__) + "/../schemas/interface.schema", "-d", args.campaign_filename]
		printVerbose(" ".join(command))
		validation_process = subprocess.run(command, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
		if validation_process.returncode == 0:
			printVerbose(args.campaign_filename + " is valid.")
		else:
			print(validation_process.stdout.decode(encoding=sys.getdefaultencoding()))
			sys.exit("Campaign " + args.campaign_filename + " file is not valid")

	printVerbose("Opening campaign file " + args.campaign_filename)
	campaign = campaignfile.openFile(args.campaign_filename)
	printVerbose(campaign)

	printVerbose("Switching into CWD of campaign file " + campaign.directory)
	os.chdir(campaign.directory)

	return campaign
