SUBDIRS=netconfpkg

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

all-local:
	rm netconf
	rm netconf-cmd
	ln -s netconf.py netconf
	ln -s netconf.py netconf-cmd

install-exec-local:
	mkdir -p $(DESTDIR)$(pkgdatadir) $(DESTDIR)$(sbindir)
	install -m 0755 netconf.py $(DESTDIR)$(pkgdatadir)/
	ln -sf $(pkgdatadir)/netconf.py $(DESTDIR)$(sbindir)/netconf
	ln -sf $(pkgdatadir)/netconf.py $(DESTDIR)$(sbindir)/netconf-cmd

docs:
	python ./pydoc.py -w Device Address EthernetDevice ipcalc DeviceList ProfileList HardwareList ProviderList NetworkList Firewall
	mv *.html doc

clean:
	rm -f *.pyo *.pyc
	rm -f ${BUILT_SOURCES}
