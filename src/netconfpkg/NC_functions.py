import re
import traceback
import sys
import os
import os.path

OLDSYSCONFDEVICEDIR='/etc/sysconfig/network-scripts/'
SYSCONFDEVICEDIR='/etc/sysconfig/networking/devices/'
SYSCONFPROFILEDIR='/etc/sysconfig/networking/profiles/'
SYSCONFNETWORK='/etc/sysconfig/network'

deviceTypes = [ 'Ethernet',
                'Modem',
                'ISDN',
                'Loopback',
                'xDSL',
                ]

deviceTypeDict = {'^eth[0-9]+(:[0-9]+)?$':'Ethernet',
               '^ppp[0-9]+(:[0-9]+)?$':'Modem',
               '^ippp[0-9]+(:[0-9]+)?$':'ISDN',
               '^lo$':'Loopback'}

def generic_error_dialog (message, parent_dialog, dialog_type="warning", widget=None, page=0, broken_widget=None):
    import gnome
    import gnome.ui

    dialog = gnome.ui.GnomeMessageBox (message, dialog_type, "Button_Ok")
    dialog.set_parent (parent_dialog)
    if widget != None:
        if isinstance (widget, gtk.GtkCList):
            widget.select_row (page, 0)
        elif isinstance (widget, gtk.GtkNotebook):
            widget.set_page (page)
    if broken_widget != None:
        broken_widget.grab_focus ()
        if isinstance (broken_widget, gtk.GtkEntry):
            broken_widget.select_region (0, -1)
    dialog.run ()

def getDeviceType(devname):
    type = 'Unknown'
    if not devname or devname == "":
        return type
    
    for i in deviceTypeDict.keys():
        if re.search(i, devname):
            type = deviceTypeDict[i]
    return type

def updateNetworkScripts():
    devlist = os.listdir(OLDSYSCONFDEVICEDIR)

    if not os.path.isdir(SYSCONFDEVICEDIR):
        os.mkdir(SYSCONFDEVICEDIR)

    if not os.path.isdir(SYSCONFPROFILEDIR):
        os.mkdir(SYSCONFPROFILEDIR)

    if not os.path.isdir(SYSCONFPROFILEDIR+'/default/'):
        os.mkdir(SYSCONFPROFILEDIR+'/default/')

    for dev in devlist:
        if dev[:6] != 'ifcfg-':
            continue

        if os.path.islink(OLDSYSCONFDEVICEDIR+'/'+dev):
            #print dev+" already a symlink, skipping it."
            continue

        if getDeviceType(dev[6:]) == 'Unknown':
            #print dev+" has unknown device type, skipping it."
            continue

        print "Moving "+dev+" to devices and putting it into the default profile."

        try:
            os.unlink(SYSCONFDEVICEDIR+'/'+dev)
        except:
            pass

        try:
            os.unlink(SYSCONFPROFILEDIR+'/default/'+dev)
        except:
            pass

        try:
            os.rename(OLDSYSCONFDEVICEDIR+'/'+dev, SYSCONFDEVICEDIR+'/'+dev)
            os.symlink(SYSCONFDEVICEDIR+'/'+dev, SYSCONFPROFILEDIR+'/default/'+dev)
            os.symlink(SYSCONFPROFILEDIR+'/default/'+dev, OLDSYSCONFDEVICEDIR+'/'+dev)
        except:
            print "An error occured during the conversion of device "+dev+", skipping."
            (type, value, tb) = sys.exc_info()
            list = traceback.format_exception (type, value, tb)
            print list
            continue

def activateDevice (deviceid, profile, state=None):
    from DeviceList import *
    from ProfileList import *

    devicelist = getDeviceList()
    profilelist = getProfileList()

    for prof in profilelist:
        if prof.Profilename != profile:
            continue
        if state:
            if deviceid not in prof.ActiveDevices:
                prof.ActiveDevices.append(deviceid)
        else:
            if deviceid in prof.ActiveDevices:
                del prof.ActiveDevices[prof.ActiveDevices.index(name)]

def switchToProfile(val):
    from DeviceList import *
    from HardwareList import *
    from ProfileList import *

    global devicelist, hardwarelist, profilelist
    devicelist = getDeviceList()
    hardwarelist = getHardwareList()
    profilelist = getProfileList()

    found = false
    for prof in profilelist:
        if prof.ProfileName == val:
            found = true
            break

    if found == false:
        print "No Profile with name "+val+" could be found."
        return

    for prof in profilelist:
        if prof.ProfileName == val:
            prof.Active = true
        else:
            prof.Active = false

    print "Switching to Profile "+val

    devicelist.save()
    hardwarelist.save()
    profilelist.save()
