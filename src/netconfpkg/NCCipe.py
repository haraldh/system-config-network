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

class ConfCipeOptions(Conf.Conf):
    def __init__(self, name):
        fname = '/etc/cipe/options.' + name
        Conf.Conf.__init__(self, fname, '#', '\t ', ' ')
        self.chmod(0600)

    def read(self):
        Conf.Conf.read(self)
        self.initvars()

    def initvars(self):
        self.vars = {}
        self.rewind()
        while self.findnextcodeline():
            #print self.getline()
            var = self.getfields()
            self.vars[var[0]] = var[1]
            self.nextline()
        self.rewind()
        
    def __getitem__(self, varname):
        if self.vars.has_key(varname):
            return self.vars[varname]
        else:
            return None
        
    def __setitem__(self, varname, value):
        # set first (should be only) instance to values in list value
        place=self.tell()
        self.rewind()
        # not a nameserver, so all items on one line...
        if self.findnextline('^' '[' + self.separators + ']*' + varname +
                             '[' + self.separators + ']+'):
            self.deleteline()
            self.insertlinelist([ varname, value ])
            self.seek(place)
        else:
            self.seek(place)
            self.insertlinelist([ varname, value ])
        # no matter what, update our idea of the variable...
        self.vars[varname] = value
        
    def __delitem__(self, varname):
        # delete *every* instance...
        self.rewind()
        while self.findnextline('[' + self.separators + ']*' + varname +
                                '[' + self.separators + ']'):
            self.deleteline()
        del self.vars[varname]
        
    def write(self):
        for key in self.vars.keys():
            self[key] = self.vars[key]
        Conf.Conf.write(self)
        
    def keys(self):
        return self.vars.keys()
    
    def has_key(self, key):
        return self.vars.has_key(key)

        
class Cipe(DeviceList.Cipe_base):
    intkeydict = {'LocalPort' : 'MYPORT',
                  }
    
    keydict = { 'RemotePeerAddress' : 'PEER',
                'RemoteVirtualAddress' : 'PTPADDR',
                }
    
    def __init__(self, list = None, parent = None):
        DeviceList.Cipe_base.__init__(self, list, parent)        
        
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


        parent = self.getParent()
        if parent:
            conf = ConfCipeOptions(parent.DeviceId)
            if conf.has_key('key'):
                self.SecretKey = conf['key']
                
        self.commit()

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

        for i in conf.keys():
            if not conf[i] or conf[i] == "": del conf[i]

        
        conf = ConfCipeOptions(parent.DeviceId)
        parent = self.getParent()
        if parent and self.SecretKey:
            conf['key'] = self.SecretKey
        if not conf.has_key("maxerr"): conf["maxerr"] = -1
        if not conf.has_key("cttl"): conf["cttl"] = 64
        
        conf.write()
