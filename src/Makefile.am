EXTRA_DIST := DeviceList.idl ProfileList.idl HardwareList.idl ProviderList.idl NetworkList.idl Firewall.idl

BUILT_SOURCES = DeviceList.py ProfileList.py HardwareList.py ProviderList.py NetworkList.py Firewall.py

#DeviceList.py: DeviceList.idl /usr/lib/rhs/genClass.py
#	python /usr/lib/rhs/genClass.py $(srcdir)/$*.idl -c $@ $* 

#pkgdata_DATA :=

#exec_SCRIPTS = bindconf-gui

execdir = $(sbindir)

install-data-local:
	#chmod 600 $(sysconfdir)/alchemist/namespace/dns/local.adl
	#chmod 600 $(sysconfdir)/alchemist/switchboard/dns.switchboard.adl
	#$(mkinstalldirs) $(localstatedir)/cache/alchemist/dns
	#$(mkinstalldirs) $(datadir)/kontrol-panel/icons
	#$(mkinstalldirs) $(sysconfdir)/X11/applnk/System
	#install -m 0644 $(srcdir)/bindconf.png $(datadir)/kontrol-panel/icons/
	#install -m 0644 $(srcdir)/bindconf-konfig.desktop $(datadir)/kontrol-panel/bindconf.desktop
	#install -m 0644 $(srcdir)/bindconf.desktop $(sysconfdir)/X11/applnk/System/

clean:
	rm -f *.pyo *.pyc

%.py: %.idl /usr/lib/rhs/python/genClass.py
	python /usr/lib/rhs/python/genClass.py -c $(srcdir)/$*.idl $@ $*

