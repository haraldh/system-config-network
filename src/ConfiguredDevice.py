#!/usr/bin/python
#
# This software may be freely redistributed under the terms of the GNU
# public license.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

"""
The ConfiguredDevice class
"""

import Conf
import Device
import os

class ConfiguredDevice(Device.Device):
    """
    This class contains routines and data for configured devices
    """

    def __init__(self):
        """
        The initialization of the common device.
        @self The object instance
        """

        Device.Device.__init__(self)
        self._onBoot=None
        self._makeDefaultRoute=None
        self._fileName=None

    def readOldFile(self,filename):
        """
        Read an existing configuration from an old style configuration file
        @self The object instance
        @filename The filename
        """

        Device.Device.readOldFile(self,filename)
        confFile=Conf.ConfShellVar(filename)
        self._onBoot=confFile["ONBOOT"]
        self._bootProto=confFile["BOOTPROTO"]
        self._fileName=None # Don't want to keep old configuration filenames around....
        

    def readFile(self,filename):
        """
        Read an existing configutation from a configuration file
        @self The object instance
        @filename The configuration file
        """

        if not os.exist.path(filename):
            raise IOError,"File not found"
        Device.Device.readFile(self,filename)
        confFile=Conf.ConfShellVar(filename)
        self._onBoot=confFile["ONBOOT"]
        self._bootProto=confFile["BOOTPROTO"]
        self._fileName=filename

    def getOnBoot(self):
        """
        Return the onboot value of the ConfiguredDevice object
        @self The object instance
        """

        return self._onBoot

    def setOnBoot(self,onboot):
        """
        Set the onboot value of the ConfiguredDevice object
        @self The object instance
        @onboot The new onboot value
        """

        self._onBoot=onboot

    def getBootproto(self):
        """
        Return the bootproto value of the ConfiguredDevice object
        @self The object instance
        """

        return self._bootproto

    def setBootproto(self,bootproto):
        """
        Set the bootproto value of the ConfiguredDevice object
        @self The object instance
        @bootproto The new bootproto value
        """

        self._bootproto=bootproto
    
    def getFileName(self):
        """
        Return the filename value of the ConfiguredDevice object
        @self The object instance
        """

        return self._fileName

    def setFileName(self,filename):
        """
        Set the filename value of the ConfiguredDevice object
        @self The object instance
        @filename The new filename value
        """

        self._fileName=filename
    
    
        
    
    
        
    
