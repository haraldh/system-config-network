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
NAME = 'Red Hat Network Control'

NETWORKDIR = '/etc/sysconfig/network-scripts/'
NETWORKPREFIX = 'ifcfg'
PROCNETDEV = '/proc/net/dev'
PROCNETROUTE = '/proc/net/route'
TRUE = (1==1)
FALSE = not TRUE
STATUS = 0
DEVICE = 1
NICKNAME = 2
ACTIVATE = 3
DEACTIVATE = 4
CONFIGURE = 5
MONITOR = 6

import re
import traceback
import sys
import os
import os.path
import shutil
import signal
import string
import ethtool
from netconfpkg import ethtool

class ProcNetDevice:
    def __init__(self):
        pass


class NetworkDevice:
    def __init__(self):
        self.activedevicelist = []
        self.load()

    def load(self):
        l = ethtool.get_active_devices()
        if l.count('lo'):
            l.remove('lo')

        self.activedevicelist = l
        
        # check isdn device for connection
        for i in l:
            if len(i) > 4:
                if i[:4] == 'isdn' or i[:4] == 'ippp':
                    if os.access('/sbin/userisdnctl', os.X_OK):
                        if os.system('/sbin/userisdnctl status %s>&/dev/null' %(i)) == 0:
                            continue
                    self.activedevicelist.remove(i)

        self.activedevicelist.sort()
        
    def get(self):
        return self.activedevicelist

    def find(self, o):
        for i in self.activedevicelist:
            if i == o:
                return TRUE
        return FALSE

class Interface:
    def __init__(self):
        pass

    def activate(self, device):
        ret = fork_exec(0, '/sbin/ifup', ['/sbin/ifup', device])
        return ret

    def deactivate(self, device):
        try:
            return(os.system('/sbin/ifdown %s >& /dev/null' %(device)))
        except:
            return -1

    def status(self, device):
        pass

    def configure(self, device):
        try:
            return(os.system('/usr/bin/redhat-config-network&'))
        except:
            return -1

    def monitor(self, device):
        ret = fork_exec(0, '/usr/bin/rp3', ['/usr/bin/rp3', '-i', device])
        return ret
    
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
        os.execvp(path, arg)
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
