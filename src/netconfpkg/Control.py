## Copyright (C) 2001-2004 Red Hat, Inc.
## Copyright (C) 2001-2004 Than Ngo <than@redhat.com>
## Copyright (C) 2001-2004 Harald Hoyer <harald@redhat.com>

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

import re
import traceback
import sys
import os
import os.path
import shutil
import signal
import string
from rhpl import ethtool
from NC_functions import *
import NCDeviceList

TRUE = (1==1)
FALSE = not TRUE

ACTIVE = _('Active')
INACTIVE = _('Inactive')

if os.getuid() == 0: isdnctrl = '/sbin/isdnctrl'
else: isdnctrl = '/usr/sbin/userisdnctl'
            
import glob

class NetworkDevice:
    def __init__(self):
        self.activedevicelist = []
        self.devicelist = NCDeviceList.getDeviceList()
        self.load()

    def load(self):
        l = ethtool.get_active_devices()

        self.activedevicelist = l
        
        # remove inactive isdn/ppp device
        for i in l:
            nickname = getNickName(self.devicelist, i)
            if getDeviceType(i) == ISDN:
                if os.access(isdnctrl, os.X_OK):
                    for nick in nickname:
                        if os.system(isdnctrl +
                                     ' %s >& /dev/null' %(nickname)) == 0:
                            break
                        else:
                            self.activedevicelist.remove(i)
                            
            elif getDeviceType(i) == MODEM:
                if (os.access('/var/run/ppp-%s.pid' %(i), os.F_OK)):
                    continue
                for nick in nickname:
                    if (os.access('/var/run/ppp-%s.pid' %(nick), os.F_OK)):
                        self.activedevicelist.append(nick)
                        break                    
                else:
                    self.activedevicelist.remove(i)
            
#         # check real ppp device
#         for i in xrange(0, 10):
#             if os.access('/var/run/ppp-ppp%s.pid' %(i), os.F_OK):
#                 self.activedevicelist.append('ppp%s' %(i))

#         for pid in glob.glob('/var/run/ppp-*.pid'):
#             pid = pid[13:]
#             pid = pid[:-4]
#             self.activedevicelist.append(pid)
                    
        self.activedevicelist.sort()
        
    def get(self):
        return self.activedevicelist

    def find(self, device):
        if device in self.activedevicelist:
            return TRUE
        return FALSE

__author__ = "Than Ngo <than@redhat.com>, Harald Hoyer <harald@redhat.com>"
