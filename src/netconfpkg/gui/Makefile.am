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
	PTPInterfaceDruid.glade \
	QethConfig.glade \
	QethInterfaceDruid.glade \
	QethHardware.glade \
	QethHardwareDruid.glade

PYTHON_FILES = \
	NCPluginADSLInterfaceDruid.py \
	NCPluginADSLInterfaceDialog.py \
	DeviceConfigDialog.py \
	DeviceTypeDialog.py \
	NCPluginDialupInterfaceDialog.py \
	DialupDruid.py \
	editadress.py \
	editdomain.py \
	edithosts.py \
	editipsec.py \
	NCPluginethernetconfig.py \
	EthernetHardwareDruid.py \
	NCPluginethernethardware.py \
	NCPluginEthernetInterface.py \
	GenericInterface.py \
	hardwaretype.py \
	HardwareDialog.py \
	NCPlugin__init__.py \
	InterfaceCreator.py \
	NCPluginisdnhardware.py \
	NCPluginIsdnInterface.py \
	maindialog.py \
	NCPluginmodemconfig.py \
	NCPluginModemInterface.py \
	NewInterfaceDialog.py \
	GUI_functions.py \
	providerdb.py \
	provider.py \
	sharedtcpip.py \
	NCPlugintokenringconfig.py \
	TokenRingHardwareDruid.py \
	NCPluginTokenRingInterface.py \
	NCPlugintokenringhardware.py \
	tonline.py \
	NCPluginwirelessconfig.py \
	NCPluginWirelessInterface.py \
	ptpconfig.py \
	PTPInterface.py \
	NCPluginQethConfig.py \
	QethInterfaceDruid.py \
	NCPluginQethHardware.py \
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
