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
import GdkImlib
import string
import gettext
import re

from providerdb import *
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
    def __init__(self, xml_main = None, xml_basic = None, xml_dialup = None):
        self.xml_main = xml_main
        self.xml_basic = xml_basic
        self.xml_dialup = xml_dialup
        self.done = FALSE
        self.country = ""
        self.city = ""
        self.name = ""
        
        xml = libglade.GladeXML("chooseprovider.glade", None, domain="netconf")

        # get the widgets we need
        self.dbtree = xml.get_widget("providerTree")
        self.dialog = xml.get_widget("Dialog")
        self.okButton = xml.get_widget("okButton")
        
        xml.signal_autoconnect(
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
        self.dialog.show()

    def on_cancelButton_clicked(self, button):
        self.done = FALSE
        self.dialog.destroy()

    def on_okButton_clicked(self, button):
        self.done = TRUE
        self.dialog.destroy()
        if self.xml_main and self.xml_basic and self.xml_dialup:
            self.updateDialog(self.get_provider())

    def updateDialog(self, list):
        self.xml_dialup.get_widget("providerName").set_text(list[3])
        self.xml_dialup.get_widget("authEntry").set_text(list[14])
        self.xml_dialup.get_widget("loginNameEntry").set_text(list[5])
        self.xml_dialup.get_widget("passwordEntry").set_text(list[6])
        self.xml_dialup.get_widget("areaCodeEntry").set_text(list[7])
        self.xml_dialup.get_widget("phoneEntry").set_text(list[8])
        self.xml_basic.get_widget("userControlCB")["active"] = TRUE

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
            
    def get_provider(self):
        if self.done:
            isp_list = get_provider_list()
            for isp in isp_list:
                if self.country == isp[0] and self.city == isp[1] \
                   and self.name == isp[3]:
                    return isp

    def setup_provider_db(self):
        self.dbtree.set_line_style(CTREE_LINES_DOTTED)
        pix_isp, mask_isp = gtk.create_pixmap_from_xpm(self.dbtree, None,
                                                       "pixmaps/isp.xpm")
        pix_city, mask_city = gtk.create_pixmap_from_xpm (self.dbtree, None,
                                                          "pixmaps/city.xpm")
        isp_list = get_provider_list()
        _country = ""
        _city = ""
        for isp in isp_list:
            if _country != isp[0]:
                pix, mask = gtk.create_pixmap_from_xpm (self.dbtree, None,
                                                        "pixmaps/"+isp[2]+".xpm")
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

# make ctrl-C work
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    window = providerDialog()
    gtk.mainloop()
    print window.get_provider()


