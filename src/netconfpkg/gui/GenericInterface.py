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

from netconfpkg.gui.GUI_functions import *
from netconfpkg.NC_functions import _
from netconfpkg import *
from netconfpkg.gui import sharedtcpip
from netconfpkg.gui import *
import gtk
from gtk import TRUE
from gtk import FALSE
import gtk.glade
import string
import os
from EthernetHardwareDruid import ethernetHardware
from TokenRingHardwareDruid import tokenringHardware
from InterfaceCreator import InterfaceCreator

class GenericInterface(InterfaceCreator):
    def __init__(self, toplevel=None, type=ETHERNET, do_save = 1,
                 druid = None):
        InterfaceCreator.__init__(self, do_save = do_save)
        self.toplevel = toplevel
        self.topdruid = druid

        glade_file = "sharedtcpip.glade"
        if not os.path.exists(glade_file):
            glade_file = GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = NETCONFDIR + glade_file
        self.sharedtcpip_xml = gtk.glade.XML (glade_file, None,
                                                  domain=PROGNAME)

        glade_file = 'GenericInterfaceDruid.glade'

        if not os.path.exists(glade_file):
            glade_file = GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, 'druid', domain=PROGNAME)
        self.xml.signal_autoconnect(
            { "on_finish_page_finish" : self.on_finish_page_finish,
              "on_finish_page_prepare" : self.on_finish_page_prepare,
              "on_finish_page_back" : self.on_finish_page_back
              }
            )


        self.devicelist = NCDeviceList.getDeviceList()
        self.device = NCDevice.Device()
        self.device.Type = type
        self.device.OnBoot = FALSE
        self.device.AllowUser = FALSE

        self.profilelist = NCProfileList.getProfileList()
        self.toplevel = toplevel

        self.druids = []
        self.druid = self.xml.get_widget('druid')
        for i in self.druid.get_children():
            self.druid.remove(i)

            self.druids.append(i)

    def get_project_name(self):
        return _('%s connection') % self.device.Type

    def get_project_description(self):
        return _("Create a new %s connection.") % self.device.Type

    def get_druids(self):
        return self.druids    
    
    def on_finish_page_back(self,druid_page, druid):
        pass
        
    def on_finish_page_prepare(self, druid_page, druid):

        s = _("This wizard still has to be written.") + "\n" + \
            _("Press Finish to get the standard configuration dialog.") +"\n"\
            + _("Then, at first, enter the nickname for the device.")
        
        druid_page.set_text(s)
        
    def editDevice(self, device):
        button = 0
        type = device.Type
        device.createDialup()
        device.createCipe()
        device.createWireless()

        if type == ETHERNET:
            cfg = ethernetConfigDialog(device)
            dialog = cfg.xml.get_widget ("Dialog")
            button = dialog.run ()

        elif type == TOKENRING:
            cfg = tokenringConfigDialog(device)
            dialog = cfg.xml.get_widget ("Dialog")
            button = dialog.run ()

        elif type == ISDN:
            cfg = ISDNDialupDialog(device)
            dialog = cfg.xml.get_widget ("Dialog")
            button = dialog.run ()

        elif type == MODEM:
            cfg = ModemDialupDialog(device)
            dialog = cfg.xml.get_widget ("Dialog")
            button = dialog.run ()

        elif type == DSL:
            cfg = dslConfigDialog(device)
            dialog = cfg.xml.get_widget ("Dialog")
            button = dialog.run ()

        elif type == CIPE:
            cfg = cipeConfigDialog(device)
            dialog = cfg.xml.get_widget ("Dialog")
            button = dialog.run ()

        elif type == WIRELESS:
            cfg = wirelessConfigDialog(device)
            dialog = cfg.xml.get_widget ("Dialog")
            button = dialog.run ()

        elif type == CTC or type == IUCV:
            cfg = ctcConfigDialog(device)
            dialog =  cfg.xml.get_widget ("Dialog")
            button = dialog.run ()

        else:
            generic_error_dialog (_('This device can not be edited with this tool!'), self.dialog)


        return button

    def on_finish_page_finish(self, druid_page, druid):
        self.toplevel.destroy()

        button = self.editDevice(self.device)

        if button == gtk.RESPONSE_YES:        
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
        
        gtk.mainquit()
