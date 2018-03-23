from pyaofit import *

class campaign(dict):
	def __init__(self, name, prefix, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.numberOfTargets = 0
		for interface in self['interfaces']:
			for target in interface['targets']:
				self.numberOfTargets += 1

		self.targetspecifiers = {}
		target_id = 0
		for interface in self['interfaces']:
			for target in interface['targets']:
				self.targetspecifiers[target['id']] = target_id
				target_id += 1

		self.__init__populate_error_values()
		self.name = name
		self.prefix = prefix
		self.errno_active = self.__init__errno_used()
		if not "ecAspects" in self:
			self["ecAspects"] = []

	def __init__populate_error_values(self):
		'''
		Propagates error_values given in higher structures down to the lower ones.
		'''
		for i, interface in enumerate(self['interfaces']):
			if not 'error_value' in interface:
				interface['error_value'] = None
			if not 'errno' in interface:
				interface['errno'] = None
			for j, target in enumerate(interface['targets']):
				if not 'error_value' in target:
					target['error_value'] = interface['error_value']
				if not 'errno' in target:
					target['errno'] = interface['errno']
				for k, error_situation in enumerate(target['error_situations']):
					if not 'error_value' in error_situation:
						error_situation['error_value'] = target['error_value']
					if not 'errno' in error_situation:
						error_situation['errno'] = target['errno']
					target['error_situations'][k] = error_situation
				interface['targets'][j] = target
			self['interfaces'][i] = interface

	def __init__errno_used(self):
		for interface in self['interfaces']:
			for target in interface['targets']:
				for error_situation in target['error_situations']:
					if error_situation['errno'] != None:
						return True
		return False

	def getTargetId(self, targetspecifier):
		if targetspecifier in self.targetspecifiers:
			return self.targetspecifiers[targetspecifier]
		else:
			return None

	def getTarget(self, targetspecifier):
		for interface in self['interfaces']:
			for target in interface['targets']:
				if targetspecifier == target['id']:
					return target
		return None
