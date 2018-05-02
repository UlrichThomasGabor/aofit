import re

from pyaofit import *

_function_matcher = re.compile(r"^\s*([^(]+?)([a-zA-Z_][a-zA-Z0-9_]+)\s*(\()(.*)(\))\s*;?\s*$")

def makeSignature(target):
	if type(target['signature']) == str:
		# Replace return type with % and params with ... and use
		# the predefined pointcut functions result/args, because only there
		# typedefs will be resolved.
		result = re.match(_function_matcher, target['signature'])
		return "% " + result.group(2) + result.group(3) + "..." + result.group(5)
	elif 'pointCutExp' in target['signature']:
		return target['signature']['pointCutExp']
	else:
		if 'resultType' in target['signature'] and target['signature']['resultType'] != "":
			resultType = target['signature']['resultType']
		else:
			resultType = "%"

		if 'namespace' in target['signature'] and target['signature']['namespace'] != "":
			namespace = target['signature']['namespace'] + "::"
		else:
			namespace = "...::"

		if 'className' in target['signature'] and target['signature']['className'] != "":
			className = target['signature']['className'] + "::"
		else:
			className = "...::"

		if 'funcName' in target['signature'] and target['signature']['funcName'] != "":
			funcName = target['signature']['funcName']
		else:
			funcName = "%"

		if not ('namespace' in target['signature'] or 'className' in target['signature']):
			namespace = ""
			className = "...::"

		return "% " + namespace + className + funcName + "(...)"

def makeResultType(target):
	if 'resultType' in target:
		return target['resultType']
	else:
		# Match type, e.g. "FILE *", in signatures, e.g. "FILE *fopen(const char *restrict pathname, const char *restrict mode);".
		result = re.match(_function_matcher, target['signature'])
		return result.group(1)

def makeArgumentTypes(target):
	# Match params, e.g. "const char *restrict pathname, const char *restrict mode", in signatures, e.g. "FILE *fopen(const char *restrict pathname, const char *restrict mode);".
	result = re.match(_function_matcher, target['signature'])
	params = result.group(4).split(",")
	params = list(filter(None, params)) # Filter empty strings
	params_without_varnames = []
	for param in params:
		types = [type.strip() for type in param.strip().split(" ")]
		# Pop of variable name.
		types.pop()
		# Remove restrict, because it is not a C++ keyword.
		if "restrict" in types:
			types.remove("restrict")
		params_without_varnames += [" ".join(types)]
	# Remove restrict again, because it might be prepended with *.
	params = [ re.sub(r"\brestrict\b", "", p) for p in params_without_varnames]
	return params

def makeValueVectors(campaign):
	definitions = ""
	definitions_errno = {}
	definitions_delay = {}
	target_id = 0
	for interface in campaign['interfaces']:
		for target in interface['targets']:
			if (not 'injectAt' in target) or (target['injectAt'] == "result"):
				error_type = makeResultType(target)
			elif target['injectAt'] == "argument":
				error_type = makeArgumentTypes(target)[target['argNumber']]

			definitions += "\t__attribute__((used)) static " + error_type + " ${aspectName}_valueVector_" + str(target_id) + "[] = {"

			errnos = []
			delays = []
			for errsituation in target['error_situations']:
				definitions += errsituation['error_value'] + ", "
				if errsituation['errno'] != None:
					errnos.append(errsituation["errno"])
				else:
					errnos.append("0")
				if errsituation['delay'] != None:
					delays.append(str(errsituation["delay"]))
				else:
					delays.append("0")
			# Append another element for custom injection values in campaign file,
			# which are not based on interface definition.
			definitions += "(" + error_type + ")NULL };\n"
			errnos.append("0")
			delays.append("0")
			definitions_errno[target_id] = errnos
			definitions_delay[target_id] = delays
			target_id += 1

	result = definitions;
	if campaign.errno_active:
		result += "\t__attribute__((used)) static int ${aspectName}_valueVectorErrno[" + str(max(definitions_errno, key=int) + 1) + "][" + str(len(definitions_errno[0])) + "] = {"
		for id, values in definitions_errno.items():
			definitions_errno[id] = ", ".join(values)
		result += ", ".join(e for i, e in definitions_errno.items())
		result += "};\n"
	if campaign.delay_active:
		result += "\t__attribute__((used)) static unsigned int ${aspectName}_valueVectorDelay[" + str(max(definitions_delay, key=int) + 1) + "][" + str(len(definitions_delay[0])) + "] = {"
		for id, values in definitions_delay.items():
			definitions_delay[id] = ", ".join(values)
		result += ", ".join(e for i, e in definitions_delay.items())
		result += "};\n"
	return result

