#!/usr/bin/python

import signal
import gnome.ui
import gtk
from gtk import TRUE
from gtk import FALSE
import libglade

import InterfaceCreator
from DialupInterface import DialupInterface
from EthernetInterface import EthernetInterface
from CableInterface import CableInterface
from ADSLInterface import ADSLInterface
from WirelessInterface import WirelessInterface
from ATMInterface import ATMInterface

Interfaces = [ DialupInterface, EthernetInterface, CableInterface, ADSLInterface, WirelessInterface, ATMInterface ]

class NewInterface:
    def __init__(self):
        self.creator = None
        xml = libglade.GladeXML ('new_interface_druid.glade', 'toplevel')

        # get the widgets we need
        self.toplevel = xml.get_widget ('toplevel')
        self.druid = xml.get_widget ('druid')
        self.interface_clist = xml.get_widget ('interface_clist')
        self.description_label = xml.get_widget ('description_label')

        xml.signal_autoconnect (
            { 'on_toplevel_delete_event' : self.on_cancel_interface,
              'on_druid_cancel' : self.on_cancel_interface,
              'on_start_page_prepare' : self.on_start_page_prepare,
              'on_start_page_next' : self.on_start_page_next,
              'on_interface_clist_select_row' : self.on_interface_clist_select_row,
              })


        # Initialize the clist
        self.interface_clist.column_titles_passive ()

        for iface_creator in Interfaces:
            iface = iface_creator ()
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
        for I in self.druid.children()[1:]:
            self.druid.remove(I)

        druid_pages = interface.get_druids ()
        for I in druid_pages:
            self.druid.append_page (I)
            I.show()
        return FALSE

    def on_cancel_interface (self, *args):
        gtk.mainquit ()

    def on_interface_clist_select_row (self, clist, row, column, event):
        interface = self.interface_clist.get_row_data (row)
        if interface == None:
            return
        self.description_label.set_text (interface.get_project_description ())

if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    interface = NewInterface ()
    gtk.mainloop ()
    
