GLADE_FILES = \
	basicdialog.glade \
	chooseprovider.glade \
	cipeconfig.glade \
	dialupconfig.glade \
	dslconfig.glade \
	editadress.glade \
	editdomain.glade \
	edithosts.glade \
	ethernetconfig.glade \
	ethernethardware.glade \
	isdnhardware.glade \
	modemconfig.glade \
	wirelessconfig.glade \
	devicetype.glade

BUILT_SOURCES = DeviceList.py ProfileList.py HardwareList.py \
                ProviderList.py NetworkList.py

IDL_FILES = \
	DeviceList.idl \
	Firewall.idl \
	HardwareList.idl \
	NetworkList.idl \
	ProfileList.idl \
	ProviderList.idl

PYTHON_FILES = \
	genClass.py \
	basicdialog.py \
	CheckList.py \
	ConfSMB.py \
	dialupconfig.py \
	dslconfig.py \
	editadress.py \
	editdomain.py \
	edithosts.py \
	ethernetconfig.py \
	ethernethardware.py \
	__init__.py \
	isdnhardware.py \
	modemconfig.py \
	providerdb.py \
	provider.py \
	NCCallback.py \
	NCCompression.py \
	NCDeviceList.py \
	NCDevice.py \
	NCDialup.py \
	NC_functions.py \
	NCHardwareList.py \
	NCProfileList.py \
	NCisdnhardware.py \

EXTRA_DIST = $(GLADE_FILES) $(IDL_FILES) $(PYTHON_FILES)

netconfpkgdir = $(pkgdatadir)/netconfpkg
netconfpkg_DATA := $(GLADE_FILES) $(PYTHON_FILES) $(BUILT_SOURCES)

execdir = $(sbindir)

clean:
	rm -f *.pyo *.pyc
	rm -f ${BUILT_SOURCES}

DeviceList.py: $(srcdir)/DeviceList.idl $(srcdir)/genClass.py $(srcdir)/NCDeviceList.py $(srcdir)/NCDevice.py $(srcdir)/NCDialup.py $(srcdir)/NCCallback.py

HardwareList.py: $(srcdir)/HardwareList.idl $(srcdir)/genClass.py $(srcdir)/NCHardwareList.py 

ProfileList.py: $(srcdir)/ProfileList.idl $(srcdir)/genClass.py $(srcdir)/NCProfileList.py 

%.py: %.idl $(srcdir)/genClass.py
	python $(srcdir)/genClass.py -f -c $(srcdir)/$*.idl $@ NC
