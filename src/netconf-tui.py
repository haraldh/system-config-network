#!/usr/bin/python
# -*- coding: utf-8 -*-

## netconf-tui - a tui network configuration tool
## Copyright (C) 2002-2003 Red Hat, Inc.
## Copyright (C) 2002-2003 Trond Eivind Glomsrød <teg@redhat.com>
## Copyright (C) 2002-2003 Harald Hoyer <harald@redhat.com>

from snack import *

PROGNAME='system-config-network'

import locale
from rhpl.translate import _, N_, textdomain_codeset
locale.setlocale(locale.LC_ALL, "")
textdomain_codeset(PROGNAME, locale.nl_langinfo(locale.CODESET))

import sys
import string

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
def handleException((type, value, tb), progname, version):
    list = traceback.format_exception (type, value, tb)
    tblast = traceback.extract_tb(tb, limit=None)
    if len(tblast):
        tblast = tblast[len(tblast)-1]
    extxt = traceback.format_exception_only(type, value)
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
    text = text + joinfields(list, "")

    print text
    import pdb
    pdb.post_mortem (tb)
    os.kill(os.getpid(), signal.SIGKILL)
        
    sys.exit(10)

sys.excepthook = lambda type, value, tb: handleException((type, value, tb),
                                                         PRG_NAME, PRG_VERSION)

from netconfpkg import *


#
# main Screen
#
def mainScreen(screen):
    """
    Displays the main screen
    @screen The snack screen instance
    """
    t=TextboxReflowed(25,_("What do you want to configure?"))
    bb=ButtonBar(screen,((_("Configure"),"configure"),(_("Exit"),"exit")))
    li=Listbox(5,width=25,returnExit=1)
    li.append("Ethernet","Ethernet")
    li.append("Modem","Modem")
    li.append("ISDN","ISDN")
    g=GridForm(screen,_("Network Configuration"),1,3)
    g.add(t,0,0)
    g.add(li,0,1)
    g.add(bb,0,2)
    while 1:
        res=g.run()
        if bb.buttonPressed(res)=='exit':
            break
        elif bb.buttonPressed(res)=='configure':
            todo=li.current()
            if(todo=="Ethernet"):
                nw=EthernetWindow(screen,getDeviceList())
                nw.runIt()
            elif(todo=="Modem"):
                mw=ModemWindow(screen,getDeviceList())
                mw.runIt()
            elif(todo=="ISDN"):
                iw=ISDNWindow(screen,getDeviceList())
                iw.runIt()
    screen.popWindow()

#
# EthernetWindow class
#
class EthernetWindow:
    def __init__(self,screen,devicelist,eth=None):
        """
        The constructor
        @screen A snack screen instance
        @devicelist A NCDeviceList
        @eth The ethernet device. If none given, the first
             ethernetdevice in devicelist will be used.
             If none are there, one will be added.
        """

        self.devicelist=devicelist
        self.screen=screen
        self.name=Entry(20,"")
        self.hwdev=Entry(20,"")
        self.dynip=Checkbox("")
        self.statip=Entry(20,"")
        self.netmask=Entry(20,"")
        self.gw=Entry(20,"")
        if not eth:
            self.eth=None
            for dev in devicelist:
                if dev.Type=="Ethernet":
                    self.eth=dev
                    break
            if not self.eth:
                df = NCDeviceFactory.getDeviceFactory()        
                self.eth = df.getDeviceClass(ETHERNET)()
                i = self.devicelist.addDevice()
                self.devicelist[i] = self.eth
        else:
            self.eth=eth

    def setState(self,eth=None):
        """
        Set the default values of the fields
        according to the given device
        @eth The NCDevice (type ethernet) to use as default values
        """

        if eth:
            if eth.DeviceId:
                self.name.set(eth.DeviceId)
            if eth.Device:
                self.hwdev.set(eth.Device)
            if eth.BootProto:
                bp=string.lower(eth.BootProto)
                if (bp=="dhcp") or (bp=="bootp"):
                    self.dynip.setValue("*")
            if eth.IP:
                self.statip.set(eth.IP)
            if eth.Netmask:
                self.netmask.set(eth.Netmask)
            if eth.Gateway:
                self.gw.set(eth.Gateway)
        
    def useDynamicCheckBox(self):
        """
        Set the static IP field to enabled/disabled
        determined by the dynamic IP field
        """
        
        if self.dynip.selected():
            state=FLAGS_SET
        else:
            state=FLAGS_RESET
        for i in self.statip,self.netmask,self.gw:
            i.setFlags(FLAG_DISABLED,state)

    def processInfo(self):
        """
        Extracts info from the screen, and puts it into a device object
        """

        self.eth.DeviceId=self.name.value()
        self.eth.Device=self.hwdev.value()
        if self.dynip.value():
            self.eth.BootProto="dhcp"
            self.eth.IP=None
            self.eth.Netmask=None
            self.eth.Gateway=None
        else:
            self.eth.IP=self.statip.value()
            self.eth.Netmask=self.netmask.value()
            self.eth.Gateway=self.gw.value()
            self.eth.BootProto=None
    
    def runIt(self):
        """
        Show and run the screen, save files if necesarry
        """
        g1=Grid(1,1)
        g2=Grid(2,6)
        g2.setField(Label (_("Name")),0,0,anchorLeft=1)
        g2.setField(Label (_("Device")),0,1,anchorLeft=1)
        g2.setField(Label (_("Use DHCP")),0,2,anchorLeft=1)
        g2.setField(Label (_("Static IP")),0,3,anchorLeft=1)
        g2.setField(Label (_("Netmask")),0,4,anchorLeft=1)
        g2.setField(Label (_("Default gateway IP")),0,5,anchorLeft=1)
        g2.setField(self.name,1,0,(1,0,0,0))
        g2.setField(self.hwdev,1,1,(1,0,0,0))
        g2.setField(self.dynip,1,2,(1,0,0,0),anchorLeft=1)
        g2.setField(self.statip,1,3,(1,0,0,0))
        g2.setField(self.netmask,1,4,(1,0,0,0))
        g2.setField(self.gw,1,5,(1,0,0,0))
        self.dynip.setCallback(self.useDynamicCheckBox)
        bb=ButtonBar(self.screen,((_("Ok"),"ok"),(_("Cancel"),"cancel")))
        self.setState(self.eth)
        tl=GridForm(screen,_("Ethernet Configuration"),1,3)
        tl.add(g1,0,0,(0,0,0,1),anchorLeft=1)
        tl.add(g2,0,1,(0,0,0,1))
        tl.add(bb,0,2,growx=1)
        self.useDynamicCheckBox()
        while 1:
            res=tl.run()
            if bb.buttonPressed(res)=="cancel":
                screen.popWindow()
                break
            elif bb.buttonPressed(res)=="ok":
                self.processInfo()
                self.devicelist.save()
                screen.popWindow()
                break


