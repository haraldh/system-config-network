#! /usr/bin/python2.2

## netconf - A network configuration tool
## Copyright (C) 2001-2003 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001-2003 Harald Hoyer <harald@redhat.com>
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

import getopt
import signal
import os
import os.path
import string
from netconfpkg import *
from rhpl.genClass import *
from rhpl.log import log
from version import PRG_VERSION
from version import PRG_NAME

PROGNAME='redhat-config-network'

import locale
from rhpl.translate import _, N_, textdomain_codeset
locale.setlocale(locale.LC_ALL, "")
textdomain_codeset(PROGNAME, locale.nl_langinfo(locale.CODESET))
import __builtin__
__builtin__.__dict__['_'] = _

def handleException((type, value, tb), progname, version, debug=None):
    import pdb
    list = traceback.format_exception (type, value, tb)
    tblast = traceback.extract_tb(tb, limit=None)
    if len(tblast):
        tblast = tblast[len(tblast)-1]
    extxt = traceback.format_exception_only(type, value)
    text = _("An unhandled exception has occured.  This "
            "is most likely a bug.\nPlease file a detailed bug "
            "report against the component %s at \n"
            "https://bugzilla.redhat.com/bugzilla\n"
             "using the text below.\n") % \
            progname
    text += "Component: %s\n" % progname
    text += "Version: %s\n" % version
    text += "Summary: TB "
    if tblast and len(tblast) > 3:
        tblast = tblast[:3]
    for t in tblast:        
        text += str(t) + ":"
    text += extxt[0]
    text += joinfields(list, "")

    trace = tb
    while trace.tb_next:
        trace = trace.tb_next
    frame = trace.tb_frame
    text += ("\nLocal variables in innermost frame:\n")
    try:
        for (key, value) in frame.f_locals.items():
            text += "%s: %s\n" % (key, value)
    except:
        pass

    sys.stderr.write(text)
    if debug:
        pdb.post_mortem (tb)
        os.kill(os.getpid(), signal.SIGKILL)
    sys.exit(10)


def Usage():
    sys.stderr.write( _("%s - network configuration commandline tool") % (sys.argv[0]) + '\n')
    sys.stderr.write( _("Copyright (c) 2001-2003 Red Hat, Inc.") + '\n')
    sys.stderr.write( _("This software is distributed under the GPL. "
            "Please Report bugs to Red Hat's Bug Tracking "
            "System: http://bugzilla.redhat.com/") + "\n\n")
    sys.stderr.write( _("Usage: %s") % (sys.argv[0]) + '\n')
    sys.stderr.write( "\t-p, --profile <profile> [--activate, -a]: %s"\
          % _("switch / activate profile") + '\n')
    sys.stderr.write( "\t-h, --hardwarelist : %s"\
          % _("export / import hardware list") + '\n')
    sys.stderr.write( "\t-d, --devicelist   : %s"\
          % _("export / import device list (default)") + '\n')
    sys.stderr.write( "\t-o, --profilelist  : %s"\
          % _("export / import profile list") + '\n')
    sys.stderr.write( "\t-r, --root=<root>  : %s"\
          % _("set the root directory") + '\n')
    sys.stderr.write( "\t-e, --export       : %s" % _("export list (default)") + '\n')
    sys.stderr.write( "\t-i, --import       : %s" % _("import list") + '\n')
    sys.stderr.write( "\t-c, --clear        : %s" % \
          _("clear existing list prior of importing") + '\n')
    sys.stderr.write( "\t-f, --file=<file>  : %s" % \
          _("import from file") + '\n')
    sys.stderr.write('\n')
    
