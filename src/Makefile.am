SUBDIRS=netconfpkg pixmaps doc

PYTHON_FILES = \
	Address.py \
	ADSLInterface.py \
	ATMInterface.py \
	CableInterface.py \
	ConfiguredDevice.py \
	Device.py \
	DialupInterface.py \
	EthernetDevice.py \
	EthernetInterface.py \
	FirewallDruid.py \
	inspect.py \
	InterfaceCreator.py \
	ipcalc.py \
	MainWindow.py \
	netconf.py \
	netiface.py \
	NewInterface.py \
	pydoc.py \
	Resolver.py \
	WirelessInterface.py

GLADE_FILES = \
	dialup.glade \
	firewall-druids.glade \
	maindialog.glade \
	mainwindow.glade \
	new_interface_druid.glade 

EXTRA_DIST = $(PYTHON_FILES) $(GLADE_FILES)

#pkgdata_DATA :=

#exec_SCRIPTS = 

execdir = $(sbindir)

all-local:
	rm -f netconf
	rm -f netconf-cmd
	ln -s netconf.py netconf
	ln -s netconf.py netconf-cmd

install-exec-local:
	mkdir -p $(DESTDIR)$(pkgdatadir) $(DESTDIR)$(sbindir)
	install -m 0755 netconf.py $(DESTDIR)$(pkgdatadir)/
	ln  $(pkgdatadir)/netconf.py $(DESTDIR)$(sbindir)/netconf
	ln  $(pkgdatadir)/netconf.py $(DESTDIR)$(sbindir)/netconf-cmd
	install -m 644 $(PYTHON_FILES) $(DESTDIR)$(pkgdatadir)/
	install -m 644 $(GLADE_FILES)  $(DESTDIR)$(pkgdatadir)/netconfpkg/

docs:
	python ./pydoc.py -w Device Address EthernetDevice ipcalc DeviceList ProfileList HardwareList ProviderList NetworkList Firewall
	mv *.html doc

clean:
	rm -f *.pyo *.pyc
	rm -f ${BUILT_SOURCES}
