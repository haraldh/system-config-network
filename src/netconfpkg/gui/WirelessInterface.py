## Copyright (C) 2001, 2002 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001, 2002 Harald Hoyer <harald@redhat.com>
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
from EthernetHardwareDruid import ethernetHardware
from InterfaceCreator import InterfaceCreator
from rhpl import ethtool

class WirelessInterface(InterfaceCreator):
    def __init__(self, toplevel=None, connection_type=WIRELESS, do_save = 1,
                 druid = None):
        InterfaceCreator.__init__(self, do_save = do_save)
        self.toplevel = toplevel
        self.topdruid = druid

        glade_file = "sharedtcpip.glade"
        if not os.path.exists(glade_file):
            glade_file = GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = NETCONFDIR + glade_file
        self.sharedtcpip_xml = gtk.glade.XML(glade_file, None,
                                                 domain=PROGNAME)

        glade_file = 'WirelessInterfaceDruid.glade'

        if not os.path.exists(glade_file):
            glade_file = GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, 'druid', domain=PROGNAME)
        self.xml.signal_autoconnect(
            { "on_hostname_config_page_back" : self.on_hostname_config_page_back,
              "on_hostname_config_page_next" : self.on_hostname_config_page_next,
              "on_hostname_config_page_prepare" : self.on_hostname_config_page_prepare,
              "on_wireless_config_page_back" : self.on_wireless_config_page_back,
              "on_wireless_config_page_next" : self.on_wireless_config_page_next,
              "on_wireless_config_page_prepare" : self.on_wireless_config_page_prepare,
              "on_hw_config_page_back" : self.on_hw_config_page_back,
              "on_hw_config_page_next" : self.on_hw_config_page_next,
              "on_hw_config_page_prepare" : self.on_hw_config_page_prepare,
              "on_finish_page_finish" : self.on_finish_page_finish,
              "on_finish_page_prepare" : self.on_finish_page_prepare,
              "on_finish_page_back" : self.on_finish_page_back,
              "on_essidAutoButton_toggled" : self.on_essidAutoButton_toggled,
              }
            )


        self.devicelist = NCDeviceList.getDeviceList()
        self.device = NCDevice.Device()
        self.device.Type = connection_type
        self.device.OnBoot = FALSE
        self.device.AllowUser = FALSE

        self.profilelist = NCProfileList.getProfileList()
        self.toplevel = toplevel
        self.connection_type = connection_type
        self.hw_sel = 0
        self.hwPage = FALSE

        window = self.sharedtcpip_xml.get_widget ('dhcpWindow')
        frame = self.sharedtcpip_xml.get_widget ('dhcpFrame')
        vbox = self.xml.get_widget ('generalVbox')
        window.remove (frame)
        vbox.pack_start (frame)
        sharedtcpip.dhcp_init (self.sharedtcpip_xml, self.device)

        self.druids = []
        self.druid = self.xml.get_widget('druid')
        for i in self.druid.get_children():
            self.druid.remove(i)
            self.druids.append(i)

        self.hwDruid = ethernetHardware(self.toplevel)
        self.hwDruid.has_ethernet = None
        self.druids = [self.druids[0]] + self.hwDruid.druids[:]\
                      + self.druids[1:]

    def get_project_name(self):
        return _('Wireless connection')

    def get_type(self):
        return WIRELESS

    def get_project_description(self):
        return _("Create a new wireless connection.")

    def get_druids(self):
        return self.druids
    
    def on_hostname_config_page_back(self, druid_page, druid):
        pass
    
    def on_hostname_config_page_next(self, druid_page, druid):
        sharedtcpip.dhcp_dehydrate (self.sharedtcpip_xml, self.device)
        if self.hwPage:
            self.device.Device = self.hwDruid.hw.Name
            self.device.Alias = None
        self.device.Hostname = self.xml.get_widget("hostnameEntry").get_text()
        pass
    
    def on_hostname_config_page_prepare(self, druid_page, druid):
        sharedtcpip.dhcp_hydrate (self.sharedtcpip_xml, self.device)
        pass

    def on_wireless_config_page_back(self, druid_page, druid):
        childs = self.topdruid.get_children()
        if self.hwPage:
            self.topdruid.set_page(childs[2])
        else:
            self.topdruid.set_page(childs[1])            
        return TRUE

    def on_wireless_config_page_next(self, druid_page, druid):
        self.device.createWireless()
        wl = self.device.Wireless

        if self.xml.get_widget("essidAutoButton").get_active():
            wl.EssId = ""
        else:
            wl.EssId = self.xml.get_widget("essidEntry").get_text()
        wl.Mode =  self.xml.get_widget("modeEntry").get_text()            
            
        wl.Channel = str(self.xml.get_widget("channelSpinButton").get_value_as_int())
        wl.Rate = self.xml.get_widget("rateEntry").get_text()
        wl.Key = self.xml.get_widget("keyEntry").get_text()

    def on_wireless_config_page_prepare(self, druid_page, druid):
        self.on_essidAutoButton_toggled(self.xml.get_widget("essidAutoButton"))
        self.xml.get_widget("modeEntry").connect("changed",
                                                 self.on_modeChanged)

    def on_modeChanged(self, entry):
        if string.lower(entry.get_text()) == "managed":
            self.xml.get_widget("channelSpinButton").set_sensitive(FALSE)
            self.xml.get_widget("rateCombo").set_sensitive(FALSE)
            self.xml.get_widget("rateEntry").set_sensitive(FALSE)
        else:
            self.xml.get_widget("channelSpinButton").set_sensitive(TRUE)
            self.xml.get_widget("rateCombo").set_sensitive(TRUE)
            self.xml.get_widget("rateEntry").set_sensitive(TRUE)
        self.on_essidAutoButton_toggled(self.xml.get_widget("essidAutoButton"))

    def on_essidAutoButton_toggled(self, check):
        self.xml.get_widget("essidEntry").set_sensitive(not check.get_active())

    def on_hw_config_page_back(self, druid_page, druid):
        pass
    
    def on_hw_config_page_next(self, druid_page, druid):
        clist = self.xml.get_widget("hardwareList")
        self.hw_sel = clist.selection[0]
        childs = self.topdruid.get_children()
        
        if (self.hw_sel + 1) == clist.rows:
            self.hwPage = TRUE
            self.topdruid.set_page(childs[2])
        else:
            self.hwPage = FALSE
            self.topdruid.set_page(childs[3])
            self.device.Device = self.devlist[clist.selection[0]]
            alias = None
            for dev in self.devicelist:
                if not dev.Device == self.device.Device:
                    continue
                if dev.Alias:
                    if not alias:
                        alias = dev.Alias
                    elif alias <= dev.Alias:
                        alias = dev.Alias + 1
                else: alias = 1
            self.device.Alias = alias
        return TRUE

    def on_hw_config_page_prepare(self, druid_page, druid):
        hardwarelist = NCHardwareList.getHardwareList()
        hardwarelist.updateFromSystem()

        clist = self.xml.get_widget("hardwareList")
        clist.clear()
        self.devlist = []
        for hw in hardwarelist:
            if hw.Type == ETHERNET:
                desc = hw.Description + " (" + hw.Name + ")"
                clist.append([desc])
                self.devlist.append(hw.Name)
                
        clist.append([_("Other Wireless Card")])
        clist.select_row (self.hw_sel, 0)
    
    def on_finish_page_back(self,druid_page, druid):
        pass
        
    def on_finish_page_prepare(self, druid_page, druid):
        self.device.DeviceId = self.device.Device
        wl = self.device.Wireless

        if self.device.Alias:
            self.device.DeviceId = self.device.DeviceId + ":" \
                                   + str(self.device.Alias)

        try: hwaddr = ethtool.get_hwaddr(self.device.Device) 
        except IOError, err:
            pass
        else:
            self.device.HardwareAddress = hwaddr

        s = _("You have selected the following information:") + "\n\n"\
            + _("Device:") + " " + str(self.device.DeviceId) + " "

        hardwarelist = NCHardwareList.getHardwareList()
        for hw in hardwarelist:
            if hw.Name == self.device.Device:
                s = s + "(" + hw.Description + ")"
                break

        s = s + "\n"

        if self.device.BootProto == "static":
            s = s + _("Address:") + " " + self.device.IP + "\n"\
            + _("Subnet Mask:") + " " + self.device.Netmask + "\n"\
            + _("Default Gateway Address:") + " " + self.device.Gateway + "\n"
        else:
            s = s + _("Automatically obtain IP address settings with:") + " "\
                + self.device.BootProto + "\n" 

        s = s + _("Mode: ") + str(wl.Mode) + "\n"
        s = s + _("ESSID (Network ID):") + " "
        if not wl.EssId:
            s = s + "Automatic\n"
        else:
            s = s + str(wl.EssId) + "\n"
        if wl.Mode != "Managed":
            s = s + _("Channel: ") + str(wl.Channel) + "\n"
        s = s + _("Transmit Rate: ") + str(wl.Rate) + "\n"\
            + _("Key: ")

        
        if wl.Key:
            s = s + str(wl.Key) + "\n"
        else:
            s = s + "encryption disabled\n"

        druid_page.set_text(s)
        
    def on_finish_page_finish(self, druid_page, druid):
        hardwarelist = NCHardwareList.getHardwareList()
        hardwarelist.commit()
        i = self.devicelist.addDevice()
        self.devicelist[i].apply(self.device)
        self.devicelist[i].commit()
        for prof in self.profilelist:
            if prof.Active == FALSE:
                continue
            prof.ActiveDevices.append(self.device.DeviceId)
            break
        self.profilelist.commit()
        self.devicelist.commit()
        
        self.toplevel.destroy()
        gtk.mainquit()
