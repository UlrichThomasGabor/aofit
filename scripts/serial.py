#!/usr/bin/env python3
import pty
import os
import subprocess
import argparse

parser = argparse.ArgumentParser(description='Start QEMU and bind serial output to openend PTS.')
parser.add_argument("image", help="The image to start.", default="build/bootdisk.vmi")
parser.add_argument("--debug", action="store_true", default=False);
args = parser.parse_args()

master, slave = pty.openpty()
if args.debug:
	print("master: " + os.ttyname(master) + "\tslave: " + os.ttyname(slave))
slave_id = os.ttyname(slave).split('/')[-1]

pts = open(master, 'rb', buffering=0)

read_input = b""
tmp = b""
stop = False
magicStr = bytearray("e84fc95d3a41b3ebfccedea78311657c", encoding='ascii')
pos = 0

# Start QEMU and redirect serial output to opened pts.
io_options = ["-chardev", "tty,id=pts" + slave_id + ",path=/dev/pts/" + slave_id, "-device", "isa-serial,chardev=pts" + slave_id]
image_options = ["-drive", "file=" + args.image + ",index=0,if=floppy,format=raw", "-boot", "a", "-k", "en-us"]
proc = subprocess.Popen(['qemu-system-x86_64'] + io_options + image_options, stdout=subprocess.PIPE)

while True:
    c = pts.read(1)
    if c[0] == magicStr[pos]:
        if pos == len(magicStr) - 1 and stop:
            print("Detected final magic string!")
            break
        elif pos == len(magicStr) - 1:
            print("Detected first magic string!")
            stop = True
            pos = 0
            tmp = b""
        pos += 1
        tmp += c #save read data in case it's not part of the magic string
        continue
    else:
        pos = 0
        read_input += tmp #tmp from previous iterations
        tmp = b""
        read_input += c

proc.terminate();
print("output: \n", read_input)

