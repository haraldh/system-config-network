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
from gtk import TRUE
from gtk import FALSE
from gtk import CTREE_LINES_DOTTED
from netconfpkg.NC_functions import *
import gtk.glade
import string
import os
import providerdb
from netconfpkg.gui import GUI_functions
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect
from netconfpkg import *
from netconfpkg import *
from netconfpkg import *
from netconfpkg import *
from netconfpkg import *
from netconfpkg import *
from InterfaceCreator import InterfaceCreator
from netconfpkg.gui.tonline import TonlineDialog

class DialupDruid(InterfaceCreator):
    def __init__ (self, toplevel=None, connection_type=ISDN,
                  do_save = 1, druid = None):
        InterfaceCreator.__init__(self, do_save = do_save)

        self.connection_type = connection_type
        df = NCDeviceFactory.getDeviceFactory()        
        self.device = df.getDeviceClass(connection_type)()
        self.toplevel = toplevel
        self.druids = []
        self.country = ""
        self.city = ""
        self.name = ""
        self.provider = None
        self.device.BootProto = 'dialup'
        self.device.AutoDNS = TRUE

        self.devicelist = NCDeviceList.getDeviceList()
        self.profilelist = NCProfileList.getProfileList()
        self.xml = None
        
    def init_gui(self):
        if self.xml:
            return
        
        glade_file = 'DialupDruid.glade'
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, 'druid',
                                 domain=GUI_functions.PROGNAME)
        xml_signal_autoconnect(self.xml,
            { "on_dialup_page_prepare" : self.on_dialup_page_prepare,
              "on_dialup_page_next" : self.on_dialup_page_next,
              "on_dhcp_page_prepare" : self.on_dhcp_page_prepare,
              "on_dhcp_page_next" : self.on_dhcp_page_next,
              "on_finish_page_finish" : self.on_finish_page_finish,
              "on_finish_page_prepare" : self.on_finish_page_prepare,
              "on_finish_page_back" : self.on_finish_page_back,
              "on_ipAutomaticRadio_toggled" : self.on_ipBootProto_toggled,
              "on_ipStaticRadio_toggled" : self.on_ipBootProto_toggled,
              "on_sync_ppp_activate" : self.on_sync_ppp_activate,
              "on_raw_ip_activate" : self.on_raw_ip_activate,              
              "on_providerNameEntry_insert_text" : \
              (self.on_generic_entry_insert_text, r"^[a-z|A-Z|0-9\-_:]+$"),
              "on_tonlineButton_clicked" : self.on_tonlineButton_clicked,
              }
            )

        self.druid = self.xml.get_widget ('druid')
        for I in self.druid.get_children():
            self.druid.remove (I)
            self.druids.append (I)


        # get the widgets we need
        self.dbtree = self.xml.get_widget("providerTree")

        self.setup_provider_db()
        
    def on_generic_entry_insert_text(self, entry, partial_text, length,
                                     pos, str):
        text = partial_text[0:length]
        if re.match(str, text):
            return
        entry.emit_stop_by_name('insert_text')

    def get_druids (self):
        self.init_gui()
        return self.druids[0:]

    def on_dialup_page_next(self, druid_page, druid):
        if self.check():
            self.dehydrate()
            return FALSE
        else:
            return TRUE

    def on_ipBootProto_toggled(self, widget):
        if widget.name == "ipAutomaticRadio":
            active = widget.get_active()
        else:
            active = not widget.get_active()
        
        self.xml.get_widget('dhcpSettingFrame').set_sensitive(active)
        self.xml.get_widget('ipSettingFrame').set_sensitive(not active)

    def dhcp_hydrate (self, xml, device):
        if device.IP:
            xml.get_widget('ipAddressEntry').set_text(device.IP)
        else:
            xml.get_widget('ipAddressEntry').set_text('')
        if device.Netmask:
            xml.get_widget('ipNetmaskEntry').set_text(device.Netmask)
        else:
            xml.get_widget('ipNetmaskEntry').set_text('')
        if device.Gateway:
            xml.get_widget('ipGatewayEntry').set_text(device.Gateway)
        else:
            xml.get_widget('ipGatewayEntry').set_text('')

        xml.get_widget('dnsSettingCB').set_active(device.AutoDNS == TRUE)

        if device.BootProto == "static" or device.BootProto == "none":
            xml.get_widget('ipAutomaticRadio').set_active(FALSE)
            xml.get_widget('ipStaticRadio').set_active(TRUE)
            self.on_ipBootProto_toggled(\
                xml.get_widget('ipAutomaticRadio')),
        else:
            device.BootProto = 'dialup'
            xml.get_widget('ipAutomaticRadio').set_active(TRUE)
            xml.get_widget('ipStaticRadio').set_active(FALSE)
            self.on_ipBootProto_toggled(\
                xml.get_widget('ipStaticRadio')),

    def dhcp_dehydrate (self, xml, device):
        if xml.get_widget('ipAutomaticRadio').get_active():
            device.BootProto = 'dialup'
            device.IP = ''
            device.Netmask = ''
            device.Gateway = ''
            device.Hostname = ''
            device.AutoDNS = xml.get_widget('dnsSettingCB').get_active()
        else:
            device.BootProto = 'none'
            device.IP = xml.get_widget('ipAddressEntry').get_text()
            device.Netmask = xml.get_widget('ipNetmaskEntry').get_text()
            device.Gateway = xml.get_widget('ipGatewayEntry').get_text()
            device.Hostname = ''

    def on_sync_ppp_activate(self, *args):
        self.xml.get_widget('ipAutomaticRadio').set_active(TRUE)
        self.xml.get_widget('ipStaticRadio').set_active(FALSE)
        self.xml.get_widget('ipAutomaticRadio').set_sensitive(TRUE)
        self.on_ipBootProto_toggled(\
                self.xml.get_widget('ipStaticRadio')),
        pass
    
    def on_raw_ip_activate(self, *args):
        self.xml.get_widget('ipAutomaticRadio').set_active(FALSE)
        self.xml.get_widget('ipStaticRadio').set_active(TRUE)
        self.on_ipBootProto_toggled(\
                self.xml.get_widget('ipAutomaticRadio')),        
        self.xml.get_widget('ipAutomaticRadio').set_sensitive(FALSE)
        dialup = self.device.createDialup()
        dialup.EncapMode = 'rawip'
        dialup.Authentication = 'noauth'
        pass

    def on_dhcp_page_back(self, druid_page, druid):
        return TRUE
    
    def on_dhcp_page_next(self, druid_page, druid):
        dialup = self.device.createDialup()

        self.dhcp_dehydrate(self.xml, self.device)
        
        if self.connection_type == ISDN and \
               (self.device.BootProto == "static" or \
                self.device.BootProto == "none"):
            dialup.EncapMode = 'rawip'
            dialup.Authentication = 'noauth'

    def on_dhcp_page_prepare(self, druid_page, druid):
        self.dhcp_hydrate(self.xml, self.device)
        dialup = self.device.createDialup()
        if self.connection_type == ISDN:
            if dialup.EncapMode == 'rawip':
                self.on_raw_ip_activate()
            else:
                self.on_sync_ppp_activate()
        else:
            self.xml.get_widget('encapModeMenu').set_sensitive(FALSE)
        pass

    def on_finish_page_back(self,druid_page, druid):
        self.devicelist.rollback()
        
    def on_dialup_page_prepare(self, druid_page, druid):
        self.setup()
        self.xml.signal_connect("on_providerTree_tree_select_row",
                                self.on_providerTree_tree_select_row)

    def on_finish_page_prepare(self, druid_page, druid):
        hardwarelist = NCHardwareList.getHardwareList()
        for hw in hardwarelist:
            if hw.Type == self.connection_type:
                break
        dialup = self.device.Dialup
        
        s = _("You have selected the following information:") + \
            "\n\n" + "    " + \
            _("Hardware:") + "  " + hw.Description + "\n" + "    " + \
            _("Provider Name:") + "  " + dialup.ProviderName + \
            "\n" +  "    " + \
            _("Login Name:") + "  " + dialup.Login + "\n" +  "    " + \
            _("Phone Number:") + "  " + dialup.PhoneNumber
        
        druid_page.set_text(s)
        
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

    def setup(self):
        if not self.provider:
            self.xml.get_widget('druid').set_buttons_sensitive(\
                FALSE, FALSE, FALSE, FALSE) 
        else:
            self.xml.get_widget('druid').set_buttons_sensitive(\
                FALSE, TRUE, TRUE, FALSE)
            self.xml.get_widget('areaCodeEntry').set_text(\
                self.provider['Areacode'])
            self.xml.get_widget('phoneEntry').set_text(\
                self.provider['PhoneNumber'])
            self.xml.get_widget('providerName').set_text(\
                self.provider['ProviderName'])
            self.xml.get_widget('dialupLoginNameEntry').set_text(\
                self.provider['Login'])
            self.xml.get_widget('dialupPasswordEntry').set_text(\
                self.provider['Password'])

    def check(self):
        return (len(string.strip(self.xml.get_widget(\
            'phoneEntry').get_text())) > 0 \
           and len(string.strip(self.xml.get_widget(\
            'phoneEntry').get_text())) > 0 \
           and len(string.strip(self.xml.get_widget(\
            'providerName').get_text())) > 0 \
           and len(string.strip(self.xml.get_widget(\
            'dialupLoginNameEntry').get_text())) > 0 \
           and len(string.strip(self.xml.get_widget(\
            'dialupPasswordEntry').get_text())) > 0)
        
    def on_providerTree_tree_select_row(self, ctree, node, column):
        node = ctree.selection[0]
        if len(node.children) == 0:
            try:
                self.country = ctree.get_node_info(node.parent.parent)[0]
                self.city = ctree.get_node_info(node.parent)[0]
                self.name = ctree.get_node_info(node)[0]
                self.provider = self.get_provider()
                self.setup()
            except(TypeError,AttributeError):
                pass

    def get_provider_list(self):
        return providerdb.get_provider_list(self.connection_type)

    def get_provider(self):
        isp_list = self.get_provider_list()
        for isp in isp_list:
            if self.country == isp['Country'] and self.city == isp['City'] \
               and self.name == isp['ProviderName']:
                return isp

    def setup_provider_db(self):
        self.dbtree.set_line_style(CTREE_LINES_DOTTED)
        self.dbtree.set_row_height(20)
        
        widget = self.xml.get_widget ('providerTree')
        
        pix_isp, mask_isp = GUI_functions.get_icon('isp.xpm', widget)
        pix_city, mask_city = GUI_functions.get_icon('city.xpm', widget)
        
        isp_list = self.get_provider_list()
        
        _country = ""
        _city = ""
        
        for isp in isp_list:
            if _country != isp['Country']:
                pix, mask = GUI_functions.get_icon(isp['Flag'] + '.xpm',
                                                   widget)
                country = self.dbtree.insert_node(None, None,
                                                  [isp['Country']], 5,
                                                  pix, mask, pix, mask,
                                                  is_leaf=FALSE)
                _country = isp['Country']
                _city = ''
            if _city != isp['City']:
                city = self.dbtree.insert_node(country, None, [isp['City']], 5,
                                               pix_city, mask_city,
                                               pix_city, mask_city,
                                               is_leaf=FALSE)
                _city = isp['City']
            name = self.dbtree.insert_node(city, None,
                                           [isp['ProviderName']], 5,
                                           pix_isp, mask_isp,
                                           pix_isp, mask_isp, is_leaf=FALSE)
            
        self.dbtree.select_row(0,0)
    
    def on_tonlineButton_clicked(self, *args):
        self.dehydrate()
        dialup = self.device.Dialup
        dialog = TonlineDialog(dialup.Login, dialup.Password)
        dl = dialog.xml.get_widget ("Dialog")
        
        dl.set_transient_for(self.toplevel)
        dl.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
        
        if dl.run() != gtk.RESPONSE_OK:
            dl.destroy()        
            return

        dl.destroy()
        dialup.Login = dialog.login
        dialup.Password = dialog.password
        self.xml.get_widget("dialupLoginNameEntry").set_text(dialup.Login)
        self.xml.get_widget("dialupPasswordEntry").set_text(dialup.Password)
        if not self.xml.get_widget("providerName").get_text():
            self.xml.get_widget("providerName").set_text("T-Online")

    def dehydrate(self):
        DeviceId = self.xml.get_widget('providerName').get_text()
        n = DeviceId
        num = 0
        while 1:
            found = 0
            for l in self.devicelist:
                if l.DeviceId == DeviceId:
                    found = 1
            if found != 1: break
            DeviceId = n + str(num)
            num = num + 1

        self.device.DeviceId = DeviceId
        self.device.Type = self.connection_type
        dialup = self.device.createDialup()
        self.device.AllowUser = TRUE
        self.device.OnBoot = FALSE
        self.device.Device = getNewDialupDevice(NCDeviceList.getDeviceList(),
                                                self.device)
        dialup.Prefix = self.xml.get_widget('prefixEntry').get_text()
        dialup.Areacode = self.xml.get_widget('areaCodeEntry').get_text()
        dialup.PhoneNumber = self.xml.get_widget('phoneEntry').get_text()
        dialup.ProviderName = self.xml.get_widget('providerName').get_text()
        dialup.Login = self.xml.get_widget('dialupLoginNameEntry').get_text()
        dialup.Password = self.xml.get_widget('dialupPasswordEntry').get_text()
        if self.provider and self.provider['Authentication']:
            dialup.Authentication = self.provider['Authentication']
        else:
            dialup.Authentication = '+pap -chap'
        dialup.DefRoute = TRUE
        dialup.DialMode = NCDialup.DM_MANUAL
            
        if self.connection_type == ISDN:
            dialup.EncapMode = 'syncppp'
            dialup.HangupTimeout = 600
            
        elif self.connection_type == MODEM:
            self.device.Name  = DeviceId
            dialup.Inherits = 'Modem0'
            dialup.StupidMode = TRUE
            dialup.InitString = ''
