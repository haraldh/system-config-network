#!/usr/bin/python

import gtk

import gtk
import gtk.glade
import signal
import os

import string
import re
from netconfpkg import NCHardwareList
from netconfpkg import NC_functions
from rhpl import ethtool

from netconfpkg.gui import GUI_functions
from netconfpkg.gui.GUI_functions import load_icon
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect

from editadress import editAdressDialog
from netconfpkg import *
import sys, traceback
from gtk import TRUE
from gtk import FALSE

###
### DHCP
###

DHCP=0
BOOTP=1
DIALUP=2

def on_ipBootProto_toggled(widget, xml):
    if widget.name == "ipAutomaticRadio":
        active = widget.get_active()
    else:
        active = not widget.get_active()
        
    xml.get_widget('ipProtocolOmenu').set_sensitive(active)
    xml.get_widget('dhcpSettingFrame').set_sensitive(active)
    xml.get_widget('ipSettingFrame').set_sensitive(not active)

def dhcp_init (xml, device):
    xml_signal_autoconnect(xml, {\
        "on_ipAutomaticRadio_toggled" : (on_ipBootProto_toggled, xml),
        "on_ipStaticRadio_toggled" : (on_ipBootProto_toggled, xml),
        })
    on_ipBootProto_toggled(xml.get_widget('ipAutomaticRadio'), xml)

def dhcp_hydrate (xml, device):
    if not device.DeviceId:
        return

    try:
        device_type = device.BootProto
    except:
        if device.Type == "ISDN" or device.Type == "Modem" or \
               device.Type == "xDSL":
            device_type = 'dialup'
        else:
            device_type = 'dhcp'

        
    if device.Hostname:
        xml.get_widget('hostnameEntry').set_text(device.Hostname)
    else:
        xml.get_widget('hostnameEntry').set_text('')

    if device.IP:
        xml.get_widget('ipAddressEntry').set_text(device.IP)
    else:
        xml.get_widget('ipAddressEntry').set_text('')
    if device.Netmask:
        xml.get_widget('ipNetmaskEntry').set_text(device.Netmask)
    else:
        xml.get_widget('ipNetmaskEntry').set_text('')
    if device.Gateway:
        xml.get_widget('ipGatewayEntry').set_text(device.Gateway)
    else:
        xml.get_widget('ipGatewayEntry').set_text('')

    if device_type == 'dialup':
        xml.get_widget("ipProtocolOmenu").set_history(DIALUP)
    elif device_type == 'bootp':
        xml.get_widget("ipProtocolOmenu").set_history(BOOTP)
    else:
        xml.get_widget("ipProtocolOmenu").set_history(DHCP)

    xml.get_widget('dnsSettingCB').set_active(device.AutoDNS == TRUE)

    if device.BootProto == "static" or device.BootProto == "none":
        xml.get_widget('ipAutomaticRadio').set_active(FALSE)
        xml.get_widget('ipStaticRadio').set_active(TRUE)
        on_ipBootProto_toggled(xml.get_widget('ipAutomaticRadio'), xml)
    else:
        xml.get_widget('ipAutomaticRadio').set_active(TRUE)
        xml.get_widget('ipStaticRadio').set_active(FALSE)
        on_ipBootProto_toggled(xml.get_widget('ipStaticRadio'), xml)


def dhcp_dehydrate (xml, device):
    if xml.get_widget('ipAutomaticRadio').get_active():
        if GUI_functions.get_history (xml.get_widget ('ipProtocolOmenu')) == DHCP:
            device.BootProto = 'dhcp'
        elif GUI_functions.get_history (xml.get_widget ('ipProtocolOmenu')) == BOOTP:
            device.BootProto = 'bootp'
        elif GUI_functions.get_history (xml.get_widget ('ipProtocolOmenu')) == DIALUP:
            device.BootProto = 'dialup'
        else:
            device.BootProto = 'none'
    else:
        device.BootProto = 'none'

    device.AutoDNS = xml.get_widget('dnsSettingCB').get_active()
    device.IP = xml.get_widget('ipAddressEntry').get_text()
    device.Netmask = xml.get_widget('ipNetmaskEntry').get_text()
    device.Gateway = xml.get_widget('ipGatewayEntry').get_text()
    hname = xml.get_widget('hostnameEntry').get_text()
    if hname != None and hname != '':
        device.Hostname = hname

