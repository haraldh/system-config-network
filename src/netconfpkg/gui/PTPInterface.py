## Copyright (C) 2001-2003 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001-2003 Harald Hoyer <harald@redhat.com>
## Copyright (C) 2001, 2002 Philipp Knirsch <pknirsch@redhat.com>

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
from netconfpkg import *
from netconfpkg.gui import sharedtcpip
import gtk
from gtk import TRUE
from gtk import FALSE
import gtk.glade
import string
import os
#from PTPHardwareDruid import PTPHardware
from InterfaceCreator import InterfaceCreator
from rhpl import ethtool
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect
from netconfpkg.gui.EthernetInterface import EthernetInterface

class PTPInterface(EthernetInterface):
    def __init__(self, toplevel=None, connection_type=CTC, do_save = 1,
                 druid = None):
        EthernetInterface.__init__(self, toplevel,
                                   connection_type,
                                   do_save, druid)

    def init_gui(self):
        class dummy:
            def __init__(self):
                self.druids = []
                
        if self.xml:
            return
        
        glade_file = 'PTPInterfaceDruid.glade'

        if not os.path.exists(glade_file):
            glade_file = GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, 'druid', domain=PROGNAME)
        xml_signal_autoconnect(self.xml,
            { "on_hostname_config_page_back" : \
              self.on_hostname_config_page_back,
              "on_hostname_config_page_next" : \
              self.on_hostname_config_page_next,
              "on_hostname_config_page_prepare" : \
              self.on_hostname_config_page_prepare,
              "on_hw_config_page_back" : self.on_hw_config_page_back,
              "on_hw_config_page_next" : self.on_hw_config_page_next,
              "on_hw_config_page_prepare" : self.on_hw_config_page_prepare,
              "on_finish_page_finish" : self.on_finish_page_finish,
              "on_finish_page_prepare" : self.on_finish_page_prepare,
              "on_finish_page_back" : self.on_finish_page_back
              }
            )

        #print "EthernetInterface getDeviceList"
        self.devicelist = getDeviceList()
        df = getDeviceFactory()
        devclass = df.getDeviceClass(self.connection_type)
        if devclass:
            self.device = devclass()
        else:
            self.device = NCDevEthernet.DevEthernet()
            
        self.device.Type = self.connection_type
        self.device.OnBoot = TRUE
        self.device.AllowUser = FALSE
        self.device.IPv6Init = FALSE
        self.profilelist = NCProfileList.getProfileList()

        self.hw_sel = 0
        self.hwPage = FALSE

        self.druids = []
        self.druid = self.xml.get_widget('druid')
        for i in self.druid.get_children():
            self.druid.remove(i)
            self.druids.append(i)

        self.hwDruid = dummy()
#XXX        self.hwDruid = PTPHardware(self.toplevel)
#XXX        self.druids = [self.druids[0]] + self.hwDruid.druids[:]\
#XXX                      + self.druids[1:]

    def get_project_name(self):
        pass

    def get_type(self):
        pass
 
    def get_project_description(self):
        pass

    def on_hostname_config_page_back(self, druid_page, druid):
        childs = self.topdruid.get_children()
        self.topdruid.set_page(childs[1])            
        return TRUE
    
    def on_hostname_config_page_next(self, druid_page, druid):
        self.device.IP = self.xml.get_widget('ipAddressEntry').get_text()
        self.device.Gateway = self.xml.get_widget('ipGatewayEntry').get_text()
        try:
            self.device.Mtu = int(self.xml.get_widget('mtuEntry').get_text())
        except:            
            self.device.Mtu = 9216
        pass
    
    def on_hostname_config_page_prepare(self, druid_page, druid):
        if self.device.IP:
            self.xml.get_widget('ipAddressEntry').set_text(self.device.IP)
        else:
            self.xml.get_widget('ipAddressEntry').set_text('')

        if self.device.Gateway:
            self.xml.get_widget('ipGatewayEntry').set_text(self.device.Gateway)
        else:
            self.xml.get_widget('ipGatewayEntry').set_text('')

        if not self.device.Mtu:
            self.device.Mtu = 9216
        self.xml.get_widget('mtuEntry').set_text(str(self.device.Mtu))

        self.device.BootProto = 'static'
        pass
    
    def on_hw_config_page_back(self, druid_page, druid):
        pass
    
    def on_hw_config_page_next(self, druid_page, druid):
        clist = self.xml.get_widget("hardwareList")
        childs = self.topdruid.get_children()

        if not len(clist.selection):
            self.topdruid.set_page(childs[1])
            return TRUE

        self.hw_sel = clist.selection[0]
        
#XXX        if (self.hw_sel + 1) == clist.rows:
        if None:
            self.hwPage = TRUE
            self.topdruid.set_page(childs[len(self.hwDruid.druids)+1])
        else:
            self.hwPage = FALSE
            self.device.Device = self.devlist[clist.selection[0]]
            
            self.device.Alias = self.getNextAlias(self.device)
            # must be at bottom, because prepare is called here
            self.topdruid.set_page(childs[len(self.hwDruid.druids)+2])
        return TRUE

    def on_hw_config_page_prepare(self, druid_page, druid):
        hardwarelist = getHardwareList()
        hardwarelist.updateFromSystem()

        clist = self.xml.get_widget("hardwareList")
        clist.clear()
        self.devlist = []
        for hw in hardwarelist:
            if hw.Type == self.connection_type:
                desc = hw.Description + " (" + hw.Name + ")"
                clist.append([desc])
                self.devlist.append(hw.Name)
                
#XXX        clist.append([_("Other PTP Card")])
        clist.select_row (self.hw_sel, 0)
        pass
    
    def on_finish_page_back(self,druid_page, druid):
        pass
        
    def on_finish_page_prepare(self, druid_page, druid):
        self.device.DeviceId = self.device.Device
        if self.device.Alias:
            self.device.DeviceId = self.device.DeviceId + ":" \
                                   + str(self.device.Alias)

        try: hwaddr = ethtool.get_hwaddr(self.device.Device) 
        except IOError, err:
            pass
        else:
            self.device.HardwareAddress = hwaddr

        s = _("You have selected the following information:") + "\n\n" + "   "\
            + _("Device:") + " " + str(self.device.DeviceId) + " "

        hardwarelist = getHardwareList()
        for hw in hardwarelist:
            if hw.Name == self.device.Device:
                s = s + "(" + hw.Description + ")"
                break

        s = s + "\n" + "   "
        
        s = s + _("Address:") + " " + self.device.IP + "\n" + "   "\
            + _("Point to Point (IP):") + " " + self.device.Gateway + "\n" + "   "

        druid_page.set_text(s)
        
    def on_finish_page_finish(self, druid_page, druid):
        hardwarelist = getHardwareList()
        hardwarelist.commit()
        #print self.devicelist
        self.devicelist.append(self.device)
        self.device.commit()
        
        for prof in self.profilelist:
            if prof.Active == FALSE:
                continue
            prof.ActiveDevices.append(self.device.DeviceId)
            break

        self.profilelist.commit()
        self.devicelist.commit()

        self.toplevel.destroy()
        gtk.mainquit()

__author__ = "Harald Hoyer <harald@redhat.com>"