if __name__ == '__main__':
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    class BadUsage: pass
    from netconfpkg import NC_functions

    progname = os.path.basename(sys.argv[0])
    NC_functions.setVerboseLevel(2)
    NC_functions.setDebugLevel(0)
    
    logfilename = "/var/log/redhat-config-network"
    do_activate = 0
    switch_profile = 0
    profile = None
    test = 0
    EXPORT = 1
    IMPORT = 2
    SWITCH = 3
    mode = EXPORT
    filename = None
    clear = 0
    list = 0
    chroot = None
    debug = None
    devlists = []
    try:
        opts, args = getopt.getopt(cmdline, "ap:?r:dhvtief:co",
                                   [
                                    "activate",
                                    "profile=",
                                    "help",
                                    "devicelist",
                                    "verbose",
                                    "test",
                                    "import",
                                    "export",
                                    "clear",
                                    "root=",
                                    "file=",
                                    "debug",
                                    "hardwarelist",
                                    "profilelist"])
        for opt, val in opts:
            if opt == '-d' or opt == '--devicelist':
                devlists.append(getDeviceList())
                continue
                
            if opt == '-h' or opt == '--hardwarelist':
                devlists.append(getHardwareList())
                continue
            
            if opt == '-o' or opt == '--profilelist':
                devlists.append(getProfileList())
                continue
            
            if opt == '-p' or opt == '--profile':
                mode = SWITCH
                switch_profile = 1
                profile = val
                continue

            if opt == '-f' or opt == '--file':
                filename = val
                continue
            
            if opt == '-r' or opt == '--root':
                chroot = val
                continue
            
            if opt == '-c' or opt == '--clear':
                clear = 1
                continue
            
            if opt == '-t' or opt == '--test':
                test = 1
                continue
            
            if opt == '-a' or opt == '--activate':
                mode = SWITCH
                do_activate = 1
                continue

            if opt == '-i' or opt == '--import':
                mode = IMPORT
                continue

            if opt == '-e' or opt == '--export':
                mode = EXPORT
                continue
                
            if opt == '-?' or opt == '--help':
                Usage()
                sys.exit(0)

            if opt == '-v' or opt == '--verbose':
                NC_functions.setVerboseLevel(NC_functions.getVerboseLevel()+1)
                continue

            if opt == '-d' or opt == '--debug':
                NC_functions.setDebugLevel(NC_functions.getDebugLevel()+1)
                debug = 1
                continue

            sys.stderr.write(_("Unknown option %s\n" % opt))
            raise BadUsage
      
    except (getopt.error, BadUsage):
        Usage()
        sys.exit(1)

    try:

        if not NC_functions.getDebugLevel():
            import os

            def log_default_handler (string):
                import time
                log.logFile.write ("%s: %s\n" % (time.ctime(), string))

            log.handler = log_default_handler

            if os.path.isfile(logfilename):
                os.chmod(logfilename, 0600)

            fd = os.open(logfilename,
                            os.O_APPEND|os.O_WRONLY|os.O_CREAT,
                            0600)

            lfile = os.fdopen(fd, "a")        
            log.open(lfile)
            
        if chroot:
            prepareRoot(chroot)

        if os.getuid() == 0 or chroot:
            NCProfileList.updateNetworkScripts()
            NCDeviceList.updateNetworkScripts()

            
        if not len(devlists):
            devlists = [getDeviceList(), getHardwareList(),
                        getProfileList()]
            
        if clear:
            for devlist in devlists:
                del devlist[0:len(devlist)-1]

        if mode == EXPORT:
            for devlist in devlists:
                devstr =  str(devlist)
                if len(devstr):
                    # remove the last \n
                    print devstr[:-1]                    
            sys.exit(0)

        elif mode == IMPORT:
            devlistsdict = {
                "HardwareList" : getHardwareList(),
                "DeviceList" : getDeviceList(),
                "ProfileList" : getProfileList() }
            
            if filename:
                file = open(filename, "r")
            else:
                file = sys.stdin
         
            lines = file.readlines()
      
            for line in lines:
                try:
                    line = line[:-1]
                    log.log(3, "Parsing '%s'\n" % line)
                    vals = string.split(line, "=")
                    if len(vals) <= 1:
                        continue
                    key = vals[0]
                    value = string.join(vals[1:], "=")

                    vals = string.split(key, ".")
                    if devlistsdict.has_key(vals[0]):
                        devlistsdict[vals[0]]._parseLine(vals, value)
                    else:
                        sys.stderr.write(_("Unknown List %s\n", vals[0]))
                        raise ParseError
                        
                except Exception, e:
                    pe = ParseError(_("Error parsing line: %s") % line)
                    pe.args += e.args
                    raise pe

                
            for devlist in devlists:
                log.log(1, devlist)
                devlist.save()
            
            sys.exit(0)

        elif test:
            sys.exit(0)

        elif mode == SWITCH:
            ret = None
            profilelist = getProfileList()
            actdev = Control.NetworkDevice()
            actdev.load()
            aprof = profilelist.getActiveProfile()
            
            if switch_profile and aprof.ProfileName != profile:
                log.log(1, "Switching to profile %s" % profile)
                if do_activate:
                    for p in profilelist:
                        if p.ProfileName == profile:
                            aprof = p
                            break
                    for device in getDeviceList():
                        if device.DeviceId not in aprof.ActiveDevices:
                            if actdev.find(device.Device):
                                (ret, msg) = device.deactivate()
                                if ret:
                                    print msg
                profilelist.switchToProfile(profile)
                profilelist.save()

            actdev.load()

            if do_activate:
                aprof = profilelist.getActiveProfile()
                for device in getDeviceList():
                    if device.DeviceId in aprof.ActiveDevices:
                        if not actdev.find(device.Device) and \
                           device.OnBoot:
                            (ret, msg) = device.activate()
                            if ret:
                                print msg
                        
                sys.exit(0)

        sys.exit(0)
    except SystemExit, code:
        #print "Exception %s: %s" % (str(SystemExit), str(code))
        sys.exit(code)
    except:
        handleException(sys.exc_info(), PROGNAME, PRG_VERSION, debug = debug)
__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2003/10/08 15:07:49 $"
__version__ = "$Revision: 1.14 $"
