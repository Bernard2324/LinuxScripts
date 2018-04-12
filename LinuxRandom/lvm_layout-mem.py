#!/usr/bin/env python

# Author: Maurice Green

import os, sys, re
import stat

class __proc():
    def __init__(self):
        uname = os.uname()
        if uname[0] == 'Linux':
            self.proc = '/proc'
        elif uname[0] == "FreeBSD":
            sys.exit(1)

    def join_path(self, *args):
        return os.path.join(self.proc, *(str(x) for x in args))

proc = __proc()

def partitions():
    lvm_partitions = []
    fs_stat = {}
    with open(proc.join_path('mounts'), 'r') as mount:
        lvmpattern = re.compile('/dev/mapper')
        for line in mount.readlines():
            line = line.strip()
            if lvmpattern.match(line) is not None:
                fs = line.split()[1]
                lvm_partitions.append(fs)
            else:
                continue
        mount.close()
    def fs_calc(filesystem):
        data = os.statvfs(filesystem)
        data_array = {}
        data_array['total_size'] = (data[1] * data[2]/1000000000)
        data_array['total_free'] = (data[1] * data[3]/1000000000)
        fs_stat[filesystem] = [data_array]
    for fs in lvm_partitions:
        fs_calc(fs)
    return fs_stat

def meminfo():
    memvals = {
        'MemTotal:': 0,
        'MemFree:': 0,
        'SwapTotal:': 0,
        'SwapFree:': 0
    }
    with open(proc.join_path('meminfo'), 'r') as memory:
        meminformation = memory.read().split()
        memory.close()
    for value in meminformation:
        if value in memvals:
            position = meminformation.index(value)
            memvals[value] = (int(meminformation[position+1])/1000000)
        else:
            continue
    return memvals

def varlog():
    file_container = {}
    _Target_DIR = '/var/log'
    os.chdir(_Target_DIR)
    largest_10 = sorted(os.listdir(_Target_DIR), key=os.path.getsize, reverse=True)[:10]
    return largest_10


if __name__ == "__main__":
    print "Parition-Data (GB)"
    print partitions()
    print "\nLog-Data (Ten Largest)"
    print [file_s for file_s in varlog()]
    print "\nMemory-Data (GB)"
    print meminfo()
    print
