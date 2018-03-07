#!/usr/bin/env python3
import sys
import subprocess
import re
import platform
import argparse

def patch_local(binaryPath, configData, configSymbol="fi_config_arr", debug=False):
    if platform.system() != "Linux":
        print("This tool works only on Linux, because only there objdump can print the necessary information.")
        return False

    print("Searching for symbol " + configSymbol + " in ELF " + binaryPath + ".")

    try:
        objdump_subprocess = subprocess.run(['objdump', '-D', '--section=.data', '--file-offsets', binaryPath], stdout=subprocess.PIPE, check=True) #only stderr is printed
    except:
        #objdump_subprocess can't be accessed: the except block assumes that it wasn't assigned. However, objdump's output is printed
        print("Objdump failed")
        return False

    objdump_output = objdump_subprocess.stdout.decode(encoding = sys.getdefaultencoding())
    if debug:
        print("Objdump output:")
        print(objdump_output)
    ln = re.findall('<' + configSymbol + '>.*\n', objdump_output) # find line about config array
    if len(ln) == 0:
        print("Could not find the symbol " + configSymbol + " with configuration information in the ELF file.")
        return False
    else:
        if debug:
            print('Found the symbol on line:', ln)
        
        offset = re.findall(r'0x[0-9a-f]+', ln[0]) # extract offset of config array (hex value)
        if debug:
            print('Found the offset:', offset)

        try:
            binary = open(binaryPath, 'r+b')
        except OSError:
            print("Failed to open binary file", binaryPath)
            return False

        offset = int(offset[0], base=16)
        binary.seek(offset)
        binary.write(configData) #write configuration data as bytes
        binary.close()

        print("Successfully patched", binaryPath)
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Modify an ELF file.')
    parser.add_argument("elf_file", help="The ELF file to modify.")
    parser.add_argument("--config_symbol", help="The symbol to modify.", default="fi_config_arr")
    parser.add_argument("config_data", help="The data to be written to the configuration space")
    parser.add_argument("--debug", action="store_true", default=False)
    args = parser.parse_args()

    binaryPath = args.elf_file
    configSymbol = args.config_symbol # name of config array, set in config aspect
    configData = bytes(args.config_data, encoding=sys.getdefaultencoding())

    exit(not patch_local(binaryPath, configData, configSymbol, args.debug))