###
### ROUTES
###
def route_update(xml, device):
    clist = xml.get_widget('networkRouteList')
    clist.clear()

    if device.StaticRoutes != None:
        for route in device.StaticRoutes:
            clist.append([route.Address, route.Netmask, route.Gateway])
    else:
        device.createStaticRoutes()

def on_routeEditButton_clicked(button, xml, device, parent_dialog):
    routes = device.StaticRoutes
    clist  = xml.get_widget("networkRouteList")

    if len(clist.selection) == 0:
        return

    route = routes[clist.selection[0]]

    dialog = editAdressDialog(route)
    dl = dialog.xml.get_widget ("Dialog")

    if parent_dialog:
        dl.set_transient_for(parent_dialog)
        dl.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
    else:
        dl.set_position (gtk.WIN_POS_CENTER)
        
    if dl.run() != gtk.RESPONSE_OK:
        dl.destroy()        
        return
    dl.destroy()
    route_update(xml, device)

    
def on_routeDeleteButton_clicked(button, xml, device):
    if not device.StaticRoutes:
        device.createStaticRoutes()

    routes = device.StaticRoutes

    clist  = xml.get_widget("networkRouteList")

    if len(clist.selection) == 0:
        return

    del routes[clist.selection[0]]
    route_update(xml, device)

def on_routeUpButton_clicked(button, xml, device):
    routes = device.StaticRoutes
    clist = xml.get_widget("networkRouteList")

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

    route_update(xml, device)

    clist.select_row(select_row-1, 0)

def on_routeDownButton_clicked(button, xml, device):
    routes = device.StaticRoutes
    clist = xml.get_widget("networkRouteList")

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

    route_update(xml, device)

    clist.select_row(select_row+1, 0)

def on_routeAddButton_clicked(button, xml, device, parent_dialog):
    if device.StaticRoutes == None:
        device.createStaticRoutes()
    routes = device.StaticRoutes
    route = Route()
    dialog = editAdressDialog(route)
    dl = dialog.xml.get_widget ("Dialog")    

    if parent_dialog:
        dl.set_transient_for(parent_dialog)
        dl.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
    else:
        dl.set_position (gtk.WIN_POS_CENTER)
        
    button = dl.run()
    dl.destroy()
    if button != gtk.RESPONSE_OK:
        return
    i = routes.addRoute()
    routes[i].apply(route)
    #routes[i].commit()
    route_update(xml, device)

def route_init(xml, device, dialog = None):
    xml_signal_autoconnect(xml, { \
        "on_routeAddButton_clicked" : (on_routeAddButton_clicked,
                                       xml, device, dialog),
        "on_routeEditButton_clicked" : (on_routeEditButton_clicked,
                                        xml, device, dialog),
        "on_routeDeleteButton_clicked" : (on_routeDeleteButton_clicked,
                                          xml, device),
        })
    route_update(xml, device)


def route_hydrate(xml, device):
    pass

def route_dehydrate(xml, device):
    pass

###
### Hardware (ethernet)
###


def on_hardwareAliasesToggle_toggled(widget, xml, device):
    xml.get_widget("hardwareAliasesSpin").set_sensitive (widget.get_active())

def on_hardwareMACToggle_toggled(widget, xml, device):
    xml.get_widget("hardwareMACEntry").set_sensitive (widget.get_active())
    xml.get_widget("hardwareProbeButton").set_sensitive (widget.get_active())

def on_hardwareProbeButton_clicked(widget, xml, device):
    omenu = xml.get_widget("hardwareDeviceOmenu")
    hw = omenu.get_children()[0].get()
    device = string.split(hw)[0]
    try: hwaddr = ethtool.get_hwaddr(device) 
    except IOError, err:
        error_str = str (err)
        GUI_functions.gui_error_dialog(error_str, omenu.get_toplevel())
    else:
        xml.get_widget("hardwareMACEntry").set_text(hwaddr)
    
def on_hardwareConfigureButton_clicked(widget, xml, device):
    pass


    
