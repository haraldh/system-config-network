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
import gnome
import gnome.help
import gnome.ui
import gnome.config
import libglade
import signal
import os
import GdkImlib
import string

from gtk import TRUE
from gtk import FALSE

##
## I18N
##
import gettext
gettext.bindtextdomain ("netconf", "/usr/share/locale")
gettext.textdomain ("netconf")
_=gettext.gettext

netconfDir = "/usr/share/netconf"
gladePath = "netconf.glade"

if not os.path.exists(gladePath):
    gladePath = netconfDir + "/netconf.glade"

xml = libglade.GladeXML (gladePath, domain="netconf")

def delete_event (win, event = None):
    win.hide ()
    # don't destroy window, just leave it hidden
    return TRUE

def on_exit_activate (*args):
    gtk.mainquit()
    
def on_mainDialog_delete_event (*args):
    on_exit_activate (args)
    return TRUE

def on_mainOkButton_clicked (*args):
    gtk.mainquit ()

def on_mainCancelButton_clicked (*args):
    gtk.mainquit ()

def on_mainHelpButton_clicked (*args):
    pass

def on_deviceAddButton_clicked (clicked):
    dialog = xml.get_widget ("basicDialog")
    dialog.set_title ("Add new Device")
    dialog.show ()

def on_deviceCopyButton_clicked (*args):
    pass

def on_deviceRenameButton_clicked (*args):
    pass

def on_deviceEditButton_clicked (*args):
    dialog = xml.get_widget ("basicDialog")
    dialog.set_title ("Edit Device")
    dialog.show ()

def on_deviceDeleteButton_clicked (*args):
    pass

def on_deviceList_select_row (*args):
    pass

def on_deviceList_click_column (*args):
    pass

def on_dnsList_select_row (*args):
    pass

def on_dnsAddButton_clicked (*args):
    pass

def on_dnsEditButton_clicked (*args):
    pass

def on_dnsUpButton_clicked (*args):
    pass

def on_dnsDownButton_clicked (*args):
    pass

def on_dnsDeleteButton_clicked (*args):
    pass

def on_profileList_click_column (*args):
    pass

def on_profileList_select_row (*args):
    pass

def on_profileAddButton_clicked (*args):
    pass

def on_profileCopyButton_clicked (*args):
    pass

def on_profileRenameButton_clicked (*args):
    pass

def on_profileDeleteButton_clicked (*args):
    pass

def on_okButton_clicked ():
    pass

def on_cancelButton_clicked (button):
    xml.get_widget ("basicDialog").hide ()

def on_helpButton_clicked (*args):
    pass

def on_deviceNameEntry_changed (entry):
    deviceName = string.strip (entry.get_text ())
    xml.get_widget ("deviceTypeMenu").set_sensitive (len(deviceName) > 0)
    xml.get_widget ("deviceConfigureButton").set_sensitive (len(deviceName) > 0)
    
def on_advancedButton_clicked (button):
    deviceType = xml.get_widget ("deviceTypeMenu").get_menu()
    index = deviceType.children().index (deviceType.get_active())
    
    if index == 0:
        xml.get_widget ("ethernetConfigDialog").show ()
    elif index == 1 or index == 2:
        xml.get_widget ("DialupConfigDialog").show ()
    elif index == 3:
        xml.get_widget ("dslConfigDialog").show ()
    elif index == 4:
        xml.get_widget ("wirelessDeviceConfigDialog").show ()

def on_onBootCB_toggled (check):
    pass

def on_userControlCB_toggled (check):
    pass

def on_ipSettingCB_toggled (check):
    xml.get_widget ("dynamicConfigMenu").set_sensitive (check["active"])
    xml.get_widget ("ipSettingFrame").set_sensitive (check["active"] != TRUE)

def on_dynamicConfigMenu_clicked (menu):
    pass

def on_addressEntry_changed (entry):
    pass

def on_netmaskEntry_changed (entry):
    pass

def on_gatewayEntry_changed (entry):
    pass

def on_hostnameEntry_changed (entry):
    pass

def on_domainEntry_changed (entry):
    pass

def on_dnsSettingCB_toggled (check):
    pass

def on_defaultRouteCB_toggled (check):
    xml.get_widget ("networkRouteFrame").set_sensitive (check["active"] != TRUE)

def on_networkRouteList_click_column (*args):
    pass

def on_networkRouteList_select_row (*args):
    pass

def on_routeAddButton_clicked (click):
    xml.get_widget ("editAddressDialog").show ()

