## Copyright (C) 2001-2005 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001-2005 Harald Hoyer <harald@redhat.com>
## Copyright (C) 2001, 2002 Philipp Knirsch <pknirsch@redhat.com>

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

import sys
import NC_functions
from netconfpkg import Cipe_base
import string

from rhpl import Conf

from NC_functions import *


class ConfCipeOptions(Conf.Conf):
    def __init__(self, name):
        fname = netconfpkg.ROOT + CIPEDIR + '/options.' + name
        Conf.Conf.__init__(self, fname, '#', '\t ', ' ')
        self.chmod(0600)

    def read(self):
        Conf.Conf.read(self)
        self.initvars()

    def initvars(self):
        self.vars = {}
        self.rewind()
        while self.findnextcodeline():
            #print self.getline()
            var = self.getfields()
            if len(var) > 1:
                self.vars[var[0]] = var[1]
            elif len(var) == 1:
                self.vars[var[0]] = ""
            self.nextline()
        self.rewind()
        
    def __getitem__(self, varname):
        if self.vars.has_key(varname):
            return self.vars[varname]
        else:
            return None
        
    def __setitem__(self, varname, value):
        # set first (should be only) instance to values in list value
        place=self.tell()
        self.rewind()
        # not a nameserver, so all items on one line...
        if self.findnextline('^' '[' + self.separators + ']*' + varname +
                             '[' + self.separators + ']+'):
            self.deleteline()
            self.insertlinelist([ varname, value ])
            self.seek(place)
        else:
            self.seek(place)
            self.insertlinelist([ varname, value ])
        # no matter what, update our idea of the variable...
        self.vars[varname] = value
        
    def __delitem__(self, varname):
        # delete *every* instance...
        self.rewind()
        while self.findnextline('[' + self.separators + ']*' + varname +
                                '[' + self.separators + ']'):
            self.deleteline()
        del self.vars[varname]
        
    def write(self):
        for key in self.vars.keys():
            self[key] = self.vars[key]
        Conf.Conf.write(self)
        
    def keys(self):
        return self.vars.keys()
    
    def has_key(self, key):
        return self.vars.has_key(key)

        
class Cipe(Cipe_base):
    intkeydict = {'LocalPort' : 'MYPORT',
                  }
    
    keydict = { 'RemotePeerAddress' : 'PEER',
                'RemoteVirtualAddress' : 'PTPADDR',
                'TunnelDevice' : 'TUNNELDEV',
                'TunnelIP' : 'ME',
                }
    
    def __init__(self, list = None, parent = None):
        Cipe_base.__init__(self, list, parent)        
        
    def load(self, parentConf):
        conf = parentConf

        for selfkey in self.keydict.keys():
            confkey = self.keydict[selfkey]
            if conf.has_key(confkey):
                self.__dict__[selfkey] = conf[confkey]

        for selfkey in self.intkeydict.keys():
            confkey = self.intkeydict[selfkey]
            if conf.has_key(confkey) and len(conf[confkey]):
                self.__dict__[selfkey] = int(conf[confkey])


        parent = self.getParent()
        if parent:
            conf = ConfCipeOptions(parent.DeviceId)
            if conf.has_key('key'):
                self.SecretKey = conf['key']
                
        self.commit(changed=false)
        
    def save(self, parentConf):
        conf = parentConf

        for selfkey in self.keydict.keys():
            confkey = self.keydict[selfkey]
            if self.__dict__[selfkey]:
                conf[confkey] = str(self.__dict__[selfkey])
            else: conf[confkey] = ""

        for selfkey in self.intkeydict.keys():
            confkey = self.intkeydict[selfkey]
            if self.__dict__[selfkey]:
                conf[confkey] = str(self.__dict__[selfkey])
            else: conf[confkey] = ""

        for i in conf.keys():
            if not conf[i] or conf[i] == "": del conf[i]

        
        parent = self.getParent()
        if parent:
            if not os.path.isdir(netconfpkg.ROOT + CIPEDIR):
                generic_error_dialog(_("Directory %s is missing!\nWill create it for you!\nYou should install the cipe rpm package!\n") % netconfpkg.ROOT + CIPEDIR)
                try:
                    os.mkdir(netconfpkg.ROOT + CIPEDIR)
                except:
                    generic_error_dialog(_("Could not create\ndirectory %s!") % netconfpkg.ROOT + CIPEDIR)
                    return
            conf = ConfCipeOptions(parent.DeviceId)
            if conf:
                if self.SecretKey: conf['key'] = self.SecretKey
                if not conf.has_key("maxerr"): conf["maxerr"] = '-1'
                if not conf.has_key("cttl"): conf["cttl"] = '64'
        
                conf.write()
__author__ = "Harald Hoyer <harald@redhat.com>"
