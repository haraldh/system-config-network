"""Implementation of the qeth device
"""
## Copyright (C) 2001-2005 Red Hat, Inc.
## Copyright (C) 2001-2005 Harald Hoyer <harald@redhat.com>

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

from netconfpkg.NCDevice import Device, ConfDevice
from netconfpkg.NCDeviceFactory import getDeviceFactory
from netconfpkg.NC_functions import QETH, getDebugLevel
from netconfpkg.plugins.NCDevEthernet import DevEthernet
from netconfpkg.NCHardwareList import getHardwareList, HW_CONF

_devQethDialog = None
_devQethWizard = None

class DevQeth(DevEthernet):  
   def __init__(self, list = None, parent = None):
      DevEthernet.__init__(self, list, parent)
      self.Type = QETH
       
   def isType(self, device):
      """returns true of the device is of the same type as this class"""
      if device.Type == QETH:
         return true
      if getDeviceType(device.Device) == QETH:
         return true
      return false

   def load(self, name):
      Device.load(self, name)
      conf = ConfDevice(name)
      self.Type = QETH
      if conf.has_key("SUBCHANNELS"):         
         hardwarelist = getHardwareList()
         hw = None
         for hw in hardwarelist:
            if hw.Name == self.Device and hw.Type == QETH:
               break
         else:
            i = hardwarelist.addHardware(QETH)
            hw = hardwarelist[i]
            hw.Status = HW_CONF
            hw.Name = self.Device
            hw.Type = QETH

         hw.Description = "qeth %s" % conf["SUBCHANNELS"]
         hw.createCard()
         hw.Card.ModuleName = "qeth"
         try:
            ports = conf["SUBCHANNELS"].split(",")
            hw.Card.IoPort = ports[0]
            hw.Card.IoPort1 = ports[1]
            hw.Card.IoPort2 = ports[2]
         except:
            pass

         hw.commit(changed=False)
         hardwarelist.commit(changed=False)
         
   def save(self):
      Device.save(self)
      conf = ConfDevice( self.DeviceId )
      conf["TYPE"]="Ethernet"
      if not self.Alias:
         conf["NETTYPE"]="qeth"
         ports = ""
         hardwarelist = getHardwareList()
         for hw in hardwarelist:
            if hw.Name == self.Device and (hw.Card.IoPort and hw.Card.IoPort1 and hw.Card.IoPort2):
               ports = "%s,%s,%s" % (hw.Card.IoPort, hw.Card.IoPort1, hw.Card.IoPort2)
               break
         if ports:
            conf["SUBCHANNELS"] = ports
         
      conf.write()

   def getDialog(self):
      """get the ctc configuration dialog"""
      if not _devQethDialog:
         return None
      dialog =  _devQethDialog(self)
      if hasattr(dialog, "xml"):
         return dialog.xml.get_widget("Dialog")

      return dialog
    
   def getWizard(self):
      """get the wizard of the ctc wizard"""
      return _devQethWizard

def setDevQethDialog(dialog):
   """Set the ctc dialog class"""
   global _devQethDialog
   _devQethDialog = dialog

def setDevQethWizard(wizard):
   """Set the ctc wizard class"""
   global _devQethWizard
   _devQethWizard = wizard


import os
machine = os.uname()[4]
if machine == 's390' or machine == 's390x':
   _df = getDeviceFactory()
   _df.register(DevQeth, QETH)
   del _df


__author__ = "Harald Hoyer <harald@redhat.com>"