def on_routeEditButton_clicked (*args):
    pass

def on_routeDeleteButton_clicked (*args):
    pass

def on_dialupOkButton_enter (*args):
    pass

def on_dialupCancelButton_clicked (click):
    xml.get_widget ("DialupConfigDialog").hide()

def on_dialupHelpButton_clicked (click):
    pass

def on_configureButton_clicked (click):
    xml.get_widget ("isdnConfigDialog").show ()

def on_msnEntry_changed (*args):
    pass

def on_dialingRuleCB_toggled (*args):
    pass

def on_prefixEntry_changed (*args):
    pass

def on_areaCodeEntry_changed (*args):
    pass

def on_phoneEntry_changed (*args):
    pass

def on_countryCodeEntry_changed (*args):
    pass

def on_authMenu_enter (*args):
    pass

def on_providerTree_tree_select_row (*args):
    pass

def on_providerTree_click_column (*args):
    pass

def on_providerTree_select_row (*args):
    pass

def on_dialupProviderNameEntry_changed (*args):
    pass

def on_dialupLoginNameEntry_activate (*args):
    pass

def on_dialupPasswordEntry_changed (*args):
    pass

def on_HeaderCompressionCB_toggled (*args):
    pass

def on_connectionCompressionCB_toggled (*args):
    pass

def on_acCompressionCB_toggled (*args):
    pass

def on_pcCompressionCB_toggled (*args):
    pass

def on_bsdCompressionCB_toggled (*args):
    pass

def on_cppCompressionCB_toggled (*args):
    pass

def on_pppOptionEntry_changed (*args):
    pass

def on_pppOptionAddButton_clicked (*args):
    pass

def on_pppOptionList_click_column (*args):
    pass

def on_pppOptionList_select_row (*args):
    pass

def on_pppOptionDeleteButton_clicked (*args):
    pass

def on_isdnOkButton_clicked (*args):
    pass

def on_isdnCancelButton_clicked (clicked):
    xml.get_widget ("isdnConfigDialog").hide ()

def on_isdnHelpButton_clicked (*args):
    pass

def on_isdnDeviceMenu_clicked (*args):
    pass

def on_encapModeMenu_clicked (*args):
    pass

def on_hangupTimeoutSpinButton_changed (*args):
    pass

def setup ():
    accountPixmapPath = "keys.png"
    if not os.path.exists (accountPixmapPath):
        accountPixmapPath = "/usr/share/pixmaps/" + accountPixmapPath
        
    xml.get_widget ("accountPixmap").load_file (accountPixmapPath)
        

