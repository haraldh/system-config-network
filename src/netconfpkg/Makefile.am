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
	wirelessconfig.glade

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
   NCDeviceList.py \
   NCDevice.py \
   NCDialup.py \
   NCCallback.py \
	NCHardwareList.py \
	NC_functions.py

EXTRA_DIST = $(GLADE_FILES) $(IDL_FILES) $(PYTHON_FILES)

netconfpkgdir = $(pkgdatadir)/netconfpkg
netconfpkg_DATA := $(GLADE_FILES) $(PYTHON_FILES) $(BUILT_SOURCES)

#exec_SCRIPTS =

execdir = $(sbindir)

#install-data-local:
#	chmod 600 $(sysconfdir)/alchemist/namespace/dns/local.adl
#	chmod 600 $(sysconfdir)/alchemist/switchboard/dns.switchboard.adl
#	$(mkinstalldirs) $(localstatedir)/cache/alchemist/dns
#	$(mkinstalldirs) $(datadir)/kontrol-panel/icons
#	$(mkinstalldirs) $(sysconfdir)/X11/applnk/System
#	install -m 0644 $(srcdir)/bindconf.png $(datadir)/kontrol-panel/icons/
#	install -m 0644 $(srcdir)/bindconf-konfig.desktop $(datadir)/kontrol-panel/bindconf.desktop
#	install -m 0644 $(srcdir)/bindconf.desktop $(sysconfdir)/X11/applnk/System/

clean:
	rm -f *.pyo *.pyc
	rm -f ${BUILT_SOURCES}

DeviceList.py: $(srcdir)/DeviceList.idl $(srcdir)/genClass.py $(srcdir)/NCDeviceList.py $(srcdir)/NCDevice.py $(srcdir)/NCDialup.py $(srcdir)/NCCallback.py

HardwareList.py: $(srcdir)/NCHardwareList.py 

%.py: %.idl $(srcdir)/genClass.py
	python $(srcdir)/genClass.py -f -c $(srcdir)/$*.idl $@ NC
