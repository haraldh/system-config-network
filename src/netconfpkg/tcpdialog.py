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
import NC_functions

from editadress import editAdressDialog
from NCDeviceList import *

from gtk import TRUE
from gtk import FALSE

##
## I18N
##
gettext.bindtextdomain(NC_functions.PROGNAME, "/usr/share/locale")
gettext.textdomain(NC_functions.PROGNAME)
_=gettext.gettext

class tcpConfigDialog:
    def __init__(self, device, xml = None):
        self.xml_main = xml
        self.device = device
        glade_file = "tcpipdialog.glade"

        if not os.path.exists(glade_file):
            glade_file = "netconfpkg/" + glade_file
        if not os.path.exists(glade_file):
            glade_file = NC_functions.NETCONFDIR + glade_file

        self.xml = libglade.GladeXML(glade_file, None, domain=NC_functions.PROGNAME)
        self.xml.signal_autoconnect(
            {
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_cancelButton_clicked" : self.on_cancelButton_clicked,
            "on_applyButton_clicked" : self.on_applyButton_clicked,
            "on_ipSettingCB_toggled" : self.on_ipSettingCB_toggled,
            "on_defaultRouteCB_toggled" : self.on_defaultRouteCB_toggled,
            "on_routeAddButton_clicked" : self.on_routeAddButton_clicked,
            "on_routeEditButton_clicked" : self.on_routeEditButton_clicked,
            "on_routeDeleteButton_clicked" : self.on_routeDeleteButton_clicked,
            "on_routeUpButton_clicked" : self.on_routeUpButton_clicked,
            "on_routeDownButton_clicked" : self.on_routeDownButton_clicked
            })

        self.dialog = self.xml.get_widget("Dialog")
        self.dialog.connect("delete-event", self.on_Dialog_delete_event)
        self.dialog.connect("hide", gtk.mainquit)
        self.xml.get_widget("networkPixmap").load_file(NC_functions.NETCONFDIR+"pixmaps/network.xpm")
        NC_functions.load_icon("network.xpm", self.dialog)

        clist = self.xml.get_widget ("networkRouteList")
        clist.column_titles_passive ()
        notebook = self.xml.get_widget("basicNotebook")

        self.hydrate()

        flist = [ "trafficFrame", "securityFrame", "accountingFrame" ]
        if self.device.Type == CIPE:
            flist.insert(0, 'hostnameFrame')
            flist.insert(0, 'tcpipFrame')

        for wname in flist:
            widget = self.xml.get_widget (wname)
            if widget != None:
                page = notebook.page_num(widget)
                if page != None:
                    notebook.remove_page(page)
                    
        self.dialog.set_close(TRUE)

    def hydrate(self):
        if self.device.DeviceId:
            if self.device.BootProto == "static" or self.device.BootProto == "none":
                self.xml.get_widget('ipSettingCB').set_active(FALSE)
                if self.device.IP:
                    self.xml.get_widget('addressEntry').set_text(self.device.IP)
                if self.device.Netmask:
                    self.xml.get_widget('netmaskEntry').set_text(self.device.Netmask)
                if self.device.Gateway:
                    self.xml.get_widget('gatewayEntry').set_text(self.device.Gateway)
            else:
                self.xml.get_widget('ipSettingCB').set_active(TRUE)
                if self.device.Type == "ISDN" or self.device.Type == "Modem" or \
                   self.device.Type == "xDSL":
                    self.xml.get_widget("dynamicConfigEntry").set_text(_("dialup"))

            if self.device.Hostname:
                self.xml.get_widget('hostnameEntry').set_text(self.device.Hostname)

            if self.device.AutoDNS != None:
                self.xml.get_widget('dnsSettingCB').set_active(self.device.AutoDNS)

            clist = self.xml.get_widget('networkRouteList')
            clist.clear()

            if self.device.StaticRoutes != None:
                for route in self.device.StaticRoutes:
                    clist.append([route.Address, route.Netmask, route.Gateway])
            else:
                self.device.createStaticRoutes()
                
    def dehydrate(self):            
        if self.xml.get_widget('ipSettingCB').get_active(): 
            self.device.BootProto = self.xml.get_widget('dynamicConfigEntry').get_text()
            if self.device.BootProto == _('dialup'): self.device.BootProto = 'dialup'
            if self.device.BootProto == _('none'): self.device.BootProto = 'none'
            self.device.IP = ''
            self.device.Netmask = ''
            self.device.Gateway = ''
        else:
            self.device.BootProto = 'static'
            self.device.IP = self.xml.get_widget('addressEntry').get_text()
            self.device.Netmask = self.xml.get_widget('netmaskEntry').get_text()
            self.device.Gateway = self.xml.get_widget('gatewayEntry').get_text()

        self.device.Hostname = self.xml.get_widget('hostnameEntry').get_text()
        self.device.AutoDNS = self.xml.get_widget('dnsSettingCB').get_active()

    def on_Dialog_delete_event(self, *args):
        self.device.rollback()
    
    def on_okButton_clicked(self, button):
        self.dehydrate()
        self.device.commit()
    
    def on_cancelButton_clicked(self, button):
        self.device.rollback()
    
    def on_applyButton_clicked(self, button):
        self.dehydrate()
        self.device.commit()
    
    def on_ipSettingCB_toggled(self, check):
        self.xml.get_widget("dynamicConfigComboBox").set_sensitive(check["active"])
        self.xml.get_widget("ipSettingFrame").set_sensitive(check["active"] != TRUE)
        if check["active"]:
            self.xml.get_widget ("dynamicConfigEntry").grab_focus()
        else:
            self.xml.get_widget ("addressEntry").grab_focus()

    def on_defaultRouteCB_toggled(self, check):
        self.xml.get_widget("networkRouteFrame").set_sensitive(check["active"] != TRUE)

    def on_routeAddButton_clicked(self, button):
        if self.device.StaticRoutes == None: self.device.createStaticRoutes()
        routes = self.device.StaticRoutes
        route = Route()
        dialog = editAdressDialog(route, self.xml)
        dl = dialog.xml.get_widget ("Dialog")
        button = dl.run ()
        if button == 0:
            i = routes.addRoute()
            routes[i].apply(route)
            routes[i].commit()
        self.hydrate()

    def on_routeEditButton_clicked(self, button):
        routes = self.device.StaticRoutes
        clist  = self.xml.get_widget("networkRouteList")

        if len(clist.selection) == 0:
            return

        route = routes[clist.selection[0]]

        dialog = editAdressDialog(route, self.xml)
        dl = dialog.xml.get_widget ("Dialog")
        dl.run ()
        self.hydrate()

    def on_routeDeleteButton_clicked(self, button):
        if not self.device.StaticRoutes:
            self.device.createStaticRoutes()

        routes = self.device.StaticRoutes

        clist  = self.xml.get_widget("networkRouteList")
      
        if len(clist.selection) == 0:
            return

        del routes[clist.selection[0]]
        self.hydrate()

    def on_routeUpButton_clicked(self, button):
        routes = self.device.StaticRoutes
        clist = self.xml.get_widget("networkRouteList")

        if len(clist.selection) == 0 or clist.selection[0] == 0:
            return

        select_row = clist.selection[0]
        dest = clist.get_text(select_row, 0)
        prefix = clist.get_text(select_row, 1)
        gateway = clist.get_text(select_row, 2)

        rcurrent = routes[select_row]
        rnew = routes[select_row-1]
        
        routes[select_row] = rnew
        routes[select_row-1] = rcurrent
        
        self.hydrate()
        
        clist.select_row(select_row-1, 0)
            
    def on_routeDownButton_clicked(self, button):
        routes = self.device.StaticRoutes
        clist = self.xml.get_widget("networkRouteList")

        if len(clist.selection) == 0 or clist.selection[0] == len(routes)-1:
            return

        select_row = clist.selection[0]
        dest = clist.get_text(select_row, 0)
        prefix = clist.get_text(select_row, 1)
        gateway = clist.get_text(select_row, 2)

        rcurrent = routes[select_row]
        rnew = routes[select_row+1]
        
        routes[select_row] = rnew
        routes[select_row+1] = rcurrent
        
        self.hydrate()
        
        clist.select_row(select_row+1, 0)



# make ctrl-C work
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    window = basicDialog()
    gtk.mainloop()

