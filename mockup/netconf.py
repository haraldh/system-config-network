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

import sys

netconf_dir = "/usr/share/netconf"
sys.path.append (netconf_dir)

import gtk
import GDK
import GTK
import libglade
import signal
import os
import GdkImlib
import string

from gtk import TRUE
from gtk import FALSE
from gtk import CTREE_LINES_DOTTED

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
    xml.get_widget ("deviceNameEntry").grab_focus ()
    dialog = xml.get_widget ("basicDialog")
    dialog.set_title (_("Add an new Device"))
    dialog.show ()

def on_deviceCopyButton_clicked (button):
    pass

def on_deviceRenameButton_clicked (button):
    pass

def on_deviceEditButton_clicked (*args):
    dialog = xml.get_widget ("basicDialog")
    dialog.set_title ("Edit Device")
    dialog.show ()

def on_deviceDeleteButton_clicked (button):
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
    xml.get_widget ("deviceTypeComboBox").set_sensitive (len(deviceName) > 0)
    xml.get_widget ("deviceConfigureButton").set_sensitive (len(deviceName) > 0)

def on_deviceTypeEntry_changed (entry):
    pass

def on_advancedButton_clicked (button):
    noteBook = xml.get_widget ("dialupNotebook")
    dialog = xml.get_widget ("DialupConfigDialog")
    deviceType = xml.get_widget ("deviceTypeEntry").get_text ()

    ## need to show all widgets in dialup notebook
    noteBook.show_all()
    
    ## show the 1 page as default
    noteBook.set_page(0);
    
    if deviceType == "Arcnet":
        pass
    elif deviceType == "Ethernet":
        xml.get_widget ("ethernetConfigDialog").show ()
    elif deviceType == "Modem":
        ## hide some widgets which are not used here
        for i in [1,2,5,7]:
            noteBook.get_nth_page (i).hide ()
        dialog.set_title ("Modem Dialup Configuration")
        dialog.show ()
    elif deviceType == "ISDN":
        ## hide some widgets which are not used here
        noteBook.get_nth_page (1).hide ()
        noteBook.get_nth_page (3).hide ()
        dialog.set_title ("ISDN Dialup Configuration")
        xml.get_widget ("DialupConfigDialog").show ()
    elif deviceType == "xDSL":
        ## hide some widgets which are not used here
        for i in [0,2,3,5,6,7]:
            noteBook.get_nth_page (i).hide ()
        dialog.set_title ("xDSL Configuration")
        dialog.show ()
    elif deviceType == "Wireless":
        xml.get_widget ("wirelessDeviceConfigDialog").show ()
    elif deviceType == "Token Ring":
        pass
    elif deviceType == "Pocket (ATP)":
        pass
    elif deviceType == "SLIP":
        pass
    elif deviceType == "PLIP":
        pass
    elif deviceType == "CIPE":
        pass
    elif deviceType == "CTC":
        pass
    
def on_onBootCB_toggled (check):
    pass

def on_userControlCB_toggled (check):
    pass

def on_ipSettingCB_toggled (check):
    xml.get_widget ("dynamicConfigComboBox").set_sensitive (check["active"])
    xml.get_widget ("ipSettingFrame").set_sensitive (check["active"] != TRUE)
    if check["active"]:
        xml.get_widget ("dynamicConfigEntry").grab_focus ()
    else:
        xml.get_widget ("addressEntry").grab_focus ()

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

def on_dialingRuleCB_toggled (check):
    prefixEntry = xml.get_widget ("prefixEntry")
    prefixEntry.set_sensitive (check["active"])
    xml.get_widget ("areaCodeEntry").set_sensitive (check["active"])
    xml.get_widget ("countryCodeCombo").set_sensitive (check["active"])
    ## set right focus
    if check["active"]:
        prefixEntry.grab_focus ()
    else:
        xml.get_widget ("phoneEntry").grab_focus ()

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

def on_pppOptionEntry_changed (entry):
    option = string.strip (entry.get_text ())
    xml.get_widget ("pppOptionAddButton").set_sensitive (len (option) > 0)

def on_pppOptionAddButton_clicked (button):
    entry = xml.get_widget ("pppOptionEntry")
    xml.get_widget ("ipppOptionList").set_sensitive (TRUE)
    xml.get_widget ("ipppOptionList").append ([entry.get_text ()])
    entry.set_text("")
    entry.grab_focus()
    
