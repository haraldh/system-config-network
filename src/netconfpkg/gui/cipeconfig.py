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

import gtk
import GDK
import GTK
import libglade
import signal
import os
import GdkImlib
import string
import gettext
import string
import commands
import sharedtcpip

from netconfpkg import NCDeviceList
from netconfpkg import NCHardwareList
from netconfpkg.gui import GUI_functions
from deviceconfig import deviceConfigDialog

from gtk import TRUE
from gtk import FALSE

##
## I18N
##
gettext.bindtextdomain(GUI_functions.PROGNAME, "/usr/share/locale")
gettext.textdomain(GUI_functions.PROGNAME)
_=gettext.gettext

class cipeConfigDialog(deviceConfigDialog):
    def __init__(self, device):
        glade_file = "sharedtcpip.glade"
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.NETCONFDIR + glade_file
        self.sharedtcpip_xml = libglade.GladeXML (glade_file, None,
                                                  domain=GUI_functions.PROGNAME)
        
        glade_file = "cipeconfig.glade"
        
        deviceConfigDialog.__init__(self, glade_file,
                                    device)    
        self.xml.signal_autoconnect(
            {
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

        window = self.sharedtcpip_xml.get_widget ('routeWindow')
        frame = self.sharedtcpip_xml.get_widget ('routeFrame')
        vbox = self.xml.get_widget ('routeVbox')
        window.remove (frame)
        vbox.pack_start (frame)
        sharedtcpip.route_init (self.sharedtcpip_xml, self.device)
        
    def hydrate(self):
        deviceConfigDialog.hydrate(self)
        ecombo = self.xml.get_widget("ethernetDeviceComboBox")

        curr = None
        desc = [_('None - Server Mode')];
        
        devlist = NCDeviceList.getDeviceList()
        for dev in devlist:
            d = str(dev.Device)
            if not dev.IP or dev.IP == "":
                d = d + _(' (dynamic)')
            else:
                d = d + ' (' + str(dev.IP) + ')'
            desc.append(d)
            if self.device.Cipe.TunnelDevice == dev.Device:
                curr = d
                            
        if len(desc):
            ecombo.set_popdown_strings(desc)

        widget = self.xml.get_widget("ethernetDeviceEntry")
        if self.device.Cipe.TunnelDevice and curr:
            widget.set_text(curr)
        widget.set_position(0)
                
        if self.device.Device:
            self.xml.get_widget("cipeDeviceEntry").set_text(self.device.Device)

        if self.device.Cipe.LocalPort:
            self.xml.get_widget("localPortEntry").set_text(str(self.device.Cipe.LocalPort))

        if self.device.Cipe.RemotePeerAddress:
            vals = string.split(self.device.Cipe.RemotePeerAddress, ":")
            addr = vals[0]
            if len(vals) > 1:
                port = vals[1]
                self.xml.get_widget("remotePeerPortEntry").set_text(port)
            self.xml.get_widget("remotePeerAddressEntry").set_text(addr)
                
        if self.device.Cipe.RemotePeerAddress == "0.0.0.0" \
           or self.device.Cipe.RemotePeerAddress == "" \
           or not self.device.Cipe.RemotePeerAddress:
            self.xml.get_widget("remotePeerAddressEntry").set_text(_("Server Mode"))
            self.xml.get_widget("remotePeerPortEntry").set_text("")
            self.xml.get_widget("remotePeerAddressEntry").set_sensitive(FALSE)
            self.xml.get_widget("remotePeerPortEntry").set_sensitive(FALSE)
            self.xml.get_widget("remotePeerAddressCB").set_active(TRUE)            

            
        if self.device.Cipe.RemoteVirtualAddress:
            self.xml.get_widget("remoteVirtualAddressEntry").set_text(self.device.Cipe.RemoteVirtualAddress)
        if self.device.IP: self.xml.get_widget("localVirtualAddressEntry").set_text(self.device.IP)
        widget = self.xml.get_widget("secretKeyEntry")
        if self.device.Cipe.SecretKey:
            widget.set_text(self.device.Cipe.SecretKey)
        widget.set_position(0)

        self.updateRemoteOptions()
        sharedtcpip.route_hydrate (self.sharedtcpip_xml, self.device)
        
    def dehydrate(self):
        deviceConfigDialog.dehydrate(self)

        hw = self.xml.get_widget("ethernetDeviceEntry").get_text()
        fields = string.split(hw)
        hw = fields[0]
        self.device.Cipe.TunnelDevice = hw

        self.device.Device = self.xml.get_widget("cipeDeviceEntry").get_text()
        self.device.Cipe.LocalPort = int(self.xml.get_widget("localPortEntry").get_text())
        self.device.Cipe.RemoteVirtualAddress = self.xml.get_widget("remoteVirtualAddressEntry").get_text()
        self.device.IP = self.xml.get_widget("localVirtualAddressEntry").get_text()
        self.device.Cipe.SecretKey = self.xml.get_widget("secretKeyEntry").get_text()
        if self.xml.get_widget("remotePeerAddressCB").get_active():
            self.device.Cipe.RemotePeerAddress = "0.0.0.0"
        else:
            self.device.Cipe.RemotePeerAddress = self.xml.get_widget("remotePeerAddressEntry").get_text() + ":" + self.xml.get_widget("remotePeerPortEntry").get_text()

        sharedtcpip.route_dehydrate (self.sharedtcpip_xml, self.device)
        
    def on_protocolEditButton_clicked(self, *args):
        self.device.IP = self.xml.get_widget("localVirtualAddressEntry").get_text()
        deviceConfigDialog.on_protocolEditButton_clicked(self, args)
        if self.device.IP:
            self.xml.get_widget("localVirtualAddressEntry").set_text(self.device.IP)
        
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
        key = commands.getoutput('(ps aux|md5sum; ps alx|md5sum) | tr -cd 0-9 2>/dev/null')
        widget = self.xml.get_widget("secretKeyEntry")
        if key:
            widget.set_text(key)            
        widget.set_position(0)
        

    def updateRemoteOptions(self, *args):

        ethw = self.xml.get_widget("ethernetDeviceEntry").get_text()
        fields = string.split(ethw)
        d = fields[0]
        ip = '0.0.0.0 (auto)'
        
        devlist = NCDeviceList.getDeviceList()
        for dev in devlist:
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
        widget = self.xml.get_widget("remoteConfigTxt")
        if widget.get_length():
            widget.delete_text(0, widget.get_length()-1)
        widget.insert_defaults(mytxt)
        widget.set_position(0)
