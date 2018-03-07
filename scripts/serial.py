#!/usr/bin/env python3

import pty
import os
import subprocess
import argparse

def launch_serial(image, magicStr, debug=False):
	master, slave = pty.openpty()
	if debug:
		print("master: " + os.ttyname(master) + "\tslave: " + os.ttyname(slave))
	slave_id = os.ttyname(slave).split('/')[-1]

	pts = open(master, 'rb', buffering=0)

	read_input = b""
	tmp = b""
	stop = False
	pos = 0

	# Start QEMU and redirect serial output to opened pts.
	io_options = ["-chardev", "tty,id=pts" + slave_id + ",path=/dev/pts/" + slave_id, "-device", "isa-serial,chardev=pts" + slave_id]
	image_options = ["-drive", "file=" + image + ",index=0,if=floppy,format=raw", "-boot", "a", "-k", "en-us"]
	try:
		proc = subprocess.Popen(['qemu-system-x86_64'] + io_options + image_options, stdout=subprocess.PIPE) # stdout=subprocess.PIPE leads to qemu not terminating
	except:
		print("Launching Qemu failed.")
		return None

	ok=False
	try:
		proc.wait(timeout=1) #wait a second for qemu to (possibly) encounter errors
		#pts buffers 4kb in each direction; further writes block
		#TODO run read thread parallely as soon as pts is opened, so no data is lost
	except subprocess.TimeoutExpired: #no termination within last second -> assume everything's ok
		ok=True

	if not ok and proc.returncode != 0:
		print("Qemu failed")
		return None

	while True:
		c = pts.read(1)
		if c[0] == magicStr[pos]:
			if pos == len(magicStr) - 1 and stop:
				if debug:
					print("Detected final magic string!")
				break
			elif pos == len(magicStr) - 1:
				if debug:
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
	return read_input

if __name__=="__main__":
	parser = argparse.ArgumentParser(description='Start QEMU and bind serial output to openend PTS.')
	parser.add_argument("image", help="The image to start.", default="build/bootdisk.vmi")
	parser.add_argument("magic_string", help="The magic string framing the relevant output")
	parser.add_argument("--debug", action="store_true", default=False);
	args = parser.parse_args()

	retval = launch_serial(args.image, bytearray(args.magic_string, encoding='ascii'), args.debug)
	if type(retval) is bool:
		exit(not retval)
	else:
		print(retval)
		exit(0)
