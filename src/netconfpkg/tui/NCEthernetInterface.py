from netconfpkg.plugins.NCDevEthernet import *
from netconfpkg.tui.NCTcpIp import NCTcpIpDialog
#
# EthernetWindow class
#
class NCEthernetInterface(NCTcpIpDialog):
    def __init__(self, dev=None):
        """
        The constructor
        @screen A snack screen instance
        @devicelist A NCDeviceList
        @eth The ethernet device. If none given, the first
             ethernetdevice in devicelist will be used.
             If none are there, one will be added.
        """


        NCTcpIpDialog.__init__(self, dev)
        if dev:
            self.setState()

setDevEthernetDialog(NCEthernetInterface)
__author__ = "Harald Hoyer <harald@redhat.com>"
