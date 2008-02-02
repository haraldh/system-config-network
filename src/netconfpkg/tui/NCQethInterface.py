from netconfpkg.plugins.NCDevQeth import *
from snack import *

#
# QETHWindow class
#
class NCQethInterface:
    def __init__(self, dev=None):
        """
        The constructor
        @screen A snack screen instance
        """

        self.dev = dev
        self.name=Entry(20,"")
        self.hwdev=Entry(20,"")
        self.dynip=Checkbox("")
        self.statip=Entry(20,"")
        self.netmask=Entry(20,"")
        self.gw=Entry(20,"")
        self.ioport=Entry(20,"")
        self.ioport1=Entry(20,"")
        self.ioport2=Entry(20,"")

        if dev:
            self.setState()

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

            hardwarelist = getHardwareList()
            for hw in hardwarelist:
                if hw.Name == dev.Device:
                    self.ioport.set(hw.Card.IoPort)
                    self.ioport1.set(hw.Card.IoPort1)
                    self.ioport2.set(hw.Card.IoPort2)
                    break
            
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
        hardwarelist = getHardwareList()
        for hw in hardwarelist:
            if hw.Name == self.dev.Device:
                break
        else:
            i = hardwarelist.addHardware(QETH)
            hw = hardwarelist[i]
            hw.Status = HW_CONF
            hw.Name = self.dev.Device
            hw.Type = QETH

        if not hw.Card:
            hw.createCard()
        hw.Card.ModuleName = "qeth"
        hw.Card.IoPort = self.ioport.value()
        hw.Card.IoPort1 = self.ioport1.value()
        hw.Card.IoPort2 = self.ioport2.value()
        ports = "%s,%s,%s" % (hw.Card.IoPort, hw.Card.IoPort1, hw.Card.IoPort2)
        hw.Description = "qeth %s" % ports

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
    
    def runIt(self, screen):
        """
        Show and run the screen, save files if necesarry
        """
        self.screen=screen
        g1=Grid(1,1)
        g2=Grid(2,9)
        g2.setField(Label (_("Name")),0,0,anchorLeft=1)
        g2.setField(Label (_("Device")),0,1,anchorLeft=1)
        g2.setField(Label (_("Use DHCP")),0,2,anchorLeft=1)
        g2.setField(Label (_("Static IP")),0,3,anchorLeft=1)
        g2.setField(Label (_("Netmask")),0,4,anchorLeft=1)
        g2.setField(Label (_("Default gateway IP")),0,5,anchorLeft=1)
        g2.setField(Label (_("Read Device Bus ID")),0,6,anchorLeft=1)
        g2.setField(Label (_("Data Device Bus ID")),0,7,anchorLeft=1)
        g2.setField(Label (_("Write Device Bus ID")),0,8,anchorLeft=1)
        g2.setField(self.name,1,0,(1,0,0,0))
        g2.setField(self.hwdev,1,1,(1,0,0,0))
        g2.setField(self.dynip,1,2,(1,0,0,0),anchorLeft=1)
        g2.setField(self.statip,1,3,(1,0,0,0))
        g2.setField(self.netmask,1,4,(1,0,0,0))
        g2.setField(self.gw,1,5,(1,0,0,0))
        g2.setField(self.ioport,1,6,(1,0,0,0))
        g2.setField(self.ioport1,1,7,(1,0,0,0))
        g2.setField(self.ioport2,1,8,(1,0,0,0))
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



setDevQethDialog(NCQethInterface)
__author__ = "Harald Hoyer <harald@redhat.com>"

