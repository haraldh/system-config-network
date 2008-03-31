## Copyright (C) 2001-2005 Red Hat, Inc.
## Copyright (C) 2001-2005 Harald Hoyer <harald@redhat.com>

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

from NC_functions import *
from netconfpkg import Hardware_base


HW_INACTIVE = _("inactive") # not found in last config and not in actual system
HW_SYSTEM = _("system")   # found in system
HW_CONF = _("configured")     # found in config but not in system
HW_OK = _("ok")       # found in system and in config

class Hardware(Hardware_base):
    def __init__(self, list = None, parent = None):
        Hardware_base.__init__(self, list, parent)
        self.Status = HW_INACTIVE

    def getDialog(self):
        return None

    def getWizard(self):
        return None

    def isType(self, device):
        return None

    def save(self):
        return None

    def postSave(self):
        return None
    
    def saveModule(self):
        from netconfpkg.NCHardwareList import getMyConfModules, getHardwareList
        if not self.Card.ModuleName:
            return
        hl = getHardwareList()
        modules = getMyConfModules()
        dic = modules[self.Name]
        if dic:
            dic['alias'] = self.Card.ModuleName
            modules[self.Name] = dic
            log.lch(2, modules.filename, "%s alias %s" % (self.Name, self.Card.ModuleName))
        # No, no, no... only delete known options!!!
        #WRONG: modules[self.Card.ModuleName] = {}
        #WRONG: modules[self.Card.ModuleName]['options'] = {}
        #
        # Better do it this way!
        
        if (modules.has_key(self.Card.ModuleName) and modules[self.Card.ModuleName].has_key('options')):
            for (key, confkey) in hl.keydict.items():
                if modules[self.Card.ModuleName]['options'].has_key(confkey):
                    del modules[self.Card.ModuleName]['options'][confkey]
                
            
        
        for (selfkey, confkey) in hl.keydict.items():
            if self.Card.__dict__[selfkey]:
                if (not (selfkey == 'IRQ' and (self.Card.IRQ == _('Unknown') or (self.Card.IRQ == 'Unknown')))):
                    dic = modules[self.Card.ModuleName]
                    if not dic.has_key('options'):
                        dic['options'] = {}
                    
                    dic['options'][confkey] = str(self.Card.__dict__[selfkey])
                    modules[self.Card.ModuleName] = dic



__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2007/03/14 09:29:37 $"
__version__ = "$Revision: 1.12 $"
