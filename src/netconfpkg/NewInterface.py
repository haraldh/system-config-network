## Copyright (C) 2001 Red Hat, Inc.
## Copyright (C) 2001 Than Ngo <than@redhat.com>
## Copyright (C) 2001 Harald Hoyer <harald@redhat.com>
## Copyright (C) 2001 Philipp Knirsch <pknirsch@redhat.com>

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
#import gnome.ui
import gtk
from gtk import TRUE
from gtk import FALSE
import libglade

from ModemInterface import ModemInterface
from ADSLInterface import ADSLInterface
from IsdnInterface import IsdnInterface
import NCHardwareList
import NCisdnhardware
from NC_functions import *

Interfaces = [ IsdnInterface, ModemInterface, ADSLInterface ]


class NewInterface:
    def __init__(self):
        self.creator = None
        glade_file = 'NewInterfaceDruid.glade'

        if not os.path.isfile(glade_file):
            glade_file = "netconfpkg/" + glade_file
        if not os.path.isfile(glade_file):
            glade_file = NETCONFDIR + glade_file
            
        xml = libglade.GladeXML (glade_file, 'toplevel')

        # get the widgets we need
        self.toplevel = xml.get_widget ('toplevel')
        self.druid = xml.get_widget ('druid')
        self.start_page = xml.get_widget('start_page')
        self.interface_clist = xml.get_widget ('interface_clist')
        self.description_label = xml.get_widget ('description_label')

        xml.signal_autoconnect (
            { 'on_toplevel_delete_event' : self.on_cancel_interface,
              'on_druid_cancel' : self.on_cancel_interface,
              'on_start_page_prepare' : self.on_start_page_prepare,
              'on_start_page_next' : self.on_start_page_next,
              'on_interface_clist_select_row' : self.on_interface_clist_select_row,
              })

        load_icon("network.xpm", self.toplevel)
        
        # Initialize the clist
        self.interface_clist.column_titles_passive ()

        for iface_creator in Interfaces:
            iface = iface_creator (self.toplevel)
            row = self.interface_clist.append ( [ iface.get_project_name () ] )
            self.interface_clist.set_row_data (row, iface)

        self.interface_clist.select_row (0, 0)

        self.toplevel.show_all ()
        self.on_start_page_prepare (None, None)
        
    def on_start_page_prepare (self, druid_page, druid):
        self.interface_clist.grab_focus ()
        self.druid.set_buttons_sensitive (FALSE, TRUE, TRUE)
        
    def on_start_page_next (self, druid, druid_page):
        interface = self.interface_clist.get_row_data (self.interface_clist.selection[0])

        # remove all other children
        for i in self.druid.children()[1:]:
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
        self.description_label.set_text (interface.get_project_description ())


if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    interface = NewInterface ()
    gtk.mainloop ()
    
