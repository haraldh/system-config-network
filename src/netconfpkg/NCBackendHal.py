
import string
import os
import sys
import dbus

from NCHardware import Hardware

HAL_DEVICE_IFACE = "org.freedesktop.Hal.Device"

class NCBackendHal:
    def __init__(self):

        self.doDebug = True

        self._dbusBus = dbus.SystemBus()
        self.halManagerObj = self._dbusBus.get_object("org.freedesktop.Hal", "/org/freedesktop/Hal/Manager")
        self.halManager = dbus.Interface(self.halManagerObj, "org.freedesktop.Hal.Manager")

        self.driverList = self.read_driver_list()

        self.cards = {}

    def destroy(self, args):
        return

    # ------------------------------------------------------------------------
    # Probe routines - drivers
    # ------------------------------------------------------------------------
    def read_driver_list(self):
        try:
            fd = open('/proc/asound/modules', 'r')
            list = fd.readlines()
            fd.close()
        except:
            return []

        drivers = []
        for line in list:
            tmp = line.split()
            drivers.append([int(tmp[0]), string.replace(tmp[1],'_','-')])

        return drivers

    def find_driver(self, list, position):
        for rec in list:
            if rec[0] == position:
                return rec[1]

        return _("Unknown")

    # ------------------------------------------------------------------------
    # Probe routines - HAL
    # ------------------------------------------------------------------------

    def getProperty(self, obj, prop):
        if not obj.PropertyExists(prop, dbus_interface=HAL_DEVICE_IFACE):
            return None
        return obj.GetProperty(prop, dbus_interface=HAL_DEVICE_IFACE)

    def getVendor(self, udi):
        parentUdi = udi
        while parentUdi and len(parentUdi):
            obj = self._dbusBus.get_object("org.freedesktop.Hal", parentUdi)

            vendor = self.getProperty(obj, "info.vendor")
            if vendor != None:
                return vendor, self.getProperty(obj, "info.product")

            new_parentUdi = self.getProperty(obj, "info.parent")
            if new_parentUdi == None:
                break
            parentUdi = new_parentUdi

    def getBus(self, udi):
        parentUdi = udi
        while parentUdi and len(parentUdi):
            obj = self._dbusBus.get_object("org.freedesktop.Hal", parentUdi)

            bus = self.getProperty(obj, "info.bus")
            if bus != None:
                return bus

            new_parentUdi = self.getProperty(obj, "info.parent")
            if new_parentUdi == None:
                break
            parentUdi = new_parentUdi

    def getDriver(self, udi):
        parentUdi = udi
        while parentUdi and len(parentUdi):
            obj = self._dbusBus.get_object("org.freedesktop.Hal", parentUdi)

            driver = self.getProperty(obj, "info.linux.driver")
            if driver != None:
                return driver

            new_parentUdi = self.getProperty(obj, "info.parent")
            if new_parentUdi == None:
                break
            parentUdi = new_parentUdi

    def getDevices(self, udi):
        obj = self._dbusBus.get_object("org.freedesktop.Hal", udi)
        category = self.getProperty(obj, "linux.subsystem")
        if category == "net" and self.getProperty(obj, "net.interface"):
            index = self.getProperty(obj, "net.physical_device")
            if index != None and not self.cards.has_key(index):
                card = Hardware()
                card.index = index
                card.active = True
                card.maker, card.model = self.getVendor(udi)
                card.Type = string.split(card.maker)[0]
                card.Bus = self.getBus(udi)
                card.ModuleName = self.find_driver(self.driverList, card.index)
                #card.driver = self.getDriver(udi)
                #card.device_list = card.loadCardDevices()
                print card
                self.cards[index] = card

    # TODO?
    # Only add USB audio devices that have snd-usb-audio as the driver
    #if card.bus() == "usb" and card.driver() != "snd-usb-audio":
    #    continue
    # Same with Mac sound devices
    #if card.bus() == "macio" and card.driver() != "snd-powermac":
    def probeCards(self):
        udiList = self.halManager.FindDeviceByCapability("net")
        for udi in udiList:
            self.getDevices(udi)

if __name__ == '__main__':
#    sys.path.append("../")
#    sys.path.append("./")
    hal = NCBackendHal()
    hal.probeCards()
