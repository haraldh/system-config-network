import re
import traceback
import sys
import os
import os.path
import shutil

OLDSYSCONFDEVICEDIR='/etc/sysconfig/network-scripts/'
SYSCONFDEVICEDIR='/etc/sysconfig/networking/devices/'
SYSCONFPROFILEDIR='/etc/sysconfig/networking/profiles/'
SYSCONFNETWORK='/etc/sysconfig/network'

deviceTypes = [ 'Ethernet',
                'Modem',
                'ISDN',
                'Loopback',
                'xDSL',
                'CIPE',
                'Wireless'
                ]

deviceTypeDict = {'^eth[0-9]+(:[0-9]+)?$':'Ethernet',
               '^ppp[0-9]+(:[0-9]+)?$':'Modem',
               '^ippp[0-9]+(:[0-9]+)?$':'ISDN',
               '^irlan[0-9]+(:[0-9]+)?$':'Wireless',
               '^cipe[0-9]+(:[0-9]+)?$':'CIPE',
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
    if not os.path.isdir(SYSCONFDEVICEDIR):
        os.mkdir(SYSCONFDEVICEDIR)

    if not os.path.isdir(SYSCONFPROFILEDIR):
        os.mkdir(SYSCONFPROFILEDIR)

    if not os.path.isdir(SYSCONFPROFILEDIR+'/default/'):
        os.mkdir(SYSCONFPROFILEDIR+'/default/')

    devlist = os.listdir(OLDSYSCONFDEVICEDIR)
    for dev in devlist:
        if dev[:6] != 'ifcfg-':
            continue

        if os.path.islink(OLDSYSCONFDEVICEDIR+'/'+dev):
            #print dev+" already a symlink, skipping it."
            continue

        if getDeviceType(dev[6:]) == 'Unknown':
            #print dev+" has unknown device type, skipping it."
            continue

        print "Copying "+dev+" to devices and putting it into the default profile."

        try:
            os.unlink(SYSCONFPROFILEDIR+'/default/'+dev)
        except:
            pass

        try:
            shutil.copy(OLDSYSCONFDEVICEDIR+'/'+dev, SYSCONFDEVICEDIR+'/'+dev)
            os.symlink(SYSCONFDEVICEDIR+'/'+dev, SYSCONFPROFILEDIR+'/default/'+dev)
#            os.symlink(SYSCONFPROFILEDIR+'/default/'+dev, OLDSYSCONFDEVICEDIR+'/'+dev)
        except:
            print "An error occured during the conversion of device "+dev+", skipping."
            (type, value, tb) = sys.exc_info()
            list = traceback.format_exception (type, value, tb)
            print list
            continue

    if not os.path.islink('/etc/hosts'):
       print "Copying /etc/hosts to default profile."
       try:
           shutil.copy('/etc/hosts', SYSCONFPROFILEDIR+'/default/hosts')
       except:
           print "An error occured during moving the /etc/hosts file."

    if not os.path.islink('/etc/resolv.conf'):
       print "Copying /etc/resolv.conf to default profile."
       try:
           shutil.copy('/etc/resolv.conf', SYSCONFPROFILEDIR+'/default/resolv.conf')
       except:
           print "An error occured during moving the /etc/resolv.conf file."
