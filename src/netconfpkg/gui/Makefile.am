GLADE_FILES = \
	ADSLInterfaceDruid.glade \
	chooseprovider.glade \
	cipeconfig.glade \
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
	hardwaretype.glade \
	IsdnHardwareDruid.glade \
	isdnhardware.glade \
	modemconfig.glade \
	ModemDruid.glade \
	NewInterfaceDruid.glade \
	sharedtcpip.glade \
	tcpipdialog.glade \
	tokenringconfig.glade \
	TokenRingHardwareDruid.glade \
	tokenringhardware.glade \
	wirelessconfig.glade \
	ctcconfig.glade

PYTHON_FILES = \
	ADSLInterface.py \
	cipeconfig.py \
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
	tcpdialog.py \
	tokenringconfig.py \
	TokenRingHardwareDruid.py \
	tokenringhardware.py \
	wirelessconfig.py \
	ctcconfig.py

EXTRA_DIST = $(GLADE_FILES)  $(PYTHON_FILES)

BUILT_SOURCES = $(patsubst %.py,%.pyc, $(PYTHON_FILES)) 

netconfpkgdir = $(pkgdatadir)/netconfpkg/gui
netconfpkg_DATA = $(GLADE_FILES) $(PYTHON_FILES) $(BUILT_SOURCES)

execdir = $(sbindir)

clean:
	rm -f *.pyo *.pyc
	rm -f ${BUILT_SOURCES}

%.pyc: %.py
	@echo "Compiling because of " $*
	python @PY_COMPILEALL@ -l -d . $(srcdir)
