#! /usr/bin/env python
## Copyright (C) 2002 Red Hat, Inc.
## Copyright (C) 2002 Than Ngo <than@redhat.com>

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

VERSION = '0.1.0'
GLADEPATH = ''
COPYRIGHT = 'Copyright (c) 2002 Red Hat, Inc.'
AUTORS = ['Than Ngo <than@redhat.com>']

NETWORKDIR = '/etc/sysconfig/network-scripts/'
NETWORKPREFIX = 'ifcfg'
PROCNETDEV = '/proc/net/dev'
TRUE = (1==1)
FALSE = not TRUE

import re
import traceback
import sys
import os
import os.path
import shutil
import signal
import string


class ProcNetDevice:
    def __init__(self):
        self.activedevicelist = []

    def load(self):
        try:
            device = open(PROCNETDEV, 'r')
            device.readline()
            device.readline()
            line = device.readline()
            while line:
                s = string.split(line, ':', 1)
                if s[0]:
                    dev = string.strip(s[0])
                    if dev != 'lo':
                        self.activedevicelist.append(dev)

                line = device.readline()
            device.close()
        except IOError:
            pass

        return self.activedevicelist



# make ctrl-C work
if __name__ == '__main__':
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    devicelist = ProcNetDevice().load()
    print devicelist