def on_pppOptionList_select_row (clist, r, c, event):
    xml.get_widget ("pppOptionDeleteButton").set_sensitive (TRUE)
    
def on_ipppOptionList_unselect_row (clist, r, c, event):
    xml.get_widget ("pppOptionDeleteButton").set_sensitive (FALSE)

def on_pppOptionDeleteButton_clicked (button):
    clist = xml.get_widget ("ipppOptionList")
    if clist.selection:
        clist.remove(clist.selection[0])

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

def on_callbackCB_toggled (check):
    xml.get_widget ("callbackFrame").set_sensitive (check["active"])
    xml.get_widget ("dialinNumberEntry").grab_focus()

def on_aliasSupportCB_toggled (check):
    xml.get_widget ("aliasSpinBox").set_sensitive (check["active"])

def set_icon (widget, pixmapFile):
    if os.path.exists (pixmapFile):
        pix, mask = gtk.create_pixmap_from_xpm (gtk.GtkWindow (), None, pixmapFile)
        widget.set (pix, mask)

def setup_provider_db():
    dbtree = xml.get_widget ("providerTree")
    dbtree.set_line_style(CTREE_LINES_DOTTED)
    pix, mask = gtk.create_pixmap_from_xpm (dbtree, None, "de.xpm")
    node1 = dbtree.insert_node(None, None, ["Germany"], 5, pix, mask, pix, mask, is_leaf=FALSE)
    node2 = dbtree.insert_node(node1, None, ["T Online"])
    node3 = dbtree.insert_node(node1, None, ["Freenet"])
    pix, mask = gtk.create_pixmap_from_xpm (dbtree, None, "us.xpm")
    node4 = dbtree.insert_node(None, None, ["America"], 5, pix, mask, pix, mask, is_leaf=FALSE)
    node5 = dbtree.insert_node(node4, None, ["ATT"])
    node6 = dbtree.insert_node(node4, None, ["Bell"])
    pix, mask = gtk.create_pixmap_from_xpm (dbtree, None, "no.xpm")
    node7 = dbtree.insert_node(None, None, ["Norway"], 5, pix, mask, pix, mask, is_leaf=FALSE)
    node8 = dbtree.insert_node(node7, None, ["Nextra"])
    
def setup ():
    accountPixmap = xml.get_widget ("accountPixmap")
    networkPixmap = xml.get_widget ("networkPixmap")
    basicNotebook = xml.get_widget ("basicNotebook")
    set_icon (accountPixmap, "keys.xpm")
    set_icon (networkPixmap, "network.xpm")
    for i in [4,5,6]:
        basicNotebook.get_nth_page (i).hide ()

    setup_provider_db()
    
def main ():
    xml.signal_autoconnect (
        {
        "delete_event" : delete_event,
        ## netconf
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
        ## Add / Edit Device
        "on_okButton_clicked" : on_okButton_clicked,
        "on_cancelButton_clicked" : on_cancelButton_clicked,
        "on_helpButton_clicked" : on_helpButton_clicked,
        "on_deviceNameEntry_changed" : on_deviceNameEntry_changed,
        "on_deviceTypeEntry_changed" : on_deviceTypeEntry_changed,
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
        ## Dialup Configuration
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
        "on_pppOptionList_select_row" : on_pppOptionList_select_row,
        "on_ipppOptionList_unselect_row" : on_ipppOptionList_unselect_row,
        "on_pppOptionDeleteButton_clicked" : on_pppOptionDeleteButton_clicked,
        "on_isdnOkButton_clicked" : on_isdnOkButton_clicked,
        "on_isdnCancelButton_clicked" : on_isdnCancelButton_clicked,
        "on_isdnHelpButton_clicked" : on_isdnHelpButton_clicked,
        "on_isdnDeviceMenu_clicked" : on_isdnDeviceMenu_clicked,
        "on_encapModeMenu_clicked" : on_encapModeMenu_clicked,
        "on_hangupTimeoutSpinButton_changed" : on_hangupTimeoutSpinButton_changed,
        "on_callbackCB_toggled" : on_callbackCB_toggled,
        ## ethernetConfigDialog
        "on_aliasSupportCB_toggled" : on_aliasSupportCB_toggled
        })

    setup ()
    xml.get_widget ("mainDialog").show_all ()
    gtk.mainloop ()

# make ctrl-C work
if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)
    main ()
    
