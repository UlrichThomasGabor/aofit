from pyaofit import *

def generateOccurenceCountConfig(campaign):
	vars = {}
	vars[campaign.prefix + '_countOccurences'] = "true"
	#vars[campaign.prefix + '_injection_mode'] = '(injection_type)none'
	vars[campaign.prefix + '_loglevel'] = int(campaign['logLevel'])
	for targetid in range(0, campaign.numberOfTargets):
		vars[campaign.prefix + '_activeTargets[' + str(targetid) + ']'] = 0
		#vars[campaign.prefix + '_callCountLimits[' + str(targetid) + ']'] = 0
		#vars[campaign.prefix + '_valueID[' + str(targetid) + ']'] = 0
	return vars

def generateGoldenRunConfig(campaign):
	vars = {}
	vars[campaign.prefix + '_countOccurences'] = "false"
	#vars[campaign.prefix + '_injection_mode'] = '(injection_type)none'
	vars[campaign.prefix + '_loglevel'] = int(campaign['logLevel'])
	for targetid in range(0, campaign.numberOfTargets):
		vars[campaign.prefix + '_activeTargets[' + str(targetid) + ']'] = 0
		#vars[campaign.prefix + '_callCountLimits[' + str(targetid) + ']'] = 0
		#vars[campaign.prefix + '_valueID[' + str(targetid) + ']'] = 0
	return vars

def writeConfig(variables, f):
	for varname, value in variables.items():
		f.write(str(varname) + "=" + str(value) + "\n")