def main ():
    xml.signal_autoconnect (
        {
        "delete_event" : delete_event,
        # netconf
        "on_mainDialog_delete_event" : on_mainDialog_delete_event,
        "on_mainOkButton_clicked" : on_mainOkButton_clicked,
        "on_mainCancelButton_clicked" : on_mainCancelButton_clicked,
        "on_mainHelpButton_clicked" : on_mainHelpButton_clicked,
        "on_deviceAddButton_clicked" : on_deviceAddButton_clicked,
        "on_deviceCopyButton_clicked" : on_deviceCopyButton_clicked,
        "on_deviceRenameButton_clicked" : on_deviceRenameButton_clicked,
        "on_deviceEditButton_clicked" : on_deviceEditButton_clicked,
        "on_deviceDeleteButton_clicked" : on_deviceDeleteButton_clicked,
        "on_deviceList_select_row" : on_deviceList_select_row,
        "on_deviceList_click_column" : on_deviceList_click_column,
        "on_dnsList_select_row" : on_dnsList_select_row,
        "on_dnsAddButton_clicked" : on_dnsAddButton_clicked,
        "on_dnsEditButton_clicked" : on_dnsEditButton_clicked,
        "on_dnsUpButton_clicked" : on_dnsUpButton_clicked,
        "on_dnsDownButton_clicked" : on_dnsDownButton_clicked,
        "on_dnsDeleteButton_clicked" : on_dnsDeleteButton_clicked,
        "on_profileList_click_column": on_profileList_click_column,
        "on_profileList_select_row" : on_profileList_select_row,
        "on_profileAddButton_clicked" : on_profileAddButton_clicked,
        "on_profileCopyButton_clicked" : on_profileCopyButton_clicked,
        "on_profileRenameButton_clicked" : on_profileRenameButton_clicked,
        "on_profileDeleteButton_clicked" : on_profileDeleteButton_clicked,
        # Add / Edit Device
        "on_okButton_clicked" : on_okButton_clicked,
        "on_cancelButton_clicked" : on_cancelButton_clicked,
        "on_helpButton_clicked" : on_helpButton_clicked,
        "on_deviceNameEntry_changed" : on_deviceNameEntry_changed,
        "on_advancedButton_clicked" : on_advancedButton_clicked,
        "on_onBootCB_toggled" : on_onBootCB_toggled,
        "on_userControlCB_toggled" : on_userControlCB_toggled,
        "on_ipSettingCB_toggled" : on_ipSettingCB_toggled,
        "on_dynamicConfigMenu_clicked" : on_dynamicConfigMenu_clicked,
        "on_addressEntry_changed" : on_addressEntry_changed,
        "on_netmaskEntry_changed" : on_netmaskEntry_changed,
        "on_gatewayEntry_changed" : on_gatewayEntry_changed,
        "on_hostnameEntry_changed" : on_hostnameEntry_changed,
        "on_domainEntry_changed" : on_domainEntry_changed,
        "on_dnsSettingCB_toggled" : on_dnsSettingCB_toggled,
        "on_defaultRouteCB_toggled" : on_defaultRouteCB_toggled,
        "on_networkRouteList_click_column" : on_networkRouteList_click_column,
        "on_networkRouteList_select_row" : on_networkRouteList_select_row,
        "on_routeAddButton_clicked" : on_routeAddButton_clicked,
        "on_routeEditButton_clicked" : on_routeEditButton_clicked,
        "on_routeDeleteButton_clicked" : on_routeDeleteButton_clicked,
        # Dialup Configuration
        "on_dialupOkButton_enter" : on_dialupOkButton_enter,
        "on_dialupCancelButton_clicked" : on_dialupCancelButton_clicked,
        "on_dialupHelpButton_clicked" : on_dialupHelpButton_clicked,
        "on_configureButton_clicked" : on_configureButton_clicked,
        "on_msnEntry_changed" : on_msnEntry_changed,
        "on_dialingRuleCB_toggled" : on_dialingRuleCB_toggled,
        "on_prefixEntry_changed" : on_prefixEntry_changed,
        "on_areaCodeEntry_changed" : on_areaCodeEntry_changed,
        "on_phoneEntry_changed" : on_phoneEntry_changed,
        "on_countryCodeEntry_changed" : on_countryCodeEntry_changed,
        "on_authMenu_enter" : on_authMenu_enter,
        "on_providerTree_tree_select_row" : on_providerTree_tree_select_row,
        "on_providerTree_click_column" : on_providerTree_click_column,
        "on_providerTree_select_row" : on_providerTree_select_row,
        "on_dialupProviderNameEntry_changed" : on_dialupProviderNameEntry_changed,
        "on_dialupLoginNameEntry_activate" : on_dialupLoginNameEntry_activate,
        "on_dialupPasswordEntry_changed" : on_dialupPasswordEntry_changed,
        "on_HeaderCompressionCB_toggled" : on_HeaderCompressionCB_toggled,
        "on_connectionCompressionCB_toggled" : on_connectionCompressionCB_toggled,
        "on_acCompressionCB_toggled" : on_acCompressionCB_toggled,
        "on_pcCompressionCB_toggled" : on_pcCompressionCB_toggled,
        "on_bsdCompressionCB_toggled" : on_bsdCompressionCB_toggled,
        "on_cppCompressionCB_toggled" : on_cppCompressionCB_toggled,
        "on_pppOptionEntry_changed" : on_pppOptionEntry_changed,
        "on_pppOptionAddButton_clicked" : on_pppOptionAddButton_clicked,
        "on_pppOptionList_click_column" : on_pppOptionList_click_column,
        "on_pppOptionList_select_row" : on_pppOptionList_select_row,
        "on_pppOptionDeleteButton_clicked" : on_pppOptionDeleteButton_clicked,
        # ISDN Configuration
        "on_isdnOkButton_clicked" : on_isdnOkButton_clicked,
        "on_isdnCancelButton_clicked" : on_isdnCancelButton_clicked,
        "on_isdnHelpButton_clicked" : on_isdnHelpButton_clicked,
        "on_isdnDeviceMenu_clicked" : on_isdnDeviceMenu_clicked,
        "on_encapModeMenu_clicked" : on_encapModeMenu_clicked,
        "on_hangupTimeoutSpinButton_changed" : on_hangupTimeoutSpinButton_changed
        })

    setup ()
    xml.get_widget ("mainDialog").show_all ()
    gtk.mainloop ()

# make ctrl-C work
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    main ()
    
