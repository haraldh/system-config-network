EXTRA_DIST = DeviceList.idl ProfileList.idl HardwareList.idl ProviderList.idl NetworkList.idl Firewall.idl genClass.py NCDeviceList.py

BUILT_SOURCES = DeviceList.py ProfileList.py HardwareList.py ProviderList.py NetworkList.py Firewall.py

#pkgdata_DATA :=

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

DeviceList.py: DeviceList.idl genClass.py NCDeviceList.py NCDevice.py NCDialup.py

HardwareList.py: NCHardwareList.py 


install-exec-local:
	mkdir -p $(DESTDIR)$(pkgdatadir)/netconfpkg
	install -m 644 *.py *.glade $(DESTDIR)$(pkgdatadir)/netconfpkg

%.py: %.idl genClass.py
	python genClass.py -f -c $(srcdir)/$*.idl $@ NC
