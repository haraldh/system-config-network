#!/usr/bin/python
#
# Network Interface Library
# Copyright (c) 2001 Red Hat, Inc. All rights reserved.
#
# This software may be freely redistributed under the terms of the GNU
# public license.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
# Author: Preston Brown <pbrown@redhat.com>

__author__ = "Preston Brown <pbrown@redhat.com>"
__date__ = "02 May 2001"
__version__ = "$Revision: 1.2 $"

import os
import re
import string

class NetDevice:
    """A generic base class describing a network device.  Do not
    instantiate this class directly; use on of the concrete
    subclasses."""
    
    def __init__(self, name="unknown", description="unknown device",
                 enabled=0, addressList=[], routeList=[]):
        self._name = name
        self._description = description
        self._id = None
        self._enabled = enabled
        self._addressList = addressList
        self._routeList = routeList
        self._type = "unknown"
        
    def name(self):
        return self._name

    def type(self):
        return self._type

    def id(self):
        return self._id

    def enabled(self):
        return self._enabled

    def addressList(self):
        return self._addressList

    def routeList(self):
        return self._routeList
    
    def __repr__(self):
        msg = "Name: %s, Type: %s, ID: %s, Enabled: %d, Addresses: %s, Routes: %s" % \
              (self.name(), self.type(), self.id(), self.enabled(),
               self.addressList(), self.routeList())
        return msg

