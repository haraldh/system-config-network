#!/usr/bin/python
#
# This software may be freely redistributed under the terms of the GNU
# public license.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

"""
Classes for managing an address and list of these
"""

import sys
if not "/usr/lib/rhs/python" in sys.path:
    sys.path.append("/usr/lib/rhs/python")
import os
import Conf
import ipcalc

class Address:
    """
    The class for address description
    """

    def __init__(self,filename="",number=""):
        """
        The initialization of an address object
        @self The object instance
        """

        if filename:
            self.readFile(filename,number)
        else:
            self._address=None
            self._prefix=None
            self._broadcast=None
            self._scope=None
            self._device=None

    def readOldFile(self,filename):
        """
        Read old ifcfg-<foo> file
        @self The object instance
        @file The file from which to read the configuration
        """
        if not os.path.exists(filename):
           raise IOError,"File not Found"
        confFile=Conf.ConfShellVar(filename)
        self._address=confFile["IPADDR"]
        self._broadcast=confFile["BROADCAST"]
        netmask=confFile["NETMASK"]
        self._device=confFile["DEVICE"]
        if self._address and netmask:
            calc=ipcalc.IPCalc(self._address,netmask)
            self._prefix=calc.prefix()
        
    
    def readFile(self,filename,number=""):
        """
        Read configuration file, and populate the object
        @self The object instance
        @filename The file to read from
        @number The address sequence no
        """
        if not os.path.exists(filename):
            raise IOError,"File not Found"

        confFile=Conf.ConfShellVar(filename)
        self._address=confFile["ADDRESS"+`number`] 
        self._broadcast=confFile["BROADCAST"+`number`]
        self._prefix=confFile["PREFIX"+`number`]
        self._scope=confFile["SCOPE"+`number`]
        self._device=confFile["DEVICE"+`number`]

    def toString(self,number=""):
        """
        Converts the structure to a multiline string,
        for storage
        @self The object instance
        @number The sequence number of this address
        """

        res=""
        if self._device:
            res="DEVICE%s=%s\n" % (number,self._device)
        if self._address:
            res=res+"ADDRESS%s=%s\n" % (number,self._address)
        if self._prefix:
            res=res+"PREFIX%s=%s\n" % (number,self._prefix)
        if self._scope:
            res=res+"SCOPE%s=%s\n" % (number,self._scope)
        if self._broadcast:
            res=res+"BROADCAST%s=%s\n" % (number,self._broadcast)
        return res

    def __str__(self):
        """
        Converts the structure to a multiline string,
        for storage
        @self The object instance
        """

        return self.toString()
            
    def device(self):
        """
        Returns the device of the address object
        @self The object instance
        """
        return self._device

    def setDevice(self,device):
        """
        Set the device of the address object
        @self The object instance
        @device The device name
        """
        self._device=device

    def scope(self):
        """
        Returns the scope of the address object
        @self The object instance
        """
        return self._scope

    def setScope(self,scope):
        """
        Set the scope of the address object
        @self The object instance
        @scope The scope 
        """
        self._scope=scope
        
    def address(self):
        """
        Return the address of the address object
        @self The object instance
        """
        return self._address

    def setAddress(self,address):
        """
        Set the address of the address object
        @self The object instance
        @address The new address
        """
        self._address=address

    def prefix(self):
        """
        Get the of the address object
        @self The object instance
        """
        return self._prefix

    def setPrefix(self,prefix):
        """
        Set the prefix of the address object
        @self The object instance
        @prefix The new prefix
        """
        self._prefix=prefix
    
    def broadcast(self):
        """
        Return the broadcast address of the address object
        @self The object instance
        """
        return self._broadcast

    def setBroadcast(self,broadcast):
        """
        Set the broadcast address of the address object
        @self The object instance
        @broadcast The new broadcast address
        """
        self._broadcast=broadcast

    def __cmp__(self,other):
        """
        Compares two addresses... returns 0 for equal
        (address and device are compared), otherwise 1
        @self The object instance
        @other The object to compare to
        """
        if ((self._address == other._address) and (self._device == other._device)):
            return 0
        return 1                     
            
        
class AddressList:
    """
    Maintains a list of addresses
    """

    def __init__(self):
        """
        Initializes an empty list of addresses
        @self The object instance
        """
        self._list=[]

    def addressList(self):
        """
        Returns an array of adress objects
        @self The object instance
        """
        return self._list

    def setAddressList(self,list):
        """
        Explicitly sets the array of array objects
        @self The object instance
        """
        self._list=list

    def addAddress(self,address):
        """
        Add an address to the array of address objects
        @self The object instance
        @address The address to add
        """
        self._list.append(address)

    def deleteAddress(self,address,device):
        """
        Delete an address object
        @self The object instance
        @address The address of the device to delete
        @device The device to delete
        """

        foo=Address()
        foo.setAddress(address)
        foo.setDevice(device)
        self._list.remove(foo)
    
    def toString(self):
        """
        Return a multiline string containing the addresses,
        in the format of ADDRESS0, ..., ADDRESS1 etc
        @self The object instance
        """

        res=""
        if(len(self._list)>1):
            for i in range(0,len(self._list)):
                res=res+self._list[i].toString(i)
        else:
            if(len(self._list)>0):
                res=self._list[0].toString() 
        return res

    def readFile(self,filename):
        """
        Read configuration file, and populate the object
        @self The object instance
        @filename The file to read from
        """

        # Handle the case where you only have one non-numbered entry
           
        address=Address(filename)
        if address.address() or address.device():
            self.addAddress(address)
            return

        # Handle the ADDRESS0, ADDRESS1, ... case
        
        n=0
        while 1:
            address=Address(filename,n)
            if not address.address():
                break
            else:
                self.addAddress(address)
                n=n+1
           
def test():
    """
    Test for AddressList and Address
    """

    addr1=Address()
    addr2=Address()
    addr1.setAddress("207.175.42.139")
    addr1.setDevice("eth0")
    addr2.setAddress("207.175.42.56")
    addr2.setDevice("eth1")
    alist1=AddressList()
    alist1.addAddress(addr1)
    alist1.addAddress(addr2)
    file=open("/tmp/foobar","w")
    file.write(alist1.toString())
    file.close()
    alist2=AddressList()
    alist2.readFile("/tmp/foobar")
    out1=alist1.toString()
    out2=alist2.toString()
    if out1==out2:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(test())
