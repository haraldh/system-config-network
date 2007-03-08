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

from netconfpkg.NCDevice import *
from netconfpkg.NCDeviceFactory import getDeviceFactory
from netconfpkg.NC_functions import *

import netconfpkg

_devIsdnDialog = None
_devIsdnWizard = None

class DevIsdn(Device):    
   def __init__(self, list = None, parent = None):
      Device.__init__(self, list, parent)
      self.Type = ISDN
      self.Dialup = netconfpkg.NCDialup.IsdnDialup(None, self)
      
   def load(self, name):
      conf = ConfDevice(name)
      Device.load(self, name)
      self.Dialup.load(conf)
      
   def createDialup(self):      
      if (self.Dialup == None) \
             or not isinstance(self.Dialup, netconfpkg.NCDialup.IsdnDialup):
         self.Dialup = netconfpkg.NCDialup.IsdnDialup(None, self)
      return self.Dialup
   
   def getDialog(self):
      dialog = _devIsdnDialog(self)
      if hasattr(dialog, "xml"):
         return dialog.xml.get_widget("Dialog")

      return dialog      
    
   def getWizard(self):
      return _devIsdnWizard

   def isType(self, device):
      if device.Type == ISDN:
         return True
      if getDeviceType(device.Device) == ISDN:
         return True
      return False

   def getHWDevice(self):
      # XXX FIXME
      return "ISDN Card 0"

   def activate( self, dialog = None ):        
      command = '/bin/sh'
      param = [ command,
                "-c",
                "/sbin/ifup %s; /usr/sbin/userisdnctl %s dial" % \
                ( self.DeviceId, self.DeviceId ) ]

      try:
         (ret, msg) =  generic_run_dialog(\
             command,
             param,
             catchfd = (1,2),
             title = _('Network device activating...'),
             label = _('Activating network device %s, '
                       'please wait...') % (self.DeviceId),
             errlabel = _('Cannot activate '
                          'network device %s!\n') % (self.DeviceId),
             dialog = dialog)

      except RuntimeError, msg:
         ret = -1        

      return ret, msg

   def deactivate(self, dialog = None):        
      command = '/bin/sh'
      param = [ command,
                "-c",
                "/usr/sbin/userisdnctl %s hangup ;/sbin/ifdown %s;" % \
                ( self.DeviceId, self.DeviceId ) ]

      try:
         (ret, msg) =  generic_run_dialog(\
             command,
             param,
             catchfd = (1,2),
             title = _('Network device deactivating...'),
             label = _('Deactivating network device %s, '
                       'please wait...') % (self.DeviceId),
             errlabel = _('Cannot deactivate '
                          'network device %s!\n') % (self.DeviceId),
             dialog = dialog)

      except RuntimeError, msg:
         ret = -1        

      return ret, msg
   
def setDevIsdnDialog(dialog):
   global _devIsdnDialog
   _devIsdnDialog = dialog
   
def setDevIsdnWizard(wizard):
   global _devIsdnWizard
   _devIsdnWizard = wizard

df = getDeviceFactory()
df.register(DevIsdn, ISDN)
__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2007/03/08 12:56:42 $"
__version__ = "$Revision: 1.13 $"
