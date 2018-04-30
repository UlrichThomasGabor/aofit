import json
import os
import re

from pyaofit import *

class campaignfile(campaign):
	@classmethod
	def openFile(cls, campaign_filename):
		with open(campaign_filename) as campaign_file:
			campaign_dict = json.load(campaign_file)
		campaign_name = os.path.splitext(os.path.basename(campaign_filename))[0]
		campaign_prefix = re.sub('[\W_]+', '', campaign_name, re.UNICODE)

		if "predefined_interfaces" in campaign_dict:
			for predefined_interface_path in campaign_dict["predefined_interfaces"]:
				predefined_interface = json.load(open(predefined_interface_path))
				campaign_dict["interfaces"] += [predefined_interface]

		campaign = cls(campaign_name, campaign_prefix, campaign_dict)

		campaign.filename = campaign_filename
		campaign.directory = os.path.dirname(os.path.realpath(campaign.filename)) + "/"
		campaign.experiment_directory = campaign.directory + campaign.name + "_experiments/"
		exp_command_array = campaign["experimentCommand"].split(" ")
		campaign.absolute_experimentCommand = os.path.realpath(exp_command_array[0]) + " ".join(exp_command_array[1:])

		return campaign
