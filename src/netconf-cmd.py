#! /usr/bin/python2.2

## netconf - A network configuration tool
## Copyright (C) 2001, 2002 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001, 2002 Harald Hoyer <harald@redhat.com>
## Copyright (C) 2001, 2002 Philipp Knirsch <pknirsch@redhat.com>
## Copyright (C) 2001, 2002 Trond Eivind Glomsrød <teg@redhat.com>

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

if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")

if not "/usr/share/redhat-config-network" in sys.path:
    sys.path.append("/usr/share/redhat-config-network")

if not "/usr/share/redhat-config-network/netconfpkg/" in sys.path:
    sys.path.append("/usr/share/redhat-config-network/netconfpkg")

# Workaround for buggy gtk/gnome commandline parsing python bindings.
cmdline = sys.argv[1:]
sys.argv = sys.argv[:1]

import getopt
import signal
import os
import gettext

PROGNAME='redhat-config-network'
gettext.bindtextdomain(PROGNAME, "/usr/share/locale")
gettext.textdomain(PROGNAME)

try:
    gettext.install(PROGNAME, "/usr/share/locale", 1)
except IOError:
    import __builtin__
    __builtin__.__dict__['_'] = unicode    

os.environ["PYgtk_FATAL_EXCEPTIONS"] = '1'

import os.path
import string
from netconfpkg import *
from rhpl import genClass

def Usage():
    print _("redhat-config-network-cmd - Python network configuration commandline tool\n\nUsage: redhat-config-network-cmd -p --profile <profile>")

def printClass(classname, parent = None):    
    for child, attr in classname.Attributes.items():
        if child == genClass.SELF: continue

        if parent: pname = "%s.%s" % (parent, classname.Attributes[SELF][NAME])
        else: pname = classname.Attributes[SELF][NAME]
        
        if attr[TYPE] != genClass.LIST:
            print "%s.%s" % (pname, child)
        else:
            printClass(getattr(netconfpkg, child),
                       pname)

def printObj(obj, parent = None):
#    if parent: pname = "%s.%s" % (parent, obj._attributes[SELF][NAME])
#    else: pname = obj._attributes[SELF][NAME]
    
    for child, attr in obj._attributes.items():
        if child == genClass.SELF: continue

        val = None
        
        if hasattr(obj, child):
            val = getattr(obj, child)
            
        if attr[TYPE] != genClass.LIST:
            if val != None:
                if attr[TYPE] != genClass.BOOL:
                    print "%s.%s=%s" % (parent, child, str(val))
                else:
                    if val: print "%s.%s=true" % (parent, child)
                    else: print "%s.%s=false" % (parent, child)
                
        else:
            if val != None:
                printObj(val, "%s.%s" % (parent, child))

if __name__ == '__main__':
#    if os.getuid() != 0:
#        print _("Please restart %s with root permissions!") % (sys.argv[0])
#        sys.exit(10)
        
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    class BadUsage: pass
    updateNetworkScripts()

    progname = os.path.basename(sys.argv[0])

    try:
        opts, args = getopt.getopt(cmdline, "p:thd",
                                   ["profile=",
                                    "test",
                                    "help",
                                    "devicelist"])
        for opt, val in opts:
            if opt == '-d' or opt == '--devicelist':
                devlist = getDeviceList()
                for dev in devlist:
                    if (not args) or (dev.DeviceId in args):
                        printObj(dev, dev.DeviceId)
                        
                sys.exit(0)
                
            if opt == '-p' or opt == '--profile':
                profilelist = getProfileList()
                profilelist.switchToProfile(val)
                sys.exit(0)

            if opt == '-h' or opt == '--help':
                Usage()
                sys.exit(0)

            raise BadUsage

    except (getopt.error, BadUsage):
        Usage()
        sys.exit(1)

    printClass(Device)