class RealDevice(NetDevice):
    """Describes a real networking device that is present on the
    system.  All of the values are read from the hardware as
    requested.  Changes are made immediately."""
    
    def __init__(self, name):
        """name is the name of the hardware device to reflect."""
        NetDevice.__init__(self, name)

        text = os.popen("/sbin/ip -o link list %s 2>&1" % self.name()).read()
        # does it really exist?
        if re.match("^\d+: %s:" % self.name(), text):
            self.description = "Active network device"
            # the rest are to be determined at query time.
        else:
            self.description = "no such device present"

    def id(self):
        """returns the ID associated with this device, usually a MAC address."""
        text = os.popen("/sbin/ip -o link list %s 2>&1" % self.name()).read()
        try:
            id = re.search("link/\w+ (\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)",
                           text).groups()[0]
        except:
            id = "00:00:00:00:00:00"
        return id

    def setId(self, newId):
        """set the ID of this device.  Returns 0 on failure; 1 on success."""
        if self.enabled():
            return 0

        if (os.system("/sbin/ip -o link set %d address %s 2>&1" % (
            self.name(), newId))):
            return 0
        else:
            return 1
        
                      
    def type(self):
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

    def enabled(self):
        """returns 1 if a device is enabled (up), 0 otherwise."""
        text = os.popen("/sbin/ip -o link list %s 2>&1" % self.name()).read()
        if re.search("%s: <\S+,UP\S*>" % self.name(), text):
            return 1
        else:
            return 0

    def addressList(self):
        """returns a list of internet addresses (both IPv4 and IPv6)
        associated with this device, including aliases."""
        addrText = os.popen("/sbin/ip -f inet -o addr list dev %s 2>&1" %
                            self.name()).readlines()
        addrText = addrText + \
                   os.popen("/sbin/ip -f inet6 -o addr list dev %s 2>&1" %
                            self.name()).readlines()
        addressList = []
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
            a = Address(type, address, prefix, broadcast, scope, device)
            addressList.append(a)
            
        return addressList

    def routeList(self):
        """returns a list of routes associated with this device."""
        routeText = os.popen("/sbin/ip -o route list dev %s 2>&1" %
                             self.name()).readlines()
        routeList = []

        for line in routeText:
            source = None
            dest = None
            prefix = None
            gateway = None
            device = self.name()
            scope = "global"

            destMatch = re.search("^(\w*[:.]\w*[:.]\w*[:.]\w*:*\w*:*\w*/*\d*|default)", line)
            if destMatch:
                dest = destMatch.groups()[0]
                if string.find(dest, "/") != -1:
                    dest, prefix = re.search("(\S+)/(\d+)", dest).groups()
            else:
                continue
            sourceMatch = re.search("src (\w*[:.]\w*[:.]\w*[:.]\w*:*\w*:*\w*)", line)
            if sourceMatch:
                source = sourceMatch.groups()[0]
            scopeMatch = re.search("scope (\w+)", line)
            if scopeMatch:
                scope = scopeMatch.groups()[0]
            gwMatch = re.search("via (\w*[:.]\w*[:.]\w*[:.]\w*:*\w*:*\w*)", line)
            if gwMatch:
                gateway = gwMatch.groups()[0]
                        
            route = Route(dest, prefix, source, gateway, device, scope)
            routeList.append(route)

        return routeList

    def essid(self):
        """For wireless devices, returns the ESS (network) ID string
        for the device.  Otherwise, returns None."""
        if self.type() != "wireless":
            return None

        line = os.popen("/sbin/iwconfig %s 2>&1" % self.name()).read()
        return re.search("ESSID:\"(\w+)\"", line).groups()[0]

    def setEssid(self, essid):
        """Set the ESS (network) ID for this wireless device.  Returns
        1 on success; 0 on failure."""
        if self.type() != "wireless":
            return 0

        if (os.system("/sbin/iwconfig %s essid %s > /dev/null 2>&1" % (
            self.name(), essid))):
            return 0
        else:
            return 1

    def nickname(self):
        """Returns the nickname (usually a hostname) of this device if
        it is wireless.  Otherwise, returns None."""
        if self.type() != "wireless":
            return None

        line = os.popen("/sbin/iwconfig %s 2>&1" % self.name()).read()
        return re.search("Nickname:\"(\w+)\"", line).groups()[0]

    def setNickname(self, nickname):
        """Set the nickname of this device/station on a wireless
        network.  Returns 1 on success; 0 on failure."""
        if self.type() != "wireless":
            return 0

        if (os.system("/sbin/iwconfig %s nick %s > /dev/null 2>&1" % (
            self.name(), nickname))):
            return 0
        else:
            return 1

    def mode(self):
        """Returns the mode the wireless device is operating in,
        i.e. "Ad-Hoc", "Managed", etc.  If not wireless, returns
        None."""
        if self.type() != "wireless":
            return None

        line = os.popen("/sbin/iwconfig %s 2>&1" % self.name()).read()
        return re.search("Mode:(\S+)", line).groups()[0]

    def setMode(self, mode):
        """Change the mode of the wireless device.  Mode must be a
        string understood by the wireless device's driver.  Returns 1
        on success; 0 on failure."""
        if self.type() != "wireless":
            return 0

        if (os.system("/sbin/iwconfig %s mode %s > /dev/null 2>&1" % (
            self.name(), mode))):
            return 0
        else:
            return 1
    
    def freq(self):
        """Returns the frequency this wireless device is operating on."""
        if self.type() != "wireless":
            return None

        line = os.popen("/sbin/iwconfig %s 2>&1" % self.name()).read()
        return re.search("Frequency:(\S+)", line).groups()[0]

    def setFreq(self, freq):
        """Set the frequency this device is operating on.  Returns 1
        on success; 0 on failure."""
        if self.type() != "wireless":
            return 0

        if (os.system("/sbin/iwconfig %s freq %s > /dev/null 2>&1" % (
            self.name(), freq))):
            return 0
        else:
            return 1

    def cell(self):
        """Returns the MAC address of the cell (access point)
        associated with this device.  Only makes sense if the device
        is in "Managed" mode."""
        if self.type() != "wireless":
            return None

        line = os.popen("/sbin/iwconfig %s 2>&1" % self.name()).read()
        return re.search("Cell:\s*(\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)", line).groups()[0]

    def setCell(self, cell):
        """Sets the MAC address of the cell (access point) to
        associate the device with.  Only makes sense if the device is
        wireless and in "Managed" mode.  Returns 1 on success; 0 on
        failure."""
        if self.type() != "wireless":
            return 0

        if (os.system("/sbin/iwconfig %s ap %s > /dev/null 2>&1" % (
            self.name(), cell))):
            return 0
        else:
            return 1

    def rate(self):
        """Returns the current transmit rate for the device, or None if
        the device is not wireless."""
        if self.type() != "wireless":
            return None

        line = os.popen("/sbin/iwconfig %s 2>&1" % self.name()).read()
        return re.search("Bit Rate(:|=)\s*(\d+|[:alpha:]+)", line).groups()[1]

    def setRate(self, rate):
        """Sets the transmit rate for the device.  Values are
        device-dependent, but usually "1M", "2M", "5M", "11M", and
        "auto" are understood.  Returns 1 on success; 0 on failure."""
        if self.type() != "wireless":
            return 0

        if (os.system("/sbin/iwconfig %s rate %s > /dev/null 2>&1" % (
            self.name(), rate))):
            return 0
        else:
            return 1
