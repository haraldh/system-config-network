from DeviceList import *
from NC_functions import *

class Compression(Compression_base):
    boolkeydict = { 'VJTcpIp' : 'VJ',
                    'VJID' : 'VJCCOMP',
                    'AdressControl' : 'AC',
                    'ProtoField' : 'PC',
                    'BSD' : 'BSDCOMP',
                    'CCP' : 'CCP',
                    }
    
    keydict = { 'Hup' : 'CBHUP',
                'Delay' : 'CBDELAY',
                'Number' : 'PHONE_IN',
                }

    def __init__(self, list = None, parent = None):
        Compression_base.__init__(self, list, parent)        

    def load(self, parentConf):
        conf = parentConf
        
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

        for selfkey in self.boolkeydict.keys():
            confkey = self.boolkeydict[selfkey]
            if self.__dict__[selfkey]:
                conf[confkey] = 'on'
            else:
                conf[confkey] = 'off'
    
