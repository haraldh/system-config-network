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

from netconfpkg.gui.GUI_functions import *
from netconfpkg.NC_functions import _
from netconfpkg import NCHardwareList
from netconfpkg import NCisdnhardware
from netconfpkg import NCDeviceList
from netconfpkg import NCDevice
from netconfpkg import NCProfileList
#import gnome.ui
import gtk
from gtk import TRUE
from gtk import FALSE
import libglade
import string
import os
from EthernetHardwareDruid import ethernetHardware
from InterfaceCreator import InterfaceCreator

class EthernetInterface(InterfaceCreator):
    def __init__(self, toplevel=None, connection_type='Ethernet'):
        self.toplevel = toplevel

        glade_file = 'EthernetInterfaceDruid.glade'

        if not os.path.exists(glade_file):
            glade_file = GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = NETCONFDIR + glade_file

        self.xml = libglade.GladeXML(glade_file, 'druid', domain=PROGNAME)
        self.xml.signal_autoconnect(
            { "on_hostname_config_page_back" : self.on_hostname_config_page_back,
              "on_hostname_config_page_next" : self.on_hostname_config_page_next,
              "on_hostname_config_page_prepare" : self.on_hostname_config_page_prepare,
              "on_hw_config_page_back" : self.on_hw_config_page_back,
              "on_hw_config_page_next" : self.on_hw_config_page_next,
              "on_hw_config_page_prepare" : self.on_hw_config_page_prepare,
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
        return _('ethernet connection')

    def get_project_description(self):
        return _("Create an ethernet connection.")

    def get_druids(self):
        hwDruid = ethernetHardware(self.toplevel)
        hwDruid.has_ethernet = None
        return [self.druids[0]] + hwDruid.druids[:] + self.druids[1:]

    def on_hostname_config_page_back(self, druid_page, druid):
        pass
    
    def on_hostname_config_page_next(self, druid_page, druid):
        pass
    
    def on_hostname_config_page_prepare(self, druid_page, druid):
        pass
    
    def on_hw_config_page_back(self, druid_page, druid):
        pass
    
    def on_hw_config_page_next(self, druid_page, druid):
        pass

    def on_hw_config_page_prepare(self, druid_page, druid):
        hardwarelist = NCHardwareList.getHardwareList()

        clist = self.xml.get_widget("hardwareList")
        clist.clear()
        for hw in hardwarelist:
            if hw.Type == ETHERNET:
                clist.append([hw.Description + " (" + hw.Name + ")"])

        clist.append([_("Other Ethernet Card")])

    def on_finish_page_back(self,druid_page, druid):
        pass
        
    def on_finish_page_prepare(self, druid_page, druid):
        s = _("You have selected the following information:") + "\n\n"        
        druid_page.set_text(s)
        
    def on_finish_page_finish(self, druid_page, druid):
        self.toplevel.destroy()
        gtk.mainquit()
