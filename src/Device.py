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

import os

NETCFGPATH="/etc/syconfig/networking"

class Device:
    """
    The class containing common fields for all classes of devices.
    """

    def __init__(self):
        """
        The initialization of the common device.
        @self The object instance
        """
        
        self._name=None
        self._addressList=None
        self._routeList=[]
        self._enabled=None
        self._identifier=None
        self._type=None
        self._description=None


    def readConfig(self,filename):
        """
        Read the configuration data for the device from the given file
        @self The object instance
        @filename The file to read the configuration from
        """

        # implement in subclasses
        pass
    

    def writeConfig(self,profile="default",mode=0644):
        """
        Write the configuration data for the device to the given file
        @self The object instance
        @filename The profile to apply the data to
        @mode The permissons for the configuration file - default 0644
        """

        filename="%s/%s/ifcfg-%s" %(NETCFGPATH,profile,self._name)
        fd = os.open(filename, os.O_WRONLY | os.O_CREAT| os.O_TRUNC, mode)
        file = os.fdopen(fd, "w")
        file.write(self.toString())
        file.close()


    def readHardware(self):
        """
        Read the active settings (and hardware specific details, like MAC addresses)
        @self The object instance
        """

        # implement in subclasses
        pass


    def writeHardware(self):
        """
        Apply the current settings to the device
        @self The object instance
        """
        

    def name(self):
        """
        Return the name of the Device object
        @self The object instance
        """

        return self._name

    def setName(self,name):
        """
        Set the name of the Device object
        @self The object instance
        @name The new name
        """

        self._name=name

    def description(self):
        """
        Return the description of the Device object
        @self The object instance
        """

        return self._description

    def setDescription(self,description):
        """
        Set the description of the Device object
        @self The object instance
        @description The new description
        """

        self._description=description

    def isEnabled(self):
        """
        Return whether or not the Device object is enabled
        @self The object instance
        """

        return self._enabled
    
    def setEnabled(self,enabled):
        """
        Set the enabled status of the Device object
        @self The object instance
        @enabled The new enabled status
        """

        self._enabled=enabled
    
        
    def identifier(self):
        """
        Return the identifier of the Device object
        @self The object instance
        """

        return self._identifier

    def setIdentifier(self,identifier):
        """
        Set the identifier of the Device object
        @self The object instance
        @identifier The new identifier
        """

        self._identifier=identifier
        
    def type(self):
        """
        Return the type of the Device object
        @self The object instance
        """

        return self._type

    def setType(self,type):
        """
        Set the type of the Device object
        @self The object instance
        @type The new type
        """

        self._type=type
        
    def addressList(self):
        """
        Return the list of addresses  of the Device object, type Address.AddressList
        @self The object instance
        """

        return self._addressList

    def setAddressList(self,list):
        """
        Set the AddressList of the Device object
        @self The object instance
        @list The new list of addresses in the object, type Address.AddressList
        """

        self._addressList=list
        
    def toString(self):
        """
        Return a string representation of the object
        @self The object instance
        """

        res=""
        if self._name:
            res="NAME=%s\n" % (self._name)
        if self._description:
            res=res+"DESCRIPTION=%s\n" % (self._description)
        if self._enabled:
            res=res+"ENABLED=%s\n" % (self._enabled)
        if self._identifier:
            res=res+"IDENTIFIER=%s\n" % (self._identifier)
        if self._type:
            res=res+"TYPE=%s\n" % (self._type)
        if self._addressList:
            res=res+self._addressList.toString()

        return res

    
        
