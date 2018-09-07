# Getting started
## Prerequisites
* Python 3
* [AspectC++](http://aspectc.org/) newer than version 2.2, which is the daily build at the moment

## Integration test
You can run `make test` to run all integration tests.

## Usage
The scripts `generate_aspect.py`, `generate_experiments.py` and `run_experiments.py` must be run in that order. Each script expects a campaign configuration in JSON format as parameter.

See one of the integration tests for more information, for example `integration-tests/aspect_ordering_ec.sh`.

# Further Information
## Validate JSON files
In the directory `schemas` there exist multiple schema definitions to validate JSON files. The tested way to do this is by using [`ajv`](https://github.com/jessedc/ajv-cli).

To use `ajv`
1. install `Node.js`,
2. execute `npm install -g ajv-cli`
3. and validate a file e.g. by executing `ajv -s schemas/posix_interface.schema -d schema_examples/posix_fputc.json`.

### Validate all example JSON files
Execute `./scripts/validate_all_posix_schema_examples.sh`.