def hardware_init(xml, device):
    xml_signal_autoconnect(xml, {\
        "on_hardwareAliasesToggle_toggled" : \
        (on_hardwareAliasesToggle_toggled, xml, device),
        "on_hardwareMACToggle_toggled" : \
        (on_hardwareMACToggle_toggled, xml, device),
        "on_hardwareProbeButton_clicked" : \
        (on_hardwareProbeButton_clicked, xml, device),
        "on_hardwareConfigureButton_clicked" : \
        (on_hardwareConfigureButton_clicked, xml, device)
        })
    xml.get_widget("hardwareSeparator").show()
    xml.get_widget("hardwareTable").show()

def hardware_hydrate(xml, device):
    hwlist = getHardwareList()
    (hwcurr, hwdesc) = NC_functions.create_ethernet_combo(hwlist, device.Device)
    omenu = xml.get_widget("hardwareDeviceOmenu")
    omenu.remove_menu()
    menu = gtk.Menu()
    history = 0
    for i in range (0, len (hwdesc)):
        item = gtk.MenuItem (hwdesc[i])
        item.show()
        menu.append (item)
        if hwdesc[i] == hwcurr:
            history = i
    omenu.set_menu (menu)
    omenu.show_all()
    omenu.set_history (history)
    omenu.show_all()

    if device.Alias != None:
        xml.get_widget("hardwareAliasesToggle").set_active(FALSE)
        xml.get_widget("hardwareAliasesToggle").set_active(TRUE)
        xml.get_widget("hardwareAliasesSpin").set_value(device.Alias)
    else:
        xml.get_widget("hardwareAliasesToggle").set_active(TRUE)
        xml.get_widget("hardwareAliasesToggle").set_active(FALSE)

    if device.HardwareAddress != None:
        xml.get_widget("hardwareMACToggle").set_active(FALSE)
        xml.get_widget("hardwareMACToggle").set_active(TRUE)
        xml.get_widget("hardwareMACEntry").set_text(device.HardwareAddress)
        xml.get_widget("hardwareMACEntry").set_sensitive(TRUE)
        xml.get_widget("hardwareProbeButton").set_sensitive(TRUE)
    else:
        xml.get_widget("hardwareMACToggle").set_active(TRUE)
        xml.get_widget("hardwareMACToggle").set_active(FALSE)
        xml.get_widget("hardwareMACEntry").set_text('')
        xml.get_widget("hardwareMACEntry").set_sensitive(FALSE)
        xml.get_widget("hardwareProbeButton").set_sensitive(FALSE)

def hardware_dehydrate(xml, device):
    omenu = xml.get_widget("hardwareDeviceOmenu")
    hw = omenu.get_child().get_label()
    device.Device = string.split(hw)[0]
    if xml.get_widget("hardwareAliasesToggle").get_active():
        device.Alias = xml.get_widget("hardwareAliasesSpin").get_value_as_int()
    else:
        device.Alias = None
    if xml.get_widget("hardwareMACToggle").get_active():
        device.HardwareAddress = xml.get_widget("hardwareMACEntry").get_text()
    else:
        device.HardwareAddress = None


def dsl_hardware_init(xml, device):
    pass

def dsl_hardware_hydrate(xml, device):
    hwlist = getHardwareList()
    (hwcurr, hwdesc) = NC_functions.create_ethernet_combo(hwlist, device.Dialup.EthDevice)
    omenu = xml.get_widget("hardwareDeviceOmenu")
    omenu.remove_menu()
    menu = gtk.Menu()
    history = 0
    for i in range (0, len (hwdesc)):
        item = gtk.MenuItem (hwdesc[i])
        item.show()
        menu.append (item)
        if hwdesc[i] == hwcurr:
            history = i
    omenu.set_menu (menu)
    omenu.show_all()
    omenu.set_history (history)
    omenu.show_all()


def dsl_hardware_dehydrate(xml, device):
    omenu = xml.get_widget("hardwareDeviceOmenu")
    hw = omenu.get_child().get_label()
    device.Dialup.EthDevice = string.split(hw)[0]

if __name__ == '__main__':
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    xml = gtk.glade.XML('sharedtcpip.glade', None, domain=GUI_functions.PROGNAME)
    dhcp_init (xml, None)
    gtk.mainloop ()
