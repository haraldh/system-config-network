"""Implementation of the generic ethernet device
"""
## Copyright (C) 2001-2003 Red Hat, Inc.
## Copyright (C) 2001-2003 Harald Hoyer <harald@redhat.com>

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

from netconfpkg.NCDevice import Device
from netconfpkg.NCDeviceFactory import getDeviceFactory
from netconfpkg.NC_functions import ETHERNET

_devEthernetDialog = None
_devEthernetWizard = None

class DevEthernet(Device):
   """An object of class DevEthernet can be obtained by calling:
   
   df = getDeviceFactory()
   ethernetclass = df.getDeviceClass(ETHERNET)
   ethernetdevice = ethernetclass()

   It has the following attributes, shown here with the corresponding
   initscripts variables:
   
   Device          - DEVICE=<name of physical device (except
                     dynamically-allocated PPP devices where it
                     is the "logical name")>
   IP              - IPADDR
   Netmask         - NETMASK
   Gateway         - GATEWAY
   Hostname        - HOSTNAME - Hint for DHCP
   BootProto       - BOOTPROTO=none|bootp|dhcp
   Type            - TYPE=ETHERNET
   HardwareAddress - HWADDR=<MAC Address>
   OnBoot          - ONBOOT=yes|no
   AllowUser       - USERCTL=yes|no
   AutoDNS         - PEERDNS=yes|no - modify /etc/resolv.conf if peer uses
                     msdns extension (PPP only) or DNS{1,2} are set, or if
                     using pump or dhcpcd. default to "yes"."""
   
   def __init__(self, list = None, parent = None):
      Device.__init__(self, list, parent)
      self.Type = ETHERNET
       
   def getDialog(self):
      """get the gtk.Dialog of the ethernet configuration dialog"""
      return _devEthernetDialog(self).xml.get_widget("Dialog")
    
   def getWizard(self):
      """get the wizard of the ethernet wizard"""
      return _devEthernetWizard

   def isType(self, device):
      """returns true of the device is of the same type as this class"""
      if device.Type == ETHERNET:
         return true
      if getDeviceType(device.Device) == ETHERNET:
         return true
      return false

def setDevEthernetDialog(dialog):
   """Set the ethernet dialog class"""
   global _devEthernetDialog
   _devEthernetDialog = dialog

def setDevEthernetWizard(wizard):
   """Set the ethernet wizard class"""
   global _devEthernetWizard
   _devEthernetWizard = wizard

_df = getDeviceFactory()
_df.register(DevEthernet, ETHERNET)

del _df
__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2003/07/08 09:45:48 $"
__version__ = "$Revision: 1.6 $"
