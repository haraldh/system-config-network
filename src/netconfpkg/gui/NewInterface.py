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

import signal
import os
import gtk
from gtk import TRUE
from gtk import FALSE
import gtk.glade
# do not remove this (needed to access methods of self.druid
import gnome.ui

from ModemInterface import ModemInterface
from ADSLInterface import ADSLInterface
from IsdnInterface import IsdnInterface
from EthernetInterface import EthernetInterface
from TokenRingInterface import TokenRingInterface
from CipeInterface import CipeInterface
from WirelessInterface import WirelessInterface
from netconfpkg import *
from netconfpkg import *
from netconfpkg.gui import GUI_functions
from netconfpkg.gui.GUI_functions import *
from netconfpkg.gui.GUI_functions import load_icon
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect

Interfaces = [ EthernetInterface, IsdnInterface, ModemInterface,
               ADSLInterface, TokenRingInterface, CipeInterface,
               WirelessInterface ]


class NewInterface:
    def __init__(self, parent_dialog = None):
        self.creator = None
        glade_file = 'NewInterfaceDruid.glade'

        if not os.path.isfile(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.isfile(glade_file):
            glade_file = NETCONFDIR + glade_file
            
        xml = gtk.glade.XML (glade_file, 'toplevel',
                                 domain=GUI_functions.PROGNAME)

        # get the widgets we need
        self.toplevel = xml.get_widget ('toplevel')
        self.druid = xml.get_widget ('druid')
        self.start_page = xml.get_widget('start_page')
        self.interface_clist = xml.get_widget ('interface_clist')
        self.description_label = xml.get_widget ('description_label')

        if parent_dialog:
            self.toplevel.set_transient_for(parent_dialog)        
            self.toplevel.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
        else:
            self.toplevel.set_position (gtk.WIN_POS_CENTER)            

        xml_signal_autoconnect (xml,
            { 'on_toplevel_delete_event' : self.on_cancel_interface,
              'on_druid_cancel' : self.on_cancel_interface,
              'on_start_page_prepare' : self.on_start_page_prepare,
              'on_start_page_next' : self.on_start_page_next,
              'on_interface_clist_select_row' : \
              self.on_interface_clist_select_row,
              })

        load_icon("network.xpm", self.toplevel)
        
        # Initialize the clist
        self.interface_clist.column_titles_passive ()
        self.interface_clist.set_row_height(20)

        for iface_creator in Interfaces:
            iface = iface_creator (self.toplevel)
            iftype = iface.get_type()
            
            row = self.interface_clist.append ( [ iface.get_project_name () ] )
            device_pixmap, device_mask = \
                           GUI_functions.get_device_icon_mask(iftype, self.toplevel)

            self.interface_clist.set_pixtext (row, 0, iface.get_project_name (), 5, device_pixmap, device_mask)
            self.interface_clist.set_row_data (row, iface)

        self.interface_clist.select_row (0, 0)

        self.toplevel.show_all ()
        self.on_start_page_prepare (None, None)
        
    def on_start_page_prepare (self, druid_page, druid):
        self.interface_clist.grab_focus ()
        self.druid.set_buttons_sensitive (FALSE, TRUE, TRUE, TRUE)
        
    def on_start_page_next (self, druid, druid_page):
        interface = self.interface_clist.get_row_data (\
            self.interface_clist.selection[0])

        # remove all other children
        for i in self.druid.get_children()[1:]:
            self.druid.remove(i)

        druid_pages = interface.get_druids()
        if druid_pages:
            for i in druid_pages:
                self.druid.append_page(i)
                i.show()
            return FALSE
        else:
            return TRUE

    def on_cancel_interface(self, *args):
        hardwarelist = NCHardwareList.getHardwareList()
        hardwarelist.rollback()
        
        self.toplevel.destroy()
        gtk.mainquit()

    def on_interface_clist_select_row (self, clist, row, column, event):
        interface = self.interface_clist.get_row_data (row)
        if interface == None:
            return
        buf = self.description_label.get_buffer()
        buf.set_text(interface.get_project_description ())

if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    interface = NewInterface ()
    gtk.mainloop ()
    
