"Package for network configuration."

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

__netconfpkg.Use_Alchemist = False

from netconfpkg.genClass import readClassfile

for _idl_file in [ "DeviceList.idl",
                   "HardwareList.idl",
                   "IPsecList.idl",
                   "ProfileList.idl" ]:
    readClassfile(__path__[0] + "/" + _idl_file, mod = __netconfpkg)

del readClassfile
del _idl_file

import os

# pylint: disable-msg=W0141
_files = map(lambda v: v[:-3], filter(lambda v: v[-3:] == ".py" and \
                                      v != "__init__.py" and \
                                      v != 'genClass.py' and \
                                      v[0] != '.', \
                                      os.listdir(__path__[0])))

import locale
locale.setlocale(locale.LC_ALL, "C")
_files.sort()
locale.setlocale(locale.LC_ALL, "")

from netconfpkg.genClassMap import * # pylint: disable-msg=W0401

del _files
del __netconfpkg
del locale
del os

__author__ = "Harald Hoyer <harald@redhat.com>"
