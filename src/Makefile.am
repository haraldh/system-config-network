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

execdir = $(sbindir)

all-local:
	rm -f redhat-config-network
	rm -f redhat-config-network-cmd
	ln -s netconf.py redhat-config-network
	ln -s netconf.py redhat-config-network-cmd

pythondir = $(pkgdatadir)
python_DATA = $(PYTHON_FILES)

gladedir = $(pkgdatadir)/netconfpkg
glade_DATA = $(GLADE_FILES)

install-exec-local:
	mkdir -p $(DESTDIR)$(pkgdatadir) $(DESTDIR)$(sbindir)
	install -m 0755 $(srcdir)/netconf.py $(DESTDIR)$(pkgdatadir)/
	ln  $(pkgdatadir)/netconf.py $(DESTDIR)$(sbindir)/redhat-config-network
	ln  $(pkgdatadir)/netconf.py $(DESTDIR)$(sbindir)/redhat-config-network-cmd
	ln  $(pkgdatadir)/netconf.py $(DESTDIR)$(sbindir)/neat

docs:
	python ./pydoc.py -w Device Address EthernetDevice ipcalc DeviceList ProfileList HardwareList ProviderList NetworkList Firewall
	mv *.html doc

check-local:
	pychecker *.py

clean:
	rm -f *.pyo *.pyc
	rm -f ${BUILT_SOURCES}