def generateAspect(campaign):
	valueVectors = makeValueVectors(campaign)

	advices = ""
	target_id = 0

	customIncludes = []
	for interface in campaign['interfaces']:
		# Include all headers, because they are required for the
		# predefined pointcut functions (see below).
		customIncludes += ["#include <" + header + ">" for header in interface['header_files']]

		for target in interface['targets']:
			signature = makeSignature(target)
			result_type = makeResultType(target)
			arg_types = makeArgumentTypes(target)
			# We cannot match for the correct return type in the PCE (pointcut
			# expression), because AC++ cannot resolve typedefs in PCEs. Instead
			# we use a PCE, which matches every type and use the
			# predefined pointcut functions result/args to match only those
			# having a type we want.
			pointcutadditions = []
			variabledefinition = []
			if result_type != "%" and result_type != None:
				pointcutadditions += ["result(theresult)"]
				variabledefinition += [result_type + " theresult"]
			if len(arg_types) != 0 and arg_types[0] != "...":
				args = []
				args_names = []
				argi = 0
				for arg_type in arg_types:
					args += [arg_type + " argument" + str(argi)]
					args_names += ["argument" + str(argi)]
					argi += 1
				argument_string = ", ".join(args)
				argument_names_string = ", ".join(args_names)
				pointcutadditions += ["args(" + argument_names_string + ")"]
				variabledefinition += [argument_string]
			pointcutadditions = " && " + " && ".join(pointcutadditions)
			variabledefinition = ", ".join(variabledefinition)

			if (not 'injectAt' in target) or (target['injectAt'] == 'result'):
				adv = templates.raw_advice_result.safe_substitute()
				adv = Template(adv).safe_substitute(signature=signature, resultType=result_type, pointcutadditions=pointcutadditions, variabledefinition=variabledefinition)
			elif target['injectAt'] == 'argument':
				arg_type = makeArgumentTypes(target)[target['argNumber']]
				adv = templates.raw_advice_argument.safe_substitute()
				adv = Template(adv).safe_substitute(signature=signature, argType=arg_type, argNumber=target['argNumber'], pointcutadditions=pointcutadditions, variabledefinition=variabledefinition)

			adv = Template(adv).safe_substitute(id=target_id)
			advices += adv + "\n"

			target_id += 1

	if campaign.errno_active:
		customIncludes += ["#include <cerrno>"]
	customIncludes = "\n".join(customIncludes) + "\n"
	if 'customIncludes' in campaign:
		for header in campaign['customIncludes']:
			customIncludes += "#include \"" + header + "\"\n"

	if campaign.delay_active:
		if 'customDelayInclude' in campaign:
			customIncludes += campaign['customDelayInclude'] + "\n"
		else:
			customIncludes += "#include <time.h>\n#include <math.h>\n"
		if 'customDelayCode' in campaign:
			delay_code = campaign['customDelayCode']
		else:
			delay_code = templates.raw_delay_code.safe_substitute()
	else:
		delay_code = ""

	ah = templates.raw_aspect_header.safe_substitute(customIncludes=customIncludes, numTargets=campaign.numberOfTargets, valueVectors=valueVectors, advices=advices, delay_code=delay_code)

	notEcAspects = "".join([" && !\"" + aspect + "\"" for aspect in campaign['ecAspects']])
	ecAspects = "".join([" || \"" + aspect + "\"" for aspect in campaign['ecAspects']])
	if len(ecAspects) > 0:
		ecAspects = ecAspects[4:] + ", "
	ah = Template(ah).safe_substitute(notEcAspects=notEcAspects, ecAspects=ecAspects)

	# Use substitute here, because we expect an error if an identifier is left in the generated code.
	ah = Template(ah).substitute(aspectName=campaign.prefix, errno_active=str(campaign.errno_active).lower(), delay_active=str(campaign.delay_active).lower())

	return ah
