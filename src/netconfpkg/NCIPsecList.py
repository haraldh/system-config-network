## Copyright (C) 2001-2003 Red Hat, Inc.
## Copyright (C) 2001-2003 Harald Hoyer <harald@redhat.com>

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
import string

from rhpl import Conf
from NC_functions import *
from netconfpkg import IPsecList_base
import netconfpkg
import UserList
from netconfpkg.NCIPsec import IPsec

class IPsecList(IPsecList_base):
    def __init__(self, list = None, parent = None):
        IPsecList_base.__init__(self, list, parent)
        self.oldname = None

    def load(self):
        from NCIPsec import ConfIPsec

        self.__delslice__(0, len(self))

        devices = ConfDevices()
        for ipsec_name in devices:
            conf = ConfIPsec(ipsec_name)
            type = None
            # take a peek in the config file
            if conf.has_key("TYPE"):
                type = conf["TYPE"]

            if type != "IPSEC":
                continue

            log.log(5, "Loading ipsec config %s" % ipsec_name)
            ipsec = IPsec()
            ipsec.load(ipsec_name)
            self.append(ipsec)
                        
        self.commit(false)
                
    def save(self):
        from NCIPsec import ConfIPsec
        for ipsec in self:
            ipsec.save()
        #
        # Remove old config files
        #
        try:
            dir = os.listdir(netconfpkg.ROOT + SYSCONFDEVICEDIR)
        except OSError, msg:
            raise IOError, 'Cannot save in ' \
                  + netconfpkg.ROOT + SYSCONFDEVICEDIR + ': ' + str(msg)
        for entry in dir:
            if (len(entry) <= 6) or \
               entry[:6] != 'ifcfg-' or \
               (not os.path.isfile(netconfpkg.ROOT + SYSCONFDEVICEDIR + entry)):
                continue
            
            ipsecid = entry[6:]
                
            for ipsec in self:
                if ipsec.IPsecId == ipsecid:
                    break
            else:
                # check for IPSEC
                conf = ConfIPsec(ipsecid)
                type = None
                if conf.has_key("TYPE"): type = conf["TYPE"]
                if type != IPSEC:
                    continue

                unlink(netconfpkg.ROOT + SYSCONFDEVICEDIR + entry)
                unlink(netconfpkg.ROOT + OLDSYSCONFDEVICEDIR+'/ifcfg-'+ipsecid)

        #
        # Remove old key files
        #
        try:
            dir = os.listdir(netconfpkg.ROOT + SYSCONFDEVICEDIR)
        except OSError, msg:
            raise IOError, 'Cannot save in ' \
                  + netconfpkg.ROOT + SYSCONFDEVICEDIR + ': ' + str(msg)
        for entry in dir:
            if (len(entry) <= 6) or \
               entry[:5] != 'keys-' or \
               (not os.path.isfile(netconfpkg.ROOT + SYSCONFDEVICEDIR + entry)):
                continue
            
            ipsecid = entry[5:]
                
            for ipsec in self:
                if ipsec.IPsecId == ipsecid:
                    break
            else:
                # check for IPSEC
                from NCDevice import ConfDevice
                conf = ConfDevice(ipsecid)
                type = None                
                if conf.has_key("TYPE"): type = conf["TYPE"]
                if type:
                    continue
                
                unlink(netconfpkg.ROOT + SYSCONFDEVICEDIR + entry)
                unlink(netconfpkg.ROOT + OLDSYSCONFDEVICEDIR+'/keys-'+ipsecid)

    def __repr__(self):
        return repr(self.__dict__)

    def _objToStr(self, parentStr = None):
        retstr = ""
        for ipsec in self:
            retstr += ipsec._objToStr("IPsecList.%s" % (ipsec.IPsecId))

        return retstr

    def _parseLine(self, vals, value):
        class BadLineException: pass
        if len(vals) <= 1:
            return
        if vals[0] == "IPsecList":
            del vals[0]
        else:
            return

        for ipsec in self:
            if ipsec.IPsecId == vals[0]:
                ipsec._parseLine(vals[1:], value)
                return
        
        i = self.addIPsec()
        self[i].IPsecId = vals[0]
        self[i]._parseLine(vals[1:], value)
    
    
IPSList = None

def getIPsecList(refresh = None):
    global IPSList
    if IPSList == None or refresh:
        IPSList = IPsecList()
        IPSList.load()
    return IPSList
