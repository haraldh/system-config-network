## Copyright (C) 2001-2005 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001-2005 Harald Hoyer <harald@redhat.com>
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
from netconfpkg import *
from netconfpkg.gui import sharedtcpip
from netconfpkg.gui import *
import gtk
import gtk.glade
import string
import os
from EthernetHardwareDruid import ethernetHardware
from TokenRingHardwareDruid import tokenringHardware
from InterfaceCreator import InterfaceCreator
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect

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
        xml_signal_autoconnect(self.xml,
            { "on_finish_page_finish" : self.on_finish_page_finish,
              "on_finish_page_prepare" : self.on_finish_page_prepare,
              "on_finish_page_back" : self.on_finish_page_back
              }
            )


        self.devicelist = NCDeviceList.getDeviceList()
        self.device = NCDevice.Device()
        self.device.Type = type
        self.device.OnBoot = False
        self.device.AllowUser = False
        self.device.IPv6Init = False

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
        ## FIXME
        button = 0
        type = device.Type

        if type == ETHERNET:
            cfg = ethernetConfigDialog(device)

        elif type == TOKENRING:
            cfg = tokenringConfigDialog(device)

        elif type == ISDN:
            device.createDialup()
            cfg = ISDNDialupInterfaceDialog(device)

        elif type == MODEM:
            device.createDialup()
            cfg = ModemDialupInterfaceDialog(device)

        elif type == DSL:
            device.createDialup()
            cfg = ADSLInterfaceDialog(device)

        elif type == CIPE:
            device.createCipe()
            cfg = CipeInterfaceDialog(device)

        elif type == WIRELESS:
            device.createWireless()
            cfg = wirelessConfigDialog(device)

        elif type == QETH:
            cfg = qethConfigDialog(device)

        else:
            generic_error_dialog (_('This device can not be edited with this tool!'), self.dialog)
            cfg = None

        if cfg:
            dialog = cfg.xml.get_widget ("Dialog")
            if self.topdruid: dialog.set_transient_for(self.topdruid)
            button = dialog.run ()
            dialog.destroy()

        return button

    def on_finish_page_finish(self, druid_page, druid):
        self.toplevel.destroy()

        button = self.editDevice(self.device)

        if button == gtk.RESPONSE_YES:
            self.devicelist.append(self.device)
            self.device.commit()
            for prof in self.profilelist:
                if prof.Active == False:
                    continue
                prof.ActiveDevices.append(self.device.DeviceId)
                break

            self.profilelist.commit()
            self.devicelist.commit()

        gtk.main_quit()
__author__ = "Harald Hoyer <harald@redhat.com>"
