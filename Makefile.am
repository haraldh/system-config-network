AUTOMAKE_OPTIONS = foreign 1.4

SUBDIRS=doc src intl po

EXTRA_DIST= redhat-config-network.spec doc/configurationfiles.txt doc/detailed_spec \
	doc/overview neat.desktop neat.console neat.pam

sysdir=$(sysconfdir)/X11/applnk/System

install-data-local:
	$(mkinstalldirs) $(sysconfdir)/security/console.apps
	$(INSTALL_DATA) neat.console $(sysconfdir)/security/console.apps/neat
	$(INSTALL_DATA) internet-druid.console $(sysconfdir)/security/console.apps/internet-druid
	$(mkinstalldirs) $(sysconfdir)/pam.d
	$(INSTALL_DATA) neat.pam $(sysconfdir)/pam.d/neat
	$(INSTALL_DATA) neat.pam $(sysconfdir)/pam.d/internet-druid
	$(mkinstalldirs) $(prefix)/bin/
	ln -fs consolehelper $(prefix)/bin/neat
	ln -fs consolehelper $(prefix)/bin/internet-druid
	$(mkinstalldirs) $(datadir)/kontrol-panel/icons $(sysconfdir)/X11/serverconfig $(sysconfdir)/X11/applnk/System/
	$(INSTALL_DATA) neat.desktop $(datadir)/kontrol-panel
	$(INSTALL_DATA) neat.desktop $(sysconfdir)/X11/serverconfig
	$(INSTALL_DATA) neat.desktop $(sysconfdir)/X11/applnk/System/neat.desktop
	$(INSTALL_DATA) internet-druid.desktop $(datadir)/kontrol-panel
	$(INSTALL_DATA) internet-druid.desktop $(sysconfdir)/X11/serverconfig
	$(INSTALL_DATA) internet-druid.desktop $(sysconfdir)/X11/applnk/System
	
srpm: distcheck
	rpmbuild --define "_sourcedir `pwd`" --define "_srcrpmdir `pwd`" --define "_specdir `pwd`" -ts @PACKAGE@-@VERSION@.tar.gz
