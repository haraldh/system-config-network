import sys
import NC_functions

import string

if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")

import Conf
import gettext

import DeviceList
from NC_functions import *

##
## I18N
##
gettext.bindtextdomain("netconf", "/usr/share/locale")
gettext.textdomain("netconf")
_=gettext.gettext

class Wireless(DeviceList.Wireless_base):
    keydict = { 'Mode' : 'MODE',
                'EssId' : 'ESSID',
                'Channel' : 'CHANNEL',
                'Freq' : 'FREQ',
                'Rate' : 'RATE',
                'Key' : 'KEY',
                }
    
    def __init__(self, list = None, parent = None):
        DeviceList.Wireless_base.__init__(self, list, parent)        
        
    def load(self, parentConf):
        conf = parentConf

        for selfkey in self.keydict.keys():
            confkey = self.keydict[selfkey]
            if conf.has_key(confkey):
                self.__dict__[selfkey] = conf[confkey]

    def save(self, parentConf):
        conf = parentConf

        for selfkey in self.keydict.keys():
            confkey = self.keydict[selfkey]
            if self.__dict__[selfkey]:
                conf[confkey] = str(self.__dict__[selfkey])
            else: conf[confkey] = ""

        for i in conf.keys():
            if not conf[i] or conf[i] == "": del conf[i]
