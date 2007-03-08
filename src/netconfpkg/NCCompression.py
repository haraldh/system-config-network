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

from netconfpkg import Compression_base
from NC_functions import *

class Compression(Compression_base):
    boolkeydict = { 'VJTcpIp' : 'VJ',
                    'VJID' : 'VJCCOMP',
                    'AdressControl' : 'AC',
                    'ProtoField' : 'PC',
                    'BSD' : 'BSDCOMP',
                    'CCP' : 'CCP',
                    }
    
    def __init__(self, list = None, parent = None):
        Compression_base.__init__(self, list, parent)        

    def load(self, parentConf):
        conf = parentConf
        
        for selfkey in self.boolkeydict.keys():
            confkey = self.boolkeydict[selfkey]
            if conf.has_key(confkey):
                if conf[confkey] == 'on':
                    self.__dict__[selfkey] = True
                else:
                    self.__dict__[selfkey] = False            
            else:
                self.__dict__[selfkey] = False            

    def save(self, parentConf):        
        conf = parentConf

        for selfkey in self.boolkeydict.keys():
            confkey = self.boolkeydict[selfkey]
            if self.__dict__[selfkey]:
                conf[confkey] = 'on'
            else:
                conf[confkey] = 'off'
    
__author__ = "Harald Hoyer <harald@redhat.com>"