class Route:
    """This is a a simple class that describes a route, and allows you to
    add and remove it from the system as well."""
    def __init__(self, dest, prefix, source, gateway, device, scope):
        self.dest = dest
        self.prefix = prefix
        self.source = source
        self.gateway = gateway
        self.device = device
        self.scope = scope

    def __repr__(self):
        msg = "(Destination: %s, Prefix: %s, Source: %s, Gateway: %s, Device: %s, Scope: %s)" % (self.dest, self.prefix, self.source, self.gateway, self.device, self.scope)
        return msg

    def add(self):
        """Physically add the route that this object describes to the
        system.  Returns 1 if request succeeds; 0 on failure."""
        cmd = "/sbin/ip route add %s" % self.dest
        if self.prefix:
            cmd = cmd + "/%s" % self.prefix
        if self.scope:
            cmd = cmd + " scope %s" % self.scope
        if self.gateway:
            cmd = cmd + " via %s" % self.gateway
        if self.device:
            cmd = cmd + " dev %s" % self.device
        if self.source:
            cmd = cmd + " src %s" % self.source
            
        if os.system(cmd):
            return 0
        else:
            return 1

    def delete(self):
        """Physically remove the route that this object describes to the
        system.  Returns 1 if request succeeds; 0 on failure."""
        cmd = "/sbin/ip route del %s" % self.dest
        if self.prefix:
            cmd = cmd + "/%s" % self.prefix
        if self.scope:
            cmd = cmd + " scope %s" % self.scope
        if self.gateway:
            cmd = cmd + " via %s" % self.gateway
        if self.device:
            cmd = cmd + " dev %s" % self.device
        if self.source:
            cmd = cmd + " src %s" % self.source
            
        if os.system(cmd):
            return 0
        else:
            return 1

class Address:
    """Describes an internet address."""
    def __init__(self, type, address, prefix, broadcast, scope, device):
        self.type = type
        self.address = address
        self.prefix = prefix
        self.broadcast = broadcast
        self.scope = scope
        self.device = device

    def __repr__(self):
        msg = "%s/%s" % (self.address, self.prefix)
        return msg    

    def add(self):
        """Physically add the address that this object describes to
        the associated device on the system.  Returns 1 if it
        succeeds; 0 on failure."""
        cmd = "/sbin/ip addr add %s/%s dev %s" % (
            self.address, self.prefix, self.device)
        if self.broadcast:
            cmd = cmd + " brd %s" % self.broadcast
        if self.scope:
            cmd = cmd + " scope %s" % self.scope

        if os.system(cmd):
            return 0
        else:
            return 1

    def delete(self):
        """Physically remove the address that this object describes
        from the associated device on the system.  Returns 1 if it
        succeeds; 0 on failure."""
        cmd = "/sbin/ip addr del %s/%s dev %s" % (
            self.address, self.prefix, self.device)

        if os.system(cmd):
            return 0
        else:
            return 1

def test(deviceName):
    """Test case for RealDevice class."""
    
    print "Text of RealDevice for %s..." % deviceName
    print "------------------------------"
    dev = RealDevice(deviceName)
    print "ID:", dev.id()
    print "Type:", dev.type()
    if dev.enabled():
        print "Device is enabled"
    else:
        print "Device is disabled"
    if dev.type() == "wireless":
        print "ESSID:", dev.essid()
        print "Nickname:", dev.nickname()
        print "Mode:", dev.mode()
        print "Frequency:", dev.freq()
        print "Cell:", dev.cell()
        print "Rate:", dev.rate()
    print "Addresses:"
    for address in dev.addressList():
        print "\t", address
    print "Routes:"
    for route in dev.routeList():
        print "\t", route
    
if __name__ == "__main__":
    test("eth0")
