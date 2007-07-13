"""Package for network configuration.
Provides reading and writing of the system's configuration files"""

# -*- python -*-
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

# Import all subpackages of our netconfpkg directory. This code is a real
# dirty hack but does the job(tm). It basically finds all .py files in the
# package directory and imports from all found files (except __init__.py that
# is) ;). Nice for plugin mechanism.

import sys

__netconfpkg = sys.modules[__name__]

__netconfpkg.Use_Alchemist = None

from genClass import GenClass_read_classfile

for _idl_file in [ "DeviceList.idl",
                   "HardwareList.idl",
                   "IPsecList.idl",
                   "ProfileList.idl" ]:
    GenClass_read_classfile(__path__[0] + "/" + _idl_file, mod = __netconfpkg)

del _idl_file

import os

_files = map(lambda v: v[:-3], filter(lambda v: v[-3:] == ".py" and \
                                      v != "__init__.py" and \
                                      v != 'genClass.py' and \
                                      v[0] != '.', \
                                      os.listdir(__path__[0])))

import locale
locale.setlocale(locale.LC_ALL, "C")
_files.sort()
locale.setlocale(locale.LC_ALL, "")


for _i in _files:
    _cmd = "from %s import *" % (_i)
    exec _cmd

del _i
del _files
del _cmd
del __netconfpkg
del locale
del os
del GenClass_read_classfile

__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2007/07/13 12:51:25 $"
__version__ = "$Revision: 1.23 $"
