#! /usr/bin/python

## netconf - A network configuration tool
## Copyright (C) 2001 Red Hat, Inc.
## Copyright (C) 2001 Than Ngo <than@redhat.com>
 
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
import re

import providerdb
from gtk import TRUE
from gtk import FALSE
from gtk import CTREE_LINES_DOTTED

##
## I18N
##
gettext.bindtextdomain("netconf", "/usr/share/locale")
gettext.textdomain("netconf")
_=gettext.gettext

class providerDialog:
    def __init__(self, xml_main = None, xml_dialup = None,
                 connection_type="isdn"):
        self.xml_main = xml_main
        self.xml_dialup = xml_dialup
        self.done = FALSE
        self.country = ""
        self.city = ""
        self.name = ""
        self.connection_type = connection_type
        
        glade_file = "chooseprovider.glade"

        if not os.path.exists(glade_file):
            glade_file = "netconfpkg/" + glade_file
        if not os.path.exists(glade_file):
            glade_file = "/usr/share/redhat-config-network/" + glade_file

        self.xml = libglade.GladeXML(glade_file, None, domain="netconf")

        # get the widgets we need
        self.dbtree = self.xml.get_widget("providerTree")
        self.dialog = self.xml.get_widget("Dialog")
        self.okButton = self.xml.get_widget("okButton")
        
        self.xml.signal_autoconnect(
            {
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_cancelButton_clicked" : self.on_cancelButton_clicked,
            "on_providerTree_tree_select_row" : self.on_providerTree_tree_select_row,
            "on_providerTree_button_press_event" : self.on_providerTree_button_press_event,
            "on_providerTree_tree_unselect_row" : self.on_providerTree_tree_unselect_row
            })

        self.dialog.connect("delete-event", gtk.mainquit)
        self.dialog.connect("hide", gtk.mainquit)
        
        self.okButton.set_sensitive(FALSE)
        self.setup_provider_db()
        self.load_icon("network.xpm")
        self.dialog.show()

    def get_icon(self, pixmap_file):
        if not os.path.exists(pixmap_file):
            pixmap_file = "pixmaps/" + pixmap_file
        if not os.path.exists(pixmap_file):
            pixmap_file = "../pixmaps/" + pixmap_file
        if not os.path.exists(pixmap_file):
            pixmap_file = "/usr/share/redhat-config-network/" + pixmap_file
        if not os.path.exists(pixmap_file):
            return None, None

        pix, mask = gtk.create_pixmap_from_xpm(self.dialog, None, pixmap_file)
        return pix, mask
    
    def load_icon(self, pixmap_file, widget = None):
        pix, mask = self.get_icon(pixmap_file)
        if not pix:
            return

        gtk.GtkPixmap(pix, mask)

        if widget:
            widget.set(pix, mask)
        else:
            self.dialog.set_icon(pix, mask)

    def on_cancelButton_clicked(self, button):
        self.done = FALSE
        self.dialog.destroy()

    def on_okButton_clicked(self, button):
        self.done = TRUE
        self.dialog.destroy()
        if self.xml_main and self.xml_dialup:
            self.updateDialog(self.get_provider())

    def updateDialog(self, list):
        self.xml_dialup.get_widget("providerName").set_text(list[3])
        self.xml_dialup.get_widget("authEntry").set_text(list[14])
        self.xml_dialup.get_widget("loginNameEntry").set_text(list[5])
        self.xml_dialup.get_widget("passwordEntry").set_text(list[6])
        self.xml_dialup.get_widget("areaCodeEntry").set_text(list[7])
        self.xml_dialup.get_widget("phoneEntry").set_text(list[8])
        self.xml_dialup.get_widget("userControlCB")["active"] = TRUE

    def on_providerTree_tree_select_row(self, ctree, node, column):
        if len(node.children) == 0:
            self.country = ctree.get_node_info(node.parent.parent)[0]
            self.city = ctree.get_node_info(node.parent)[0]
            self.name = ctree.get_node_info(node)[0]
            self.okButton.set_sensitive(TRUE)

    def on_providerTree_tree_unselect_row(self, ctree, list, column):
        self.okButton.set_sensitive(FALSE)

    def on_providerTree_button_press_event(self, clist, event):
        if event.type == GDK._2BUTTON_PRESS:
            self.is_provider_selected = TRUE

    def get_provider_list(self):
        return providerdb.get_provider_list()
    
    def get_provider(self):
        if self.done:
            isp_list = self.get_provider_list()
            for isp in isp_list:
                if self.country == isp[0] and self.city == isp[1] \
                   and self.name == isp[3]:
                    return isp

    def setup_provider_db(self):
        self.dbtree.set_line_style(CTREE_LINES_DOTTED)
        
        pix_isp, mask_isp = self.get_icon("isp.xpm")
        pix_city, mask_city = self.get_icon("city.xpm")
        isp_list = self.get_provider_list()
        _country = ""
        _city = ""
        for isp in isp_list:
            if _country != isp[0]:
                pix, mask = self.get_icon(isp[2]+".xpm")
                country = self.dbtree.insert_node(None, None, [isp[0]], 5,
                                                  pix, mask, pix, mask, is_leaf=FALSE)
                _country = isp[0]
            if _city != isp[1]:
                city = self.dbtree.insert_node(country, None, [isp[1]], 5,
                                               pix_city, mask_city,
                                               pix_city, mask_city, is_leaf=FALSE)
                _city = isp[1]
            name = self.dbtree.insert_node(city, None, [isp[3]], 5,
                                           pix_isp, mask_isp,
                                           pix_isp, mask_isp, is_leaf=FALSE)

class ISDNproviderDialog(providerDialog):
    def __init__(self, xml_main = None, xml_dialup = None):
        providerDialog.__init__(self, xml_main, xml_dialup)

    def get_provider_list(self):
        return providerdb.get_provider_list("isdn")

class ModemproviderDialog(providerDialog):
    def __init__(self, xml_main = None, xml_dialup = None):
        providerDialog.__init__(self, xml_main, xml_dialup)

    def get_provider_list(self):
        return providerdb.get_provider_list("modem") 


# make ctrl-C work
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    window = providerDialog()
    window.run()
    gtk.mainloop()
    print window.get_provider()


