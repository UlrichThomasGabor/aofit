# Getting started
*to be filled*

# Futher Information
## Validate JSON files
In the directory `schemas` there exist multiple schema definitions to validate JSON files. The tested way to do this is by using [`ajv`](https://github.com/jessedc/ajv-cli).

To use `ajv`
1. install `Node.js`,
2. execute `npm install -g ajv-cli`
3. and validate a file e.g. by executing `ajv -s schemas/posix_interface.schema -d schema_examples/posix_fputc.json`.

### Validate all example JSON files
Execute `./scripts/validate_all_posix_schema_examples.sh`.
