"Tokenring Hardware Device Plugin"
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

from netconfpkg.NCHardware import Hardware
from netconfpkg.NCHardwareFactory import getHardwareFactory
from netconfpkg.NC_functions import TOKENRING, getHardwareType, _

_hwTokenringDialog = None
_hwTokenringWizard = None

class HwTokenring(Hardware):
    "Tokenring Hardware Device Class"
    def __init__(self, mlist = None, parent = None):
        Hardware.__init__(self, mlist, parent)
        self.Type = TOKENRING
        self.createCard() # pylint: disable-msg=E1101

    def getDialog(self):
        """
        returns a gtk dialog
        """
        if _hwTokenringDialog == None:
            return None
        if hasattr(_hwTokenringDialog, "getDialog"):
            return _hwTokenringDialog(self).getDialog()
        return _hwTokenringDialog(self).xml.get_widget("Dialog")

    def getWizard(self):
        """
        returns a gtk wizard
        """
        return _hwTokenringWizard

    def isType(self, hardware):
        """
        check if device is of type ISDN
        """
        if hardware.Type == TOKENRING:
            return True
        if getHardwareType(hardware.Hardware) == TOKENRING:
            return True
        return False

    def save(self, *args, **kwargs): # pylint: disable-msg=W0613
        """
        save the Tokenring configuration
        """
        from netconfpkg.NCHardwareList import getMyConfModules, getHardwareList

        hl = getHardwareList()

        # pylint: disable-msg=E1101

        modules = getMyConfModules()
        dic = modules[self.Name]
        dic['alias'] = self.Card.ModuleName
        modules[self.Name] = dic

        # No, no, no... only delete known options!!!
        #WRONG: modules[self.Card.ModuleName] = {}
        #WRONG: modules[self.Card.ModuleName]['options'] = {}
        #
        # Better do it this way!
        if modules[self.Card.ModuleName].has_key('options'):
            for confkey in hl.keydict.values():
                if modules[self.Card.ModuleName]\
                       ['options'].has_key(confkey):
                    del modules[self.Card.ModuleName]['options'][confkey]

        for (selfkey, confkey) in hl.keydict.items():
            if self.Card.__dict__[selfkey]:
                if selfkey == 'IRQ' \
                   and (self.Card.IRQ == _('Unknown') \
                        or (self.Card.IRQ == 'Unknown')):
                    continue
                dic = modules[self.Card.ModuleName]
                if not dic.has_key('options'):
                    dic['options'] = {}
                dic['options'][confkey] = \
                                        str(self.Card.__dict__[selfkey])
                modules[self.Card.ModuleName] = dic


def setHwTokenringDialog(dialog):
    """
    Set the gtk Dialog
    """
    global _hwTokenringDialog # pylint: disable-msg=W0603
    _hwTokenringDialog = dialog

def setHwTokenringWizard(wizard):
    """
    Set the gtk Wizard
    """
    global _hwTokenringWizard # pylint: disable-msg=W0603
    _hwTokenringWizard = wizard

def register_plugin():
    __df = getHardwareFactory()
    __df.register(HwTokenring, TOKENRING)

__author__ = "Harald Hoyer <harald@redhat.com>"
