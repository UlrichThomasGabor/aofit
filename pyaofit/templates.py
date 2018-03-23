from string import Template
import os

with open(os.path.dirname(__file__) + "/../include-templates/aspect.ah") as f:
	raw_aspect_header = Template(f.read())

with open(os.path.dirname(__file__) + "/../include-templates/advice_param.ah") as f:
	raw_advice_argument = Template(f.read())

with open(os.path.dirname(__file__) + "/../include-templates/advice_result.ah") as f:
	raw_advice_result = Template(f.read())
