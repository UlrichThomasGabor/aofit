#!/usr/bin/env python3
import sys
import subprocess
import re
import platform
import argparse

parser = argparse.ArgumentParser(description='Modify an ELF file.')
parser.add_argument("elf_file", help="The ELF file to modify.", default="build/kratos.elf")
parser.add_argument("--config_symbol", help="The symbol to modify.", default="fi_config_arr")
parser.add_argument("--debug", action="store_true", default=False);
args = parser.parse_args()

if platform.system() != "Linux":
    print("This tool works only on Linux, because only there objdump can print the necessary information.")
    exit(1)

binaryPath = args.elf_file
configSymbol = args.config_symbol # name of config array, set in config aspect

print("Searching for symbol " + configSymbol + " in ELF " + args.elf_file + ".")

objdump_subprocess = subprocess.run(['objdump', '-D', '--section=.data', '--file-offsets', args.elf_file], stdout=subprocess.PIPE)
objdump_output = objdump_subprocess.stdout.decode(encoding=sys.getdefaultencoding())
if args.debug:
	print("objdump output:")
	print(objdump_output)

ln = re.findall('<' + args.config_symbol + '>.*\n', objdump_output) # find line about config array
if len(ln) == 0:
	print("Could not find the symbol " + args.config_symbol + " with configuration information in the ELF file.")
	exit(1)
else:
	if args.debug:
		print('Found the symbol on line: ' + ln)
	
	offset = re.findall(r'0x[0-9a-f]+', ln[0]) # extract offset of config array (hex value)
	if args.debug:
		print('Found the offset: ' + offset)

	binary = open(binaryPath, 'r+b')
	offset = int(offset[0], base=16)
	binary.seek(offset)
	binary.write(b'$BCDEFGHIJKLMNO$') # write configuration data as bytes
	binary.close()

