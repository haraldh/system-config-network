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

from netconfpkg.conf import Conf
from NC_functions import *
from netconfpkg import IPsec_base

class ConfIPsec(Conf.ConfShellVar):
    def __init__(self, name):
        Conf.ConfShellVar.__init__(self, getRoot() + SYSCONFDEVICEDIR + 'ifcfg-' + name)
        self.chmod(0644)

class IPsec(IPsec_base):
    #"IPsecId" : "IPSECID",
    boolkeydict = {
        'OnBoot' : 'ONBOOT',
        }
    ipsec_entries = {
        "LocalNetwork" : "SRCNET",
        "LocalGateway" : "SRCGW",
        "RemoteNetwork" : "DSTNET",
        "RemoteGateway" : "DSTGW",
        "RemoteIPAddress" : "DST",
        "OnBoot" : "ONBOOT",
        "SPI_AH_IN" : "SPI_AH_IN",
        "SPI_AH_OUT" : "SPI_AH_OUT",
        "SPI_ESP_IN" : "SPI_ESP_IN",
        "SPI_ESP_OUT" : "SPI_ESP_OUT",
        }
    key_entries = {
        "AHKey" : "KEY_AH",
        "ESPKey" : "KEY_ESP",
        "IKEKey" : "IKE_PSK",
        }

    def __init__(self, list = None, parent = None):
        IPsec_base.__init__(self, list, parent)
        self.oldname = None

    def load(self, name):
        # load ipsec

        conf = ConfIPsec(name)
        for selfkey in self.ipsec_entries.keys():
            confkey = self.ipsec_entries[selfkey]
            if conf.has_key(confkey):
                self.__dict__[selfkey] = conf[confkey] or None

        for selfkey in self.boolkeydict.keys():
            confkey = self.boolkeydict[selfkey]
            if conf.has_key(confkey):
                if conf[confkey] == 'yes':
                    self.__dict__[selfkey] = True
                else:
                    self.__dict__[selfkey] = False
            elif not self.__dict__.has_key(selfkey):
                self.__dict__[selfkey] = False

        conf = ConfKeys(name)
        for selfkey in self.key_entries.keys():
            confkey = self.key_entries[selfkey]
            if conf.has_key(confkey):
                self.__dict__[selfkey] = conf[confkey] or None

        if conf.has_key("IKE_PSK") and conf["IKE_PSK"]:
            self.EncryptionMode = "auto"
        else:
            self.EncryptionMode = "manual"

        if not self.IPsecId:
            self.IPsecId = name

        if self.LocalNetwork:
            vals = string.split(self.LocalNetwork, "/")
            if len(vals) >= 1:
                self.LocalNetwork = vals[0]
                self.LocalNetmask = bits_to_netmask(vals[1])

        if self.RemoteNetwork:
            vals = string.split(self.RemoteNetwork, "/")
            if len(vals) >= 1:
                self.RemoteNetwork = vals[0]
                self.RemoteNetmask = bits_to_netmask(vals[1])
            self.ConnectionType = "Net2Net"
        else:
            self.ConnectionType = "Host2Host"

        self.oldname = self.IPsecId

        self.commit(changed=False)
        pass

    def save(self):
        # FIXME: [163040] "Exception Occurred" when saving
        # fail gracefully, with informing, which file, and why

        # Just to be safe...
        os.umask(0022)
        self.commit()

        if self.oldname and (self.oldname != self.IPsecId):
            for prefix in [ 'ifcfg-', 'keys-' ]:
                rename(getRoot() + SYSCONFDEVICEDIR + \
                       prefix + self.oldname,
                       getRoot() + SYSCONFDEVICEDIR + \
                       prefix + self.IPsecId)

        # save ipsec settings
        conf = ConfIPsec(self.IPsecId)
        conf.fsf()
        conf["TYPE"] = "IPSEC"
        conf["DST"] = self.RemoteIPAddress

        if self.ConnectionType == "Net2Net":
            conf["SRCNET"] = self.LocalNetwork + "/" + \
                             str(netmask_to_bits(self.LocalNetmask))
            conf["DSTNET"] = self.RemoteNetwork + "/" + \
                             str(netmask_to_bits(self.RemoteNetmask))
            conf["SRCGW"] = self.LocalGateway
            conf["DSTGW"] = self.RemoteGateway
        else:
            for key in ["SRCNET", "DSTNET", "SRCGW", "DSTGW"]:
                del conf[key]

        if self.EncryptionMode == "auto":
            conf["IKE_METHOD"] = "PSK"
        else:
            del conf["IKE_METHOD"]
            spi_entries = { "SPI_AH_IN" : "SPI_AH_IN",
                            "SPI_AH_OUT" : "SPI_AH_OUT",
                            "SPI_ESP_IN" : "SPI_ESP_IN",
                            "SPI_ESP_OUT" : "SPI_ESP_OUT" }

            for selfkey in spi_entries.keys():
                confkey = spi_entries[selfkey]
                if self.__dict__[selfkey]:
                    conf[confkey] = str(self.__dict__[selfkey])
                else: conf[confkey] = ""


        for selfkey in self.boolkeydict.keys():
            confkey = self.boolkeydict[selfkey]
            if self.__dict__[selfkey]:
                conf[confkey] = 'yes'
            else:
                conf[confkey] = 'no'

        conf.write()

        conf = ConfKeys(self.IPsecId)
        conf.fsf()
        for selfkey in self.key_entries.keys():
            confkey = self.key_entries[selfkey]
            if self.__dict__[selfkey]:
                conf[confkey] = str(self.__dict__[selfkey])
            else: del conf[confkey]

        conf.write()

        #
        self.oldname = self.IPsecId

    def activate(self, dialog = None):
        command = '/sbin/ifup'
        param = [command, self.IPsecId, "up"]

        try:
            (ret, msg) =  generic_run_dialog(\
                command,
                param,
                catchfd = (1,2),
                title = _('IPsec activating...'),
                label = _('Activating IPsec connection %s, '
                          'please wait...') % (self.IPsecId),
                errlabel = _('Cannot activate '
                             'IPsec connection %s!\n') % (self.IPsecId),
                dialog = dialog)

        except RuntimeError, msg:
            ret = -1

        return ret, msg

    def deactivate(self, dialog = None):
        command = '/sbin/ifdown'
        param = [command, self.IPsecId, "down"]

        try:
            (ret, msg) = generic_run_dialog(\
                command, param,
                catchfd = (1,2),
                title = _('IPsec deactivating...'),
                label = _('Deactivating IPsec connection %s, '
                          'please wait...') % (self.IPsecId),
                errlabel = _('Cannot deactivate '
                             'IPsec connection %s!\n') % (self.IPsecId),
                dialog = dialog)

        except RuntimeError, msg:
            ret = -1

        return ret, msg

import netconfpkg
netconfpkg.IPsec = IPsec
