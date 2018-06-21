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

		self.__init__propagate_global_error_situations()
		self.__init__populate_values_down()
		self.__init__error_situation_ids()
		self.__init__set_error_situation_index_for_custom_error_value()
		self.name = name
		self.prefix = prefix
		self.errno_active = self.__init__errno_used()
		self.delay_active = self.__init__delay_used()
		self.environment_config_active = self.__init__environment_config_used()
		if not "ecAspects" in self:
			self["ecAspects"] = []

	def __init__populate_values_down(self):
		'''
		Propagate values, e.g. error_value, errno and delay, given at interface level
		down to each error_situation.
		'''
		propagate_values = ['error_value', 'errno', 'delay']
		for i, interface in enumerate(self['interfaces']):
			for key in propagate_values:
				if not key in interface:
					interface[key] = None
			for j, target in enumerate(interface['targets']):
				for key in propagate_values:
					if not key in target:
						target[key] = interface[key]
				for k, error_situation in enumerate(target['error_situations']):
					for key in propagate_values:
						if not key in error_situation:
							error_situation[key] = target[key]
					target['error_situations'][k] = error_situation
				interface['targets'][j] = target
			self['interfaces'][i] = interface

	def __init__propagate_global_error_situations(self):
		'''
		Propagate global error situations of an interface to its targets.
		'''
		for i, interface in enumerate(self['interfaces']):
			if "error_situations" in interface:
				for j, target in enumerate(interface['targets']):
					target["error_situations"] = interface["error_situations"] + target["error_situations"]
					interface['targets'][j] = target
				self['interfaces'][i] = interface

	def __init__error_situation_ids(self):
		'''
		Set default ids for error_situations.
		'''
		for i, interface in enumerate(self['interfaces']):
			for j, target in enumerate(interface['targets']):
				for k, error_situation in enumerate(target['error_situations']):
					if not "id" in error_situation:
						if error_situation["errno"] != None:
							error_situation["id"] = error_situation["errno"]
						elif error_situation["error_value"] != None:
							error_situation["id"] = error_situation["error_value"]
						else:
							error_situation["id"] = k
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

	def __init__delay_used(self):
		for interface in self['interfaces']:
			for target in interface['targets']:
				for error_situation in target['error_situations']:
					if error_situation['delay'] != None:
						return True
		return False

	def __init__environment_config_used(self):
		return 'useEnvironmentVariables' in self and self['useEnvironmentVariables']


	def __init__set_error_situation_index_for_custom_error_value(self):
		'''
		This generates new error_situation_indexes per target for the custom
		values given in experiments.
		'''
		index = {}
		for interface in self['interfaces']:
			for target in interface['targets']:
				index[self.getTargetId(target['id'])] = len(target['error_situations'])
		for i, experiment in enumerate(self['experiments']):
			if 'error_value' in experiment:
				experiment['error_situation_index'] = index[self.getTargetId(experiment['target'])]
				index[self.getTargetId(experiment['target'])] = index[self.getTargetId(experiment['target'])] + 1
			self['experiments'][i] = experiment

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
