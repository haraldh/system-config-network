## Copyright (C) 2001 Red Hat, Inc.
## Copyright (C) 2001 Than Ngo <than@redhat.com>
## Copyright (C) 2001 Harald Hoyer <harald@redhat.com>
## Copyright (C) 2001 Philipp Knirsch <pknirsch@redhat.com>

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

import NC_functions
from NC_functions import _
import HardwareList
import NCisdnhardware
import NCDeviceList
import NCDevice
import NCProfileList
#import gnome.ui
import gtk
from gtk import TRUE
from gtk import FALSE
import libglade
import string
import os
from EthernetHardwareDruid import ethernetHardware
from InterfaceCreator import InterfaceCreator

class ADSLInterface(InterfaceCreator):
    def __init__(self, toplevel=None, connection_type='Ethernet'):
        self.toplevel = toplevel

        glade_file = 'ADSLInterfaceDruid.glade'

        if not os.path.exists(glade_file):
            glade_file = "netconfpkg/" + glade_file
        if not os.path.exists(glade_file):
            glade_file = NC_functions.NETCONFDIR + glade_file

        self.xml = libglade.GladeXML(glade_file, 'druid')
        self.xml.signal_autoconnect(
            { "on_dsl_config_page_back" : self.on_dsl_config_page_back,
              "on_dsl_config_page_next" : self.on_dsl_config_page_next,
              "on_dsl_config_page_prepare" : self.on_dsl_config_page_prepare,
              "on_finish_page_finish" : self.on_finish_page_finish,
              "on_finish_page_prepare" : self.on_finish_page_prepare,
              "on_finish_page_back" : self.on_finish_page_back
              }
            )

        self.devicelist = NCDeviceList.getDeviceList()
        self.device = NCDevice.Device()
        self.profilelist = NCProfileList.getProfileList()
        self.toplevel = toplevel
        self.connection_type = connection_type
        self.druids = []
        
        self.druid = self.xml.get_widget('druid')
        for i in self.druid.children():
            self.druid.remove(i)
            self.druids.append(i)

    def get_project_name(self):
        return _('xDSL connection')

    def get_project_description(self):
        return _('Create a new xDSL connection.  The xDSL connection is used primarily for connecting to an ISP over a ethernet.')

    def get_druids(self):
        hwDruid = ethernetHardware(self.toplevel)
        druid = hwDruid.get_druids()
        if druid: return druid + self.druids[0:]
        else: return self.druids[0:]

    def on_dsl_config_page_back(self, druid_page, druid):
        pass
    
    def on_dsl_config_page_next(self, druid_page, druid):
        if self.check():
            self.dehydrate()
            return FALSE
        else:
            return TRUE

    def on_dsl_config_page_prepare(self, druid_page, druid):
        self.hydrate()
        
    def on_finish_page_back(self,druid_page, druid):
        self.devicelist.rollback()
        
    def on_finish_page_prepare(self, druid_page, druid):
        hardwarelist = HardwareList.getHardwareList()
        for hw in hardwarelist:
            if hw.Type == self.connection_type:
                break

        dialup = self.device.Dialup
        s = _("You have selected the following information:") + "\n\n" + "    " + \
            _("Ethernet Device:") + "  " + dialup.EthDevice + "\n" + "    " + \
            _("Provider Name:") + "  " + dialup.ProviderName + "\n" +  "    " + \
            _("Login Name:") + "  " + dialup.Login + "\n\n\n" +  "    " + \
            _("Press \"Finish\" to create this account")
        
        druid_page.set_text(s)
        
    def on_finish_page_finish(self, druid_page, druid):
        hardwarelist = HardwareList.getHardwareList()
        hardwarelist.commit()
        i = self.devicelist.addDevice()
        self.devicelist[i].apply(self.device)
        self.devicelist[i].commit()
        for prof in self.profilelist:
            if prof.Active == FALSE:
                continue
            prof.ActiveDevices.append(self.device.DeviceId)
            break

        self.save()
        self.toplevel.destroy()
        gtk.mainquit()

    def check(self):
        return (len(string.strip(self.xml.get_widget("providerNameEntry").get_text())) >0 \
           and len(string.strip(self.xml.get_widget("loginNameEntry").get_text())) >0 \
           and len(string.strip(self.xml.get_widget("passwordEntry").get_text())) >0 \
           and len(string.strip(self.xml.get_widget("ethernetDeviceEntry").get_text())) >0)
    
    def hydrate(self):
        dialup = self.device.Dialup
        ecombo = self.xml.get_widget("ethernetDeviceComboBox")
 
        hwdesc = []
        hwcurr = None
        hardwarelist = HardwareList.getHardwareList()
        for hw in hardwarelist:
            if hw.Type == "Ethernet":
                desc = str(hw.Name) + ' (' + hw.Description + ')'
                hwdesc.append(desc)
                if dialup and dialup.EthDevice and \
                   hw.Name == dialup.EthDevice:
                    hwcurr = desc

        if len(hwdesc):
            hwdesc.sort()
            ecombo.set_popdown_strings(hwdesc)
 
        if not hwcurr and len(hwdesc):
            hwcurr = hwdesc[0]
 
        widget = self.xml.get_widget("ethernetDeviceEntry")
        if dialup and dialup.EthDevice:
            widget.set_text(hwcurr)
        widget.set_position(0)
 
    def dehydrate(self):
        self.device.DeviceId = self.xml.get_widget('providerNameEntry').get_text()
        self.device.Type = 'xDSL'
        self.device.BootProto = 'DIALUP'
        self.device.AllowUser = TRUE
        self.device.AutoDNS = TRUE
        dialup = self.device.createDialup()
        hw = self.xml.get_widget("ethernetDeviceEntry").get_text()
        fields = string.split(hw)
        hw = fields[0]
        dialup.EthDevice = hw
        dialup.ProviderName = self.xml.get_widget("providerNameEntry").get_text()
        dialup.Login = self.xml.get_widget("loginNameEntry").get_text()
        dialup.Password = self.xml.get_widget("passwordEntry").get_text()
        dialup.SyncPPP = FALSE
        self.device.Device = "dsl"
        dialup.DefRoute = TRUE
        dialup.PeerDNS = TRUE


