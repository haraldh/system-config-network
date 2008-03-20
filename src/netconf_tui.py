#!/usr/bin/python
# -*- coding: utf-8 -*-

## netconf-tui - a tui network configuration tool
## Copyright (C) 2002-2003 Red Hat, Inc.
## Copyright (C) 2002-2003 Trond Eivind Glomsrød <teg@redhat.com>
## Copyright (C) 2002-2005 Harald Hoyer <harald@redhat.com>

#from snack import *

PROGNAME='system-config-network'

import os
import sys
import locale
import signal

from snack import SnackScreen
import netconfpkg # pylint: disable-msg=W0611
from netconfpkg import NC_functions
from netconfpkg.NC_functions import log, generic_error_dialog
from netconfpkg.NCDeviceList import getDeviceList
from netconfpkg.NCProfileList import getProfileList
from rhpl.translate import _, textdomain_codeset
locale.setlocale(locale.LC_ALL, "")
textdomain_codeset(PROGNAME, locale.nl_langinfo(locale.CODESET))

if not "/usr/share/system-config-network" in sys.path:
    sys.path.append("/usr/share/system-config-network")

if not "/usr/share/system-config-network/netconfpkg/" in sys.path:
    sys.path.append("/usr/share/system-config-network/netconfpkg")

from version import PRG_VERSION
from version import PRG_NAME
import traceback
import types

dumpHash = {}
# XXX do length limits on obj dumps.
def dumpClass(instance, fd, level=0):
    # protect from loops
    if not dumpHash.has_key(instance):
        dumpHash[instance] = None
    else:
        fd.write("Already dumped\n")
        return
    if (instance.__class__.__dict__.has_key("__str__") or
        instance.__class__.__dict__.has_key("__repr__")):
        fd.write("%s\n" % (instance,))
        return
    fd.write("%s instance, containing members:\n" %
             (instance.__class__.__name__))
    pad = ' ' * ((level) * 2)
    for key, value in instance.__dict__.items():
        if type(value) == types.ListType:
            fd.write("%s%s: [" % (pad, key))
            first = 1
            for item in value:
                if not first:
                    fd.write(", ")
                else:
                    first = 0
                if type(item) == types.InstanceType:
                    dumpClass(item, fd, level + 1)
                else:
                    fd.write("%s" % (item,))
            fd.write("]\n")
        elif type(value) == types.DictType:
            fd.write("%s%s: {" % (pad, key))
            first = 1
            for k, v in value.items():
                if not first:
                    fd.write(", ")
                else:
                    first = 0
                if type(k) == types.StringType:
                    fd.write("'%s': " % (k,))
                else:
                    fd.write("%s: " % (k,))
                if type(v) == types.InstanceType:
                    dumpClass(v, fd, level + 1)
                else:
                    fd.write("%s" % (v,))
            fd.write("}\n")
        elif type(value) == types.InstanceType:
            fd.write("%s%s: " % (pad, key))
            dumpClass(value, fd, level + 1)
        else:
            fd.write("%s%s: %s\n" % (pad, key, value))

#
# handleException function
#
def handleException((mtype, value, tb), progname, version):
    mlist = traceback.format_exception (mtype, value, tb)
    tblast = traceback.extract_tb(tb, limit=None)
    if len(tblast):
        tblast = tblast[len(tblast)-1]
    extxt = traceback.format_exception_only(mtype, value)
    text = "Component: %s\n" % progname
    text = text + "Version: %s\n" % version
    text = text + "Summary: TB "
    text = _("An unhandled exception has occured.  This "
             "is most likely a bug.  Please save the crash "
             "dump and file a detailed bug "
             "report against system-config-network at "
             "https://bugzilla.redhat.com/bugzilla") + "\n" + text

    if tblast and len(tblast) > 3:
        tblast = tblast[:3]
    for t in tblast:
        text = text + str(t) + ":"
    text = text + extxt[0]
    text = text + "".join(mlist)

    print text
    import pdb
    pdb.post_mortem (tb)
    os.kill(os.getpid(), signal.SIGKILL)

    sys.exit(10)

sys.excepthook = lambda type, value, tb: handleException((type, value, tb),
                                                         PRG_NAME, PRG_VERSION)



from netconfpkg import exception
from netconfpkg.NCHardwareList import getHardwareList
from snack import GridForm, TextboxReflowed, Listbox, ButtonBar
from netconfpkg.NC_functions import ETHERNET, ISDN, MODEM, QETH
from netconfpkg.NCDeviceFactory import getDeviceFactory

# load all plugins by importing the base module directory
import netconfpkg.tui # pylint: disable-msg=W0611

def loadConfig(mscreen):
    exception.action(_("Loading configuration"))
    t=TextboxReflowed(10, _("Loading Device Configuration"))
    g=GridForm(mscreen,_("Network Configuration"),1,1)
    g.add(t,0,0)
    g.draw()
    mscreen.refresh()
    devicelist = getDeviceList()
    t.setText(_("Loading Hardware Configuration"))
    g.draw()
    mscreen.refresh()
    hardwarelist = getHardwareList()
    t.setText(_("Loading Profile Configuration"))
    g.draw()
    mscreen.refresh()
    profilelist = getProfileList()
    mscreen.popWindow()

