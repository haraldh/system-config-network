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
COPYRIGHT = 'Copyright (C) 2002 Red Hat, Inc.'
AUTORS = ['Than Ngo <than@redhat.com>']

NETWORKDIR = '/etc/sysconfig/network-scripts/'
NETWORKPREFIX = 'ifcfg'
PROCNETDEV = '/proc/net/dev'
PROCNETROUTE = '/proc/net/route'
TRUE = (1==1)
FALSE = not TRUE
STATUS = 0
DEVICE = 1
NICKNAME = 2

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
        pass


class ProcNetRoute:
    def __init__(self):
        self.activedevicelist = []

    def load(self):
        try:
            device = open(PROCNETROUTE, 'r')
            device.readline()
            line = device.readline()
            while line:
                s = string.split(line)
                if s[0]:
                    dev = string.strip(s[0])
                    if dev != 'lo':
                        self.activedevicelist.append(dev)

                line = device.readline()
            device.close()
        except IOError:
            pass

        return self.activedevicelist


class Interface:
    def __init__(self):
        pass

    def activate(self, device):
        print 'waiting to connect to %s' % (device)

    def deactivate(self, device):
        pid = os.fork()
        if not pid:
            pass
        print 'waiting to disconnect from %s' % (device)

    def status(self, device):
        print 'status from %s' % (device)

    def configure(self, device):
        print 'configure %s' % (device)

    def monitor(self, device):
        print 'monitor %s' % (device)
    
    def allow(self, device):
        pass

    
class Monitor:
    def __init__(self):
        pass

    def txrx_update(self):
        pass

    def onlinetime_update(self):
        pass

    def cost_update(self):
        pass

    def speed_update(self):
        pass
    

def fork_exec(wait, path, arg):
    child = os.fork()
    
    if not child:
        os.execl(path, arg)
        os._exit(1)

    if not wait: return child

    status = os.wait(child)
    if os.WIFEXITED(status) and (WEXITSTATUS(status) == 0):
        return WEXITSTATUS(status)
    return -1

    
# make ctrl-C work
if __name__ == '__main__':
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    devicelist = ProcNetRoute().load()
    print devicelist
