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

#import gnome.ui
import GDK
import gtk
from gtk import TRUE
from gtk import FALSE
from gtk import CTREE_LINES_DOTTED
from netconfpkg.NC_functions import _
from netconfpkg.NC_functions import *
import libglade
import string
import os
import providerdb
from netconfpkg.gui import GUI_functions
from netconfpkg import NCHardwareList
from netconfpkg import NCisdnhardware
from netconfpkg import NCDeviceList
from netconfpkg import NCDevice
from netconfpkg import NCProfileList
from netconfpkg import NCDialup
from InterfaceCreator import InterfaceCreator

class DialupDruid(InterfaceCreator):
    def __init__ (self, toplevel=None, connection_type='ISDN', do_save = 1, druid = None):
        InterfaceCreator.__init__(self, do_save = do_save)
        glade_file = 'DialupDruid.glade'

        if not os.path.exists(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.NETCONFDIR + glade_file

        self.xml = libglade.GladeXML(glade_file, 'druid', domain=GUI_functions.PROGNAME)
        self.xml.signal_autoconnect(
            { "on_dialup_page_prepare" : self.on_dialup_page_prepare,
              "on_dialup_page_next" : self.on_dialup_page_next,
              "on_finish_page_finish" : self.on_finish_page_finish,
              "on_finish_page_prepare" : self.on_finish_page_prepare,
              "on_finish_page_back" : self.on_finish_page_back
              }
            )

        self.devicelist = NCDeviceList.getDeviceList()
        self.device = NCDevice.Device()
        self.profilelist = NCProfileList.getProfileList()
        self.toplevel = toplevel
        self.druids = []
        
        self.druid = self.xml.get_widget ('druid')
        for I in self.druid.children ():
            self.druid.remove (I)
            self.druids.append (I)

        self.country = ""
        self.city = ""
        self.name = ""
        self.connection_type = connection_type
        self.provider = None

        # get the widgets we need
        self.dbtree = self.xml.get_widget("providerTree")

        self.setup_provider_db()
        
    def get_druids (self):
        return self.druids[0:]

    def on_dialup_page_next(self, druid_page, druid):
        if self.check():
            self.dehydrate()
            return FALSE
        else:
            return TRUE

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
        
        s = _("You have selected the following information:") + "\n\n" + "    " + \
            _("Hardware:") + "  " + hw.Description + "\n" + "    " + \
            _("Provider Name:") + "  " + dialup.ProviderName + "\n" +  "    " + \
            _("Login Name:") + "  " + dialup.Login + "\n" +  "    " + \
            _("Phone Number:") + "  " + dialup.PhoneNumber + "\n\n\n" + \
            _("Press \"Finish\" to create this account")
        
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
                
        self.save()
        self.toplevel.destroy()
        gtk.mainquit()

    def setup(self):
        if not self.provider:
            self.xml.get_widget('druid').set_buttons_sensitive(FALSE, FALSE, FALSE) 
        else:
            self.xml.get_widget('druid').set_buttons_sensitive(FALSE, TRUE, TRUE)
            self.xml.get_widget('areaCodeEntry').set_text(self.provider['Areacode'])
            self.xml.get_widget('phoneEntry').set_text(self.provider['PhoneNumber'])
            self.xml.get_widget('providerName').set_text(self.provider['ProviderName'])
            self.xml.get_widget('dialupLoginNameEntry').set_text(self.provider['Login'])
            self.xml.get_widget('dialupPasswordEntry').set_text(self.provider['Password'])

    def check(self):
        return (len(string.strip(self.xml.get_widget('phoneEntry').get_text())) > 0 \
           and len(string.strip(self.xml.get_widget('phoneEntry').get_text())) > 0 \
           and len(string.strip(self.xml.get_widget('providerName').get_text())) > 0 \
           and len(string.strip(self.xml.get_widget('dialupLoginNameEntry').get_text())) > 0 \
           and len(string.strip(self.xml.get_widget('dialupPasswordEntry').get_text())) > 0)
        
    def on_providerTree_tree_select_row(self, ctree, node, column):
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
                pix, mask = GUI_functions.get_icon(isp['Flag'] + '.xpm', widget)
                country = self.dbtree.insert_node(None, None, [isp['Country']], 5,
                                                  pix, mask, pix, mask, is_leaf=FALSE)
                _country = isp['Country']
                _city = ''
            if _city != isp['City']:
                city = self.dbtree.insert_node(country, None, [isp['City']], 5,
                                               pix_city, mask_city,
                                               pix_city, mask_city, is_leaf=FALSE)
                _city = isp['City']
            name = self.dbtree.insert_node(city, None, [isp['ProviderName']], 5,
                                           pix_isp, mask_isp,
                                           pix_isp, mask_isp, is_leaf=FALSE)
 
        self.dbtree.select_row(0,0)
    
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
        self.device.BootProto = 'dialup'
        self.device.AllowUser = TRUE

        if self.connection_type == ISDN:
            dialup.EncapMode = 'syncppp'
            
        if self.connection_type == MODEM:
            self.device.Name  = DeviceId
            dialup.Inherits = 'Modem0'
            dialup.StupidMode = TRUE
            dialup.InitString = ''

        self.device.Device = getNewDialupDevice(NCDeviceList.getDeviceList(), self.device)
        self.device.AutoDNS = TRUE
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
        self.device.AutoDNS = TRUE
        dialup.DialMode = NCDialup.DM_MANUAL

            
