from pyaofit import *
import os, shutil
import sys
import subprocess
import xml.etree.ElementTree
import lxml.etree
import tempfile
import atexit

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

def writeConfig(campaign, variables, f):
	if campaign.environment_config_active:
		re_index = re.compile('.*\[(\d+)\].*')
		for varname, value in variables.items():
			printVerbose("-- writeConfig at key " + str(varname) + " value " + str(value))
			mtch = re_index.match(varname)
			if mtch:
				indx = mtch.group(1)
				varname_new = varname.replace('['+indx+']', '')
				printVerbose("array, writing: export " + str(varname_new) + "=\"" + str(value) + ";" + str(indx) + "\"\n")
				f.write("export " + str(varname_new) + "=\"" + str(value) + ";" + str(indx) + "\"\n")
			else:
				printVerbose("NON-ARRAY, writing: export " + str(varname) + "=\"" + str(value) + "\"\n")
				f.write("export " + str(varname) + "=\"" + str(value) + "\"\n")
	else:
		for varname, value in variables.items():
			f.write(str(varname) + "=" + str(value) + "\n")

def ignorableErrorSituationsForJPID(repository, qualifiedAttributeName, jpid):
	if False and shutil.which("xqilla") != None:
		(configFD, configFileName) = tempfile.mkstemp(text=True)
		atexit.register(os.remove, configFileName)
		# Seems to be closed by ElementTree.write().
		#atexit.register(os.close, configFD)

		aofitnamespace = "https://ulrichgabor.de/aofit/config"

		rootElement = xml.etree.ElementTree.Element("{" + aofitnamespace + "}config")
		repofilenameElement = xml.etree.ElementTree.SubElement(rootElement, "{" + aofitnamespace + "}repofilename")
		repofilenameElement.text = repository
		attributeQualifierElement = xml.etree.ElementTree.SubElement(rootElement, "{" + aofitnamespace + "}attributeQualifier")
		attributeQualifierElement.text = qualifiedAttributeName
		jpidElement = xml.etree.ElementTree.SubElement(rootElement, "{" + aofitnamespace + "}jpid")
		jpidElement.text = str(jpid)

		# print(xml.etree.ElementTree.tostring(rootElement))
		tree = xml.etree.ElementTree.ElementTree(rootElement)
		tree.write(configFD, xml_declaration=True, encoding="utf-8", method="xml", default_namespace=aofitnamespace)

		dir_path = os.path.dirname(os.path.realpath(__file__))
		printVerbose("xqilla " + dir_path + "/../scripts/repo_attribute.xquery -i " + configFileName)
		xqilla = subprocess.run("xqilla " + dir_path + "/../scripts/repo_attribute.xquery -i " + configFileName, shell=True, stdout=subprocess.PIPE)
		if xqilla.returncode != 0:
			sys.exit("Call to xqilla failed.")
		stdout = xqilla.stdout.decode(encoding = sys.getdefaultencoding())
		parameters = stdout.strip().split(",")
		ignoreErrorSituations = [x.strip('"') for x in parameters]
		return ignoreErrorSituations
	else:
		repo = lxml.etree.parse(repository)
		nsmap = {"acc": "https://aspectc.org/schemas/ac-model"}

		splitAttributeName = qualifiedAttributeName.split("::")
		namespaces = splitAttributeName[0:-1]
		namespaces[0] = "::" # First namespace has a special name.
		attributeName = splitAttributeName[-1]

		# Construct XPath query to find the correct acc:Attribute node and its id attribute.
		xpathNamespaces = list(map(lambda x: "acc:Namespace[@name=\"" + x + "\"]/acc:children", namespaces))
		xpathAttribute = xpathNamespaces + ["acc:Attribute[@name=\"" + attributeName + "\"]"]
		attributes = repo.xpath("./acc:root/" + "/".join(xpathAttribute) + "/@id", namespaces=nsmap)
		if len(attributes) != 1:
			sys.exit("Found more or none attribute(s) in " + repository + ". Please check.")
		attributeid = attributes[0]

		# Construct XPath query to find all expression attributes of Parameters belonging to this attribute on Call nodes.
		parameters = repo.xpath(".//acc:Call[@jpid=\"" + str(jpid) + "\"]/ancestor::acc:*/acc:annotations/acc:Annotation[@attribute=\"" + str(attributeid) + "\"]/acc:parameters/acc:Parameter/@expression", namespaces=nsmap)
		ignoreErrorSituations = [x.strip('"') for x in parameters]
		return ignoreErrorSituations
