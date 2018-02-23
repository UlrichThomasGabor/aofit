#!/usr/bin/env python3
import pty, os, subprocess

master, slave = pty.openpty()
print("master: ", os.ttyname(master), "slave: ", os.ttyname(slave))
slave_id = os.ttyname(slave).split('/')[-1]

pts = open(master, 'rb', buffering=0)

read_input = b""
tmp = b""
stop = False
magicStr = bytearray("e84fc95d3a41b3ebfccedea78311657c", encoding='ascii')
pos = 0
imagePath = 'build/bootdisk.vmi'

#start qemu with built OS concurrently and redirect serial output to opened pts
proc = subprocess.Popen(['qemu-system-x86_64', '-chardev', 'tty,id=pts'+slave_id+',path=/dev/pts/'+slave_id, '-device', 'isa-serial,chardev=pts'+slave_id, imagePath], stdout=subprocess.PIPE)

while True:
    c = pts.read(1)
    if c[0]==magicStr[pos]:
        if pos==len(magicStr)-1 and stop:
            print("detected final magic string!")
            break
        elif pos==len(magicStr)-1:
            print("detected first magic string!")
            stop = True
            pos=0
            tmp=b""
        pos += 1
        tmp += c #save read data in case it's not part of the magic string
        continue
    else:
        pos=0
        read_input += tmp #tmp from previous iterations
        tmp = b""
        read_input += c

proc.terminate();
print("output: \n", read_input)    
    