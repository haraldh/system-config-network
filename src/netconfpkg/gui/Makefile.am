GLADE_FILES = \
	ADSLInterfaceDruid.glade \
	chooseprovider.glade \
	cipeconfig.glade \
	CipeInterfaceDruid.glade \
	devicetype.glade \
	dialupconfig.glade \
	DialupDruid.glade \
	dslconfig.glade \
	editadress.glade \
	editdomain.glade \
	edithosts.glade \
	editipsec.glade \
	ethernetconfig.glade \
	EthernetHardwareDruid.glade \
	ethernethardware.glade \
	EthernetInterfaceDruid.glade \
	GenericInterfaceDruid.glade \
	hardwaretype.glade \
	IsdnHardwareDruid.glade \
	isdnhardware.glade \
	infodialog.glade \
	maindialog.glade \
	modemconfig.glade \
	ModemDruid.glade \
	NewInterfaceDruid.glade \
	neat-control-debugdialog.glade \
	neat-control-monitordialog.glade \
	neat-control-popupmenu.glade \
	neat-control-propertiesdialog.glade \
	neat-control-statusdialog.glade \
	sharedtcpip.glade \
	tokenringconfig.glade \
	TokenRingHardwareDruid.glade \
	TokenRingInterfaceDruid.glade \
	tokenringhardware.glade \
	tonline.glade \
	wirelessconfig.glade \
	WirelessInterfaceDruid.glade \
	neat-control.glade \
	ptpconfig.glade \
	PTPInterfaceDruid.glade

PYTHON_FILES = \
	ADSLInterface.py \
	cipeconfig.py \
	CipeInterface.py \
	deviceconfig.py \
	devicetype.py \
	dialupconfig.py \
	DialupDruid.py \
	dslconfig.py \
	editadress.py \
	editdomain.py \
	edithosts.py \
	editipsec.py \
	ethernetconfig.py \
	EthernetHardwareDruid.py \
	ethernethardware.py \
	EthernetInterface.py \
	GenericInterface.py \
	hardwaretype.py \
	HardwareDialog.py \
	__init__.py \
	InterfaceCreator.py \
	isdnhardware.py \
	IsdnInterface.py \
	maindialog.py \
	modemconfig.py \
	ModemInterface.py \
	NewInterfaceDialog.py \
	GUI_functions.py \
	providerdb.py \
	provider.py \
	sharedtcpip.py \
	tokenringconfig.py \
	TokenRingHardwareDruid.py \
	TokenRingInterface.py \
	tokenringhardware.py \
	tonline.py \
	wirelessconfig.py \
	WirelessInterface.py \
	ctcconfig.py \
	iucvconfig.py \
	CTCInterface.py \
	IUCVInterface.py \
	ptpconfig.py \
	PTPInterface.py

EXTRA_DIST = $(GLADE_FILES)  $(PYTHON_FILES)

netconfpkgdir = $(pkgdatadir)/netconfpkg/gui
netconfpkg_DATA = $(GLADE_FILES)
netconfpkg_PYTHON = $(PYTHON_FILES)

execdir = $(sbindir)

CLEANFILES := $(notdir $(wildcard *~)) $(notdir $(wildcard *\#)) $(notdir $(wildcard \.\#*))