#
# ModemWindow class
#
class ModemWindow:
    def __init__(self,screen,devicelist,modem=None):
        """
        The constructor
        @screen A snack screen instance
        @devicelist A NCDeviceList
        @modem The modem device. If none given, the first
               modem in devicelist will be used.
               If none are there, one will be added.
        """

        self.devicelist=devicelist
        self.screen=screen
        self.name=Entry(20,"")
        self.hwdev=Entry(20,"")
        self.login=Entry(20,"")
        self.phoneno=Entry(20,"")
        self.password=Entry(20,"",password=1)
        self.initstring=Entry(20,"")
        if not modem:
            self.modem=None
            for dev in devicelist:
                if dev.Type=="Modem":
                    self.modem=dev
                    break
            if not self.modem:
                df = NCDeviceFactory.getDeviceFactory()        
                self.modem = df.getDeviceClass(MODEM)()
                i = self.devicelist.addDevice()
                self.devicelist[i] = self.modem
        else:
            self.modem=modem

    def setState(self,modem=None):
        """
        Set the default values of the fields
        according to the given device
        @modem The NCDevice (type modem) to use as default values
        """


        if modem:
            if modem.DeviceId:
                self.name.set(modem.DeviceId)
            if modem.Device:
                self.hwdev.set(modem.Device)
            if modem.Dialup.Login:
                self.login.set(modem.Dialup.Login)
            if modem.Dialup.Password:
                self.password.set(modem.Dialup.Password)
            if modem.Dialup.InitString:
                self.initstring.set(modem.Dialup.InitString)
            if modem.Dialup.PhoneNumber:
                self.phoneno.set(modem.Dialup.PhoneNumber)

    def processInfo(self):
        """
        Extracts info from the screen, and puts it into a device object
        """

        self.modem.DeviceId=self.name.value()
        self.modem.Device=self.hwdev.value()
        self.modem.Dialup.Login=self.login.value()
        self.modem.Dialup.Password=self.password.value()
        self.modem.Dialup.InitString=self.initstring.value()
        self.modem.Dialup.PhoneNumber=self.phoneno.value()

    
    def runIt(self):
        """
        Show and run the screen, save files if necesarry
        """
        g1=Grid(1,1)
        g2=Grid(2,6)
        g2.setField(Label (_("Name")),0,0,anchorLeft=1)
        g2.setField(Label (_("Device")),0,1,anchorLeft=1)
        g2.setField(Label (_("ISP Phonenumber")),0,2,anchorLeft=1)
        g2.setField(Label (_("ISP Login")),0,3,anchorLeft=1)
        g2.setField(Label (_("ISP Password")),0,4,anchorLeft=1)
        g2.setField(Label (_("Modem Initstring")),0,5,anchorLeft=1)
        g2.setField(self.name,1,0,(1,0,0,0))
        g2.setField(self.hwdev,1,1,(1,0,0,0))
        g2.setField(self.phoneno,1,2,(1,0,0,0),anchorLeft=1)
        g2.setField(self.login,1,3,(1,0,0,0))
        g2.setField(self.password,1,4,(1,0,0,0))
        g2.setField(self.initstring,1,5,(1,0,0,0))
        bb=ButtonBar(self.screen,((_("Ok"),"ok"),(_("Cancel"),"cancel")))
        tl=GridForm(screen,_("Modem Configuration"),1,3)
        tl.add(g1,0,0,(0,0,0,1),anchorLeft=1)
        tl.add(g2,0,1,(0,0,0,1))
        tl.add(bb,0,2,growx=1)
        self.setState(self.modem)
        while 1:
            res=tl.run()
            if bb.buttonPressed(res)=="cancel":
                screen.popWindow()
                break
            elif bb.buttonPressed(res)=="ok":
                self.processInfo()
                self.devicelist.save()
                screen.popWindow()
                break

