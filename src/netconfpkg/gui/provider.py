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

import gtk
import gtk.glade
import signal
import os

import string
import re

import providerdb
from netconfpkg.gui import GUI_functions
from netconfpkg.gui.GUI_functions import load_icon

from gtk import TRUE
from gtk import FALSE
from gtk import CTREE_LINES_DOTTED

class providerDialog:
    def __init__(self, device, connection_type="isdn"):
        self.device = device
        self.done = FALSE
        self.country = ""
        self.city = ""
        self.name = ""
        self.connection_type = connection_type
        self.provider = None
        
        glade_file = "chooseprovider.glade"
        
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, None, domain=GUI_functions.PROGNAME)

        # get the widgets we need
        self.dbtree = self.xml.get_widget("providerTree")
        self.dialog = self.xml.get_widget("Dialog")
        self.okButton = self.xml.get_widget("okButton")
        
        self.xml.signal_autoconnect(
            {
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_cancelButton_clicked" : self.on_cancelButton_clicked,
            "on_providerTree_tree_select_row" : self.on_providerTree_tree_select_row,
            "on_providerTree_button_press_event" : (self.on_providerTree_button_press_event,
                                                    self.on_okButton_clicked),
            "on_providerTree_tree_unselect_row" : self.on_providerTree_tree_unselect_row
            })

        self.okButton.set_sensitive(FALSE)
        self.setup_provider_db()
        load_icon("network.xpm", self.dialog)
        

    def on_Dialog_delete_event(self, *args):
        pass
    
    def on_cancelButton_clicked(self, button):
        self.done = FALSE

    def on_okButton_clicked(self, *args):
        self.done = TRUE
        self.provider = self.get_provider()
        self.dehydrate()
        self.dialog.destroy()
        self.device.commit()
        
    def on_providerTree_tree_select_row(self, ctree, node, column):
        node = ctree.selection[0]
        if len(node.children) == 0:
            try:
                self.country = ctree.get_node_info(node.parent.parent)[0]
                self.city = ctree.get_node_info(node.parent)[0]
                self.name = ctree.get_node_info(node)[0]
                self.okButton.set_sensitive(TRUE)
            except(TypeError,AttributeError):
                pass

    def on_providerTree_tree_unselect_row(self, ctree, list, column):
        self.okButton.set_sensitive(FALSE)

    def on_providerTree_button_press_event(self, clist, event, func):
        return
        if event.type == gtk.gdk._2BUTTON_PRESS:
            if self.okButton.get_property("sensitive"):
                info = clist.get_selection_info(event.x, event.y)
                if info != None:
                    id = clist.signal_connect("button_release_event",
                                              self.on_providerTree_button_release_event,
                                              func)
                    clist.set_data("signal_id", id)

    def on_providerTree_button_release_event(self, clist, event, func):
        if self.okButton.get_property("sensitive"):
            id = clist.get_data ("signal_id")
            clist.disconnect (id)
            clist.remove_data ("signal_id")
            apply(func)
        
    def get_provider_list(self):
        return providerdb.get_provider_list()
    
    def get_provider(self):
        if self.done:
            isp_list = self.get_provider_list()
            for isp in isp_list:
                if self.country == isp['Country'] and self.city == isp['City'] \
                   and self.name == isp['ProviderName']:
                    return isp

    def setup_provider_db(self):
        self.dbtree.set_line_style(CTREE_LINES_DOTTED)
        self.dbtree.set_row_height(20)
        
        pix_isp, mask_isp = GUI_functions.get_icon("isp.xpm", self.dialog)
        pix_city, mask_city = GUI_functions.get_icon("city.xpm", self.dialog)

        isp_list = self.get_provider_list()
        _country = ""
        _city = ""

        for isp in isp_list:
            if _country != isp['Country']:
                pix, mask = GUI_functions.get_icon(isp['Flag']+".xpm", self.dialog)
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

    def hydrate(self):
        pass

    def dehydrate(self):
        if not self.provider: return
        if self.device.Dialup == None: self.device.createDialup()
        self.device.Dialup.ProviderName = self.provider['ProviderName']
        self.device.Dialup.Login = self.provider['Login']
        self.device.Dialup.Password = self.provider['Password']
        self.device.Dialup.Areacode = self.provider['Areacode']
        self.device.Dialup.PhoneNumber = self.provider['PhoneNumber']
        self.device.AllowUser = TRUE
        self.device.BootProto = 'dialup'
        self.device.Domain = self.provider['Domain']
        if len(self.provider['DNS']) >0:
            dns = string.split(self.provider['DNS'])
            if dns[0]: self.device.Dialup.PrimaryDNS = dns[0]
            try:
                if dns[1]: self.device.Dialup.SecondaryDNS = dns[1]
            except(IndexError):
                pass
            self.device.AutoDNS = FALSE
        else:
            self.device.AutoDNS = TRUE


class ISDNproviderDialog(providerDialog):
    def __init__(self, device):
        providerDialog.__init__(self, device)

    def get_provider_list(self):
        return providerdb.get_provider_list("isdn")

    def dehydrate(self):
        providerDialog.dehydrate(self)
        self.device.Type = 'ISDN'
        self.device.Dialup.Authentication = string.lower(self.provider['Authentication'])


class ModemproviderDialog(providerDialog):
    def __init__(self, device):
        providerDialog.__init__(self, device)

    def get_provider_list(self):
        return providerdb.get_provider_list("modem") 

    def dehydrate(self):
        providerDialog.dehydrate(self)
        self.device.Type = 'Modem'
        

        
# make ctrl-C work
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    window = providerDialog()
    window.run()
    gtk.mainloop()
    print window.get_provider()


