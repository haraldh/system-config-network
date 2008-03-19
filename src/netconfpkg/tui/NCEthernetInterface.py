"TUI Ethernet Interface Module"

from netconfpkg.tui.NCTcpIp import NCTcpIpDialog
#
# EthernetWindow class
#
class NCEthernetInterfaceTui(NCTcpIpDialog):
    "TUI ISDN Interface Dialog"
    def __init__(self, dev = None):
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

def register_plugin():
    from netconfpkg.plugins.NCDevEthernet import setDevEthernetDialog     
    setDevEthernetDialog(NCEthernetInterfaceTui)
    
__author__ = "Harald Hoyer <harald@redhat.com>"
