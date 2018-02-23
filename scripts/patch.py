#!/usr/bin/env python3
import sys
import subprocess
import re

binaryPath = 'build/kratos.elf'
configSymbol = 'fi_config_arr' # name of config array, set in config aspect

objdump_output = subprocess.run(['objdump', '-D', '--section=.data', '--file-offsets', binaryPath], stdout=subprocess.PIPE).stdout.decode(encoding=sys.getdefaultencoding())

ln = re.findall('<'+configSymbol+'>.*\n', objdump_output) # find line about config array
print('line: ', ln)
if(len(ln) > 0):
    offset = re.findall(r'0x[0-9a-f]+', ln[0]) # extract offset of config array (hex value)
    print('offset: ', offset)

binary = open(binaryPath, 'r+b')
offset = int(offset[0], base = 16)
binary.seek(offset)
binary.write(b'$BCDEFGHIJKLMNO$') # write configuration data as bytes
binary.close()
