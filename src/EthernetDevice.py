#!/usr/bin/python
#
# This software may be freely redistributed under the terms of the GNU
# public license.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

"""
A generic network device class, containg data and functionality shared
between different kinds of network devices
"""

import Device
import Address
import os
import string
import re
import sys
if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")
import Conf

class EthernetDevice(Device.Device):
    """
    A specialization of the Device class for Ethernet devices
    """

    def __init__(self):
        """
        The initialization routine for an EthernetDevice object
        @self The object instance
        """

        Device.Device.__init__(self)
        self._macaddress=None
        self._bootproto=None

        # remove when proper routing is working
        self._gateway=None


    #remove when proper routing is working

    def setGateway(self,gateway):
        """
        FIXME: Remove
        """
        self._gateway=gateway

    def gateWay(self):
        """
        FIXME: Remove
        """
        return self._gateway

    def readHardware(self):
        """
        Read the active settings (and hardware specific details, like MAC addresses)
        @self The object instance
        """
        
        self._macaddress=self.HWid()
        self.setType(self.HWtype())
        self.setAddressList(self.HWaddressList())
        self.setEnabled(self.HWenabled())

    def writeHardware(self):
        """
        Apply the current configuration to the system
        @self The object instance
        """
        pass # To be written
                                 

    def setMACAddress(self,macaddress):
        """
        Set the MAC address for the EthernetDevice object
        @self The object instance
        @macaddress The new MAC address
        """
        self._macaddress=macaddress

    def getMACAddress(self):
        """
        Return the currently configured MAC address
        @self The object instance
        """

        return self._macaddress

    def setBootProto(self,boot):
        """
        Set the boot protocol for the EthernetDevice object
        @self The object instance
        @macaddress The new boot protocol
        """
        self._bootproto=bootproto

    def getBootProto(self):
        """
        Return the currently configured boot protocol
        @self The object instance
        """

        return self._bootproto
    
    def readConfig(self,filename):
        """
        Read the configuration of this device
        from the given file
        @self The object instance
        """
        
        addresses=Address.AddressList()
        addresses.readFile(filename)
        self.setAddressList(addresses)
        confFile=Conf.ConfShellVar(filename)


    def toString(self):
        """
        Return the current configuration in string
        form
        """

        res=Device.Device.toString(self)
        if self._macaddress:
            res=res+"MACADDRESS=%s\n" % (self._macaddress)
        
        return res
    




# These methods query the systems, not the objects, and are thus prefixed
# with HW


    def HWid(self):
        """returns the ID associated with this device, usually a MAC address."""
        text = os.popen("/sbin/ip -o link list %s 2>&1" % self.name()).read()
        try:
            id = re.search("link/\w+ (\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)",
                           text).groups()[0]
        except:
            id = "00:00:00:00:00:00"
        return id

    def HWsetId(self, newId):
        """set the ID of this device.  Returns 0 on failure; 1 on success."""
        if self.enabled():
            return 0

        if (os.system("/sbin/ip -o link set %d address %s 2>&1" % (
            self.name(), newId))):
            return 0
        else:
            return 1

    def HWtype(self):
        """return the type of device, i.e. "wireless", "ethernet", "loopback", etc."""
        if os.access("/sbin/iwconfig", os.X_OK):
            line = os.popen("/sbin/iwconfig %s 2>&1" % self.name()).read()
            if string.find(line, "no wireless extensions") == -1:
                return "wireless"

        devText = os.popen("/sbin/ip -o link list dev %s 2>&1" % self.name()).read()
        typeMatch = re.search("link/(\w+)", devText)
        if typeMatch:
            devType = typeMatch.groups()[0]
            if devType == "ether":
                return "ethernet"
            elif devType == "loopback":
                return "loopback"

        return "unknown"


    def HWaddressList(self):
        """returns a list of internet addresses (both IPv4 and IPv6)
        associated with this device, including aliases."""
        addrText = os.popen("/sbin/ip -f inet -o addr list dev %s 2>&1" %
                            self.name()).readlines()
        addrText = addrText + \
                   os.popen("/sbin/ip -f inet6 -o addr list dev %s 2>&1" %
                            self.name()).readlines()
        addressList = Address.AddressList()
        for line in addrText:
            broadcast = None
            try:
                type, address, prefix, broadcast, scope, device = \
                      re.search("\d+:\s+\w+\s+(\w+)\s+(\w*[:.]\w*[:.]\w*[:.]\w*:*\w*:*\w*)/(\d+)\s+brd\s+(\w*[:.]\w*[:.]\w*[:.]\w*:*\w*:*\w*)\s+scope\s+(\w+)\s+(\w+)", line).groups()
            except:
                try:
                    type, address, prefix, scope, device = \
                          re.search("\d+:\s+\w+\s+(\w+)\s+(\w*[:.]\w*[:.]\w*[:.]\w*:*\w*:*\w*)/(\d+)\s+scope\s+(\w+)\s+(\w+)", line).groups()
                except:
                    continue
            a = Address.Address()
            if address:
                a.setAddress(address)
            if prefix:
                a.setPrefix(prefix)
            if scope:
                a.setScope(scope)
            if broadcast:
                a.setBroadcast(broadcast)
            if device:
                a.setDevice(device)
            addressList.addAddress(a)
            
        return addressList

    def HWenabled(self):
        """returns 1 if a device is enabled (up), 0 otherwise."""
        text = os.popen("/sbin/ip -o link list %s 2>&1" % self.name()).read()
        if re.search("%s: <\S+,UP\S*>" % self.name(), text):
            return 1
        else:
            return 0

def test():
    """
    Test for EthernetDevice
    """

    device=EthernetDevice()
    device.setName("eth0")
    device.readHardware()
    print device.toString()

if __name__ == "__main__":
    import sys
    sys.exit(test())