#
# main Screen
#
def newDevice(mscreen):
    """
    Displays the main screen
    @screen The snack screen instance
    """
    t=TextboxReflowed(25,_("Which device type do you want to add?"))
    bb=ButtonBar(mscreen,((_("Add"),"add"),(_("Cancel"),"cancel")))
    li=Listbox(5,width=25,returnExit=1)
    li.append(_("Ethernet"), ETHERNET)
    li.append(_("Modem"), MODEM)
    li.append(_("ISDN"), ISDN)

    machine = os.uname()[4]
    if machine == 's390' or machine == 's390x':
        li.append(_("QETH"), QETH)

    g=GridForm(mscreen,_("Network Configuration"),1,3)
    g.add(t,0,0)
    g.add(li,0,1)
    g.add(bb,0,2)
    res=g.run()
    mscreen.popWindow()
    if bb.buttonPressed(res) != 'cancel':
        todo=li.current()
        df = getDeviceFactory()
        dev = None
        devclass = df.getDeviceClass(todo)
        devlist = getDeviceList()
        if not devclass: return -1
        dev = devclass()
        if dev:
            i = devlist.addDevice() # pylint: disable-msg=E1101
            devlist[i] = dev
            return dev
    return -2

def selectDevice(mscreen):
    li=Listbox(5,returnExit=1)
    l = 0
    le = mscreen.width - 6
    if le <= 0: le = 5
    for dev in getDeviceList():
        if not hasattr(dev, "getDialog") or not dev.getDialog():
            #li.append("No dialog for %s" % dev.Device, None)
            continue

        l += 1
        for hw in getHardwareList():
            if hw.Name == dev.Device and hw.Description:
                li.append(("%s (%s) - %s" % (dev.DeviceId,
                                             dev.Device,
                                             hw.Description))[:le], dev)
                break

        else:
            li.append(("%s (%s) - %s" % (dev.DeviceId,
                                    dev.Device, dev.Type))[:le], dev)

    if not l:
        return None

    li.append(_("<New Device>"), None)
    g=GridForm(mscreen,_("Select A Device"),1,3)
    bb=ButtonBar(mscreen,((_("Quit"),"quit"), (_("Cancel"),"cancel")))
    g.add(li,0,1)
    g.add(bb,0,2,growx=1)
    res = g.run()
    mscreen.popWindow()
    if bb.buttonPressed(res)=="quit":
        ret = -1
    elif bb.buttonPressed(res)=="cancel":
        ret = None
    else:
        ret=li.current()
        if not ret:
            ret = newDevice(mscreen)
    return ret


def Usage():
    print _("system-config-network - network configuration tool\n\nUsage: system-config-network -v --verbose -d --debug")

#
# __main__
#
def main():
    import getopt
    class BadUsage(Exception):
        pass
    NC_functions.setVerboseLevel(2)
    NC_functions.setDebugLevel(0)
    chroot = None
    debug = 0

    # FIXME: add --root= option

    try:
        opts, args = getopt.getopt(sys.argv[1:], "vh?r:d",
                                   [
                                    "verbose",
                                    "debug",
                                    "help",
                                    "root="
                                    ])
        for opt, val in opts:
            if opt == '-v' or opt == '--verbose':
                NC_functions.setVerboseLevel(NC_functions.getVerboseLevel()+1)
                continue

            if opt == '-d' or opt == '--debug':
                NC_functions.setDebugLevel(NC_functions.getDebugLevel()+1)
                debug = 1
                continue

            if opt == '-h' or opt == "?" or opt == '--help':
                Usage()
                return 0

            if opt == '-r' or opt == '--root':
                chroot = val
                continue

            raise BadUsage

    except (getopt.error, BadUsage):
        Usage()
        return 1


    if not NC_functions.getDebugLevel():
        log.handler = log.syslog_handler
        log.open()
    else:
        log.handler = log.file_handler
        log.open(sys.stderr)

    if chroot:
        NC_functions.setRoot(chroot)

    if not os.access(NC_functions.getRoot(), os.W_OK):
        if os.getuid() != 0:
            generic_error_dialog (_("Please start system-config-network "
                                    "with root permissions!\n"))
            return 10

    if chroot:
        NC_functions.prepareRoot(chroot)
        
#    exception.installExceptionHandler(PRG_NAME, PRG_VERSION, gui=0,
#                                      debug=debug)
    screen = SnackScreen()
    plist = getProfileList()
    devlist = getDeviceList()
    try:
        #mainScreen(screen)
        loadConfig(screen)
        while True:
            dev = selectDevice(screen)
            # pylint: disable-msg=E1101
            # pylint: disable-msg=E1103
            if dev == -1:
                if devlist.modified():
                    devlist.save()
                if plist.modified():
                    plist.save()
                break
            elif dev == -2:
                continue
            elif dev == None:
                break

            dialog = dev.getDialog()
            if dialog.runIt(screen):
                dev.commit()     
                devlist.commit() 
                plist.activateDevice(dev.DeviceId,
                                     plist.getActiveProfile().ProfileName,
                                     state = True)
                plist.commit()
            else:
                dev.rollback()     
                devlist.rollback() 

        screen.finish()
        #print dir(screen)
        #print dev
    except SystemExit, code:
        screen.finish()
        return code
    except:
        screen.finish()
        raise

if __name__=="__main__":
    sys.exit(main())

__author__ = "Trond Eivind Glomsrød <teg@redhat.com>, Harald Hoyer <harald@redhat.com>"
