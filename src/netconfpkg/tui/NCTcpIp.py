from snack import *
from rhpl import ethtool
#
# General TCP/IP
#
class NCTcpIpDialog:
    def __init__(self, dev):
        """
        The constructor
        @screen A snack screen instance
        @devicelist A NCDeviceList
        @dev The devernet device. If none given, the first
             devernetdevice in devicelist will be used.
             If none are there, one will be added.
        """
        self.dev = dev
        self.name=Entry(20,"")
        self.hwdev=Entry(20,"")
        self.dynip=Checkbox("")
        self.statip=Entry(20,"")
        self.netmask=Entry(20,"")
        self.gw=Entry(20,"")

    def setState(self, dev=None):
        """
        Set the default values of the fields
        according to the given device
        @dev The NCDevice (type devernet) to use as default values
        """
        if not dev:
            dev = self.dev
            
        if dev:
            if dev.DeviceId:
                self.name.set(dev.DeviceId)
            if dev.Device:
                self.hwdev.set(dev.Device)
            if dev.BootProto:
                bp=string.lower(dev.BootProto)
                if (bp=="dhcp") or (bp=="bootp"):
                    self.dynip.setValue("*")
            if dev.IP:
                self.statip.set(dev.IP)
            if dev.Netmask:
                self.netmask.set(dev.Netmask)
            if dev.Gateway:
                self.gw.set(dev.Gateway)
        
    def useDynamicCheckBox(self):
        """
        Set the static IP field to enabled/disabled
        determined by the dynamic IP field
        """
        
        if self.dynip.selected():
            state=FLAGS_SET
        else:
            state=FLAGS_RESET
        for i in self.statip,self.netmask,self.gw:
            i.setFlags(FLAG_DISABLED,state)

    def processInfo(self):
        """
        Extracts info from the screen, and puts it into a device object
        """

        self.dev.DeviceId=self.name.value()
        self.dev.Device=self.hwdev.value()
        if self.dynip.value():
            self.dev.BootProto="dhcp"
            self.dev.IP=None
            self.dev.Netmask=None
            self.dev.Gateway=None
        else:
            self.dev.IP=self.statip.value()
            self.dev.Netmask=self.netmask.value()
            self.dev.Gateway=self.gw.value()
            self.dev.BootProto=None
        try: hwaddr = ethtool.get_hwaddr(self.dev.Device) 
        except IOError, err:
            pass
        else:
            self.dev.HardwareAddress = hwaddr
    
    def runIt(self, screen):
        """
        Show and run the screen, save files if necesarry
        """
        self.screen=screen
        g1=Grid(1,1)
        g2=Grid(2,6)
        g2.setField(Label (_("Name")),0,0,anchorLeft=1)
        g2.setField(Label (_("Device")),0,1,anchorLeft=1)
        g2.setField(Label (_("Use DHCP")),0,2,anchorLeft=1)
        g2.setField(Label (_("Static IP")),0,3,anchorLeft=1)
        g2.setField(Label (_("Netmask")),0,4,anchorLeft=1)
        g2.setField(Label (_("Default gateway IP")),0,5,anchorLeft=1)
        g2.setField(self.name,1,0,(1,0,0,0))
        g2.setField(self.hwdev,1,1,(1,0,0,0))
        g2.setField(self.dynip,1,2,(1,0,0,0),anchorLeft=1)
        g2.setField(self.statip,1,3,(1,0,0,0))
        g2.setField(self.netmask,1,4,(1,0,0,0))
        g2.setField(self.gw,1,5,(1,0,0,0))
        self.dynip.setCallback(self.useDynamicCheckBox)
        bb=ButtonBar(self.screen,((_("Ok"),"ok"),(_("Cancel"),"cancel")))
        self.setState(self.dev)
        tl=GridForm(screen,_("Devernet Configuration"),1,3)
        tl.add(g1,0,0,(0,0,0,1),anchorLeft=1)
        tl.add(g2,0,1,(0,0,0,1))
        tl.add(bb,0,2,growx=1)
        self.useDynamicCheckBox()
        while 1:
            res=tl.run()
            if bb.buttonPressed(res)=="cancel":
                screen.popWindow()
                return False
                break
            elif bb.buttonPressed(res)=="ok":
                screen.popWindow()
                self.processInfo()
                return True
                break