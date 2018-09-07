# Getting started
This project allows for the injection of errors at interfaces according to a configurable error model given as JSON file. It utilizes AspectC++ to modify the behavior of a C++ application, without requiring changes to its source code. This approach is especially dedicated to inject errors into software running on embedded systems.

## Prerequisites
* Python 3
* [AspectC++](http://aspectc.org/) newer than version 2.2, which is the daily build at the moment

## Integration test
You can run `make test` to run all integration tests.

## Usage
The scripts `generate_aspect.py`, `generate_experiments.py` and `run_experiments.py` must be run in that order. Each script expects a campaign configuration in JSON format as parameter.

The `generate_aspect.py` script generates an aspect based on the given JSON file. The `generate_experiments.py` script builds the software-under-test with the previously built aspect, runs it with the specified workload to obtain some information required to setup the experiments and finally creates a new directory for each experiment containing a configuration file. The `run_experiments.py` script iterates over all directories, starts the software-under-test and configures the global variables introduced by the aspect according to the configuration file created in the previous step via GDB or another mechanism.

See one of the integration tests for more information, for example `integration-tests/aspect_ordering_ec.sh`.

# Further Information
## Validate JSON files
In the directory `schemas` there exist multiple schema definitions to validate JSON files. Sorrowfully, this does not work at the moment, as we were not able to find a validator, which implements an up-to-date draft of the specification including all our used features of the specification.

The most promising tool is [`ajv`](https://github.com/jessedc/ajv-cli).

To use `ajv`
1. install `Node.js`,
2. execute `npm install -g ajv-cli`
3. and validate a file e.g. by executing `ajv -s schemas/posix_interface.schema -d schema_examples/posix_fputc.json`.

### Validate all example JSON files
Execute `./scripts/validate_all_campaign_schema_examples.sh` and `./scripts/validate_all_interface_schema_examples.sh`. The files do not pass at the moment for the mentioned reasons.
