from DeviceList import *
from NC_functions import *

class Callback(Callback_base):
    boolkeydict = { 'Compression' : 'CBCP', }
    
    keydict = { 'Number' : 'PHONE_IN',
                'Type' : 'CALLBACK',
                }

    intkeydict = { 'Hup' : 'CBHUP',
                   'Delay' : 'CBDELAY',
                   }

    def __init__(self, list = None, parent = None):
        Callback_base.__init__(self, list, parent)        

    def load(self, parentConf):
        conf = parentConf
        
        for selfkey in self.keydict.keys():
            confkey = self.keydict[selfkey]
            if conf.has_key(confkey):
                self.__dict__[selfkey] = conf[confkey]

        for selfkey in self.intkeydict.keys():
            confkey = self.intkeydict[selfkey]
            if conf.has_key(confkey) and len(conf[confkey]):
                self.__dict__[selfkey] = int(conf[confkey])

        for selfkey in self.boolkeydict.keys():
            confkey = self.boolkeydict[selfkey]
            if conf.has_key(confkey):
                if conf[confkey] == 'on':
                    self.__dict__[selfkey] = true
                else:
                    self.__dict__[selfkey] = false            
            else:
                self.__dict__[selfkey] = false            

    def save(self, parentConf):
        conf = parentConf
        
        for selfkey in self.keydict.keys():
            confkey = self.keydict[selfkey]
            if self.__dict__[selfkey]:
                conf[confkey] = str(self.__dict__[selfkey])
            else: conf[confkey] = ""

        for selfkey in self.intkeydict.keys():
            confkey = self.intkeydict[selfkey]
            if self.__dict__[selfkey]:
                conf[confkey] = str(self.__dict__[selfkey])
            else: conf[confkey] = ""

        for selfkey in self.boolkeydict.keys():
            confkey = self.boolkeydict[selfkey]
            if self.__dict__[selfkey]:
                conf[confkey] = 'on'
            else:
                conf[confkey] = 'off'

        if conf.has_key('CALLBACK') and conf['CALLBACK'] == "off":
            if conf.has_key('CBCP'): del conf['CBCP']
