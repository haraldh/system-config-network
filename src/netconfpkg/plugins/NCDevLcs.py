"""Implementation of the lcs device
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
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from netconfpkg.NCDevice import Device, ConfDevice
from netconfpkg.NCDeviceFactory import getDeviceFactory
from netconfpkg.NC_functions import LCS, getDebugLevel
from netconfpkg.plugins.NCDevEthernet import DevEthernet
from netconfpkg.NCHardwareList import getHardwareList, HW_CONF
import os

_devLcsDialog = None
_devLcsWizard = None

class DevLcs(DevEthernet):
   def __init__(self, list = None, parent = None):
      DevEthernet.__init__(self, list, parent)
      self.Type = LCS

   def isType(self, device):
      """returns true of the device is of the same type as this class"""
      if device.Type == LCS:
         return true
      if getDeviceType(device.Device) == LCS:
         return true
      return false

   def load(self, name):
      Device.load(self, name)
      conf = ConfDevice(name)
      self.Type = LCS
      if conf.has_key("SUBCHANNELS"):
         hardwarelist = getHardwareList()
         hw = None
         for hw in hardwarelist:
            if hw.Name == self.Device and hw.Type == LCS:
               break
         else:
            i = hardwarelist.addHardware(LCS)
            hw = hardwarelist[i]
            hw.Status = HW_CONF
            hw.Name = self.Device
            hw.Type = LCS

         hw.Description = "lcs %s" % conf["SUBCHANNELS"]
         hw.createCard()
         hw.Card.ModuleName = "lcs"
         try:
            hw.MacAddress = conf["MACADDR"]
         except:
            pass

         try:
            ports = conf["SUBCHANNELS"].split(",")
            hw.Card.IoPort = ports[0]
            hw.Card.IoPort1 = ports[1]
            hw.Card.IoPort2 = ports[2]
            hw.Card.Options = conf["OPTIONS"]
         except:
            pass

         hw.commit(changed=False)
         hardwarelist.commit(changed=False)

   def save(self):
      Device.save(self)
      conf = ConfDevice( self.DeviceId )
      conf["TYPE"]="Ethernet"
      if not self.Alias:
         conf["NETTYPE"]="lcs"
         ports = ""
         hardwarelist = getHardwareList()
         for hw in hardwarelist:
            if hw.Name == self.Device:
               if hw.MacAddress:
                  conf["MACADDR"] = hw.MacAddress
               else:
                  del conf["MACADDR"]

               if (hw.Card.IoPort and hw.Card.IoPort1 and hw.Card.IoPort2):
                  ports = "%s,%s,%s" % (hw.Card.IoPort, hw.Card.IoPort1, hw.Card.IoPort2)
               break
         if ports:
            conf["SUBCHANNELS"] = ports
         if hw.Card.Options:
            conf["OPTIONS"] = hw.Card.Options
         else:
            if conf.has_key("OPTIONS"):
               del conf["OPTIONS"]

      conf.write()

   def getDialog(self):
      """get the lcs configuration dialog"""
      if not _devLcsDialog:
         return None
      dialog =  _devLcsDialog(self)
      if hasattr(dialog, "xml"):
         return dialog.xml.get_widget("Dialog")

      return dialog

   def getWizard(self):
      """get the wizard of the lcs wizard"""
      return _devLcsWizard

   def deactivate( self, dialog = None ):
      ret = DevEthernet.deactivate(self, dialog)
      if not self.Alias:
         hardwarelist = getHardwareList()
         for hw in hardwarelist:
            if hw.Name == self.Device and (hw.Card.IoPort and hw.Card.IoPort1 and hw.Card.IoPort2):
               os.system("echo 0 > /sys/bus/ccwgroup/drivers/lcs/%s/online; echo 1 > /sys/bus/ccwgroup/drivers/lcs/%s/ungroup" % (hw.Card.IoPort, hw.Card.IoPort))
               break

      return ret

   def activate( self, dialog = None ):
      """activate the lcs device"""
      if not self.Alias:
         hardwarelist = getHardwareList()
         for hw in hardwarelist:
            if hw.Name == self.Device and (hw.Card.IoPort and hw.Card.IoPort1 and hw.Card.IoPort2):
               os.system('SUBSYSTEM="ccw" DEVPATH="bus/ccwgroup/drivers/lcs/%s" /lib/udev/ccw_init' % hw.Card.IoPort)
               break

      return DevEthernet.activate(self, dialog)

def setDevLcsDialog(dialog):
   """Set the lcs dialog class"""
   global _devLcsDialog
   _devLcsDialog = dialog

def setDevLcsWizard(wizard):
   """Set the lcs wizard class"""
   global _devLcsWizard
   _devLcsWizard = wizard


import os
machine = os.uname()[4]
if machine == 's390' or machine == 's390x':
   _df = getDeviceFactory()
   _df.register(DevLcs, LCS)
   del _df


__author__ = "Harald Hoyer <harald@redhat.com>"
