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
	ethernetconfig.glade \
	EthernetHardwareDruid.glade \
	ethernethardware.glade \
	EthernetInterfaceDruid.glade \
	GenericInterfaceDruid.glade \
	hardwaretype.glade \
	IsdnHardwareDruid.glade \
	isdnhardware.glade \
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
	wirelessconfig.glade \
	WirelessInterfaceDruid.glade \
	ctcconfig.glade

PYTHON_FILES = \
	ADSLInterface.py \
	cipeconfig.py \
	CipeInterface.py \
	deviceconfig.py \
	devicetype.py \
	dialupconfig.py \
	exception.py \
	DialupDruid.py \
	dslconfig.py \
	editadress.py \
	editdomain.py \
	edithosts.py \
	ethernetconfig.py \
	EthernetHardwareDruid.py \
	ethernethardware.py \
	EthernetInterface.py \
	GenericInterface.py \
	hardwaretype.py \
	__init__.py \
	InterfaceCreator.py \
	isdnhardware.py \
	IsdnInterface.py \
	modemconfig.py \
	ModemInterface.py \
	NewInterface.py \
	NewInterfaceDialog.py \
	GUI_functions.py \
	providerdb.py \
	provider.py \
	sharedtcpip.py \
	tokenringconfig.py \
	TokenRingHardwareDruid.py \
	TokenRingInterface.py \
	tokenringhardware.py \
	wirelessconfig.py \
	WirelessInterface.py \
	ctcconfig.py

EXTRA_DIST = $(GLADE_FILES)  $(PYTHON_FILES)

BUILT_SOURCES = $(if $(shell test -w $(srcdir) && echo OK), \
		     $(patsubst %.py,%.pyc,$(PYTHON_FILES)))

netconfpkgdir = $(pkgdatadir)/netconfpkg/gui
netconfpkg_DATA = $(GLADE_FILES) $(PYTHON_FILES) $(BUILT_SOURCES)

execdir = $(sbindir)

clean:
	rm -f *.pyo *.pyc
	rm -f ${BUILT_SOURCES}

%.pyc: %.py
	@echo "Compiling because of " $*
	@PYTHON@ @PY_COMPILEALL@ -l -d . $(srcdir)