#
# ISDNWindow class
#
class ISDNWindow:
    def __init__(self,screen,devicelist,isdn=None):
        """
        The constructor
        @screen A snack screen instance
        @devicelist A NCDeviceList
        @isdn The ISDN device. If none given, the first
               isdndevice in devicelist will be used.
               If none are there, one will be added.
        """

        self.devicelist=devicelist
        self.screen=screen
        self.name=Entry(20,"")
        self.hwdev=Entry(20,"")
        self.login=Entry(20,"")
        self.phoneno=Entry(20,"")
        self.password=Entry(20,"",password=1)
        self.msn=Entry(20,"")
        if not isdn:
            self.isdn=None
            for dev in devicelist:
                if dev.Type=="ISDN":
                    self.isdn=dev
                    break
            if not self.isdn:
                df = NCDeviceFactory.getDeviceFactory()        
                self.isdn = df.getDeviceClass(ISDN)()
                i = self.devicelist.addDevice()
                self.devicelist[i] = self.isdn
        else:
            self.isdn=isdn

    def setState(self,isdn=None):
        """
        Set the default values of the fields
        according to the given device
        @isdn The Device (type isdn) to use as default values
        """


        if isdn:
            if isdn.DeviceId:
                self.name.set(isdn.DeviceId)
            if isdn.Device:
                self.hwdev.set(isdn.Device)
            if isdn.Dialup.Login:
                self.login.set(isdn.Dialup.Login)
            if isdn.Dialup.Password:
                self.password.set(isdn.Dialup.Password)
            if isdn.Dialup.PhoneNumber:
                self.phoneno.set(isdn.Dialup.PhoneNumber)
            if isdn.Dialup.MSN:
                self.msn.set(isdn.Dialup.MSN)

    def processInfo(self):
        """
        Extracts info from the screen, and puts it into a device object
        """

        self.isdn.DeviceId=self.name.value()
        self.isdn.Device=self.hwdev.value()
        self.isdn.Dialup.Login=self.login.value()
        self.isdn.Dialup.Password=self.password.value()
        self.isdn.Dialup.PhoneNumber=self.phoneno.value()
        self.isdn.Dialup.MSN=self.msn.value()

    
    def runIt(self):
        """
        Show and run the screen, save files if necesarry
        """
        g1=Grid(1,1)
        g2=Grid(2,6)
        g2.setField(Label (_("Name")),0,0,anchorLeft=1)
        g2.setField(Label (_("Device")),0,1,anchorLeft=1)
        g2.setField(Label (_("ISP Phonenumber")),0,2,anchorLeft=1)
        g2.setField(Label (_("ISP Login")),0,3,anchorLeft=1)
        g2.setField(Label (_("ISP Password")),0,4,anchorLeft=1)
        g2.setField(Label (_("MSN")),0,5,anchorLeft=1)
        g2.setField(self.name,1,0,(1,0,0,0))
        g2.setField(self.hwdev,1,1,(1,0,0,0))
        g2.setField(self.phoneno,1,2,(1,0,0,0),anchorLeft=1)
        g2.setField(self.login,1,3,(1,0,0,0))
        g2.setField(self.password,1,4,(1,0,0,0))
        g2.setField(self.msn,1,5,(1,0,0,0))
        bb=ButtonBar(self.screen,((_("Ok"),"ok"),(_("Cancel"),"cancel")))
        tl=GridForm(screen,_("ISDN Configuration"),1,3)
        tl.add(g1,0,0,(0,0,0,1),anchorLeft=1)
        tl.add(g2,0,1,(0,0,0,1))
        tl.add(bb,0,2,growx=1)
        self.setState(self.isdn)
        while 1:
            res=tl.run()
            if bb.buttonPressed(res)=="cancel":
                screen.popWindow()
                break
            elif bb.buttonPressed(res)=="ok":
                self.processInfo()
                self.devicelist.save()
                screen.popWindow()
                break


                
#
# __main__
#
if __name__=="__main__":
    screen=SnackScreen()
    try:
        mainScreen(screen)
        screen.finish()
    except SystemExit, code:
        screen.finish()
        sys.exit(code)
    except:
        screen.finish()
        handleException(sys.exc_info(), PROGNAME, PRG_VERSION)

    screen.finish()
__author__ = "Trond Eivind Glomsrød <teg@redhat.com>, Harald Hoyer <harald@redhat.com>"
