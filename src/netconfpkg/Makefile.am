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
	IsdnHardwareDruid.glade \
	isdnhardware.glade \
	modemconfig.glade \
	ModemDruid.glade \
	NewInterfaceDruid.glade \
	tcpipdialog.glade \
	wirelessconfig.glade

BUILT_SOURCES = DeviceList.py ProfileList.py HardwareList.py \
                ProviderList.py NetworkList.py	Firewall.py 

IDL_FILES = \
	DeviceList.idl \
	Firewall.idl \
	HardwareList.idl \
	NetworkList.idl \
	ProfileList.idl \
	ProviderList.idl

PYTHON_FILES = \
	ADSLInterface.py \
	cipeconfig.py \
	ConfPAP.py \
	ConfSMB.py \
	deviceconfig.py \
	devicetype.py \
	dialupconfig.py \
	DialupDruid.py \
	dslconfig.py \
	editadress.py \
	editdomain.py \
	edithosts.py \
	ethernetconfig.py \
	EthernetHardwareDruid.py \
	ethernethardware.py \
	genClass.py \
	__init__.py \
	InterfaceCreator.py \
	isdnhardware.py \
	IsdnInterface.py \
	modemconfig.py \
	ModemInterface.py \
	NCCallback.py \
	NCCipe.py \
	NCCompression.py \
	NCDeviceList.py \
	NCDevice.py \
	NCDialup.py \
	NC_functions.py \
	NCHardwareList.py \
	NCisdnhardware.py \
	NCProfileList.py \
	NCWireless.py \
	NewInterface.py \
	providerdb.py \
	provider.py \
	tcpdialog.py \
	wirelessconfig.py

EXTRA_DIST = $(GLADE_FILES) $(IDL_FILES) $(PYTHON_FILES)

netconfpkgdir = $(pkgdatadir)/netconfpkg
netconfpkg_DATA = $(GLADE_FILES) $(PYTHON_FILES) $(BUILT_SOURCES)

execdir = $(sbindir)

clean:
	rm -f *.pyo *.pyc
	rm -f ${BUILT_SOURCES}

DeviceList.py: $(srcdir)/DeviceList.idl $(srcdir)/genClass.py $(srcdir)/NCDeviceList.py $(srcdir)/NCDevice.py $(srcdir)/NCDialup.py $(srcdir)/NCCallback.py

HardwareList.py: $(srcdir)/HardwareList.idl $(srcdir)/genClass.py $(srcdir)/NCHardwareList.py 

ProfileList.py: $(srcdir)/ProfileList.idl $(srcdir)/genClass.py $(srcdir)/NCProfileList.py 

%.py: %.idl $(srcdir)/genClass.py
	python $(srcdir)/genClass.py -f -c $(srcdir)/$*.idl $@ NC
