from NCDeviceList import *
from NCDevice import *
from NCProfileList import *
from NCHardwareList import *

class InterfaceCreator:
    def __init__ (self):
        raise NotImplementedError

    def get_project_name (self):
        raise NotImplementedError

    def get_project_description (self):
        raise NotImplementedError

    def get_druids (self):
        raise NotImplementedError

    def finish (self):
        raise NotImplementedError

    def save(self):
        self.saveDevices()
        self.saveHardware()
        self.saveProfiles()

    def saveDevices(self):
        devicelist = getDeviceList()
        devicelist.save()

    def saveHardware(self):
        hardwarelist = getHardwareList()
        hardwarelist.save()

    def saveProfiles(self):
        profilelist = getProfileList()
        profilelist.save()
