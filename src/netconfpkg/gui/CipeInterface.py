## Copyright (C) 2001-2003 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
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

from netconfpkg.gui import GUI_functions
from netconfpkg.NC_functions import *
from netconfpkg.NC_functions import NETCONFDIR
from netconfpkg import *
from netconfpkg import *
from netconfpkg import *
from netconfpkg import *
from netconfpkg.gui import GUI_functions
from rhpl.executil import *
import gtk
from gtk import TRUE
from gtk import FALSE
import gtk.glade
import string
import os
import gtk.glade
from InterfaceCreator import InterfaceCreator
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect

from gtk import TRUE
from gtk import FALSE

class CipeInterface(InterfaceCreator):
    def __init__ (self, toplevel=None, connection_type=CIPE,
                  do_save = 1, druid = None):
        InterfaceCreator.__init__(self, do_save = do_save)
        self.do_save = do_save
        self.toplevel = toplevel
        self.druids = []
        self.device = NCDevCipe.DevCipe()
        self.device.Type = connection_type
        self.xml = None
        
    def init_gui(self):
        if self.xml:
            return
       
        if request_rpms(["cipe"]):
            return 
 
        glade_file = 'CipeInterfaceDruid.glade'

        if not os.path.isfile(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.isfile(glade_file):
            glade_file = NETCONFDIR + glade_file
            
        self.xml = gtk.glade.XML(glade_file, 'druid', GUI_functions.PROGNAME)
        
        xml_signal_autoconnect(self.xml,
            {
            "on_tunnel_setting_page_next" : self.on_tunnel_setting_page_next,
            "on_tunnel_setting_page_prepare" : self.on_tunnel_setting_page_prepare,
            "on_finish_page_finish" : self.on_finish_page_finish,
            "on_finish_page_prepare" : self.on_finish_page_prepare,
            "on_finish_page_back" : self.on_finish_page_back,
            "on_remotePeerAddressCB_toggled" : self.on_remotePeerAddressCB_toggled,
            "on_generateKeyButton_clicked" : self.on_generateKeyButton_clicked,
            "on_localPortEntry_changed" : self.updateRemoteOptions,
            "on_ethernetDeviceEntry_changed" : self.updateRemoteOptions,
            "on_cipeDeviceEntry_changed" : self.updateRemoteOptions,
            "on_remoteVirtualAddressEntry_changed" : self.updateRemoteOptions,
            "on_secretKeyEntry_changed" : self.updateRemoteOptions,
            "on_remotePeerAddressEntry_changed" : self.updateRemoteOptions,
            "on_localVirtualAddressEntry_changed" : self.updateRemoteOptions,
            })
        

        self.devicelist = NCDeviceList.getDeviceList()
        self.profilelist = NCProfileList.getProfileList()
        self.device.OnBoot = FALSE
        self.device.AllowUser = FALSE
        
        druid = self.xml.get_widget ('druid')
        for I in druid.get_children():
            druid.remove(I)
            self.druids.append(I)

    def get_project_name(self):
        return _('CIPE (VPN) connection')

    def get_project_description(self):
        return _("Create a new virtual private network connection with CIPE.")

    def get_type(self):
        return CIPE

    def get_druids(self):
        self.init_gui()
        
        return self.druids
            
    def on_tunnel_setting_page_prepare(self, druid_page, druid):
        self.device.createCipe()
        self.hydrate()

    def on_tunnel_setting_page_next(self, druid_page, druid):
        if self.check():
            self.dehydrate()
            return FALSE
        else:
            return TRUE
    
    def on_finish_page_finish(self, druid_page, druid):
        hardwarelist = NCHardwareList.getHardwareList()
        hardwarelist.commit()
        self.devicelist.append(self.device)
        self.device.commit()
        for prof in self.profilelist:
            if prof.Active == FALSE:
                continue
            prof.ActiveDevices.append(self.device.DeviceId)
            break
        
        self.profilelist.commit()
        self.devicelist.commit()
        self.save()
        self.toplevel.destroy()
        gtk.mainquit()
        
    def on_finish_page_back(self, druid_page, druid):
        self.devicelist.rollback()

    def on_finish_page_prepare(self, druid_page, druid):
        self.device.DeviceId = self.device.Device
        cipe = self.device.Cipe
        
        s = _("You have selected the following information:") + "\n\n" + "    "\
            + _("Device:") + " " + str(self.device.Device) + "\n" + "    "\
            + _("Tunnel through Device:") + " " + str(cipe.TunnelDevice) + "\n" + "    "\
            + _("Local Port:") + " " + str(cipe.LocalPort) + "\n" + "    "
        
        if not cipe.RemotePeerAddress \
               or cipe.RemotePeerAddress == "0.0.0.0" \
               or cipe.RemotePeerAddress == "" :
            s = s + _("Remote Peer Address:") + " " + _("Auto") + "\n" + "    "
        else:
            s = s + _("Remote Peer Address:") + " " + cipe.RemotePeerAddress + "\n" + "    "\
                + _("Remote Peer Port:") + " " + str(cipe.LocalPort) + "\n" + "    "
    
        s = s + _("Remote Virtual Address:") + " " + str(cipe.RemoteVirtualAddress) + "\n" + "    "
        s = s + _("Local Virtual Address:") + " " + str(self.device.IP)
        
        druid_page.set_text(s)
        
    def hydrate(self):
        cipe = self.device.Cipe
        ecombo = self.xml.get_widget("ethernetDeviceComboBox")

        curr = None
        desc = [_('None - Server Mode')];

        for dev in self.devicelist:
            if self.device.Device and dev.Device == self.device.Device:
                continue
            d = str(dev.Device)
            if not dev.IP or dev.IP == "":
                d = d + _(' (dynamic)')
            else:
                d = d + ' (' + str(dev.IP) + ')'
            desc.append(d)
            if cipe.TunnelDevice == dev.Device:
                curr = d

        if len(desc):
            ecombo.set_popdown_strings(desc)

        widget = self.xml.get_widget("ethernetDeviceEntry")
        if cipe.TunnelDevice and curr:
           widget.set_text(curr)
        #widget.set_position(0)

        if self.device.Device:
            self.xml.get_widget("cipeDeviceEntry").set_text(self.device.Device)
        else:
            nextdev = NCDeviceList.getNextDev("cipcb")
            self.xml.get_widget("cipeDeviceEntry").set_text(nextdev)
            
        if not cipe.LocalPort:
            cipe.LocalPort = 7777
            
        self.xml.get_widget("localPortEntry").set_text(str(cipe.LocalPort))

        if cipe.RemotePeerAddress:
            vals = string.split(cipe.RemotePeerAddress, ":")
            addr = vals[0]
            if len(vals) > 1:
                port = vals[1]
                self.xml.get_widget("remotePeerPortEntry").set_text(port)
            self.xml.get_widget("remotePeerAddressEntry").set_text(addr)

        if cipe.RemotePeerAddress == "0.0.0.0" \
           or cipe.RemotePeerAddress == "" \
           or not cipe.RemotePeerAddress:
            self.xml.get_widget("remotePeerAddressEntry").set_text(_("Server Mode"))
            self.xml.get_widget("remotePeerPortEntry").set_text("")
            self.xml.get_widget("remotePeerAddressEntry").set_sensitive(FALSE)
            self.xml.get_widget("remotePeerPortEntry").set_sensitive(FALSE)
            self.xml.get_widget("remotePeerAddressCB").set_active(TRUE)


        if cipe.RemoteVirtualAddress:
            self.xml.get_widget("remoteVirtualAddressEntry").set_text(self.device.Cipe.RemoteVirtualAddress)
        if self.device.IP: self.xml.get_widget("localVirtualAddressEntry").set_text(self.device.IP)

        widget = self.xml.get_widget("secretKeyEntry")
        
        if cipe.SecretKey:
            widget.set_text(self.device.Cipe.SecretKey)
        #else:
        #    self.on_generateKeyButton_clicked()
            
        #widget.set_position(0)

        self.updateRemoteOptions()

    def dehydrate(self):
        hw = self.xml.get_widget("ethernetDeviceEntry").get_text()
        if hw == _('None - Server Mode'):
            self.device.Cipe.TunnelDevice = None
            self.device.Cipe.TunnelIP = "0.0.0.0"
        else:
            fields = string.split(hw)
            hw = fields[0]
            self.device.Cipe.TunnelDevice = hw
            self.device.Cipe.TunnelIP = "0.0.0.0"
            devlist = NCDeviceList.getDeviceList()
            for dev in devlist:
                if dev.Device == hw and dev.IP:
                    self.device.Cipe.TunnelIP = dev.IP


        self.device.Device = self.xml.get_widget("cipeDeviceEntry").get_text()
        self.device.DeviceId = self.device.Device
        self.device.Cipe.LocalPort = int(self.xml.get_widget("localPortEntry").get_text())
        self.device.Cipe.RemoteVirtualAddress = self.xml.get_widget("remoteVirtualAddressEntry").get_text()
        self.device.IP = self.xml.get_widget("localVirtualAddressEntry").get_text()        
        self.device.Cipe.SecretKey = self.xml.get_widget("secretKeyEntry").get_text()

        if self.xml.get_widget("remotePeerAddressCB").get_active():
            self.device.Cipe.RemotePeerAddress = "0.0.0.0"
        else:
            self.device.Cipe.RemotePeerAddress = self.xml.get_widget("remotePeerAddressEntry").get_text() + ":" + self.xml.get_widget("remotePeerPortEntry").get_text()

    def on_remotePeerAddressCB_toggled(self, *args):
        if self.xml.get_widget("remotePeerAddressCB").get_active():
            self.xml.get_widget("remotePeerAddressEntry").set_sensitive(FALSE)
            self.xml.get_widget("remotePeerPortEntry").set_sensitive(FALSE)
            self.xml.get_widget("remotePeerAddressEntry").set_text(_("Server Mode"))
            self.xml.get_widget("remotePeerPortEntry").set_text("")
        else:
            self.xml.get_widget("remotePeerAddressEntry").set_sensitive(TRUE)
            self.xml.get_widget("remotePeerPortEntry").set_sensitive(TRUE)
            self.xml.get_widget("remotePeerAddressEntry").set_text("0.0.0.0")

        self.updateRemoteOptions()

    def on_generateKeyButton_clicked(self, *args):
        command = '/bin/sh'
        (status , key ) = gtkExecWithCaptureStatus(command = command,
                                                   argv = [command, '-c',
                                                           '(ps aux|md5sum; ps alx|md5sum) | tr -cd 0-9 2>/dev/null'])
        
        widget = self.xml.get_widget("secretKeyEntry")
        if key:
            widget.set_text(key)
        #widget.set_position(0)


    def updateRemoteOptions(self, *args):
        ethw = self.xml.get_widget("ethernetDeviceEntry").get_text()
        fields = string.split(ethw)
        ip = '0.0.0.0 (auto)'
        
        if len(fields):
            d = fields[0]
            for dev in self.devicelist:
                if dev.Device == d:
                    ip = dev.IP

        addr = self.xml.get_widget("remotePeerAddressEntry").get_text()
        port = self.xml.get_widget("remotePeerPortEntry").get_text()
        if not port or port == "":
            port = _("(own choice)")

        localport = self.xml.get_widget("localPortEntry").get_text()
        remotevirtualaddress = self.xml.get_widget("remoteVirtualAddressEntry").get_text()
        if addr == "0.0.0.0" or addr == "":
            addr = _("(own choice)")

        localvirtualaddress = self.xml.get_widget("localVirtualAddressEntry").get_text()

        secretkey = self.xml.get_widget("secretKeyEntry").get_text()
        mytxt = ""
        mytxt = mytxt + _("IP Address of Tunnel Device: ") + str(addr) + "\n"
        mytxt = mytxt + _("Local Port: ") + port + "\n"
        mytxt = mytxt + _("Remote Peer Address: ") + str(ip)
        if localport and localport != "":
            mytxt = mytxt + ":" + str(localport)
        mytxt = mytxt + "\n"
        mytxt = mytxt + _("Remote Virtual Address: ") + str(localvirtualaddress) + "\n"
        mytxt = mytxt + _("Local Virtual Address: ") + str(remotevirtualaddress) + "\n"
        mytxt = mytxt + _("Secret Key: ") + str(secretkey) + "\n"
        
        widget = self.xml.get_widget("remoteConfigTxt").get_buffer()
        widget.set_text(mytxt)
        #widget.set_position(0)

    def check(self):
        keywidget = self.xml.get_widget("secretKeyEntry")
        txt = keywidget.get_text()
        if not txt or txt == "":
            GUI_functions.gui_error_dialog(_("You must enter a secret key \n"
                                             "or generate one"),
                                           self.toplevel,
                                           broken_widget = keywidget)
            return FALSE
        return TRUE
            
NCDevCipe.setDevCipeWizard(CipeInterface)
