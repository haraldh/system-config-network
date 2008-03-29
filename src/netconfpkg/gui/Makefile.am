GLADE_FILES = \
	ADSLInterfaceDruid.glade \
	ADSLInterfaceDialog.glade \
	ChooseProvider.glade \
	DeviceConfigDialog.glade \
	DeviceTypeDialog.glade \
	DialupInterfaceDialog.glade \
	DialupDruid.glade \
	editadress.glade \
	editdomain.glade \
	edithosts.glade \
	editipsec.glade \
	ethernetconfig.glade \
	EthernetHardwareDruid.glade \
	ethernethardware.glade \
	EthernetInterfaceDruid.glade \
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
	PTPInterfaceDruid.glade \
	QethConfig.glade \
	QethInterfaceDruid.glade \
	QethHardware.glade \
	QethHardwareDruid.glade

PYTHON_FILES = \
	ADSLInterfaceDruid.py \
	ADSLInterfaceDialog.py \
	DeviceConfigDialog.py \
	DeviceTypeDialog.py \
	DialupInterfaceDialog.py \
	DialupDruid.py \
	editadress.py \
	editdomain.py \
	edithosts.py \
	editipsec.py \
	ethernetconfig.py \
	EthernetHardwareDruid.py \
	ethernethardware.py \
	EthernetInterface.py \
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
	ptpconfig.py \
	PTPInterface.py \
	QethConfig.py \
	QethInterfaceDruid.py \
	QethHardware.py \
	QethHardwareDruid.py


EXTRA_DIST = $(GLADE_FILES)  $(PYTHON_FILES)

netconfpkgdir = $(pkgdatadir)/netconfpkg/gui
netconfpkg_DATA = $(GLADE_FILES)
netconfpkg_PYTHON = $(PYTHON_FILES)

execdir = $(sbindir)

CLEANFILES = $(notdir $(wildcard *~)) $(notdir $(wildcard *\#)) $(notdir $(wildcard \.\#*)) $(notdir $(wildcard *.gladep)) $(notdir $(wildcard *.bak)) $(notdir $(wildcard *.pyc))

fixpath:
	perl -pi -e 's#logo">([^/>][^>]*)<#logo">/usr/share/system-config-network/pixmaps/$$1<#g'  *.glade
	perl -pi -e 's#pixbuf">([^/>][^>]*)<#pixbuf">/usr/share/system-config-network/pixmaps/$$1<#g'  *.glade

check:
	@fgrep glade_file *.py|fgrep 'glade_file ='|fgrep '.glade'|while read file a b gfile; do gfile=$${gfile:1};gfile=$${gfile%\'};gfile=$${gfile%\"}; test -f $$gfile || (echo "Error $$file: $$gfile does not exist";exit 1)||exit 1; fgrep -q $$gfile Makefile.am||(echo "File $$gfile missing in Makefile.am";exit 1)||exit 1;done && echo "Glade file test PASSED"
